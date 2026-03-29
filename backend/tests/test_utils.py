from utils import clean_value, detect_unit, format_material_data_detailed


def test_detect_unit_prefers_kpa_over_pa():
    assert detect_unit("200 kPa") in {"kPa", "kpa"}


def test_clean_value_kpa_conversion():
    assert clean_value("200 kPa", "tensile_yield") == 200000.0


def test_clean_value_range_and_scientific_notation():
    assert clean_value("0.27 - 0.30", "poissons_ratio") == 0.29
    assert clean_value("2.00e+11 Pa", "youngs_modulus") == 200000000000.0


def test_format_material_data_reports_defaults():
    detailed = format_material_data_detailed({"density": "7.85 g/cc"})
    assert detailed["properties"]["density"] == 7850.0
    assert "youngs_modulus" in detailed["used_defaults"]
    assert "poissons_ratio" in detailed["missing_or_unparsed"]


def test_parse_raw_matweb_text_american_thousands_comma():
    """55,800 psi must be read as 55800 psi, not 55.8 psi."""
    from utils import parse_raw_matweb_text
    raw = (
        "Tensile Strength, Yield  55,800 psi\n"
        "Tensile Strength, Ultimate  75,000 psi\n"
        "Modulus of Elasticity  200 GPa\n"
        "Density  7.85 g/cc\n"
        "Poisson's Ratio  0.29\n"
    )
    result = parse_raw_matweb_text(raw)
    props = result["properties"]
    expected_yield = round(55800 * 6894.757, 2)
    assert props["tensile_yield"] == expected_yield
    assert "tensile_yield" not in result["used_defaults"]
