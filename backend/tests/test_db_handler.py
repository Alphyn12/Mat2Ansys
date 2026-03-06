from pathlib import Path

import db_handler


def _point_cache_to_tmp(tmp_path: Path, monkeypatch):
    cache_file = tmp_path / "bizim_malzemeler.json"
    monkeypatch.setattr(db_handler, "CACHE_FILE", str(cache_file))
    monkeypatch.setattr(db_handler, "LOCK_FILE", f"{cache_file}.lock")


def test_save_and_get_material_by_url(tmp_path, monkeypatch):
    _point_cache_to_tmp(tmp_path, monkeypatch)

    db_handler.save_material(
        "SAE 8620 H",
        "https://www.matweb.com/search/datasheet.aspx?matguid=abc",
        {
            "density": 7850.0,
            "tensile_yield": 250000000.0,
            "tensile_ultimate": 460000000.0,
            "youngs_modulus": 200000000000.0,
            "poissons_ratio": 0.3,
        },
    )

    item = db_handler.get_material("https://www.matweb.com/search/datasheet.aspx?matguid=abc")
    assert item is not None
    assert item["name"] == "SAE 8620 H"
    assert item["density"] == 7850.0


def test_search_cache_shape(tmp_path, monkeypatch):
    _point_cache_to_tmp(tmp_path, monkeypatch)

    results = [{"name": "X", "url": "https://www.matweb.com/x"}]
    db_handler.save_search_cache("SAE 8620", results)
    assert db_handler.get_search_cache("sae 8620") == results
