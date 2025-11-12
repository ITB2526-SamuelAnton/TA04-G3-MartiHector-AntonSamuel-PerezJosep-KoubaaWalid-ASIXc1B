import csv
import os
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import unicodedata

INPUT_DIR = 'CSV'
OUTPUT_DIR = 'XML'

def _is_letter(ch):
    return unicodedata.category(ch).startswith('L')

def _sanitize_tag(tag):
    if tag is None:
        return 'field'
    tag = str(tag).strip()
    if tag == '':
        return 'field'
    tag = unicodedata.normalize('NFC', tag)
    new_chars = []
    for ch in tag:
        if ch == "'":
            new_chars.append('_')
        elif ch.isspace():
            new_chars.append('_')
        elif _is_letter(ch) or ch.isdigit() or ch in ('_', '-s', '.'):
            new_chars.append(ch)
        else:
            new_chars.append('_')
    tag = ''.join(new_chars)
    tag = re.sub(r'_+', '_', tag)
    tag = tag.strip('_')
    if tag == '':
        return 'field'
    if not (_is_letter(tag[0]) or tag[0] == '_'):
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
