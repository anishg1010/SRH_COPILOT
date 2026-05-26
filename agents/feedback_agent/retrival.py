import chromadb


db_path = r"./database/"
client = chromadb.PersistentClient(path = db_path)
collection = client.get_or_create_collection(name  = "feedback_bot")
print("question asked successfully")
results = collection.query(
    query_texts = ["How can I create learning objectives for a course?"],
    n_results = 2
)

print(results)