import pandas as pd
import os

excel_files = [
    "charles_architect_env/project_docs/סוכני_המערכת_המלאים (9).xlsx",
    "charles_architect_env/project_docs/פירוט קבצי מערכת.xlsx"
]
output_dir = "charles_architect_env/project_docs/"

for excel_path in excel_files:
    xls = pd.ExcelFile(excel_path)
    base_name = os.path.splitext(os.path.basename(excel_path))[0]
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name)
        # שם הקובץ: שם_הקובץ_שם_הגיליון.csv
        safe_sheet = sheet_name.replace("/", "_").replace("\\", "_")
        csv_path = os.path.join(output_dir, f"{base_name}_{safe_sheet}.csv")
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"שמרתי: {csv_path}") 