import os
import logging
from lxml import etree

NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

def extract_figures_and_tables(tei_path):
    try:
        with open(tei_path, 'rb') as f:
            tree = etree.parse(f)

        figures = []
        tables = []

        for figure in tree.findall('.//tei:figure', namespaces=NS):
            fig_id = figure.get('{http://www.w3.org/XML/1998/namespace}id', 'unknown')
            caption_el = figure.find('tei:figDesc', namespaces=NS)
            caption = caption_el.text.strip() if caption_el is not None and caption_el.text else 'No caption'
            figures.append({'id': fig_id, 'caption': caption, 'type': 'figure'})

        for table in tree.findall('.//tei:table', namespaces=NS):
            tab_id = table.get('{http://www.w3.org/XML/1998/namespace}id', 'unknown')
            caption_el = table.find('tei:head', namespaces=NS)
            caption = caption_el.text.strip() if caption_el is not None and caption_el.text else 'No caption'

            # Try to extract rows and cells if available
            structured_rows = []
            rows = table.findall('.//tei:row', namespaces=NS)
            for row in rows:
                cells = row.findall('.//tei:cell', namespaces=NS)
                structured_rows.append([cell.text.strip() if cell.text else "" for cell in cells])

            # Fallback to paragraph content if rows/cells not found
            if not structured_rows:
                paragraphs = [p.text.strip() for p in table.findall('.//tei:p', namespaces=NS) if p.text]
                table_content = "\n".join(paragraphs)
            else:
                table_content = structured_rows

            tables.append({
                'id': tab_id,
                'caption': caption,
                'type': 'table',
                'content': table_content
            })

        logging.info(f"[{os.path.basename(tei_path)}] Found {len(figures)} figures and {len(tables)} tables.")
        return figures, tables

    except Exception as e:
        logging.error(f"Failed to extract figures/tables from {tei_path}: {e}")
        return [], []
