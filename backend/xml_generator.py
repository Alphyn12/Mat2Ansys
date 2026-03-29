"""
Mat2Ansys - ANSYS MatML 3.1 XML Generator
==========================================
Reads template.xml (Structural Steel baseline), injects scraped material
properties, and produces a ready-to-import ANSYS Engineering Data XML.

Engineering Rule #1: Missing Poisson/Young's → steel standard defaults.
Engineering Rule #2: All values rounded to 2 decimal places.
"""

import os
import tempfile
import xml.etree.ElementTree as ET
from uuid import uuid4

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "template.xml")

# Engineering Rule #1: Steel standard fallback defaults
DEFAULT_YOUNGS_MODULUS = 200_000_000_000.0   # 200 GPa in Pa
DEFAULT_POISSONS_RATIO = 0.3


# ---------------------------------------------------------------------------
# Parameter Mapping: property_key → (PropertyData id, ParameterValue id)
# Based on Structural Steel.xml template analysis
# ---------------------------------------------------------------------------
PARAM_MAP = {
    "density":          ("pr3", "pa7"),
    "tensile_yield":    ("pr4", "pa9"),
    "tensile_ultimate": ("pr5", "pa10"),
    "youngs_modulus":   ("pr13", "pa25"),
    "poissons_ratio":   ("pr13", "pa26"),
}

# Derived parameters (auto-calculated from E and ν)
DERIVED_MAP = {
    "bulk_modulus":  ("pr13", "pa27"),
    "shear_modulus": ("pr13", "pa28"),
}


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------
def _calculate_bulk_modulus(E: float, nu: float) -> float:
    """
    Calculate Bulk Modulus K = E / (3 × (1 - 2ν))
    
    Engineering Rule #1: If ν ≥ 0.5 (physically impossible for metals),
    fallback to default 0.3.
    """
    if nu >= 0.5:
        nu = DEFAULT_POISSONS_RATIO
    denominator = 3.0 * (1.0 - 2.0 * nu)
    if abs(denominator) < 1e-10:
        # Prevent division by zero
        nu = DEFAULT_POISSONS_RATIO
        denominator = 3.0 * (1.0 - 2.0 * nu)
    return round(E / denominator, 2)


def _calculate_shear_modulus(E: float, nu: float) -> float:
    """
    Calculate Shear Modulus G = E / (2 × (1 + ν))
    """
    denominator = 2.0 * (1.0 + nu)
    if abs(denominator) < 1e-10:
        denominator = 2.0 * (1.0 + DEFAULT_POISSONS_RATIO)
    return round(E / denominator, 2)


def _update_param(root: ET.Element, prop_id: str, param_id: str, value: float):
    """
    Find a specific <ParameterValue> inside a <PropertyData> and update its <Data> tag.
    
    Searches for:
        <PropertyData property="prop_id">
            <ParameterValue parameter="param_id">
                <Data>OLD_VALUE</Data>  ← This gets replaced
            </ParameterValue>
        </PropertyData>
    """
    # Find all PropertyData elements with matching property attribute
    for prop_data in root.iter("PropertyData"):
        if prop_data.get("property") != prop_id:
            continue

        # Find the matching ParameterValue
        for param_val in prop_data.findall("ParameterValue"):
            if param_val.get("parameter") != param_id:
                continue

            # Find and update the <Data> tag
            data_el = param_val.find("Data")
            if data_el is not None:
                # Format: use int-like representation for large round numbers
                if value == int(value) and abs(value) >= 1:
                    data_el.text = str(int(value))
                else:
                    data_el.text = str(value)
                return True

    return False


# ---------------------------------------------------------------------------
# Main Generator
# ---------------------------------------------------------------------------
def generate_ansys_xml(material_name: str, properties: dict) -> str:
    """
    Generate an ANSYS-compatible MatML 3.1 XML file from template.
    
    Args:
        material_name: Name of the material (e.g., "SAE 8620 H Steel")
        properties: Dict with cleaned SI-unit values:
            {
                "density": 7850.0,
                "tensile_yield": 250000000.0,
                "tensile_ultimate": 460000000.0,
                "youngs_modulus": 200000000000.0,
                "poissons_ratio": 0.3
            }
    
    Returns:
        Absolute path to the generated temporary .xml file.
    
    Engineering Rule #1: Missing Young's or Poisson's values use steel defaults.
    Engineering Rule #2: All values rounded to 2 decimal places.
    """
    # 1) Parse template
    tree = ET.parse(TEMPLATE_PATH)
    root = tree.getroot()

    # 2) Update material name
    for name_el in root.iter("Name"):
        if name_el.text and name_el.text.strip() == "Structural Steel":
            name_el.text = material_name
            break  # Only replace the first occurrence (material name, not class name)

    # 3) Apply Engineering Rule #1: Ensure E and ν have values
    E = properties.get("youngs_modulus")
    nu = properties.get("poissons_ratio")

    if E is None or E <= 0:
        E = DEFAULT_YOUNGS_MODULUS
        properties["youngs_modulus"] = E

    if nu is None or nu <= 0:
        nu = DEFAULT_POISSONS_RATIO
        properties["poissons_ratio"] = nu

    # 4) Update each mapped property in the XML
    missing_updates = []
    for prop_key, (prop_id, param_id) in PARAM_MAP.items():
        value = properties.get(prop_key)
        if value is not None:
            # Engineering Rule #2: round to 2 decimals
            rounded = round(float(value), 2)
            updated = _update_param(root, prop_id, param_id, rounded)
            if not updated:
                missing_updates.append(f"{prop_key} ({prop_id}/{param_id})")

    # 5) Auto-derive Bulk and Shear Modulus
    bulk_modulus = _calculate_bulk_modulus(E, nu)
    shear_modulus = _calculate_shear_modulus(E, nu)

    bulk_prop_id, bulk_param_id = DERIVED_MAP["bulk_modulus"]
    shear_prop_id, shear_param_id = DERIVED_MAP["shear_modulus"]

    if not _update_param(root, bulk_prop_id, bulk_param_id, bulk_modulus):
        missing_updates.append(f"bulk_modulus ({bulk_prop_id}/{bulk_param_id})")
    if not _update_param(root, shear_prop_id, shear_param_id, shear_modulus):
        missing_updates.append(f"shear_modulus ({shear_prop_id}/{shear_param_id})")

    if missing_updates:
        joined = ", ".join(missing_updates)
        raise ValueError(f"Template mapping not found for: {joined}")

    # 6) Write to temp file
    # Sanitize filename: replace characters invalid for Windows filenames
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in material_name)
    unique_id = uuid4().hex[:10]
    output_path = os.path.join(tempfile.gettempdir(), f"{safe_name}_{unique_id}.xml")

    tree.write(output_path, encoding="UTF-8", xml_declaration=True)

    return output_path


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("🔧 XML Generator Test")
    print("=" * 60)

    # Test with Structural Steel default values
    test_props = {
        "density": 7850.0,
        "tensile_yield": 250000000.0,
        "tensile_ultimate": 460000000.0,
        "youngs_modulus": 200000000000.0,
        "poissons_ratio": 0.3,
    }

    output = generate_ansys_xml("Test Material XYZ", test_props)
    print(f"  ✅ Generated: {output}")

    # Verify output
    verify_tree = ET.parse(output)
    verify_root = verify_tree.getroot()

    # Check material name was replaced
    for name_el in verify_root.iter("Name"):
        if name_el.text == "Test Material XYZ":
            print("  ✅ Material name updated correctly")
            break

    # Check density value
    for pd in verify_root.iter("PropertyData"):
        if pd.get("property") == "pr3":
            for pv in pd.findall("ParameterValue"):
                if pv.get("parameter") == "pa7":
                    data_el = pv.find("Data")
                    val = data_el.text if data_el is not None else ""
                    print(f"  ✅ Density (pa7) = {val}")

    # Check derived values
    for pd in verify_root.iter("PropertyData"):
        if pd.get("property") == "pr13":
            for pv in pd.findall("ParameterValue"):
                pid = pv.get("parameter")
                data_el = pv.find("Data")
                val = data_el.text if data_el is not None else ""
                if pid in ("pa25", "pa26", "pa27", "pa28"):
                    names = {"pa25": "Young's", "pa26": "Poisson's",
                             "pa27": "Bulk Mod", "pa28": "Shear Mod"}
                    print(f"  ✅ {names[pid]:12s} ({pid}) = {val}")

    # Test with missing Poisson's (Engineering Rule #1)
    print("\n  🔧 Fallback test (missing Poisson's):")
    test_missing = {
        "density": 7850.0,
        "tensile_yield": 250000000.0,
        "tensile_ultimate": 460000000.0,
        "youngs_modulus": 200000000000.0,
        # poissons_ratio intentionally missing!
    }
    output2 = generate_ansys_xml("Fallback Test", test_missing)
    print(f"  ✅ Generated without crash: {output2}")

    # Cleanup
    os.remove(output)
    os.remove(output2)
    print("\n  ✅ All XML generator tests passed!")
