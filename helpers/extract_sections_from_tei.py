import os
import json
import logging
from lxml import etree

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

def extract_sections_from_tei(tei_path):
    """Extract sections from a TEI XML file produced by GROBID."""
    try:
        with open(tei_path, 'rb') as f:
            tree = etree.parse(f)

        body = tree.find('.//tei:body', namespaces=NS)
        if body is None:
            logging.warning(f"No <body> found in TEI file: {tei_path}")
            return []

        sections = []
        divs = body.findall('tei:div', namespaces=NS)
        if divs:
            logging.info(f"Found {len(divs)} section divs in {os.path.basename(tei_path)}")
            for div in divs:
                heading_el = div.find('tei:head', namespaces=NS)
                heading = heading_el.text.strip() if heading_el is not None and heading_el.text else "Untitled Section"
                paragraphs = [p.text.strip() for p in div.findall('tei:p', namespaces=NS) if p.text]
                section_text = '\n'.join(paragraphs).strip()
                if section_text:
                    sections.append({'heading': heading, 'text': section_text})
        else:
            logging.warning(f"No structured sections found in {tei_path}, falling back to all paragraphs.")
            paragraphs = [p.text.strip() for p in body.findall('.//tei:p', namespaces=NS) if p.text]
            if paragraphs:
                fallback_text = '\n'.join(paragraphs)
                sections.append({'heading': 'Full Text', 'text': fallback_text})

        return sections

    except Exception as e:
        logging.error(f"Error parsing TEI file {tei_path}: {e}")
        return []

def process_all_tei_files(tei_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    tei_files = [f for f in os.listdir(tei_dir) if f.endswith('.tei.xml')]
    logging.info(f"Processing {len(tei_files)} TEI files...")

    for tei_file in tei_files:
        base = os.path.splitext(os.path.splitext(tei_file)[0])[0]  # remove .tei.xml
        out_path = os.path.join(output_dir, f"{base}.sections.json")
        tei_path = os.path.join(tei_dir, tei_file)
        sections = extract_sections_from_tei(tei_path)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({
                'filename': base + '.pdf',
                'sections': sections,
                'figures': []  # leave figures blank if you combine later
            }, f, indent=2)
        logging.info(f"Saved extracted sections for {base} to {out_path}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--tei_dir', required=True, help='Directory containing .tei.xml files')
    parser.add_argument('--output_dir', required=True, help='Where to save the JSON output')
    args = parser.parse_args()

    process_all_tei_files(args.tei_dir, args.output_dir)
