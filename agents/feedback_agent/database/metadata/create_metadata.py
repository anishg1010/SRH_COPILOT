import json
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


RAW_DOCS_DIR = Path(r"C:\Users\yuvra\Desktop\UNI\Collabortive industry project\Main\agents\feedback_agent\database\raw_doc")
METADATA_FILE = Path(r"C:\Users\yuvra\Desktop\UNI\Collabortive industry project\Main\agents\feedback_agent\database\metadata\metadata.json")
OUTPUT_FILE = Path(r"C:\Users\yuvra\Desktop\UNI\Collabortive industry project\Main\agents\feedback_agent\database\metadata\metadata_preview.json")


REMOVE_KEYS = [
    "title",
    "original_pdf_title",
    "access_level",
    "audience",
    "topic",
    "page_id",
    "page_number"
]


def load_json_metadata(metadata_file):
    with open(metadata_file, "r", encoding="utf-8") as f:
        return json.load(f)


def find_pdf_files(raw_docs_dir):
    return list(raw_docs_dir.rglob("*.pdf"))


def clean_metadata(metadata):
    for key in REMOVE_KEYS:
        metadata.pop(key, None)
    return metadata


def add_metadata_to_pdf_pages(pdf_path, custom_metadata_map):
    loader = PyPDFLoader(str(pdf_path))
    pages = loader.load()

    filename = pdf_path.name

    if filename not in custom_metadata_map:
        print(f"Metadata not found for: {filename}")
        return pages

    custom_metadata = custom_metadata_map[filename]

    for page in pages:
        # Remove unwanted metadata from PyPDFLoader
        page.metadata = clean_metadata(page.metadata)

        # Add your custom metadata from JSON
        page.metadata.update(custom_metadata)

        # Add normalized filename
        page.metadata["source_file"] = filename

    return pages


def create_metadata_documents():
    custom_metadata_map = load_json_metadata(METADATA_FILE)
    pdf_files = find_pdf_files(RAW_DOCS_DIR)

    all_pages = []
    metadata_preview = []

    for pdf_path in pdf_files:
        pages = add_metadata_to_pdf_pages(pdf_path, custom_metadata_map)
        all_pages.extend(pages)

        for page in pages:
            metadata_preview.append(page.metadata)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata_preview, f, indent=4, ensure_ascii=False)

    print("Metadata creation completed.")
    print(f"Total PDFs found: {len(pdf_files)}")
    print(f"Total pages loaded: {len(all_pages)}")
    print(f"Metadata preview saved to: {OUTPUT_FILE}")

    return all_pages


if __name__ == "__main__":
    documents = create_metadata_documents()

    print("\nExample metadata from first page:\n")
    print(documents[0].metadata)