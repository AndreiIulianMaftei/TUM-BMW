import re
from io import BytesIO
from pypdf import PdfReader
from docx import Document

def extract_text_from_pdf(file_content: bytes) -> str:
    pdf_reader = PdfReader(BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(file_content: bytes) -> str:
    doc = Document(BytesIO(file_content))
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def filter_sensitive_data(text: str) -> str:
    filtered = text
    
    filtered = re.sub(r'CONFIDENTIAL\s*', '', filtered, flags=re.IGNORECASE)
    filtered = re.sub(r'\b\d{2}\.\d{2}\.\d{4}\b', '[DATE]', filtered)
    filtered = re.sub(r'\b[A-Z]{2,3}-\d{1,3}\b', '[DEPT]', filtered)
    filtered = re.sub(r'\b[A-Z]{2,3}-[A-Z]\b', '[DEPT]', filtered)
    filtered = re.sub(r'\bLohhof\b', '[LOCATION]', filtered, flags=re.IGNORECASE)
    filtered = re.sub(r'\bParsdorf\b', '[LOCATION]', filtered, flags=re.IGNORECASE)
    
    lines = filtered.split('\n')
    skip_section = False
    filtered_lines = []
    
    for line in lines:
        if 'FTEs / Capacities' in line or 'RESOURCES FOR VALIDATION' in line:
            skip_section = True
        if skip_section and (line.strip().startswith('RED FLAGS') or line.strip().startswith('NEXT STEPS')):
            skip_section = False
        if not skip_section:
            filtered_lines.append(line)
    
    filtered = '\n'.join(filtered_lines)
    filtered = re.sub(r'\n{3,}', '\n\n', filtered)
    
    return filtered.strip()

def process_file(file_content: bytes, file_type: str) -> str:
    print(f"\n📄 PROCESSOR: Starting file processing")
    print(f"   File type: {file_type}")
    print(f"   File size: {len(file_content)} bytes")
    
    try:
        if file_type == "pdf":
            print(f"   Extracting from PDF...")
            raw_text = extract_text_from_pdf(file_content)
        elif file_type == "docx":
            print(f"   Extracting from DOCX...")
            raw_text = extract_text_from_docx(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        print(f"   ✓ Raw text extracted: {len(raw_text)} characters")
        print(f"   ✓ Preview: {raw_text[:150]}...")
        
        print(f"   🔒 Filtering sensitive data...")
        filtered = filter_sensitive_data(raw_text)
        print(f"   ✓ Filtered text: {len(filtered)} characters")
        print(f"   ✓ Removed: {len(raw_text) - len(filtered)} characters")
        
        return filtered
        
    except Exception as e:
        print(f"   ❌ PROCESSOR ERROR: {type(e).__name__}: {str(e)}")
        raise
