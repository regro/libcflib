from pathlib import Path

from libcflib.symbol_inspection import get_all_symbol_names


def test_get_all_symbol_names():
    top_dir = Path(__file__).parent / Path("..") / Path("libcflib")
    assert "libcflib.symbol_inspection.get_all_symbol_names" in get_all_symbol_names(
        str(top_dir)
    )
