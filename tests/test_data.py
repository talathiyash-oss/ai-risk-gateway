import re

from airg.data import generate_clients, load_clients, write_clients


def test_meets_minimum_size():
    records = generate_clients(seed=42)
    assert len(records) >= 50
    assert len({r.rm_id for r in records}) >= 10


def test_identifiers_are_unique_and_well_formed():
    records = generate_clients(seed=42)
    assert len({r.client_id for r in records}) == len(records)
    assert len({r.account_number for r in records}) == len(records)
    assert len({r.name for r in records}) == len(records)
    assert all(re.fullmatch(r"C-\d{4}", r.client_id) for r in records)
    assert all(re.fullmatch(r"BMT-\d{8}", r.account_number) for r in records)


def test_same_seed_gives_byte_identical_files(tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    write_clients(generate_clients(seed=7), a)
    write_clients(generate_clients(seed=7), b)
    assert a.read_bytes() == b.read_bytes()


def test_different_seed_gives_different_data():
    assert generate_clients(seed=1) != generate_clients(seed=2)


def test_round_trip(tmp_path):
    records = generate_clients(seed=42)
    path = tmp_path / "clients.json"
    write_clients(records, path)
    assert load_clients(path) == records
