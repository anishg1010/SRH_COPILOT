import chromadb 

db_path = r"./database/"
client = chromadb.PersistentClient(path = db_path)
collection = client.get_or_create_collection(name  = "feedback_bot") 

collection.add(
    documents = [
        "Learning objectives should describe what students will be able to do after completing the course.",
        "Competence-oriented teaching focuses on skills, knowledge, and abilities students can apply in real-world situations.",
        "Rubrics help lecturers evaluate student performance using clear criteria and performance levels."
    ], 
    metadatas = [
        {"category": "learning_objectives"},
        {"category": "course_design"},
        {"category": "rubric"}
    ],
    ids = [
        "doc1",
        "doc2",
        "doc3"
    ]
)


print("successfully added to chorma db")