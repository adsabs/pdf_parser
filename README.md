# 📄 PDF Parser for Scientific Literature

This tool extracts structured content (sections, figures, tables, and captions) from scientific PDFs using [GROBID](https://github.com/kermitt2/grobid) and [pdffigures2](https://github.com/allenai/pdffigures2). It is designed for use with NASA ADS or other scientific corpora.

---

## 🧩 Project Structure

```
pdf_parser/
├── input_pdfs/                   # Input PDFs to process
├── tei_xml/                      # TEI XML output from GROBID
├── structured_output/            # Output JSON and figure images
├── grobid/                       # GROBID repo (included)
├── pdffigures2/                  # pdffigures2 repo (included)
├── helpers/
│   ├── extract_sections_from_tei.py
│   └── extract_figures_and_tables.py
├── process_pdfs.py               # Main pipeline
├── requirements.txt
└── README.md
```

---

## 🚀 Setup

1. **Clone the repo**:
   ```bash
   git clone https://github.com/adsabs/pdf_parser.git
   cd pdf_parser
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv scipdf-env
   source scipdf-env/bin/activate
   pip install -r requirements.txt
   ```

---

## 📦 GROBID (included)

The `grobid/` repo is already included. To launch it:

```bash
cd grobid
./gradlew run
# GROBID will run at http://localhost:8070
```

To update or reinstall GROBID:

```bash
rm -rf grobid
git clone https://github.com/kermitt2/grobid.git
cd grobid
./gradlew run
```

---

## 🖼️ pdffigures2 (included)

The `pdffigures2/` repo is also included. To compile it:

```bash
cd pdffigures2
sbt assembly
```

After building, update the path to the JAR file in `process_pdfs.py` if necessary (e.g., `target/scala-2.12/pdffigures2-assembly-*.jar`).

To update pdffigures2 manually:

```bash
rm -rf pdffigures2
git clone https://github.com/allenai/pdffigures2.git
cd pdffigures2
sbt assembly
```

---

## ⚙️ Usage

Place PDFs in the `input_pdfs/` directory and run:

```bash
python process_pdfs.py
```

You can customize paths like this:

```bash
python process_pdfs.py \
  --input_dir input_pdfs \
  --tei_dir tei_xml \
  --output_dir structured_output
```

Skip GROBID step (if TEI XMLs already exist):

```bash
python process_pdfs.py --skip_grobid
```

---

## 🧪 Output

- `*.structured.json` with:
  - `sections`: structured text with headings
  - `figures`: TEI + pdffigures2 captions
  - `tables`: TEI table captions (with optional extracted contents)
- Extracted figure images from pdffigures2 are saved as PNGs in:
  ```
  structured_output/<paper_id>_figures/
  ```

---

## 📌 Requirements

- Python 3.8+
- Java 8+
- [GROBID](https://github.com/kermitt2/grobid)
- [pdffigures2](https://github.com/allenai/pdffigures2)

Install Python dependencies:

```bash
pip install -r requirements.txt
```

---

## 📄 License

MIT License
