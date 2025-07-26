# ✅ שלב ראשון – עקיפת SSL
import ssl
import httpx
import os
import openai  # ⬅️ הוספה חשובה!

# ביטול בדיקות SSL בכל הרכיבים
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""
ssl._create_default_https_context = ssl._create_unverified_context
httpx._config.DEFAULT_CA_BUNDLE_PATH = None
openai.verify_ssl = False  # ⬅️ הוספה קריטית!

# ✅ המשך הקוד הרגיל
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()

VECTORSTORE_DIR = r"C:\Users\rani\Desktop\Charles_FocusedSpec\vectorstore"

embeddings = OpenAIEmbeddings()
db = Chroma(persist_directory=VECTORSTORE_DIR, embedding_function=embeddings)
retriever = db.as_retriever()

llm = ChatOpenAI(model_name="gpt-4", temperature=0)

prompt = ChatPromptTemplate.from_template("""
המסמכים הבאים רלוונטיים לשאלה:
{context}

אתה עוזר חכם בשם Charles Architect – GPT מומחה לפיתוח מערכות AI מתקדמות לזיהוי מניות פורצות.

ענה על השאלה הבאה בעברית, בצורה ברורה, מסודרת ומקצועית, כאילו אתה חלק מצוות הפיתוח.

🔍 בכל תשובה:
- אם מצאת תשובה, ציין גם את מקור המידע לפי שדות ה־metadata:
  📄 שם הקובץ (filename)  
  𞲂️ סוג הקובץ (category: code/spec/excel/log)  
  📅 תאריך יצירה (created_at)
- אם לא מצאת מידע ודאי, אמור "לא מצאתי מידע רלוונטי".
- תעדף תשובות ממקורות מסוג code או spec אם קיימים.

שאלה:
{question}
""")

def filter_documents(docs, filters, mode="strict"):
    result = []
    for doc in docs:
        meta = doc.metadata
        score = 0

        if filters.get("categories"):
            if meta.get("category") in filters["categories"]:
                score += 1
            elif mode == "strict":
                continue

        if filters.get("min_date"):
            created_str = meta.get("created_at")
            if created_str:
                created_dt = datetime.strptime(created_str, "%Y-%m-%d %H:%M:%S")
                if created_dt >= filters["min_date"]:
                    score += 1
                elif mode == "strict":
                    continue

        if filters.get("folder_keywords"):
            source = meta.get("source", "")
            if any(folder in source for folder in filters["folder_keywords"]):
                score += 1
            elif mode == "strict":
                continue

        if filters.get("filename_keywords"):
            filename = meta.get("filename", "").lower()
            if any(kw in filename for kw in filters["filename_keywords"]):
                score += 1
            elif mode == "strict":
                continue

        if mode == "soft" and score > 0:
            result.append(doc)
        elif mode == "strict" and score == len(filters):
            result.append(doc)
        elif not filters:
            result.append(doc)

    return result

def print_docs(input, filters=None, mode="strict"):
    docs = retriever.invoke(input)
    docs = filter_documents(docs, filters, mode)

    print("\n📄 מסמכים שנשלפו:")
    for doc in docs:
        meta = doc.metadata
        print(f"- 📄 {meta.get('filename')} | 𞲂️ {meta.get('category')} | 📅 {meta.get('created_at')}")
        snippet = doc.page_content[:300].replace("\n", " ")
        print(f"  ✂️ תוכן: {snippet}\n")
    return docs

def format_docs(docs):
    formatted = []
    for doc in docs:
        meta = doc.metadata
        snippet = doc.page_content[:300].replace("\n", " ")
        formatted.append(f"[📄 {meta.get('filename')} | 𞲂️ {meta.get('category')} | 📅 {meta.get('created_at')}\n{snippet}]")
    return "\n\n".join(formatted)

def build_chain(question, filters=None, mode="strict"):
    docs = print_docs(question, filters, mode)
    context = format_docs(docs)
    return chain.invoke({"question": question, "context": context}, config=RunnableConfig())

chain = (
    RunnableLambda(lambda x: {"question": x["question"], "context": x["context"]}) |
    prompt |
    llm |
    StrOutputParser()
)

print('\n🔍 Charles Architect – שאל שאלה על המערכת שלך ("exit" כדי לצאת):\n')

while True:
    mode = input("🏛️ מצב סינון (strict/soft): ").strip().lower() or "strict"
    categories = input("𞲂️ קטגוריות (code,spec,excel,log,other): ").strip()
    min_date = input("📅 תאריך מינימום (yyyy-mm-dd): ").strip()
    folders = input("📂 תיקיות מקור (core/, utils/, וכו'): ").strip()
    names = input("📄 מילות מפתח בשם קובץ (מופרד בפסיקים): ").strip()

    filters = {}
    if categories:
        filters["categories"] = [c.strip() for c in categories.split(",")]
    if min_date:
        filters["min_date"] = datetime.strptime(min_date, "%Y-%m-%d")
    if folders:
        filters["folder_keywords"] = [f.strip() for f in folders.split(",")]
    if names:
        filters["filename_keywords"] = [n.strip().lower() for n in names.split(",")]

    query = input("\n❓ שאלה: ")
    if query.lower() in ["exit", "quit", "bye"]:
        print("\n👋 ביי!")
        break

    response = build_chain(query, filters, mode)
    print("\n🧐 תשובה:\n", response)
