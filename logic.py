import hashlib, io, os
import PyPDF2
from PIL import Image, ImageEnhance
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from werkzeug.utils import secure_filename

# Add your find_tesseract and pytesseract logic here...
# (Referencing the previous optimized OCR code)

# logic.py
import hashlib
import os

def extract_text(file_path):
    # Get the filename to check extension
    filename = os.path.basename(file_path).lower()
    
    # 1. Open the file in Binary Read mode
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # 2. Generate SHA-256 Hash
    # FIXED: Change .he_hex() to .hexdigest()
    f_hash = hashlib.sha256(content).hexdigest()

    # 3. Text Extraction Placeholder
    # Replace this with your actual OCR or PDF extraction code
    text = ""
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        # text = your_ocr_function(file_path)
        text = "Extracted OCR text goes here" 
    elif filename.endswith('.pdf'):
        # text = your_pdf_function(file_path)
        text = "Extracted PDF text goes here"
        
    return text, content, f_hash

# def run_plagiarism_check(new_text, new_hash, course_id, current_user_id, Submission):
#     # Check exact hash match in this course
#     existing = Submission.query.filter_by(course_id=course_id, content_hash=new_hash).first()
#     if existing: return 1.0, f"Duplicate of {existing.author.username}"

#     # Vector check against other students
#     others = Submission.query.filter(Submission.course_id == course_id, 
#                                     Submission.user_id != current_user_id).all()
#     if not others or not new_text: return 0.0, None

#     docs = [s.text_content for s in others]
#     try:
#         vectorizer = TfidfVectorizer(stop_words='english')
#         tfidf = vectorizer.fit_transform(docs + [new_text])
#         sims = cosine_similarity(tfidf[-1:], tfidf[:-1])[0]
#         return float(sims.max()), others[sims.argmax()].author.username
#     except: return 0.0, None
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compare_texts(text1, text2):
    """
    Calculates similarity between two strings using TF-IDF and Cosine Similarity.
    """
    if not text1.strip() or not text2.strip():
        return 0.0
    
    try:
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([text1, text2])
        # Calculate the cosine similarity between the two vectors
        result = cosine_similarity(tfidf[0:1], tfidf[1:2])
        return float(result[0][0])
    except:
        return 0.0

# logic.py

def run_plagiarism_check(file_path, new_hash, course_id, current_user_id, Submission):
    # 1. EXACT HASH CHECK (Catches 100% identical files instantly)
    # We look for ANY submission in this course with the same hash
    duplicate = Submission.query.filter(
        Submission.course_id == course_id,
        Submission.content_hash == new_hash,
        Submission.user_id != current_user_id  # Don't flag the student's own file
    ).first()
    
    if duplicate:
        return 1.0, f"Exact duplicate of {duplicate.author.username}'s file"

    # 2. READ FILE CONTENT
    current_text = ""
    try:
        # If you are using PDFs/Docx, you need specific libraries. 
        # For plain text/code:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            current_text = f.read().strip()
    except Exception as e:
        return 0.0, "Error reading file content"

    # If the file is empty or unreadable, current_text is "", similarity will be 0.
    if len(current_text) < 10:
        return 0.0, "Low quality scan or empty file"

    # 3. COMPARE TEXT
    others = Submission.query.filter(
        Submission.course_id == course_id,
        Submission.user_id != current_user_id
    ).all()
    
    max_score = 0.0
    reason = "No significant matches"

    for s in others:
        # IMPORTANT: Get the full path to the other file
        # If app.py saves to 'uploads/', make sure this matches
        base_dir = os.path.dirname(file_path)
        other_path = os.path.join(base_dir, s.filename) 
        
        if os.path.exists(other_path):
            with open(other_path, 'r', encoding='utf-8', errors='ignore') as f:
                other_text = f.read().strip()
            
            # Use the compare_texts function we defined earlier
            score = compare_texts(current_text, other_text)
            
            if score > max_score:
                max_score = score
                if score > 0.3:
                    reason = f"Highly similar to {s.author.username}"

    return max_score, reason