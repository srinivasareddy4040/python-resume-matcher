import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import sqlite3
import datetime

import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Setup ---

logging.basicConfig(filename='resume_matcher.log', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

conn = sqlite3.connect('resume_match_history.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS match_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        resume_path TEXT,
        jd_path TEXT,
        tfidf_score REAL,
        skill_score REAL
    )
''')
conn.commit()

# --- Constants ---

SKILLS = [
    "python", "sql", "machine learning", "nlp", "tensorflow",
    "deep learning", "pandas", "numpy", "excel", "data analysis",
    "communication", "java", "c++"
]

# --- Text Extraction Functions ---

def extract_text_from_pdf(path):
    text = ""
    try:
        doc = fitz.open(path)
        for page in doc:
            text += page.get_text()
    except Exception as e:
        logging.warning(f"PyMuPDF extraction failed for {path}, switching to OCR. Reason: {e}")
        text = extract_text_with_ocr(path)
    return text.strip()

def extract_text_with_ocr(path):
    images = convert_from_path(path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img)
    return text.strip()

def extract_text_from_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(path)
    elif ext == '.txt':
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError("Unsupported file format. Please use PDF or TXT.")

# --- Text Cleaning & Skill Extraction ---

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_skills(text, skills_list=SKILLS):
    text_words = set(text.split())
    matched_skills = [skill for skill in skills_list if skill.lower() in text_words]
    return matched_skills

# --- Scoring ---

def calculate_tfidf_similarity(text1, text2):
    if not text1 or not text2:
        return 0.0
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return similarity

def compute_skill_score(resume_text, jd_text):
    resume_skills = set(extract_skills(resume_text))
    jd_skills = set(extract_skills(jd_text))
    if not jd_skills:
        return 0.0
    overlap = resume_skills.intersection(jd_skills)
    return len(overlap) / len(jd_skills)

# --- Matching Logic ---

def match_resume(resume_path, jd_path):
    resume_text = extract_text_from_file(resume_path)
    jd_text = extract_text_from_file(jd_path)

    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)

    tfidf_score = calculate_tfidf_similarity(resume_clean, jd_clean)
    skill_score = compute_skill_score(resume_clean, jd_clean)

    timestamp = datetime.datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO match_history (timestamp, resume_path, jd_path, tfidf_score, skill_score)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, resume_path, jd_path, tfidf_score, skill_score))
    conn.commit()

    logging.info(f"Match: {resume_path} vs {jd_path} | TF-IDF: {tfidf_score:.4f} | Skill: {skill_score:.4f}")
    return tfidf_score, skill_score

# --- GUI ---

class ResumeMatcherApp:
    def __init__(self, root):
        self.root = root
        root.title("Resume Matcher")

        tk.Label(root, text="Resume File:").grid(row=0, column=0, sticky="e")
        self.resume_entry = tk.Entry(root, width=50)
        self.resume_entry.grid(row=0, column=1)
        tk.Button(root, text="Browse", command=self.browse_resume).grid(row=0, column=2)

        tk.Label(root, text="Job Description File:").grid(row=1, column=0, sticky="e")
        self.jd_entry = tk.Entry(root, width=50)
        self.jd_entry.grid(row=1, column=1)
        tk.Button(root, text="Browse", command=self.browse_jd).grid(row=1, column=2)

        tk.Button(root, text="Match", command=self.run_match).grid(row=2, column=1, pady=10)

        self.result_text = tk.Text(root, height=6, width=70)
        self.result_text.grid(row=3, column=0, columnspan=3, pady=10)

    def browse_resume(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF/TXT files", "*.pdf *.txt")])
        if file_path:
            self.resume_entry.delete(0, tk.END)
            self.resume_entry.insert(0, file_path)

    def browse_jd(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF/TXT files", "*.pdf *.txt")])
        if file_path:
            self.jd_entry.delete(0, tk.END)
            self.jd_entry.insert(0, file_path)

    def run_match(self):
        resume_path = self.resume_entry.get()
        jd_path = self.jd_entry.get()
        if not resume_path or not jd_path:
            messagebox.showerror("Input Error", "Please select both resume and job description files.")
            return
        if not os.path.exists(resume_path) or not os.path.exists(jd_path):
            messagebox.showerror("File Error", "One or both files do not exist.")
            return
        try:
            tfidf_score, skill_score = match_resume(resume_path, jd_path)
            result = f"TF-IDF Similarity Score: {tfidf_score:.2%}\nSkill Match Score: {skill_score:.2%}"
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            logging.error(f"Error in matching: {e}")

# --- CLI Support ---
def run_cli():
    resume_path = input("Enter path to resume (PDF/TXT): ").strip().strip('"')
    jd_path = input("Enter path to job description (PDF/TXT): ").strip().strip('"')
    
    if not os.path.exists(resume_path) or not os.path.exists(jd_path):
        print("Error: One or both files not found.")
        return
    try:
        tfidf_score, skill_score = match_resume(resume_path, jd_path)
        print(f"\nTF-IDF Similarity Score: {tfidf_score:.2%}")
        print(f"Skill Match Score: {skill_score:.2%}")
    except Exception as e:
        print(f"Error: {e}")


# --- Main ---

if __name__ == '__main__':
    mode = input("Choose mode: (1) CLI or (2) GUI: ").strip()
    if mode == '1':
        run_cli()
    elif mode == '2':
        root = tk.Tk()
        app = ResumeMatcherApp(root)
        root.mainloop()
    else:
        print("Invalid selection.")
