import os
import base64

exclude_dirs = {'__pycache__', '.git', '.vscode', 'Charles_FocusedSpec_Backup'}
binary_exts = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.xls', '.xlsx', '.pdf', '.zip'}

def is_binary(filename):
    return os.path.splitext(filename)[1].lower() in binary_exts

text_output = "all_text_files.txt"
binary_output = "all_binary_files.txt"

with open(text_output, "w", encoding="utf-8") as text_out, \
     open(binary_output, "w", encoding="utf-8") as binary_out:

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for filename in files:
            filepath = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1].lower()
            # בודק האם קובץ בינארי (תמונה/אקסל וכו')
            try:
                if is_binary(filename):
                    with open(filepath, "rb") as binfile:
                        encoded = base64.b64encode(binfile.read()).decode('ascii')
                    binary_out.write(f"\n\n##### FILE: {filepath} #####\n")
                    binary_out.write(f"[BINARY FILE: {ext} | BASE64 ENCODED BELOW]\n")
                    binary_out.write(encoded)
                else:
                    with open(filepath, "r", encoding="utf-8") as infile:
                        text_out.write(f"\n\n##### FILE: {filepath} #####\n")
                        text_out.write(infile.read())
            except Exception as e:
                # קבצים שלא קריאים כאחד מהסוגים
                err_text = f"[UNREADABLE FILE: {e}]\n"
                if is_binary(filename):
                    binary_out.write(f"\n\n##### FILE: {filepath} #####\n")
                    binary_out.write(err_text)
                else:
                    text_out.write(f"\n\n##### FILE: {filepath} #####\n")
                    text_out.write(err_text)
