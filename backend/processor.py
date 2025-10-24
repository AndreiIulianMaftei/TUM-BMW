import PyPDF2
import docx
from io import BytesIO


def extract_text_from_pdf(file_content: bytes) -> str:
    pdf_file = BytesIO(file_content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def extract_text_from_docx(file_content: bytes) -> str:
    docx_file = BytesIO(file_content)
    doc = docx.Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def process_file(file_content: bytes, file_type: str) -> str:
    if file_type == "pdf":
        return extract_text_from_pdf(file_content)
    elif file_type == "docx":
        return extract_text_from_docx(file_content)
    else:
        raise ValueError("Unsupported file type")
