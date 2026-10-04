"""Property tests: each states a rule that must hold for every input, and Hypothesis searches for a counterexample."""

from datetime import datetime, timedelta

from hypothesis import assume, example, given, settings
from hypothesis import strategies as st

from blocky import config as config_module
from blocky import domainfield, hosts, rules, timefield
from blocky.config import Config
from blocky.domains import covered_hostnames, validate
from blocky.schedule import Schedule, parse_time, window_end

labels = st.from_regex(r"[a-z0-9]([a-z0-9-]{0,20}[a-z0-9])?", fullmatch=True)
top_levels = st.from_regex(r"[a-z]{2,6}", fullmatch=True)
domains = st.builds(lambda parts, top: ".".join([*parts, top]), st.lists(labels, min_size=1, max_size=3), top_levels)
times = st.builds(lambda hour, minute: f"{hour:02d}:{minute:02d}", st.integers(0, 23), st.integers(0, 59))
# Text that looks like digits: Unicode digits (Nd) and digit-like signs such as superscripts (No).
digit_like = st.one_of(st.text(), st.text(st.characters(categories=("Nd", "No")), max_size=3))
moments = st.datetimes(min_value=datetime(2026, 1, 1), max_value=datetime(2027, 12, 31))


@st.composite
def schedules(draw):
    start, end = sorted(draw(st.lists(times, min_size=2, max_size=2, unique=True)))
    weekdays = sorted(draw(st.sets(st.integers(0, 6))))
    return Schedule(weekdays=weekdays, start=start, end=end)


# Lines another program could have put in the hosts file: anything but a line break or Blocky's markers.
hosts_lines = st.text(st.characters(exclude_characters="\r\n")).filter(
    lambda line: line.strip() not in (hosts.BEGIN, hosts.END)
)


@given(st.lists(hosts_lines), st.lists(domains), st.booleans())
@example(lines=["127.0.0.1 a\x85b"], hostnames=[], windows_newlines=False)  # found by Hypothesis
def test_hosts_render_keeps_other_lines_and_removes_cleanly(lines, hostnames, windows_newlines):
    newline = "\r\n" if windows_newlines else "\n"
    original = "".join(line + newline for line in lines)
    blocked = hosts.render(original, hostnames)
    assert hosts.render(blocked, hostnames) == blocked
    assert hosts.render(blocked, []) == original


@given(domains, st.sampled_from(["", "http://", "https://"]), st.sampled_from(["", "/", "/r/all?x=1", ":443/"]))
def test_a_valid_domain_survives_being_typed_as_a_web_address(domain, scheme, rest):
    assert validate(f"  {scheme}{domain.upper()}{rest} ") == domain


@given(st.text())
def test_validation_either_rejects_or_gives_a_stable_domain(text):
    try:
        domain = validate(text)
    except ValueError:
        return
    assert validate(domain) == domain
    assert domainfield.allowed(domain)
    for hostname in covered_hostnames(domain):
        assert hosts.render("", [hostname]).count("\n") == 3


@given(st.text())
def test_a_paste_always_fits_the_domain_box(text):
    assert domainfield.allowed(domainfield.cleaned_paste(text))


@given(st.text(), st.lists(domains))
def test_the_domain_hint_never_crashes(text, existing):
    addable, _ = domainfield.hint(text, existing)
    if addable:
        assert validate(text) not in existing


@given(st.integers(0, 23), st.integers(0, 59))
def test_parse_time_pads_any_real_time(hour, minute):
    assert parse_time(f" {hour}:{minute:02d} ") == f"{hour:02d}:{minute:02d}"


@given(digit_like)
@example("\u0661\u0662:\u0663\u0660")  # Arabic-Indic digits, found by Hypothesis
def test_parse_time_either_rejects_or_gives_a_valid_time(text):
    try:
        result = parse_time(text)
    except ValueError:
        return
    assert result in {f"{h:02d}:{m:02d}" for h in range(24) for m in range(60)}


@given(digit_like, st.sampled_from([23, 59]))
@example("\u00b2", 59)  # superscript two, found by Hypothesis
def test_time_box_never_crashes(text, maximum):
    if timefield.allowed(text, maximum):
        assert len(timefield.finish(text, "09")) == 2


@given(digit_like, st.integers(-100, 100), st.sampled_from([23, 59]))
def test_stepping_a_time_box_stays_in_range(text, delta, maximum):
    result = timefield.step(text, delta, maximum)
    assert timefield.allowed(result, maximum)
    assert len(result) == 2


@given(schedules(), moments)
def test_window_end_matches_the_schedule(schedule, now):
    end = window_end(schedule, now)
    inside = now.weekday() in schedule.weekdays and schedule.start <= f"{now:%H:%M}" < schedule.end
    assert (end is not None) == inside
    if end is not None:
        assert now < end <= now + timedelta(days=1)
        assert f"{end:%H:%M}" == schedule.end


@given(st.lists(domains, unique=True), schedules(), st.lists(st.text()))
@example(domain_list=[], schedule=Schedule(), shortlist=["walk\x85"])  # found by Hypothesis
# Writes a real file, which on GitHub's Windows runner can take over a second; no per-example time limit.
@settings(deadline=None)
def test_a_saved_config_loads_back_the_same(tmp_path_factory, domain_list, schedule, shortlist):
    path = tmp_path_factory.mktemp("config") / "config.yaml"
    config = Config(domains=domain_list, schedule=schedule, shortlist=shortlist)
    config_module.save(path, config)
    assert config_module.load(path) == config


@st.composite
def moments_inside(draw, schedule):
    start = datetime(2026, 10, 5) + timedelta(days=draw(st.sampled_from(schedule.weekdays)))
    first = datetime.combine(start, datetime.strptime(schedule.start, "%H:%M").time())
    last = datetime.combine(start, datetime.strptime(schedule.end, "%H:%M").time()) - timedelta(microseconds=1)
    return draw(st.datetimes(min_value=first, max_value=last))


@given(st.lists(domains, min_size=1, unique=True), schedules().filter(lambda s: s.weekdays), st.data())
def test_override_and_undo_release_and_reblock_exactly_one_domain(domain_list, schedule, data):
    config = Config(domains=domain_list, schedule=schedule)
    now = data.draw(moments_inside(schedule))
    blocked_before = rules.blocked_domains(config, now)
    assert set(blocked_before) == {host for domain in domain_list for host in covered_hostnames(domain)}

    domain = data.draw(st.sampled_from(domain_list))
    rules.override(config, domain, "reason", now)
    blocked = rules.blocked_domains(config, now)
    assert set(blocked) == {host for other in domain_list if other != domain for host in covered_hostnames(other)}

    rules.undo_override(config, domain, now)
    assert rules.blocked_domains(config, now) == blocked_before


@given(st.lists(domains, unique=True), schedules(), moments)
def test_nothing_is_blocked_outside_the_window(domain_list, schedule, now):
    assume(window_end(schedule, now) is None)
    assert rules.blocked_domains(Config(domains=domain_list, schedule=schedule), now) == []
