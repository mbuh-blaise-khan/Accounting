"""Part 1 hardening: unit tests for the pure reference-query parser.

The Journal's Reference column shows "TX-{id:04d}". These tests lock the
search contract WITHOUT any database: ids resolve from common user inputs,
and digit-less queries (a description word, a single letter) can never match
a reference and must yield None -> zero rows at the service layer.
"""
from app.services.journal_service import parse_reference_query


def test_full_reference_with_prefix():
    assert parse_reference_query("TX-0016") == 16


def test_full_reference_lowercase_and_underscore_variants():
    assert parse_reference_query("tx_0012") == 12
    assert parse_reference_query("TX 12") == 12
    assert parse_reference_query("tx-12") == 12


def test_bare_digits_resolve_to_id():
    assert parse_reference_query("0012") == 12
    assert parse_reference_query("12") == 12


def test_whitespace_is_ignored():
    assert parse_reference_query("  TX-0007  ") == 7


def test_digitless_query_yields_none():
    # A description word or a single letter can never match a reference.
    assert parse_reference_query("one") is None
    assert parse_reference_query("T") is None
    assert parse_reference_query("") is None
    assert parse_reference_query(None) is None


def test_embedded_number_still_resolves():
    # Loose by design: any digit token in the query resolves to an id.
    assert parse_reference_query("ref nr 5 please") == 5
