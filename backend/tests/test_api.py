from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_search_rejects_blank_query():
    res = client.get("/api/search", params={"q": "   "})
    assert res.status_code == 422
    payload = res.json()
    assert payload["detail"]["error_code"] == "INVALID_QUERY"


def test_generate_rejects_non_matweb_url():
    res = client.post(
        "/api/generate",
        json={"name": "X", "url": "https://localhost/admin"},
    )
    assert res.status_code == 422
    payload = res.json()
    assert payload["detail"]["error_code"] == "INVALID_URL"


def test_generate_sets_default_headers(monkeypatch, tmp_path):
    xml_file = tmp_path / "out.xml"
    xml_file.write_text("<EngineeringData />", encoding="utf-8")

    monkeypatch.setattr(main, "validate_and_normalize_matweb_url", lambda url: url)
    monkeypatch.setattr(main, "get_material", lambda _url: None)
    monkeypatch.setattr(
        main,
        "get_material_details",
        lambda _url: {
            "density": "7.85 g/cc",
            "tensile_yield": "250 MPa",
            "tensile_ultimate": "460 MPa",
            "youngs_modulus": "200 GPa",
            # Missing Poisson on purpose
        },
    )
    monkeypatch.setattr(main, "save_material", lambda *args, **kwargs: None)
    monkeypatch.setattr(main, "generate_ansys_xml", lambda *_args, **_kwargs: str(xml_file))

    res = client.post(
        "/api/generate",
        json={"name": "SAE 8620", "url": "https://www.matweb.com/x"},
    )
    assert res.status_code == 200
    assert res.headers.get("x-mat2ansys-defaults-count") == "1"
    assert "poissons_ratio" in (res.headers.get("x-mat2ansys-used-defaults") or "")
