"""
Fix unmerged NCERT books: find chapter PDFs buried in nested folders,
merge them into a single PDF per book, place in Subject folder, clean up.
"""
import os
import re
import shutil
import fitz  # PyMuPDF

NCERT_DIR = "NCERT"

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def find_chapter_pdfs(directory):
    """Recursively find all PDFs in a directory tree."""
    pdfs = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.lower().endswith('.pdf'):
                pdfs.append(os.path.join(root, f))
    return pdfs

def merge_and_cleanup(book_folder, subject_folder, book_name):
    """Merge all PDFs inside book_folder, save to subject_folder/book_name.pdf, delete book_folder."""
    pdfs = find_chapter_pdfs(book_folder)
    if not pdfs:
        print(f"  [SKIP] No PDFs found in {book_folder}")
        return False
    
    # Sort by filename only (natural sort)
    pdfs.sort(key=lambda p: natural_sort_key(os.path.basename(p)))
    
    print(f"  [MERGE] {book_name}: {len(pdfs)} chapters")
    for p in pdfs:
        print(f"    -> {os.path.basename(p)}")
    
    merged = fitz.open()
    for pdf_path in pdfs:
        try:
            doc = fitz.open(pdf_path)
            merged.insert_pdf(doc)
            doc.close()
        except Exception as e:
            print(f"    [ERROR] Could not read {pdf_path}: {e}")
    
    final_path = os.path.join(subject_folder, f"{book_name}.pdf")
    if os.path.exists(final_path):
        os.remove(final_path)
    
    merged.save(final_path)
    merged.close()
    print(f"  [SAVED] {final_path} ({os.path.getsize(final_path) / (1024*1024):.1f} MB)")
    
    # Remove the old book folder entirely
    shutil.rmtree(book_folder)
    print(f"  [CLEANUP] Removed {book_folder}")
    return True

# --- Main ---
fixed = 0

for class_folder in sorted(os.listdir(NCERT_DIR)):
    class_path = os.path.join(NCERT_DIR, class_folder)
    if not os.path.isdir(class_path):
        continue
    
    for subject_folder_name in sorted(os.listdir(class_path)):
        subject_path = os.path.join(class_path, subject_folder_name)
        if not os.path.isdir(subject_path):
            continue
        
        for item in sorted(os.listdir(subject_path)):
            item_path = os.path.join(subject_path, item)
            if not os.path.isdir(item_path):
                continue  # Already a PDF file, skip
            
            # This is a book-title folder that shouldn't exist
            # Check if it contains chapter PDFs (directly or nested)
            pdfs = find_chapter_pdfs(item_path)
            if pdfs:
                print(f"\n[FOUND] {class_folder}/{subject_folder_name}/{item}")
                if merge_and_cleanup(item_path, subject_path, item):
                    fixed += 1
            else:
                # Empty folder, just remove it
                shutil.rmtree(item_path)
                print(f"[REMOVED] Empty folder: {class_folder}/{subject_folder_name}/{item}")

print(f"\n{'='*60}")
print(f"Done! Fixed {fixed} unmerged books.")
