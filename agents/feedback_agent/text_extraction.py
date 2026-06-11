import sys
import os
import re
import io
import shutil
import unicodedata
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image, ImageOps


# ============================================================
# PATH CONFIGURATION
# ============================================================

# This file location:
# main/agents/feedback/text_extraction.py
SCRIPT_DIR = Path(__file__).resolve().parent

# Your local tessdata folder:
# main/agents/feedback/tessdata
TESSDATA_DIR = SCRIPT_DIR / "tessdata"

# Common Windows Tesseract installation paths
WINDOWS_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text: str) -> str:
    """
    Cleans extracted PDF/OCR text.
    Fixes broken words like:
    Be- urlaubung -> Beurlaubung
    Studie- rende -> Studierende
    """

    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)

    # Remove common PDF artifacts
    text = text.replace("\u00ad", "")  # soft hyphen
    text = text.replace("￾", "")
    text = text.replace("\xa0", " ")

    # Fix hyphenated words split across lines/spaces
    text = re.sub(
        r"([A-Za-zÄÖÜäöüß])-[\s\r\n]+([a-zäöüß])",
        r"\1\2",
        text,
    )

    # Remove extra spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Clean spaces around line breaks
    text = re.sub(r" *\n *", "\n", text)

    # Reduce excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================
# TESSERACT SETUP
# ============================================================

def setup_tesseract() -> bool:
    """
    Finds tesseract.exe and sets it for pytesseract.
    Returns True if found, False otherwise.
    """

    # First check if tesseract is available in PATH
    detected_path = shutil.which("tesseract")

    if detected_path:
        pytesseract.pytesseract.tesseract_cmd = detected_path
        return True

    # Then check common Windows installation paths
    for path in WINDOWS_TESSERACT_PATHS:
        if Path(path).exists():
            pytesseract.pytesseract.tesseract_cmd = path
            return True

    return False


def get_available_local_languages() -> list:
    """
    Checks which .traineddata files exist inside:
    main/agents/feedback/tessdata
    """

    if not TESSDATA_DIR.exists():
        return []

    languages = []

    for file in TESSDATA_DIR.glob("*.traineddata"):
        languages.append(file.stem)

    return languages


def get_ocr_language() -> str:
    """
    Selects the best OCR language based on files available
    inside the local tessdata folder.
    """

    local_langs = get_available_local_languages()

    if "deu" in local_langs and "eng" in local_langs:
        return "deu+eng"

    if "deu" in local_langs:
        return "deu"

    if "eng" in local_langs:
        return "eng"

    return "eng"


def get_tessdata_config() -> str:
    """
    Returns Tesseract config for local tessdata folder.
    """

    if TESSDATA_DIR.exists():
        os.environ["TESSDATA_PREFIX"] = str(TESSDATA_DIR)
        return "--oem 3 --psm 6"  # no --tessdata-dir here
    return "--oem 3 --psm 6"


# ============================================================
# OCR EXTRACTION
# ============================================================

def ocr_page(fitz_doc, page_index: int, dpi: int = 300) -> str:
    if not setup_tesseract():
        return "[OCR skipped: tesseract.exe was not found]"

    # Set tessdata path via env var (avoids spaces-in-path issue)
    if TESSDATA_DIR.exists():
        os.environ["TESSDATA_PREFIX"] = str(TESSDATA_DIR)

    lang = get_ocr_language()

    page = fitz_doc[page_index]
    pix = page.get_pixmap(dpi=dpi)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    img = img.convert("L")
    img = ImageOps.autocontrast(img)

    configs = ["--oem 3 --psm 6", "--oem 3 --psm 11"]
    best_text = ""

    for config in configs:
        try:
            text = pytesseract.image_to_string(img, lang=lang, config=config)
        except Exception as e:
            text = f"[OCR failed: {e}]"
        text = clean_text(text)
        if len(text.split()) > len(best_text.split()):
            best_text = text

    return best_text


# ============================================================
# TABLE EXTRACTION
# ============================================================

TABLE_SETTINGS = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "intersection_tolerance": 5,
    "snap_tolerance": 3,
    "join_tolerance": 3,
}


def is_process_step(value: str) -> bool:
    """
    Detects rows like:
    01, 02, 03a, 03b, 08a, 08b, 10, 12
    """

    if not value:
        return False

    value = value.strip()
    return bool(re.match(r"^\d{2}[a-zA-Z]?$", value))


def extract_process_table_as_text(tables) -> str:
    """
    Converts process table rows into clean semantic text.
    This format is better for RAG / VectorDB than messy raw table text.
    """

    extracted_steps = []
    seen_steps = set()

    for table in tables:
        for row in table:
            if not row:
                continue

            row = [clean_text(cell) if cell else "" for cell in row]

            if len(row) == 0:
                continue

            step_no = row[0].strip()

            if not is_process_step(step_no):
                continue

            if step_no in seen_steps:
                continue

            seen_steps.add(step_no)

            responsible = row[1] if len(row) > 1 else ""
            deadline = row[2] if len(row) > 2 else ""
            action = row[3] if len(row) > 3 else ""
            documents = row[4] if len(row) > 4 else ""
            information_to = " ".join(row[5:]) if len(row) > 5 else ""

            step_text = f"""
Schritt {step_no}
Verantwortlich: {responsible}
Frist/Zeitpunkt: {deadline}
Aktion: {action}
Benötigte Unterlagen: {documents}
Abgabe/Information an: {information_to}
""".strip()

            extracted_steps.append(step_text)

    return "\n\n".join(extracted_steps)


def extract_page_context(normal_text: str) -> str:
    """
    Extracts useful non-table context such as title, purpose,
    process description, legend, and IT systems.
    """

    text = clean_text(normal_text)

    if not text:
        return ""

    context_parts = []

    # Keep introduction before the process table starts
    if "Wer?" in text:
        intro = text.split("Wer?")[0].strip()
        if intro:
            context_parts.append(intro)

    # Keep legend and supporting systems
    if "Legende:" in text:
        legend = text[text.find("Legende:"):].strip()
        if legend:
            context_parts.append(legend)

    # If no structure is detected, keep short text only
    if not context_parts and len(text.split()) < 100:
        context_parts.append(text)

    return "\n\n".join(context_parts).strip()


def extract_tables_clean(plumber_page) -> str:
    """
    Extracts tables using pdfplumber and converts process rows
    into structured semantic text.
    """

    try:
        tables = plumber_page.extract_tables(table_settings=TABLE_SETTINGS)
    except Exception:
        tables = plumber_page.extract_tables()

    if not tables:
        return ""

    process_text = extract_process_table_as_text(tables)

    return clean_text(process_text)


# ============================================================
# PAGE CLASSIFICATION
# ============================================================

def classify_page(fitz_page, plumber_page) -> dict:
    """
    Automatically detects whether a page is:
    - normal digital text
    - table/layout PDF
    - scanned/image/diagram page
    - blank/unreadable page
    """

    raw_text = fitz_page.get_text("text", sort=True)
    cleaned_text = clean_text(raw_text)
    word_count = len(re.findall(r"\w+", cleaned_text))

    try:
        image_count = len(fitz_page.get_images(full=True))
    except Exception:
        image_count = 0

    try:
        drawing_count = len(fitz_page.get_drawings())
    except Exception:
        drawing_count = 0

    try:
        tables = plumber_page.extract_tables(table_settings=TABLE_SETTINGS)
        table_count = len(tables) if tables else 0
    except Exception:
        table_count = 0

    if table_count > 0:
        page_type = "table_or_layout_pdf"
        method = "pdfplumber_table_extraction"

    elif word_count >= 40:
        page_type = "digital_text_pdf"
        method = "pymupdf_text_extraction"

    elif image_count > 0 or drawing_count > 20:
        page_type = "scanned_or_diagram_pdf"
        method = "ocr_extraction"

    elif word_count > 0:
        page_type = "low_text_pdf"
        method = "ocr_extraction"

    else:
        page_type = "blank_or_unreadable_page"
        method = "skip_or_ocr"

    return {
        "page_type": page_type,
        "method": method,
        "word_count": word_count,
        "image_count": image_count,
        "drawing_count": drawing_count,
        "table_count": table_count,
    }


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf_auto(pdf_path: Path) -> list:
    """
    Extracts one PDF page-by-page using automatic method selection.
    Returns a list of dictionaries.
    """

    results = []

    fitz_doc = fitz.open(str(pdf_path))

    with pdfplumber.open(str(pdf_path)) as plumber_doc:
        total_pages = len(fitz_doc)

        for page_index in range(total_pages):
            fitz_page = fitz_doc[page_index]
            plumber_page = plumber_doc.pages[page_index]

            page_info = classify_page(fitz_page, plumber_page)

            page_number = page_index + 1
            method = page_info["method"]

            if method == "pdfplumber_table_extraction":
                normal_text = plumber_page.extract_text() or ""
                context_text = extract_page_context(normal_text)
                table_text = extract_tables_clean(plumber_page)

                final_parts = []

                if context_text:
                    final_parts.append("KONTEXT:\n" + context_text)

                if table_text:
                    final_parts.append("PROZESSSCHRITTE:\n" + table_text)

                if final_parts:
                    final_text = "\n\n".join(final_parts)
                else:
                    final_text = clean_text(normal_text)

            elif method == "pymupdf_text_extraction":
                final_text = fitz_page.get_text("text", sort=True)
                final_text = clean_text(final_text)

            elif method == "ocr_extraction":
                final_text = ocr_page(fitz_doc, page_index)

            else:
                final_text = ""

            results.append(
                {
                    "pdf_name": pdf_path.name,
                    "page": page_number,
                    "page_type": page_info["page_type"],
                    "method": method,
                    "word_count": page_info["word_count"],
                    "image_count": page_info["image_count"],
                    "drawing_count": page_info["drawing_count"],
                    "table_count": page_info["table_count"],
                    "text": final_text,
                }
            )

    fitz_doc.close()

    return results


# ============================================================
# PRINT OUTPUT IN TERMINAL
# ============================================================

def print_extracted_pages(extracted_pages: list):
    """
    Prints extracted output directly in terminal.
    Does not save anything to output.txt.
    """

    for page in extracted_pages:
        print("\n" + "=" * 90)
        print(f"PDF: {page['pdf_name']}")
        print(f"Page: {page['page']}")
        print(f"Detected type: {page['page_type']}")
        print(f"Extraction method: {page['method']}")
        print(f"Words detected before extraction: {page['word_count']}")
        print(f"Images: {page['image_count']}")
        print(f"Drawings: {page['drawing_count']}")
        print(f"Tables: {page['table_count']}")
        print("-" * 90)

        if page["text"]:
            print(page["text"])
        else:
            print("[No extractable text found]")


# ============================================================
# PROCESS SINGLE PDF OR FOLDER
# ============================================================

def process_input(input_path: Path):
    """
    If input_path is a PDF, process one PDF.
    If input_path is a folder, process all PDFs inside it.
    """

    if input_path.is_file() and input_path.suffix.lower() == ".pdf":
        extracted_pages = extract_pdf_auto(input_path)
        print_extracted_pages(extracted_pages)

    elif input_path.is_dir():
        pdf_files = list(input_path.glob("*.pdf"))

        if not pdf_files:
            print(f"No PDF files found in folder: {input_path}")
            return

        for pdf_file in pdf_files:
            print("\n\n" + "#" * 100)
            print(f"Processing PDF: {pdf_file.name}")
            print("#" * 100)

            try:
                extracted_pages = extract_pdf_auto(pdf_file)
                print_extracted_pages(extracted_pages)
            except Exception as e:
                print(f"Error processing {pdf_file.name}: {e}")

    else:
        print("Invalid input path. Please provide a PDF file or a folder containing PDFs.")


# ============================================================
# DEBUG INFORMATION
# ============================================================

def print_tesseract_debug_info():
    """
    Prints useful OCR setup information.
    """

    print("\nOCR DEBUG INFO")
    print("-" * 60)
    print(f"Script directory: {SCRIPT_DIR}")
    print(f"Tessdata directory: {TESSDATA_DIR}")
    print(f"Tessdata exists: {TESSDATA_DIR.exists()}")
    print(f"Local OCR languages: {get_available_local_languages()}")

    found = setup_tesseract()
    print(f"Tesseract found: {found}")

    if found:
        print(f"Tesseract path: {pytesseract.pytesseract.tesseract_cmd}")
        print(f"OCR language selected: {get_ocr_language()}")

    print("-" * 60)


# ============================================================
# RUN SCRIPT
# ============================================================

if __name__ == "__main__":
    """
    Usage:

    1. Process one PDF:
       python .\\agents\\feedback\\text_extraction.py .\\2601_Beurlaubung.pdf

    2. Process all PDFs inside a folder:
       python .\\agents\\feedback\\text_extraction.py .\\pdfs

    3. Show OCR debug info:
       python .\\agents\\feedback\\text_extraction.py --debug
    """

    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        print_tesseract_debug_info()
        sys.exit()

    if len(sys.argv) > 1:
        input_path = Path(sys.argv[1])
    else:
        input_path = Path(r"C:\Users\yuvra\Desktop\UNI\Collabortive industry project\Main\agents\feedback_agent\database\docx\2601_Beurlaubung.pdf")

    process_input(input_path)