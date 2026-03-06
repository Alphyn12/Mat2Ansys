import os
import xml.etree.ElementTree as ET

from xml_generator import generate_ansys_xml


def _read_param_value(root: ET.Element, prop_id: str, param_id: str) -> str:
    for prop_data in root.iter("PropertyData"):
        if prop_data.get("property") != prop_id:
            continue
        for param_val in prop_data.findall("ParameterValue"):
            if param_val.get("parameter") == param_id:
                data_el = param_val.find("Data")
                return data_el.text if data_el is not None and data_el.text is not None else ""
    return ""


def test_generate_xml_writes_unique_file_and_values():
    props = {
        "density": 8000.0,
        "tensile_yield": 300000000.0,
        "tensile_ultimate": 500000000.0,
        "youngs_modulus": 210000000000.0,
        "poissons_ratio": 0.29,
    }

    p1 = generate_ansys_xml("Material A", props)
    p2 = generate_ansys_xml("Material A", props)
    assert p1 != p2

    tree = ET.parse(p1)
    root = tree.getroot()
    assert _read_param_value(root, "pr3", "pa7") == "8000"
    assert _read_param_value(root, "pr4", "pa9") == "300000000"
    assert _read_param_value(root, "pr13", "pa25") == "210000000000"

    os.remove(p1)
    os.remove(p2)
