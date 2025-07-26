import os
import shutil
import glob
import datetime
import ssl
import sys  # ✅ חדש – דרוש לעצירת הריצה

from dotenv import load_dotenv

# ✅ טעינת משתני סביבה
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ שגיאה: מפתח OPENAI_API_KEY לא הוגדר בקובץ .env או במשתני הסביבה")
    sys.exit(1)
else:
    print("🔑 מפתח נטען בהצלחה")

# ✅ עקיפת שגיאת תעודת SSL מול OpenAI
ssl._create_default_https_context = ssl._create_unverified_context

from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader,
    UnstructuredExcelLoader,
    UnstructuredFileLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHROMA_DIR = os.getenv("VECTORSTORE_DIR", os.path.join(BASE_DIR, "vectorstore"))
LOG_FILE = os.path.join(BASE_DIR, "ingest_log.txt")

SUPPORTED_EXTENSIONS = [
    ".txt", ".md", ".py", ".ipynb", ".pdf", ".xlsx", ".xls", ".csv", ".json", ".log", ".html"
]
MAX_DOCS_PER_BATCH = 100

def write_log(successful, unsupported, errors):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("✅ קבצים שנקלטו בהצלחה:\n")
        for path in successful:
            f.write(f"{path}\n")
        f.write("\n⚠️ קבצים שלא נתמכים:\n")
        for path in unsupported:
            f.write(f"{path}\n")
        f.write("\n❌ קבצים שגרמו לשגיאה:\n")
        for path, msg in errors:
            f.write(f"{path} | {msg}\n")

def clean_vectorstore():
    if os.path.exists(CHROMA_DIR):
        print("🧹 מוחק Vector DB ישן...")
        shutil.rmtree(CHROMA_DIR)

def get_file_metadata(path):
    filename = os.path.basename(path)
    file_type = os.path.splitext(filename)[1][1:].lower()
    created_at = datetime.datetime.fromtimestamp(os.path.getctime(path)).strftime("%Y-%m-%d %H:%M:%S")

    if file_type in ["py", "ipynb"]:
        category = "code"
    elif file_type in ["pdf"]:
        category = "spec"
    elif file_type in ["xlsx", "xls", "csv"]:
        category = "excel"
    elif file_type in ["log"]:
        category = "log"
    else:
        category = "other"

    return {
        "source": os.path.relpath(path, BASE_DIR),
        "filename": filename,
        "file_type": file_type,
        "created_at": created_at,
        "category": category
    }

def load_documents():
    docs, successful, unsupported, errors = [], [], [], []
    all_files = glob.glob(f"{BASE_DIR}/**/*", recursive=True)
    print(f"📂 נמצאו {len(all_files)} קבצים. טוען נתונים...")
    loaded_paths = set()

    for path in all_files:
        ext = os.path.splitext(path)[1].lower()
        if path in loaded_paths:
            continue
        try:
            loaded = []
            if ext in [".txt", ".md", ".py", ".ipynb"]:
                loaded = TextLoader(path, encoding="utf-8").load()
            elif ext == ".pdf":
                loaded = PyMuPDFLoader(path).load()
            elif ext in [".xlsx", ".xls"]:
                loaded = UnstructuredExcelLoader(path).load()
            elif ext in [".csv", ".json", ".log", ".html"]:
                loaded = UnstructuredFileLoader(path).load()
            else:
                print(f"⚠️ פורמט לא נתמך: {path}")
                unsupported.append(path)
                continue

            metadata = get_file_metadata(path)
            for doc in loaded:
                doc.metadata.update(metadata)

            docs += loaded
            successful.append(path)
            loaded_paths.add(path)
            print(f"✅ נטען: {path}")

        except Exception as e:
            print(f"❌ שגיאה בקריאה: {path} | {e}")
            errors.append((path, str(e)))

    write_log(successful, unsupported, errors)
    return docs

def batch_documents(docs, batch_size):
    for i in range(0, len(docs), batch_size):
        yield docs[i:i + batch_size]

def ingest():
    clean_vectorstore()
    print("📥 טוען מסמכים...")
    raw_docs = load_documents()

    print("🔗 מפצל למסמכים קטנים...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.split_documents(raw_docs)
    print(f"📑 לאחר פיצול: {len(docs)} מסמכים")

    print("🧠 מחשב Embeddings באצוות...")
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)

    for i, doc_batch in enumerate(batch_documents(docs, MAX_DOCS_PER_BATCH)):
        try:
            print(f"🔢 קבוצה {i+1}: {len(doc_batch)} מסמכים")
            vectordb.add_documents(doc_batch)
        except Exception as e:
            print(f"❌ שגיאה בשלב ההטמעה (Embeddings): {e}")
            print("🔁 המשך עם הקבוצה הבאה...")

    print("✅ הושלם! Vector DB נבנה ונשמר. לוג נכתב ל-ingest_log.txt")

if __name__ == "__main__":
    ingest()
