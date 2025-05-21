
📝 Description:
This is a Python-based Resume Matcher tool that compares a resume with a job description (JD) using two metrics:
1. TF-IDF Similarity Score – Measures overall textual similarity.
2. Skill Match Score – Compares key skills extracted from both documents.

---

💡 Features:
- Supports PDF and TXT files.
- GUI interface with tkinter.
- Command-Line Interface (CLI) support.
- OCR fallback for scanned PDFs (using pytesseract).
- Match history stored in a local SQLite database (`resume_match_history.db`).
- Logs actions to `resume_matcher.log`.



## 🧰 Technologies Used

- Python 3
- `PyMuPDF (fitz)`
- `pdf2image`
- `pytesseract`
- `scikit-learn`
- `sqlite3`
- `tkinter` (standard library)
- `logging` (standard library)
to install technologies use 
🔧 Dependencies:

Install required packages via pip:

```bash
pip install PyMuPDF pdf2image pytesseract scikit-learn
```

---

📂 Supported File Formats:
- `.pdf` (both digital and scanned)
- `.txt`

---

📌 Skills Considered (customizable in code):
```python
SKILLS = [
    "python", "sql", "machine learning", "nlp", "tensorflow",
    "deep learning", "pandas", "numpy", "excel", "data analysis",
    "communication", "java", "c++"
]
```

---

🚀 Usage:

▶ GUI Mode:

1. Run the script.
2. When prompted: enter `2` for GUI mode.
3. A window opens. Use "Browse" buttons to select Resume and JD files.
4. Click "Match".
5. Scores are displayed in the bottom box.

📸 Screenshot (example):
```
TF-IDF Similarity Score: 75.33%
Skill Match Score: 33.54%
```

▶ CLI Mode:

1. Run the script.
2. When prompted: enter `1` for CLI mode.
3. Input full paths for the resume and JD files when asked.

💻 Sample Output:
```
Enter path to resume (PDF/TXT): C:\Users\User\Documents\resume.pdf
Enter path to job description (PDF/TXT): C:\Users\User\Downloads\jd.txt

TF-IDF Similarity Score: 75.12%
Skill Match Score: 24.85%

---

🗂 Match History:
- Stored in `resume_match_history.db` with timestamp, file paths, TF-IDF, and Skill Score.

📋 Log File:
- See `resume_matcher.log` for warnings, errors, and activity logs.
