from core.orchestrator import handle_user_query


def main() -> None:
    print("SRH AI Copilot - Local MVP")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Ask LINC: ").strip()
        if query.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        response = handle_user_query(query)
        print("\n" + response + "\n")


if __name__ == "__main__":
    main()
