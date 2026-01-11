"""
----------------------------------------------------------------------------------
AUTOMATIC SPAWNER GENERATOR FOR EGGWARS (PGM)
----------------------------------------------------------------------------------

PURPOSE:
    This script automates the tedious task of writing XML logic for upgradable 
    resource generators in EggWars maps for PGM.

    It reads an existing 'map.xml' file, detects generator regions based on their 
    ID, and automatically generates:
    1. State variables (Filters) for each level (lv0, lv1, lv2, etc.).
    2. <spawner> blocks configured with the correct delays for each level.

MANDATORY REQUIREMENT (NAMING CONVENTION):
    For the script to detect the generators, the regions in your 'map.xml' must
    strictly follow this ID format:

    team-{COLOR/NUMBER}-generator-{MATERIAL}-{NUMBER}

    Valid Examples:
    - id="team-red-generator-iron-1"
    - id="team-blue-generator-gold-2"
    - id="team-green-generator-diamond-1"
    - id="team-one-generator-iron-1"

CONFIGURATION:
    Generation timings (delays) per level are configured in the 
    'CONFIG_GENERADORES' dictionary within this script.

USAGE:
    1. Run the script using python.
    2. Ensure you are inputing the relative or full location path of the 'map.xml', e.g. 'EggWars/tiki/map.xml', or 'C:\User\****\Documents\EggWars\tiki\map.xml'
    3. Copy the console output and paste it into the <filters> and <spawners>
       sections of your XML file where it coresponds.

AUTHOR:
    ElBuenAnvita
    Script generated to facilitate EggWars recreation (MineLC style).
----------------------------------------------------------------------------------
"""

import xml.etree.ElementTree as ET
import re

# --- CONFIGURACIÓN DE NIVELES Y TIEMPOS ---
# Aquí definimos los delays para cada material y nivel.
CONFIG_GENERADORES = {
    'iron': [
        {'lvl': 1, 'delay': '1s'},
        {'lvl': 2, 'delay': '0.75s'},
        {'lvl': 3, 'delay': '0.5s'},
        {'lvl': 4, 'delay': '0.25s'}
    ],
    'gold': [
        {'lvl': 1, 'delay': '5s'},
        {'lvl': 2, 'delay': '3.5s'},
        {'lvl': 3, 'delay': '2s'},
        {'lvl': 4, 'delay': '1s'}
    ],
    'diamond': [
        {'lvl': 1, 'delay': '10s'},
        {'lvl': 2, 'delay': '5s'},
        {'lvl': 3, 'delay': '2.5s'}
        # Diamante no tiene lvl 4 en la configuración de MineLC original
        # Si lo quieres poner pues ponlo acá, equisde
    ]
}

def generar_xml_eggwars(archivo_mapa):
    try:
        tree = ET.parse(archivo_mapa)
        root = tree.getroot()
        
        # Regex para capturar: team-COLOR-generator-MATERIAL-NUMERO
        # Ejemplo: team-orange-generator-iron-1
        patron = re.compile(r"^team-(.+)-generator-(.+)-(\d+)$")
        
        generadores_encontrados = []

        # 1. BUSCAR REGIONES EN EL XML
        # Buscamos en cualquier elemento que tenga un atributo 'id'
        for elem in root.iter():
            if 'id' in elem.attrib:
                region_id = elem.attrib['id']
                match = patron.match(region_id)
                if match:
                    color = match.group(1)
                    material = match.group(2)
                    numero = match.group(3)
                    
                    if material in CONFIG_GENERADORES:
                        generadores_encontrados.append({
                            'full_id': region_id,
                            'color': color,
                            'material': material,
                            'num': numero,
                            'team_id': f"team-{color}" # Asumimos que el ID del team es team-color
                        })

        if not generadores_encontrados:
            print("No se encontraron regiones con el formato 'team-*-generator-*-*' en el mapa.")
            return

        # Ordenamos para que salga bonito (por equipo, luego material, luego numero)
        generadores_encontrados.sort(key=lambda x: (x['color'], x['material'], x['num']))

        print(f"\n")

        # --- 2. GENERAR FILTROS (VARIABLES) ---
        print("")
        print("")
        
        # Primero generamos todos los LVL 0 (Inicialización)
        print("\n\t")
        for gen in generadores_encontrados:
            # Variable interna: team_generator_iron_1 (con underscores, sin color pq es scope team)
            var_name = f"team_generator_{gen['material']}_{gen['num']}"
            # ID único del filtro: team-orange-generator-iron-1-lv0
            filter_id = f"{gen['full_id']}-lv0"
            
            print(f'\t<variable id="{filter_id}" var="{var_name}" team="{gen["team_id"]}">0</variable>')

        # Ahora generamos los niveles 1, 2, 3, 4...
        # Calculamos el nivel máximo global para iterar ordenadamente
        max_levels = 4 
        
        for i in range(1, max_levels + 1):
            print(f"\n\t")
            for gen in generadores_encontrados:
                # Verificamos si este material llega a este nivel
                config = CONFIG_GENERADORES.get(gen['material'])
                if i <= len(config):
                    var_name = f"team_generator_{gen['material']}_{gen['num']}"
                    filter_id = f"{gen['full_id']}-lv{i}"
                    print(f'\t<variable id="{filter_id}" var="{var_name}" team="{gen["team_id"]}">{i}</variable>')

        print("\n\n")
        print("")

        # --- 3. GENERAR SPAWNERS ---
        for gen in generadores_encontrados:
            config_niveles = CONFIG_GENERADORES.get(gen['material'])
            full_id = gen['full_id']
            
            # Mapeo de material para el item
            item_material = "iron ingot"
            if gen['material'] == "gold": item_material = "gold ingot"
            elif gen['material'] == "diamond": item_material = "diamond"
            elif gen['material'] == "emerald": item_material = "emerald"

            for nivel_data in config_niveles:
                lvl = nivel_data['lvl']
                delay = nivel_data['delay']
                filter_ref = f"{full_id}-lv{lvl}"
                
                print(f'\t<spawner spawn-region="{full_id}" delay="{delay}" filter="{filter_ref}">')
                print(f'\t    <item amount="1" material="{item_material}"/>')
                print(f'\t</spawner>')

    except Exception as e:
        print(f"Error procesando el archivo: {e}")

if __name__ == "__main__":
    file_location = input("¿Dónde esta el archivo? (relativo a esta carpeta o absoluto C:) >> ")
    generar_xml_eggwars(file_location)