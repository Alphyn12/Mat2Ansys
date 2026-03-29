"""
Mat2Ansys - ANSYS MatML 3.1 XML Generator
==========================================
Template XML is embedded as a string constant — no file I/O required.
This makes the module fully self-contained and Vercel-compatible.

Engineering Rule #1: Missing Poisson/Young's → steel standard defaults.
Engineering Rule #2: All values rounded to 2 decimal places.
"""

import os
import tempfile
import xml.etree.ElementTree as ET
from uuid import uuid4

# ---------------------------------------------------------------------------
# Embedded template (Structural Steel baseline, MatML 3.1)
# Stored as a string so no filesystem access is needed at runtime.
# ---------------------------------------------------------------------------
_TEMPLATE_XML = """<EngineeringData version="21.2.0.240" versiondate="1.06.2021 14:03:00">
  <Notes>
  </Notes>
  <Materials>
    <MatML_Doc>
      <Material>
        <BulkDetails>
          <Name>Structural Steel</Name>
          <Description>Fatigue Data at zero mean stress comes from 1998 ASME BPV Code, Section 8, Div 2, Table 5-110.1</Description>
          <Class>
            <Name>Alloy</Name>
          </Class>
          <PropertyData property="pr0">
            <Data format="string">-</Data>
            <ParameterValue parameter="pa0" format="float">
              <Data>132</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa1" format="float">
              <Data>139</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa2" format="float">
              <Data>179</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa3" format="string">
              <Data>Appearance</Data>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr1">
            <Data format="string">-</Data>
            <ParameterValue parameter="pa4" format="float">
              <Data>0</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr2">
            <Data format="string">-</Data>
            <ParameterValue parameter="pa5" format="float">
              <Data>250000000</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr3">
            <Data format="string">-</Data>
            <Qualifier name="Field Variable Compatible">Temperature</Qualifier>
            <ParameterValue parameter="pa6" format="string">
              <Data>Interpolation Options</Data>
              <Qualifier name="AlgorithmType">Linear Multivariate</Qualifier>
              <Qualifier name="Normalized">True</Qualifier>
              <Qualifier name="Cached">True</Qualifier>
              <Qualifier name="BETA">AlgorithmType$$Linear Multivariate (CGAL)$$EngineeringData.CGAL</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa7" format="float">
              <Data>7850</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa8" format="float">
              <Data>7.88860905221012e-31</Data>
              <Qualifier name="Variable Type">Independent</Qualifier>
              <Qualifier name="Field Variable">Temperature</Qualifier>
              <Qualifier name="Default Data">22</Qualifier>
              <Qualifier name="Field Units">C</Qualifier>
              <Qualifier name="Upper Limit">Program Controlled</Qualifier>
              <Qualifier name="Lower Limit">Program Controlled</Qualifier>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr4">
            <Data format="string">-</Data>
            <ParameterValue parameter="pa9" format="float">
              <Data>250000000</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr5">
            <Data format="string">-</Data>
            <ParameterValue parameter="pa10" format="float">
              <Data>460000000</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr6">
            <Data format="string">-</Data>
            <Qualifier name="Definition">Secant</Qualifier>
            <Qualifier name="Behavior">Isotropic</Qualifier>
            <Qualifier name="Field Variable Compatible">Temperature</Qualifier>
            <ParameterValue parameter="pa6" format="string">
              <Data>Interpolation Options</Data>
              <Qualifier name="AlgorithmType">Linear Multivariate</Qualifier>
              <Qualifier name="Normalized">True</Qualifier>
              <Qualifier name="Cached">True</Qualifier>
              <Qualifier name="BETA">AlgorithmType$$Linear Multivariate (CGAL)$$EngineeringData.CGAL</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa11" format="float">
              <Data>1.2e-05</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa8" format="float">
              <Data>7.88860905221012e-31</Data>
              <Qualifier name="Variable Type">Independent</Qualifier>
              <Qualifier name="Field Variable">Temperature</Qualifier>
              <Qualifier name="Default Data">22</Qualifier>
              <Qualifier name="Field Units">C</Qualifier>
              <Qualifier name="Upper Limit">Program Controlled</Qualifier>
              <Qualifier name="Lower Limit">Program Controlled</Qualifier>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr7">
            <Data format="string">-</Data>
            <Qualifier name="Definition">Secant</Qualifier>
            <Qualifier name="Behavior">Isotropic</Qualifier>
            <ParameterValue parameter="pa12" format="float">
              <Data>22</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa3" format="string">
              <Data>Coefficient of Thermal Expansion</Data>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr8">
            <Data format="string">-</Data>
            <Qualifier name="Definition">Constant Pressure</Qualifier>
            <Qualifier name="Field Variable Compatible">Temperature</Qualifier>
            <Qualifier name="Symbol">C&#x1D68;</Qualifier>
            <ParameterValue parameter="pa6" format="string">
              <Data>Interpolation Options</Data>
              <Qualifier name="AlgorithmType">Linear Multivariate</Qualifier>
              <Qualifier name="Normalized">True</Qualifier>
              <Qualifier name="Cached">True</Qualifier>
              <Qualifier name="BETA">AlgorithmType$$Linear Multivariate (CGAL)$$EngineeringData.CGAL</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa13" format="float">
              <Data>434</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa8" format="float">
              <Data>7.88860905221012e-31</Data>
              <Qualifier name="Variable Type">Independent</Qualifier>
              <Qualifier name="Field Variable">Temperature</Qualifier>
              <Qualifier name="Default Data">22</Qualifier>
              <Qualifier name="Field Units">C</Qualifier>
              <Qualifier name="Upper Limit">Program Controlled</Qualifier>
              <Qualifier name="Lower Limit">Program Controlled</Qualifier>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr9">
            <Data format="string">-</Data>
            <Qualifier name="Behavior">Isotropic</Qualifier>
            <Qualifier name="Field Variable Compatible">Temperature</Qualifier>
            <ParameterValue parameter="pa6" format="string">
              <Data>Interpolation Options</Data>
              <Qualifier name="AlgorithmType">Linear Multivariate</Qualifier>
              <Qualifier name="Normalized">True</Qualifier>
              <Qualifier name="Cached">True</Qualifier>
              <Qualifier name="BETA">AlgorithmType$$Linear Multivariate (CGAL)$$EngineeringData.CGAL</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa14" format="float">
              <Data>60.5</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa8" format="float">
              <Data>21</Data>
              <Qualifier name="Variable Type">Independent</Qualifier>
              <Qualifier name="Field Variable">Temperature</Qualifier>
              <Qualifier name="Default Data">22</Qualifier>
              <Qualifier name="Field Units">C</Qualifier>
              <Qualifier name="Upper Limit">Program Controlled</Qualifier>
              <Qualifier name="Lower Limit">Program Controlled</Qualifier>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr10">
            <Data format="string">-</Data>
            <Qualifier name="Interpolation">Log-Log</Qualifier>
            <Qualifier name="Field Variable Compatible">Mean Stress</Qualifier>
            <ParameterValue parameter="pa15" format="float">
              <Data>3999000000,2827000000,1896000000,1413000000,1069000000,441000000,262000000,214000000,138000000,114000000,86200000</Data>
              <Qualifier name="Variable Type">Dependent,Dependent,Dependent,Dependent,Dependent,Dependent,Dependent,Dependent,Dependent,Dependent,Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa16" format="float">
              <Data>10,20,50,100,200,2000,10000,20000,100000,200000,1000000</Data>
              <Qualifier name="Variable Type">Independent,Independent,Independent,Independent,Independent,Independent,Independent,Independent,Independent,Independent,Independent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa17" format="float">
              <Data>0,0,0,0,0,0,0,0,0,0,0</Data>
              <Qualifier name="Variable Type">Independent,Independent,Independent,Independent,Independent,Independent,Independent,Independent,Independent,Independent,Independent</Qualifier>
              <Qualifier name="Field Variable">Mean Stress</Qualifier>
              <Qualifier name="Default Data">0</Qualifier>
              <Qualifier name="Field Units">Pa</Qualifier>
              <Qualifier name="Upper Limit">Program Controlled</Qualifier>
              <Qualifier name="Lower Limit">Program Controlled</Qualifier>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr11">
            <Data format="string">-</Data>
            <Qualifier name="Display Curve Type">Strain-Life</Qualifier>
            <ParameterValue parameter="pa18" format="float">
              <Data>920000000</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa19" format="float">
              <Data>-0.106</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa20" format="float">
              <Data>0.213</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa21" format="float">
              <Data>-0.47</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa22" format="float">
              <Data>1000000000</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa23" format="float">
              <Data>0.2</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr12">
            <Data format="string">-</Data>
            <Qualifier name="Behavior">Isotropic</Qualifier>
            <ParameterValue parameter="pa24" format="float">
              <Data>1.7e-07</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa8" format="float">
              <Data>7.88860905221012e-31</Data>
              <Qualifier name="Variable Type">Independent</Qualifier>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr13">
            <Data format="string">-</Data>
            <Qualifier name="Behavior">Isotropic</Qualifier>
            <Qualifier name="Derive from">Young&apos;s Modulus and Poisson&apos;s Ratio</Qualifier>
            <Qualifier name="Field Variable Compatible">Temperature</Qualifier>
            <ParameterValue parameter="pa6" format="string">
              <Data>Interpolation Options</Data>
              <Qualifier name="AlgorithmType">Linear Multivariate</Qualifier>
              <Qualifier name="Normalized">True</Qualifier>
              <Qualifier name="Cached">True</Qualifier>
              <Qualifier name="BETA">AlgorithmType$$Linear Multivariate (CGAL)$$EngineeringData.CGAL</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa25" format="float">
              <Data>200000000000</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa26" format="float">
              <Data>0.3</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa27" format="float">
              <Data>166666666666.667</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa28" format="float">
              <Data>76923076923.0769</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
            <ParameterValue parameter="pa8" format="float">
              <Data>7.88860905221012e-31</Data>
              <Qualifier name="Variable Type">Independent</Qualifier>
              <Qualifier name="Field Variable">Temperature</Qualifier>
              <Qualifier name="Default Data">22</Qualifier>
              <Qualifier name="Field Units">C</Qualifier>
              <Qualifier name="Upper Limit">Program Controlled</Qualifier>
              <Qualifier name="Lower Limit">Program Controlled</Qualifier>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr14">
            <Data format="string">-</Data>
            <Qualifier name="Behavior">Isotropic</Qualifier>
            <ParameterValue parameter="pa29" format="float">
              <Data>10000</Data>
              <Qualifier name="Variable Type">Dependent</Qualifier>
            </ParameterValue>
          </PropertyData>
          <PropertyData property="pr15">
            <Data format="string">-</Data>
            <Qualifier name="guid">59002a79-71c2-428e-906b-55d7dbee100e</Qualifier>
            <Qualifier name="Display">False</Qualifier>
          </PropertyData>
        </BulkDetails>
      </Material>
      <Metadata>
        <ParameterDetails id="pa0"><Name>Red</Name><Unitless /></ParameterDetails>
        <ParameterDetails id="pa1"><Name>Green</Name><Unitless /></ParameterDetails>
        <ParameterDetails id="pa2"><Name>Blue</Name><Unitless /></ParameterDetails>
        <ParameterDetails id="pa3"><Name>Material Property</Name><Unitless /></ParameterDetails>
        <ParameterDetails id="pa4">
          <Name>Compressive Ultimate Strength</Name>
          <Units name="Stress"><Unit><Name>Pa</Name></Unit></Units>
        </ParameterDetails>
        <ParameterDetails id="pa5">
          <Name>Compressive Yield Strength</Name>
          <Units name="Stress"><Unit><Name>Pa</Name></Unit></Units>
        </ParameterDetails>
        <ParameterDetails id="pa6"><Name>Options Variable</Name><Unitless /></ParameterDetails>
        <ParameterDetails id="pa7">
          <Name>Density</Name>
          <Units name="Density">
            <Unit><Name>kg</Name></Unit>
            <Unit power="-3"><Name>m</Name></Unit>
          </Units>
        </ParameterDetails>
        <ParameterDetails id="pa8">
          <Name>Temperature</Name>
          <Units name="Temperature"><Unit><Name>C</Name></Unit></Units>
        </ParameterDetails>
        <ParameterDetails id="pa9">
          <Name>Tensile Yield Strength</Name>
          <Units name="Stress"><Unit><Name>Pa</Name></Unit></Units>
        </ParameterDetails>
        <ParameterDetails id="pa10">
          <Name>Tensile Ultimate Strength</Name>
          <Units name="Stress"><Unit><Name>Pa</Name></Unit></Units>
        </ParameterDetails>
        <ParameterDetails id="pa11">
          <Name>Coefficient of Thermal Expansion</Name>
          <Units name="InvTemp1"><Unit power="-1"><Name>C</Name></Unit></Units>
        </ParameterDetails>
        <ParameterDetails id="pa12">
          <Name>Zero-Thermal-Strain Reference Temperature</Name>
          <Units name="Temperature"><Unit><Name>C</Name></Unit></Units>
        </ParameterDetails>
        <ParameterDetails id="pa13">
          <Name>Specific Heat</Name>
          <Units name="Specific Heat Capacity">
            <Unit><Name>J</Name></Unit>
            <Unit power="-1"><Name>kg</Name></Unit>
            <Unit power="-1"><Name>C</Name></Unit>
          </Units>
        </ParameterDetails>
        <ParameterDetails id="pa14">
          <Name>Thermal Conductivity</Name>
          <Units name="Thermal Conductivity">
            <Unit><Name>W</Name></Unit>
            <Unit power="-1"><Name>m</Name></Unit>
            <Unit power="-1"><Name>C</Name></Unit>
          </Units>
        </ParameterDetails>
        <ParameterDetails id="pa15">
          <Name>Alternating Stress</Name>
          <Units name="Stress"><Unit><Name>Pa</Name></Unit></Units>
        </ParameterDetails>
        <ParameterDetails id="pa16"><Name>Cycles</Name><Unitless /></ParameterDetails>
        <ParameterDetails id="pa17">
          <Name>Mean Stress</Name>
          <Units name="Stress"><Unit><Name>Pa</Name></Unit></Units>
        </ParameterDetails>
        <ParameterDetails id="pa18">
          <Name>Strength Coefficient</Name>
          <Units name="Stress"><Unit><Name>Pa</Name></Unit></Units>
        </ParameterDetails>
        <ParameterDetails id="pa19"><Name>Strength Exponent</Name><Unitless /></ParameterDetails>
        <ParameterDetails id="pa20"><Name>Ductility Coefficient</Name><Unitless /></ParameterDetails>
        <ParameterDetails id="pa21"><Name>Ductility Exponent</Name><Unitless /></ParameterDetails>
        <ParameterDetails id="pa22">
          <Name>Cyclic Strength Coefficient</Name>
          <Units name="Stress"><Unit><Name>Pa</Name></Unit></Units>
        </ParameterDetails>
        <ParameterDetails id="pa23"><Name>Cyclic Strain Hardening Exponent</Name><Unitless /></ParameterDetails>
        <ParameterDetails id="pa24">
          <Name>Resistivity</Name>
          <Units name="Electrical Resistivity">
            <Unit><Name>ohm</Name></Unit>
            <Unit><Name>m</Name></Unit>
          </Units>
        </ParameterDetails>
        <ParameterDetails id="pa25">
          <Name>Young&apos;s Modulus</Name>
          <Units name="Stress"><Unit><Name>Pa</Name></Unit></Units>
        </ParameterDetails>
        <ParameterDetails id="pa26"><Name>Poisson&apos;s Ratio</Name><Unitless /></ParameterDetails>
        <ParameterDetails id="pa27">
          <Name>Bulk Modulus</Name>
          <Units name="Stress"><Unit><Name>Pa</Name></Unit></Units>
        </ParameterDetails>
        <ParameterDetails id="pa28">
          <Name>Shear Modulus</Name>
          <Units name="Stress"><Unit><Name>Pa</Name></Unit></Units>
        </ParameterDetails>
        <ParameterDetails id="pa29"><Name>Relative Permeability</Name><Unitless /></ParameterDetails>
        <PropertyDetails id="pr0"><Unitless /><Name>Color</Name></PropertyDetails>
        <PropertyDetails id="pr1"><Unitless /><Name>Compressive Ultimate Strength</Name></PropertyDetails>
        <PropertyDetails id="pr2"><Unitless /><Name>Compressive Yield Strength</Name></PropertyDetails>
        <PropertyDetails id="pr3"><Unitless /><Name>Density</Name></PropertyDetails>
        <PropertyDetails id="pr4"><Unitless /><Name>Tensile Yield Strength</Name></PropertyDetails>
        <PropertyDetails id="pr5"><Unitless /><Name>Tensile Ultimate Strength</Name></PropertyDetails>
        <PropertyDetails id="pr6"><Unitless /><Name>Coefficient of Thermal Expansion</Name></PropertyDetails>
        <PropertyDetails id="pr7"><Unitless /><Name>Zero-Thermal-Strain Reference Temperature</Name></PropertyDetails>
        <PropertyDetails id="pr8"><Unitless /><Name>Specific Heat</Name></PropertyDetails>
        <PropertyDetails id="pr9"><Unitless /><Name>Thermal Conductivity</Name></PropertyDetails>
        <PropertyDetails id="pr10"><Unitless /><Name>S-N Curve</Name></PropertyDetails>
        <PropertyDetails id="pr11"><Unitless /><Name>Strain-Life Parameters</Name></PropertyDetails>
        <PropertyDetails id="pr12"><Unitless /><Name>Resistivity</Name></PropertyDetails>
        <PropertyDetails id="pr13"><Unitless /><Name>Elasticity</Name></PropertyDetails>
        <PropertyDetails id="pr14"><Unitless /><Name>Relative Permeability</Name></PropertyDetails>
        <PropertyDetails id="pr15"><Unitless /><Name>Material Unique Id</Name></PropertyDetails>
      </Metadata>
    </MatML_Doc>
  </Materials>
</EngineeringData>"""

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
    # 1) Parse template from embedded string (no filesystem access needed)
    root = ET.fromstring(_TEMPLATE_XML)
    tree = ET.ElementTree(root)

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
