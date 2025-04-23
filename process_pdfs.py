import os
import argparse
import json
import subprocess
from pathlib import Path
from helpers.extract_sections_from_tei import extract_sections_from_tei
from helpers.extract_figures_and_tables import extract_figures_and_tables

PDFFIGURES_JAR = Path("pdffigures2/pdffigures2/pdffigures2.jar")


def run_grobid(input_dir, tei_dir):
    os.makedirs(tei_dir, exist_ok=True)
    print("[INFO] Running GROBID on PDFs...")
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            with open(pdf_path, 'rb') as f:
                subprocess.run([
                    'curl', '--silent', '--show-error', '--form', f"input=@{pdf_path}",
                    'http://localhost:8070/api/processFulltextDocument',
                    '--output', os.path.join(tei_dir, filename.replace(".pdf", ".tei.xml"))
                ], check=True)

def run_pdffigures2(pdf_path, figures_out_dir):
    figures_out_dir.mkdir(parents=True, exist_ok=True)
    stem = pdf_path.stem
    json_prefix = figures_out_dir / f"figures_{stem}"
    image_prefix = figures_out_dir / f"fig_{stem}-"

    subprocess.run([
        "java", "-jar", str(PDFFIGURES_JAR),
        "--figure-data-prefix", str(json_prefix),
        "--figure-prefix", str(image_prefix),
        "--figure-format", "png",
        "--threads", "1",
        str(pdf_path)
    ], check=True)

    json_output = json_prefix.with_suffix(".json")
    if json_output.exists():
        with open(json_output) as f:
            return json.load(f)
    else:
        return []

def process_tei_files(tei_dir, output_dir, input_dir):
    os.makedirs(output_dir, exist_ok=True)
    tei_files = [f for f in os.listdir(tei_dir) if f.endswith('.tei.xml')]
    print(f"[INFO] Found {len(tei_files)} TEI files to process.")

    for tei_file in tei_files:
        base = os.path.splitext(os.path.splitext(tei_file)[0])[0]  # remove .tei.xml
        tei_path = os.path.join(tei_dir, tei_file)
        pdf_path = Path(input_dir) / f"{base}.pdf"
        figures_out_dir = Path(output_dir) / f"{base}_figures"

        sections = extract_sections_from_tei(tei_path)
        tei_figures, tei_tables = extract_figures_and_tables(tei_path)
        pdffigures_extraction = run_pdffigures2(pdf_path, figures_out_dir)

        out_path = os.path.join(output_dir, f"{base}.structured.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({
                'filename': base + '.pdf',
                'sections': sections,
                'tei_figures': tei_figures,
                'tei_tables': tei_tables,
                'pdffigures2': pdffigures_extraction
            }, f, indent=2)
        print(f"[INFO] Saved structured output for {base} to {out_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', default='input_pdfs', help='Directory of input PDFs')
    parser.add_argument('--tei_dir', default='tei_xml', help='Directory for GROBID TEI output')
    parser.add_argument('--output_dir', default='structured_output', help='Where to save JSON outputs')
    parser.add_argument('--skip_grobid', action='store_true', help='Skip GROBID processing if TEI already exists')
    args = parser.parse_args()

    if not args.skip_grobid:
        run_grobid(args.input_dir, args.tei_dir)

    process_tei_files(args.tei_dir, args.output_dir, args.input_dir)

if __name__ == '__main__':
    main()