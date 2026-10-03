import pytest

from blocky.domains import covered_hostnames, validate


def test_valid_domain_is_normalized():
    assert validate(" YouTube.com ") == "youtube.com"


@pytest.mark.parametrize("entry", ["reddit", "red dit.com", "", "http://reddit.com", "reddit..com", "-bad.com", "reddit.c1"])
def test_malformed_domain_is_rejected(entry):
    with pytest.raises(ValueError):
        validate(entry)


def test_entry_also_covers_www_variant():
    assert covered_hostnames("youtube.com") == ["youtube.com", "www.youtube.com"]


def test_www_entry_is_not_expanded_again():
    assert covered_hostnames("www.youtube.com") == ["www.youtube.com"]
