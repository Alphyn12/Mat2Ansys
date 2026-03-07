
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from utils import parse_raw_matweb_text
from xml_generator import generate_ansys_xml

raw_text = """
3M Nextel™ 312 Industrial Ceramic Fiber
Categories:	Ceramic; Oxide; Aluminum Oxide; Silicon Oxide; Other Engineering Material; Composite Fibers
Material Notes:	Chemical composition above is wt%. Crystal phase is mullite + amorphous (or 100% amorphous). Filament diameter is 10-12 µm.
3M Nextel fibers 312, 440, and 550 are designed for non-structural applications where their primary purpose is to act as a flame barrier. 3M Nextel Ceramic Fiber 312 is made from Al2O3, SiO2, and B2O3. Because B2O3 is present, this composition has both crystalline and glassy phases. The glassy phase helps the fiber retain strength after exposure to high temperatures because it slows the growth of crystalline phases that weaken the fiber. However, when the fiber is stressed at high temperature, the glassy phase weakens the fiber due to viscous flow much like a glass fiber.

Information provided by 3M Ceramic Textile and Composites.

Key Words:	Alumina, Aluminum Oxide
Vendors:	No vendors are listed for this material. Please click here if you are a supplier and would like information on how to add your listing to this material.
 
Physical Properties	Metric	English	Comments
Density 	2.70 g/cc	0.0975 lb/in³	
Particle Size 	<= 0.50 µm	<= 0.50 µm	Crystal size
Specific Surface Area 	<= 0.20 m²/g	<= 0.20 m²/g	
 
Mechanical Properties	Metric	English	Comments
Tensile Strength, Ultimate 	1700 MPa
@Thickness 25.4 mm	247000 psi
@Thickness 1.00 in	filament
Tensile Modulus 	150 GPa	21800 ksi	Filament property
 
Electrical Properties	Metric	English	Comments
Dielectric Constant 	5.2
@Frequency 9.375e+9 Hz	5.2
@Frequency 9.375e+9 Hz	
Dissipation Factor 	0.018
@Frequency 9.375e+9 Hz	0.018
@Frequency 9.375e+9 Hz	
 
Thermal Properties	Metric	English	Comments
CTE, linear 	3.00 µm/m-°C
@Temperature 25.0 - 500 °C	1.67 µin/in-°F
@Temperature 77.0 - 932 °F	
Specific Heat Capacity 	1.05 J/g-°C
@Temperature 500 °C	0.251 BTU/lb-°F
@Temperature 932 °F	
Melting Point 	1800 °C	3270 °F	
 
Optical Properties	Metric	English	Comments
Refractive Index 	1.568	1.568	
 
Component Elements Properties	Metric	English	Comments
Al2O3 	62.5 %	62.5 %	
B2O3 	13 %	13 %	
SiO2 	24.5 %	24.5 %	
 
Descriptive Properties
Color	White	
"""

material_name = "3M Nextel™ 312 Industrial Ceramic Fiber"

try:
    from db_handler import save_material, get_material

    print("Step 1: Parsing...")
    parsed_data = parse_raw_matweb_text(raw_text)
    properties = parsed_data["properties"]
    print("Parsed Properties:", properties)
    
    print("\nStep 2: Testing DB Cache...")
    save_material(
        name=material_name,
        url="smart_paste_test",
        properties=properties,
        used_defaults=parsed_data["used_defaults"]
    )
    print("DB Save Success!")

    print("\nStep 3: Generating XML...")
    xml_path = generate_ansys_xml(material_name, properties)
    print("Success! XML Path:", xml_path)
    
    if os.path.exists(xml_path):
        os.remove(xml_path)
        print("Cleaned up.")
except Exception as e:
    print(f"\nERROR DETECTED: {e}")
    import traceback
    traceback.print_exc()
