import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"

DIAGRAM_INDEX_FILE = DATABASE_DIR / "metadata" / "diagram_index.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_diagram_index():
    return load_json(DIAGRAM_INDEX_FILE)


def load_graph_from_index_record(index_record):
    graph_path = Path(index_record["graph_path"])
    return load_json(graph_path)


def get_node(graph, node_id):
    for node in graph["nodes"]:
        if node["id"] == node_id:
            return node
    return None


def get_next_steps(graph, node_id):
    next_steps = []

    for edge in graph["edges"]:
        if edge["from"] == node_id:
            next_node = get_node(graph, edge["to"])

            next_steps.append({
                "condition": edge.get("condition", ""),
                "next_node": next_node
            })

    return next_steps


def get_previous_steps(graph, node_id):
    previous_steps = []

    for edge in graph["edges"]:
        if edge["to"] == node_id:
            previous_node = get_node(graph, edge["from"])

            previous_steps.append({
                "condition": edge.get("condition", ""),
                "previous_node": previous_node
            })

    return previous_steps


def find_steps_by_actor(graph, actor_name):
    actor_name = actor_name.lower()
    results = []

    for node in graph["nodes"]:
        actor = node.get("actor", "").lower()

        if actor_name in actor:
            results.append(node)

    return results


def search_steps(graph, keyword):
    keyword = keyword.lower()
    results = []

    for node in graph["nodes"]:
        searchable_text = " ".join([
            node.get("id", ""),
            node.get("actor", ""),
            node.get("action", ""),
            node.get("question", ""),
            node.get("deadline", ""),
            node.get("required_documents", "")
        ]).lower()

        if keyword in searchable_text:
            results.append(node)

    return results


def select_graph(keyword):
    """
    Select graph using keyword.
    Example keywords:
    - beurlaubung
    - academic leave
    - studienstart
    - 2 semester
    - standortwechsel
    """
    keyword = keyword.lower()

    diagram_index = load_diagram_index()

    for record in diagram_index:
        searchable_text = " ".join([
            record.get("source_file", ""),
            record.get("related_pdf", ""),
            record.get("graph_file", ""),
            record.get("category", ""),
            record.get("doc_type", "")
        ]).lower()

        graph = load_graph_from_index_record(record)

        searchable_text += " " + " ".join([
            graph.get("graph_id", ""),
            graph.get("process_name_de", ""),
            graph.get("process_name_en", "")
        ]).lower()

        if keyword in searchable_text:
            return graph, record

    return None, None


def validate_graph(graph):
    node_ids = {node["id"] for node in graph["nodes"]}
    errors = []

    for edge in graph["edges"]:
        if edge["from"] not in node_ids:
            errors.append(f"Invalid FROM node: {edge['from']}")

        if edge["to"] not in node_ids:
            errors.append(f"Invalid TO node: {edge['to']}")

    return errors


if __name__ == "__main__":
    # Select graph
    graph, record = select_graph("beurlaubung")

    if graph is None:
        print("No graph found.")
        exit()

    print("Selected graph:")
    print(graph["process_name_en"])

    # Validate graph
    errors = validate_graph(graph)

    if errors:
        print("\nGraph errors:")
        for error in errors:
            print("-", error)
    else:
        print("\nGraph is valid.")

    # Test next steps
    print("\nNext steps after node 02:")

    next_steps = get_next_steps(graph, "02")

    for item in next_steps:
        print("\nCondition:", item["condition"])
        print("Next node:", item["next_node"])

    # Test actor search
    print("\nSteps handled by Student Service:")

    sts_steps = find_steps_by_actor(graph, "Student Service")

    for step in sts_steps:
        print(step["id"], "-", step.get("action", step.get("question", "")))

    # Test keyword search
    print("\nSteps related to fees:")

    fee_steps = search_steps(graph, "fee")

    for step in fee_steps:
        print(step["id"], "-", step.get("action", step.get("question", "")))