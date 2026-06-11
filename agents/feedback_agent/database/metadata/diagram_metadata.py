import json
from pathlib import Path


IMAGE_DIR = Path(r"C:\Users\yuvra\Desktop\UNI\Collabortive industry project\Main\agents\feedback_agent\database\Images\Process_diagrams")
DIAGRAM_METADATA_FILE = Path(r"C:\Users\yuvra\Desktop\UNI\Collabortive industry project\Main\agents\feedback_agent\database\metadata\diagram_metadata.json")
GRAPH_DIR = Path(r"C:\Users\yuvra\Desktop\UNI\Collabortive industry project\Main\agents\feedback_agent\database\graphs\process_graphs")
OUTPUT_FILE = Path(r"C:\Users\yuvra\Desktop\UNI\Collabortive industry project\Main\agents\feedback_agent\database\metadata\diagram_index.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_png_files(image_dir):
    return list(image_dir.rglob("*.png"))


def create_diagram_index():
    diagram_metadata = load_json(DIAGRAM_METADATA_FILE)

    png_files = find_png_files(IMAGE_DIR)

    diagram_index = []

    for png_path in png_files:
        filename = png_path.name

        if filename not in diagram_metadata:
            print(f"Metadata not found for PNG: {filename}")
            continue

        metadata = diagram_metadata[filename]

        graph_file = metadata.get("graph_file")
        graph_path = GRAPH_DIR / graph_file

        if not graph_path.exists():
            print(f"Graph file not found for {filename}: {graph_file}")
            continue

        record = {
            "source_file": filename,
            "image_path": str(png_path),
            **metadata,
            "graph_path": str(graph_path)
        }

        diagram_index.append(record)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(diagram_index, f, indent=4, ensure_ascii=False)

    print("Diagram index created successfully.")
    print(f"Total PNG files found: {len(png_files)}")
    print(f"Total indexed diagrams: {len(diagram_index)}")
    print(f"Saved to: {OUTPUT_FILE}")

    return diagram_index


if __name__ == "__main__":
    index = create_diagram_index()

    print("\nExample diagram metadata:\n")
    if index:
        print(index[0])