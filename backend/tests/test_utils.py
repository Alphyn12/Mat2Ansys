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
