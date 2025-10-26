"""
Utility functions for PDF processing and file operations
"""

import PyPDF2
import json
from typing import Dict, Any


def format_large_number(value, currency="€"):
    """
    Format large numbers with K (thousands), M (millions), or B (billions).
    
    Args:
        value: Numeric value to format
        currency: Currency symbol (default "€")
        
    Returns:
        Formatted string (e.g., "€1.5M", "€500K", "€2.3B")
    """
    if value is None or value == 0:
        return f"{currency}0"
    
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_value >= 1_000_000_000:
        return f"{sign}{currency}{abs_value/1_000_000_000:.1f}B"
    elif abs_value >= 1_000_000:
        return f"{sign}{currency}{abs_value/1_000_000:.1f}M"
    elif abs_value >= 1_000:
        return f"{sign}{currency}{abs_value/1_000:.0f}K"
    else:
        return f"{sign}{currency}{abs_value:,.0f}"


def format_number(value, suffix=""):
    """
    Format large numbers without currency symbol.
    
    Args:
        value: Numeric value to format
        suffix: Optional suffix (e.g., " customers", " units")
        
    Returns:
        Formatted string (e.g., "1.5M customers", "500K units", "2.3B")
    """
    if value is None or value == 0:
        return f"0{suffix}"
    
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_value >= 1_000_000_000:
        return f"{sign}{abs_value/1_000_000_000:.1f}B{suffix}"
    elif abs_value >= 1_000_000:
        return f"{sign}{abs_value/1_000_000:.1f}M{suffix}"
    elif abs_value >= 10_000:
        return f"{sign}{abs_value/1_000:.0f}K{suffix}"
    else:
        return f"{sign}{abs_value:,.0f}{suffix}"


def read_pdf_file(pdf_path: str) -> str:
    """
    Extract text from PDF file path.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text from all pages
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""


def read_pdf_upload(uploaded_file) -> str:
    """
    Extract text from uploaded PDF file (Streamlit file uploader).
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Extracted text from all pages
    """
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {e}")


def save_json(data: Dict[str, Any], filename: str) -> bool:
    """
    Save data to JSON file with pretty formatting.
    
    Args:
        data: Dictionary to save
        filename: Output filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False


def load_json(filename: str) -> Dict[str, Any]:
    """
    Load JSON file.
    
    Args:
        filename: JSON file path
        
    Returns:
        Dictionary with loaded data
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {}
