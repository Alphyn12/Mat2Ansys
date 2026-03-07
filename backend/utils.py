"""
Mat2Ansys - Data Cleaning & Unit Conversion Utilities
=====================================================
Cleans raw MatWeb text data and converts to ANSYS-compatible SI units.

Engineering Rule #2: All float values are rounded to 2 decimal places
with round(value, 2) for XML integrity.
"""

import re
from typing import Optional


# ---------------------------------------------------------------------------
# Unit Conversion Multipliers
# ---------------------------------------------------------------------------
DENSITY_CONVERSIONS = {
    "g/cc": 1000.0,
    "g/cm³": 1000.0,
    "g/cm3": 1000.0,
    "kg/m³": 1.0,
    "kg/m3": 1.0,
    "lb/in³": 27679.9,
    "lb/in3": 27679.9,
}

STRESS_CONVERSIONS = {
    "kPa": 1_000.0,
    "kpa": 1_000.0,
    "GPa": 1_000_000_000.0,
    "gpa": 1_000_000_000.0,
    "MPa": 1_000_000.0,
    "mpa": 1_000_000.0,
    "ksi": 6_894_757.0,
    "psi": 6_894.757,
    "Pa": 1.0,
    "pa": 1.0,
}

# Properties that use stress units (Pa)
STRESS_PROPERTIES = {
    "tensile_yield",
    "tensile_ultimate",
    "youngs_modulus",
    "compressive_yield",
    "compressive_ultimate",
}

# Properties that use density units (kg/m³)
DENSITY_PROPERTIES = {
    "density",
}

# Properties that are unitless
UNITLESS_PROPERTIES = {
    "poissons_ratio",
}

# Prefer longer tokens first to avoid partial match issues (e.g., kPa vs Pa)
DENSITY_UNIT_ORDER = sorted(DENSITY_CONVERSIONS.keys(), key=len, reverse=True)
STRESS_UNIT_ORDER = sorted(STRESS_CONVERSIONS.keys(), key=len, reverse=True)

# ---------------------------------------------------------------------------
# Engineering Rule #1: Steel industry standard fallback defaults
# ---------------------------------------------------------------------------
STEEL_DEFAULTS = {
    "density": 7850.0,           # kg/m³
    "tensile_yield": 250e6,      # Pa (250 MPa)
    "tensile_ultimate": 460e6,   # Pa (460 MPa)
    "youngs_modulus": 200e9,     # Pa (200 GPa)
    "poissons_ratio": 0.3,      # Unitless
}


# ---------------------------------------------------------------------------
# Core Functions
# ---------------------------------------------------------------------------
def extract_number(raw: Optional[str]) -> Optional[float]:
    """
    Extract the first numeric value from a raw string.
    
    Handles formats like:
        "7.85 g/cc"         -> 7.85
        "200 GPa"           -> 200.0
        "250 MPa"           -> 250.0
        "0.27 - 0.30"       -> 0.285 (average of range)
        "36.3 ksi"          -> 36.3
        "7,850 kg/m³"       -> 7850.0
        "2.00e+11"          -> 2e11
    
    Returns None if no number found.
    """
    if not raw or not isinstance(raw, str):
        return None

    raw = raw.strip()

    # Check for range format "X - Y" → take average
    range_match = re.match(
        r"([\d.,]+(?:[eE][+-]?\d+)?)\s*[-–—]\s*([\d.,]+(?:[eE][+-]?\d+)?)",
        raw
    )
    if range_match:
        try:
            val1 = float(range_match.group(1).replace(",", ""))
            val2 = float(range_match.group(2).replace(",", ""))
            return (val1 + val2) / 2.0
        except ValueError:
            pass

    # Extract first number (including scientific notation)
    num_match = re.search(r"([\d.,]+(?:[eE][+-]?\d+)?)", raw)
    if num_match:
        try:
            return float(num_match.group(1).replace(",", ""))
        except ValueError:
            return None

    return None


def detect_unit(raw: Optional[str]) -> Optional[str]:
    """
    Detect the unit from a raw MatWeb string.
    
    Returns the matched unit key or None.
    """
    if not raw or not isinstance(raw, str):
        return None

    lowered = raw.lower()

    # Density tokens can include special chars (/ and superscripts), substring check is enough.
    for unit in DENSITY_UNIT_ORDER:
        if unit.lower() in lowered:
            return unit

    # Stress units should be token-aware to avoid matching "Pa" inside "kPa".
    for unit in STRESS_UNIT_ORDER:
        pattern = rf"(?<![a-zA-Z]){re.escape(unit)}(?![a-zA-Z])"
        if re.search(pattern, raw, flags=re.IGNORECASE):
            return unit

    return None


def clean_value(raw: Optional[str], property_type: str) -> Optional[float]:
    """
    Extract numeric value from raw MatWeb text and convert to SI units.
    
    Args:
        raw: Raw text from MatWeb (e.g., "7.85 g/cc", "200 GPa")
        property_type: One of "density", "tensile_yield", "tensile_ultimate",
                       "youngs_modulus", "poissons_ratio"
    
    Returns:
        Float value in SI units, rounded to 2 decimal places.
        Returns None if value cannot be parsed.
    
    Engineering Rule #2: All values rounded with round(value, 2).
    """
    number = extract_number(raw)
    if number is None:
        return None

    unit = detect_unit(raw)
    converted = number  # default: no conversion

    if property_type in DENSITY_PROPERTIES:
        if unit and unit in DENSITY_CONVERSIONS:
            converted = number * DENSITY_CONVERSIONS[unit]
        elif unit is None:
            # If no unit detected, assume g/cc (most common on MatWeb)
            converted = number * 1000.0

    elif property_type in STRESS_PROPERTIES:
        if unit and unit in STRESS_CONVERSIONS:
            converted = number * STRESS_CONVERSIONS[unit]
        elif unit is None:
            # If no unit detected, assume MPa (most common on MatWeb)
            converted = number * 1_000_000.0

    elif property_type in UNITLESS_PROPERTIES:
        converted = number  # No conversion needed

    # Engineering Rule #2: round to 2 decimal places
    return round(converted, 2)


def format_material_data_detailed(raw_props: dict) -> dict:
    """
    Convert a dict of raw MatWeb strings into clean SI-unit floats.
    
    Args:
        raw_props: Dict with keys matching property_type names,
                   values are raw MatWeb text strings.
                   Example: {"density": "7.85 g/cc", "youngs_modulus": "200 GPa"}
    
    Returns:
        Dict with clean float values in SI units.
        Missing/unparseable values get steel standard defaults (Engineering Rule #1).
    
    Example output:
        {
            "density": 7850.0,
            "tensile_yield": 250000000.0,
            "tensile_ultimate": 460000000.0,
            "youngs_modulus": 200000000000.0,
            "poissons_ratio": 0.3
        }
    """
    result = {}
    used_defaults = []
    missing_or_unparsed = []

    for prop_name, default_value in STEEL_DEFAULTS.items():
        raw = raw_props.get(prop_name)
        if raw is not None and isinstance(raw, str) and raw.strip():
            cleaned = clean_value(raw, prop_name)
            if cleaned is not None and cleaned > 0:
                result[prop_name] = cleaned
            else:
                # Engineering Rule #1: Fallback to steel standard
                result[prop_name] = round(default_value, 2)
                used_defaults.append(prop_name)
                missing_or_unparsed.append(prop_name)
        elif raw is not None and isinstance(raw, (int, float)):
            # Already a number (maybe from cache), just round it
            result[prop_name] = round(float(raw), 2)
        else:
            # Missing property → use steel standard default
            result[prop_name] = round(default_value, 2)
            used_defaults.append(prop_name)
            missing_or_unparsed.append(prop_name)

    return {
        "properties": result,
        "used_defaults": used_defaults,
        "missing_or_unparsed": missing_or_unparsed,
    }


def format_material_data(raw_props: dict) -> dict:
    """Backward-compatible wrapper returning only cleaned properties."""
    return format_material_data_detailed(raw_props)["properties"]


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_cases = {
        "density": "7.85 g/cc",
        "tensile_yield": "250 MPa",
        "tensile_ultimate": "460 MPa",
        "youngs_modulus": "200 GPa",
        "poissons_ratio": "0.3",
    }

    print("🔧 Unit Conversion Test:")
    print("-" * 50)
    result = format_material_data(test_cases)
    for key, val in result.items():
        print(f"  {key:25s} → {val}")

    print("\n🔧 Missing Data Fallback Test:")
    print("-" * 50)
    partial = {"density": "7.85 g/cc"}  # Missing all others
    result2 = format_material_data(partial)
    for key, val in result2.items():
        print(f"  {key:25s} → {val}")

    print("\n🔧 Edge Cases:")
    print("-" * 50)
    print(f"  Range '0.27 - 0.30'  → {extract_number('0.27 - 0.30')}")
    print(f"  Comma '7,850 kg/m³'  → {clean_value('7,850 kg/m³', 'density')}")
    print(f"  SciNot '2.00e+11 Pa' → {clean_value('2.00e+11 Pa', 'youngs_modulus')}")
    print(f"  Empty string ''      → {clean_value('', 'density')}")
print(f"  None/invalid         → {clean_value('', 'density')}")

def parse_raw_matweb_text(raw_text: str) -> dict:
    """
    Parses raw MatWeb "Printer Friendly Version" text to extract properties
    and converts them to SI units, applying steel defaults for missing values.
    Handles multiple aliases for the same properties.
    """
    import re
    
    # 1) Search with multiple aliases
    # Density: Supports g/cc, g/cm3, kg/m3
    density_m = re.search(r"Density\s+([0-9.,]+)\s*(?:g/cc|g/cm³|g/cm3|kg/m³|kg/m3)", raw_text, re.IGNORECASE)
    
    # Yield Strength: Supports 'Tensile Strength, Yield'
    yield_m = re.search(r"Tensile Strength, Yield\s+([0-9.,]+)\s*MPa", raw_text, re.IGNORECASE)
    
    # Ultimate Strength: Supports 'Tensile Strength, Ultimate'
    ult_m = re.search(r"Tensile Strength, Ultimate\s+([0-9.,]+)\s*MPa", raw_text, re.IGNORECASE)
    
    # Modulus: Supports 'Modulus of Elasticity' and 'Tensile Modulus'
    mod_m = re.search(r"(?:Modulus of Elasticity|Tensile Modulus)\s+([0-9.,]+)\s*GPa", raw_text, re.IGNORECASE)
    
    # Poisson: Supports 'Poisson's Ratio'
    poisson_m = re.search(r"Poisson's Ratio\s+([0-9.,]+)", raw_text, re.IGNORECASE)

    props = {}
    used_defaults = []
    missing_or_unparsed = []

    def clean_val(val_str: str) -> float:
        # Handle decimal comma if present (MatWeb usually uses dot, but let's be safe)
        if "," in val_str and "." in val_str:
            # Format like 1,234.56 or 1.234,56
            if val_str.rfind(",") > val_str.rfind("."):
                # 1.234,56
                return float(val_str.replace(".", "").replace(",", "."))
            else:
                # 1,234.56
                return float(val_str.replace(",", ""))
        elif "," in val_str:
            # Could be 1,23 (decimal) or 1,234 (thousands)
            # MatWeb properties are usually small numbers for g/cc or Poisson, or large for MPa
            # If it's something like "0,3" it's decimal. If it's "1200,0" it's decimal.
            # Usually MatWeb uses dots. We'll try to treat comma as decimal if it's the only separator.
            return float(val_str.replace(",", "."))
        return float(val_str)

    # DENSITY
    if density_m:
        try:
            match_str = density_m.group(0).lower()
            val = clean_val(density_m.group(1))
            if "kg/m" in match_str: # catches kg/m³ and kg/m3
                props['density'] = round(val, 2)
            else:
                # g/cc to kg/m3
                props['density'] = round(val * 1000.0, 2)
        except (ValueError, TypeError):
            props['density'] = round(STEEL_DEFAULTS['density'], 2)
            used_defaults.append('density')
    else:
        props['density'] = round(STEEL_DEFAULTS['density'], 2)
        used_defaults.append('density')
        missing_or_unparsed.append('density')

    # YIELD
    if yield_m:
        try:
            props['tensile_yield'] = round(clean_val(yield_m.group(1)) * 1e6, 2)
        except (ValueError, TypeError):
            props['tensile_yield'] = round(STEEL_DEFAULTS['tensile_yield'], 2)
            used_defaults.append('tensile_yield')
    else:
        props['tensile_yield'] = round(STEEL_DEFAULTS['tensile_yield'], 2)
        used_defaults.append('tensile_yield')
        missing_or_unparsed.append('tensile_yield')
        
    # ULTIMATE
    if ult_m:
        try:
            props['tensile_ultimate'] = round(clean_val(ult_m.group(1)) * 1e6, 2)
        except (ValueError, TypeError):
            props['tensile_ultimate'] = round(STEEL_DEFAULTS['tensile_ultimate'], 2)
            used_defaults.append('tensile_ultimate')
    else:
        props['tensile_ultimate'] = round(STEEL_DEFAULTS['tensile_ultimate'], 2)
        used_defaults.append('tensile_ultimate')
        missing_or_unparsed.append('tensile_ultimate')
        
    # MODULUS
    if mod_m:
        try:
            props['youngs_modulus'] = round(clean_val(mod_m.group(1)) * 1e9, 2)
        except (ValueError, TypeError):
            props['youngs_modulus'] = round(STEEL_DEFAULTS['youngs_modulus'], 2)
            used_defaults.append('youngs_modulus')
    else:
        props['youngs_modulus'] = round(STEEL_DEFAULTS['youngs_modulus'], 2)
        used_defaults.append('youngs_modulus')
        missing_or_unparsed.append('youngs_modulus')
        
    # POISSON
    if poisson_m:
        try:
            props['poissons_ratio'] = round(clean_val(poisson_m.group(1)), 2)
        except (ValueError, TypeError):
            props['poissons_ratio'] = round(STEEL_DEFAULTS['poissons_ratio'], 2)
            used_defaults.append('poissons_ratio')
    else:
        props['poissons_ratio'] = round(STEEL_DEFAULTS['poissons_ratio'], 2)
        used_defaults.append('poissons_ratio')
        missing_or_unparsed.append('poissons_ratio')

    return {
        "properties": props,
        "used_defaults": used_defaults,
        "missing_or_unparsed": missing_or_unparsed,
    }
