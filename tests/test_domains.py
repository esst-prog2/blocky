import pytest

from blocky.domains import covered_hostnames, validate


def test_valid_domain_is_normalized():
    assert validate(" YouTube.com ") == "youtube.com"


@pytest.mark.parametrize("entry", ["reddit", "red dit.com", "", "https://reddit/", "reddit..com", "-bad.com", "reddit.c1"])
def test_malformed_domain_is_rejected(entry):
    with pytest.raises(ValueError):
        validate(entry)


@pytest.mark.parametrize(
    "entry, domain",
    [
        ("https://www.reddit.com/r/all?sort=new", "www.reddit.com"),
        ("http://reddit.com", "reddit.com"),
        ("reddit.com/r/all", "reddit.com"),
        ("https://nos.nl:443/#top", "nos.nl"),
    ],
)
def test_pasted_address_is_reduced_to_its_domain(entry, domain):
    assert validate(entry) == domain


def test_entry_also_covers_www_variant():
    assert covered_hostnames("youtube.com") == ["youtube.com", "www.youtube.com"]


def test_www_entry_is_not_expanded_again():
    assert covered_hostnames("www.youtube.com") == ["www.youtube.com"]
