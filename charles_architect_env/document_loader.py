import os

# יצירת שלד לקובץ document_loader.py לפי ההסבר
document_loader_code = """
import os
import json
import pandas as pd
from PyPDF2 import PdfReader

def summarize_pdf(path):
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\\n"
        return text[:3000]  # חיתוך כדי למנוע עומס
    except Exception as e:
        return f"שגיאה בקריאת PDF {path}: {str(e)}"

def summarize_all_pdfs(folder_path):
    summaries = {}
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            path = os.path.join(folder_path, file)
            summaries[file] = summarize_pdf(path)
    return summaries

def read_excel_summary(file_path):
    try:
        df = pd.read_excel(file_path)
        return df.head(10).to_dict(orient="records")  # דוגמית כדי לא להעמיס על הזיכרון
    except Exception as e:
        return { "error": str(e) }

def list_all_python_files(base_dir):
    structure = {}
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    try:
                        content = f.read()
                        relative_path = os.path.relpath(path, base_dir)
                        structure[relative_path] = content[:3000]
                    except Exception as e:
                        structure[path] = f"שגיאה בקריאת הקובץ: {str(e)}"
    return structure

def load_system_documents(folder: str, excel_files: list) -> dict:
    context = {}
    context["pdf_summaries"] = summarize_all_pdfs(folder)
    for excel_file in excel_files:
        context[excel_file] = read_excel_summary(os.path.join(folder, excel_file))
    context["code_files_structure"] = list_all_python_files(base_dir="../")
    return context
"""

# שמירה לקובץ document_loader.py
document_loader_path = "/mnt/data/document_loader.py"
with open(document_loader_path, "w", encoding="utf-8") as f:
    f.write(document_loader_code)

document_loader_path
