import csv
import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

INPUT_DIR = 'CSV'
OUTPUT_DIR = 'XML'

def _sanitize_tag(tag):
    if tag is None:
        return 'field'
    tag = re.sub(r'\s+', '_', str(tag))
    tag = re.sub(r'[^A-Za-z0-9_\-\.]', '_', tag)
    if re.match(r'^[^A-Za-z_]', tag):
        tag = 'field_' + tag
    return tag

def csv_to_xml(csv_file_path, xml_file_path, root_element_name='formulari', row_element_name='resposta'):
    root = ET.Element(root_element_name)
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row_el = ET.SubElement(root, row_element_name)
                for key, value in row.items():
                    tag = _sanitize_tag(key)
                    child = ET.SubElement(row_el, tag)
                    child.text = '' if value is None else str(value)
        rough = ET.tostring(root, 'utf-8')
        pretty = minidom.parseString(rough).toprettyxml(indent="  ", encoding='utf-8')
        with open(xml_file_path, 'wb') as f:
            f.write(pretty)
    except Exception as e:
        print(f"Error converting `{csv_file_path}`: {e}")

def batch_convert_csv_to_xml(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR):
    if not os.path.exists(input_dir):
        print(f"Input directory `{input_dir}` does not exist.")
        return
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.csv'):
            csv_path = os.path.join(input_dir, filename)
            xml_filename = os.path.splitext(filename)[0] + '.xml'
            xml_path = os.path.join(output_dir, xml_filename)
            csv_to_xml(csv_path, xml_path)
            print(f"Converted `{csv_path}` -> `{xml_path}`")

if __name__ == '__main__':
    batch_convert_csv_to_xml()
