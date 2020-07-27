"""Tests for the root polymatheia package."""
from polymatheia import placeholder


def test_placeholder():
    """Test the placeholder function."""
    assert placeholder() == '<<placeholder>>'
