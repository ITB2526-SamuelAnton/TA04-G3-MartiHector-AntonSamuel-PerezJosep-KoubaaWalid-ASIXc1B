import csv
import os
import re
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from xml.sax.saxutils import escape  # Para escapar entidades XML

INPUT_DIR = 'CSV'
OUTPUT_DIR = 'XML'
JSON_OUTPUT = '../Dades_a_Json/Incidencies.json'


def _sanitize_tag(tag):
    try:
        if tag is None or tag == '':
            return 'field'
        tag = re.sub(r'\s+', '_', str(tag))
        tag = re.sub(r'[^A-Za-z0-9_\-\.]', '_', tag)
        if re.match(r'^[^A-Za-z_]', tag):
            tag = 'field_' + tag
        return tag
    except Exception as e:
        print(f"Error sanitizando tag '{tag}': {e}. Usando 'field' por defecto.")
        return 'field'


def _normalize_key_for_json(key):
    try:
        if key is None:
            return 'field'
        # Accept apostrophes: replace l_ with l'
        key = key.replace('l_', "l'")
        # Keep original accents and other chars; strip surrounding whitespace
        return key.strip()
    except Exception as e:
        print(f"Error normalizando clave '{key}': {e}. Usando 'field' por defecto.")
        return 'field'


def read_csv_rows(csv_file_path):
    rows = []
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                normalized = {}
                for k, v in row.items():
                    nk = _normalize_key_for_json(k)
                    normalized[nk] = None if v is None else v
                rows.append(normalized)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{csv_file_path}'.")
    except UnicodeDecodeError as e:
        print(f"Error de codificación en '{csv_file_path}': {e}. Intenta con otra codificación.")
    except csv.Error as e:
        print(f"Error leyendo CSV '{csv_file_path}': {e}.")
    except Exception as e:
        print(f"Error inesperado leyendo '{csv_file_path}': {e}.")
    return rows


def csv_to_xml(csv_file_path, xml_file_path, root_element_name='root', row_element_name='row'):
    try:
        root = ET.Element(root_element_name)
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row_el = ET.SubElement(root, row_element_name)
                for key, value in row.items():
                    tag = _sanitize_tag(key)
                    child = ET.SubElement(row_el, tag)
                    child.text = '' if value is None else escape(str(value))

        rough = ET.tostring(root, 'utf-8')
        pretty = minidom.parseString(rough).toprettyxml(indent="  ", encoding='utf-8')
        os.makedirs(os.path.dirname(xml_file_path) or '.', exist_ok=True)
        with open(xml_file_path, 'wb') as f:
            f.write(pretty)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo CSV '{csv_file_path}'.")
    except PermissionError:
        print(f"Error: No hay permisos para escribir en '{xml_file_path}'.")
    except ET.ParseError as e:
        print(f"Error parseando XML para '{csv_file_path}': {e}.")
    except Exception as e:
        print(f"Error convirtiendo '{csv_file_path}' a XML: {e}.")


def write_combined_json(rows, json_path=JSON_OUTPUT):
    try:
        os.makedirs(os.path.dirname(json_path) or '.', exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
    except PermissionError:
        print(f"Error: No hay permisos para escribir en '{json_path}'.")
    except json.JSONEncodeError as e:
        print(f"Error codificando JSON para '{json_path}': {e}.")
    except Exception as e:
        print(f"Error escribiendo '{json_path}': {e}.")


def batch_convert_csv_to_xml(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR, json_output=JSON_OUTPUT):
    if not os.path.exists(input_dir):
        print(f"El directorio de entrada '{input_dir}' no existe.")
        return
    try:
        os.makedirs(output_dir, exist_ok=True)
    except PermissionError:
        print(f"Error: No hay permisos para crear el directorio '{output_dir}'.")
        return
    except Exception as e:
        print(f"Error creando directorio '{output_dir}': {e}.")
        return

    converted_count = 0
    all_rows = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.csv'):
            csv_path = os.path.join(input_dir, filename)
            xml_filename = os.path.splitext(filename)[0] + '.xml'
            xml_path = os.path.join(output_dir, xml_filename)
            # Intentar conversión XML
            csv_to_xml(csv_path, xml_path)
            # Intentar leer filas para JSON
            try:
                rows = read_csv_rows(csv_path)
                all_rows.extend(rows)
                converted_count += 1
                print(f"Convertido '{csv_path}' -> '{xml_path}'")
            except Exception as e:
                print(f"Error procesando '{csv_path}' para JSON: {e}. Continuando con el siguiente.")

    # Escribir JSON combinado, incluso si algunos fallaron
    write_combined_json(all_rows, json_output)
    print(f"Conversión completada. Archivos procesados: {converted_count}. JSON escrito en '{json_output}'.")


if __name__ == '__main__':
    batch_convert_csv_to_xml()