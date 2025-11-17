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
    if tag is None or tag == '':
        return 'field'
    tag = re.sub(r'\s+', '_', str(tag))
    tag = re.sub(r'[^A-Za-z0-9_\-\.]', '_', tag)
    if re.match(r'^[^A-Za-z_]', tag):
        tag = 'field_' + tag
    return tag


def _normalize_key_for_json(key):
    if key is None:
        return 'field'
    # Accept apostrophes: replace l_ with l'
    key = key.replace('l_', "l'")
    # Keep original accents and other chars; strip surrounding whitespace
    return key.strip()


def read_csv_rows(csv_file_path):
    rows = []
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            normalized = {}
            for k, v in row.items():
                nk = _normalize_key_for_json(k)
                normalized[nk] = None if v is None else v
            rows.append(normalized)
    return rows


def csv_to_xml(csv_file_path, xml_file_path, root_element_name='root', row_element_name='row'):
    root = ET.Element(root_element_name)
    try:
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
    except Exception as e:
        print(f"Error convirtiendo `{csv_file_path}`: {e}")


def write_combined_json(rows, json_path=JSON_OUTPUT):
    os.makedirs(os.path.dirname(json_path) or '.', exist_ok=True)
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error escribiendo `{json_path}`: {e}")


def batch_convert_csv_to_xml(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR, json_output=JSON_OUTPUT):
    if not os.path.exists(input_dir):
        print(f"El directorio de entrada `{input_dir}` no existe.")
        return
    os.makedirs(output_dir, exist_ok=True)
    converted_count = 0
    all_rows = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.csv'):
            csv_path = os.path.join(input_dir, filename)
            xml_filename = os.path.splitext(filename)[0] + '.xml'
            xml_path = os.path.join(output_dir, xml_filename)
            csv_to_xml(csv_path, xml_path)
            # Leer filas para JSON (normaliza claves para aceptar l')
            try:
                rows = read_csv_rows(csv_path)
                all_rows.extend(rows)
            except Exception as e:
                print(f"Error leyendo `{csv_path}` para JSON: {e}")
            print(f"Convertido `{csv_path}` -> `{xml_path}`")
            converted_count += 1

    # Escribir JSON combinado
    write_combined_json(all_rows, json_output)
    print(f"Conversión completada. Archivos procesados: {converted_count}. JSON escrito en `{json_output}`")


if __name__ == '__main__':
    batch_convert_csv_to_xml()
