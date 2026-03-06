# PROJECT CONTEXT & AI AGENT INSTRUCTIONS: Mat2Ansys (Material Data Integration Tool)

## 1. Project Vision & Purpose
The goal of this project is to build a full-stack web application that acts as a bridge between the MatWeb material database and ANSYS Workbench. 
Engineers often struggle to find specific industrial materials (e.g., SAE 8620 H for gear manufacturing, specific case-hardening steels, or Nextel composites) inside the default Ansys Engineering Data library. Entering these properties manually is time-consuming and error-prone. 

This tool will:
1. Allow users to search for any material via a modern web interface.
2. Scrape the required mechanical and physical properties from MatWeb on-demand.
3. Cache the scraped data locally to build a custom, reusable database.
4. Inject this data into a pre-defined Ansys `MatML 3.1` XML template.
5. Provide the user with a ready-to-import `.xml` file that works across Ansys versions (from 2021 R2 up to 2024).

## 2. Target Audience & Scope
* **Users:** Mechanical engineering students and professionals performing static structural, kinematic, and fatigue analyses (e.g., analyzing power transmission systems, gearboxes, or press-fit assemblies).
* **Scale:** Private/Internal use. Not a commercial SaaS. IP banning from MatWeb must be avoided through local caching and targeted "on-demand" scraping rather than bulk scraping.

## 3. Tech Stack Architecture
* **Frontend:** Next.js / React (using Tailwind CSS and UI components from `21st.dev` for a modern, sleek interface).
* **Backend:** Python + FastAPI (Lightweight, fast, and excellent for bridging Python scripts with a web interface).
* **Scraping Engine:** Python + `Playwright` (Strict requirement. MatWeb uses legacy ASP.NET WebForms with complex `__VIEWSTATE` tokens. Standard `requests` or `BeautifulSoup` will fail. Playwright must be used in headless mode to simulate a real browser).
* **Database/Cache:** A local JSON file (`bizim_malzemeler.json`) managed by Python.
* **File Generator:** Standard Python XML parsing (`xml.etree.ElementTree` or `BeautifulSoup` with XML parser) to modify the `template.xml`.

## 4. System Workflow (The 2-Step Process)

### Step 1: The "Search & List" Phase (Ağ Atma)
1. User types a query (e.g., "SAE 8620") in the frontend search bar.
2. Frontend sends query to backend `/search` endpoint.
3. Backend checks `bizim_malzemeler.json` cache first. 
4. If not found in cache, Playwright opens MatWeb search page, inputs the query, and submits.
5. Playwright scrapes the **Result List** (Material Names and their specific MatWeb detail URLs).
6. Backend returns this list as JSON to the Frontend. Frontend displays a selectable table/list.

### Step 2: The "Fetch Details & Generate XML" Phase (Nokta Atışı)
1. User selects a specific variation from the list (e.g., "SAE 8620 H") and clicks "Download for Ansys".
2. Frontend sends the specific MatWeb URL and Material Name to backend `/generate-xml` endpoint.
3. Playwright navigates directly to that URL.
4. Playwright scrapes the core Ansys-required properties:
   * Density
   * Tensile Strength, Yield
   * Tensile Strength, Ultimate
   * Modulus of Elasticity (Young's Modulus)
   * Poisson's Ratio
5. The extracted numerical data is cleaned (units converted to standard SI: Pascal, kg/m³, etc.).
6. Data is saved to `bizim_malzemeler.json` for future instant access.
7. Backend opens `template.xml` (the Ansys MatML structural steel base file), replaces the placeholder tags with the new scraped values, and renames the `<Name>` tag to the selected material.
8. Backend returns the generated `.xml` file to the frontend as a downloadable blob.

## 5. Strict AI Agent Directives & Rules

* **RULE 1 - Playwright is Mandatory:** Do not attempt to use `requests` for MatWeb form submissions. Assume all MatWeb interactions require Playwright's page navigation and DOM waiting features.
* **RULE 2 - Data Cleaning:** MatWeb presents data as text with units (e.g., "7.85 g/cc" or "200 GPa"). The AI must write robust parsing functions to extract the float values and convert them to Ansys defaults (Density -> kg/m³, Stress/Modulus -> Pa).
* **RULE 3 - XML Integrity:** The `template.xml` structure must not be broken. Only modify the text inside specific `<Data>` tags corresponding to the relevant `<ParameterValue parameter="paX">`. 
* **RULE 4 - Modular Code:** Separate the logic into distinct Python files: `main.py` (FastAPI), `scraper.py` (Playwright logic), `xml_generator.py` (XML parsing), and `db_handler.py` (JSON caching).
* **RULE 5 - UI Guidelines:** Use minimal, dark-mode friendly, engineering-focused design. Prompt the user visually while scraping is happening (e.g., "Connecting to MatWeb...", "Extracting Properties...").

## 6. Target XML Tag Mapping Reference (MatML 3.1)
When modifying the `template.xml`, target the following (based on Ansys Structural Steel baseline):
* **Material Name:** `<Name>Structural Steel</Name>` -> `<Name>NEW_MATERIAL_NAME</Name>`
* **Density (pr3 -> pa7):** `kg/m³`
* **Tensile Yield Strength (pr4 -> pa9):** `Pa`
* **Tensile Ultimate Strength (pr5 -> pa10):** `Pa`
* **Young's Modulus (pr13 -> pa25):** `Pa`
* **Poisson's Ratio (pr13 -> pa26):** Unitless

## 7. Next Steps for AI Implementation
When prompted to begin, start by generating the `scraper.py` using Playwright to handle the Step 1 Search function, ensuring headless browser setup is correct.