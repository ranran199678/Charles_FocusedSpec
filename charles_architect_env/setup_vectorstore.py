# setup_vectorstore.py - גרסה יציבה, בטוחה ומעודכנת
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings  # עדכון לפי LangChain v0.2+
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

SOURCE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VECTORSTORE_DIR = os.path.join(SOURCE_DIR, "vectorstore")

# סיומות קבצים תקפות בלבד (לא כולל xlsx וכו')
valid_extensions = [".py", ".md", ".txt", ".json", ".yaml", ".yml", ".cfg", ".ini"]

def is_valid_file(filepath):
    return os.path.splitext(filepath)[1].lower() in valid_extensions

def load_documents():
    loader = DirectoryLoader(
        SOURCE_DIR,
        glob="**/*",
        loader_cls=TextLoader,
        loader_kwargs={"autodetect_encoding": True}
    )

    print("📦 טוען מסמכים...")
    try:
        all_docs = loader.load()
    except Exception as e:
        print(f"⚠️ שגיאה בטעינת קבצים: {e}")
        all_docs = []

    valid_docs = []
    for doc in all_docs:
        source_path = doc.metadata.get("source", "")
        if is_valid_file(source_path):
            valid_docs.append(doc)
        else:
            print(f"⛔ מדלג על קובץ לא נתמך: {source_path}")

    return valid_docs

def build_vectorstore():
    documents = load_documents()
    print(f"✅ נמצאו {len(documents)} קבצים מתאימים")

    if not documents:
        print("🚫 אין קבצים מתאימים לטעינה. הפעולה הופסקה.")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    print(f"✂️ פיצול למסמכים: {len(docs)} קטעים")

    if not docs:
        print("🚫 אין טקסטים אחרי פיצול. הפעולה הופסקה.")
        return

    embeddings = OpenAIEmbeddings()
    print("💾 בונה מאגר Vectorstore...")
    vectorstore = Chroma.from_documents(docs, embeddings, persist_directory=VECTORSTORE_DIR)
    vectorstore.persist()

    print(f"🎉 Vectorstore נבנה בהצלחה ונשמר ב: {VECTORSTORE_DIR}")

if __name__ == "__main__":
    build_vectorstore()
