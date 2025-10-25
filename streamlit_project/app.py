"""
Streamlit App for PDF to Structured JSON Conversion
"""

import streamlit as st
import json
import PyPDF2
from openai import OpenAI
from datetime import datetime
import os
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()

# Configure OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None

# Page configuration
st.set_page_config(
    page_title="PDF to JSON Converter",
    page_icon="📄",
    layout="wide"
)

def read_pdf(uploaded_file) -> str:
    """Extract text from uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def generate_structured_json(pdf_content: str, structure_type: str, custom_prompt: str = "") -> dict:
    """Generate structured JSON from PDF content using OpenAI."""
    
    if not OPENAI_API_KEY:
        st.error("OpenAI API Key not found. Please set it in .env file.")
        return {}
    
    # Define different structure templates
    if structure_type == "Business Analysis":
        prompt = f"""
        Analyze the following document and create a structured JSON with business insights.
        
        Document Content:
        {pdf_content}
        
        Create a JSON structure with:
        1. executive_summary: Brief overview
        2. key_metrics: Important business metrics found
        3. market_analysis: Market insights
        4. financial_projections: Any financial data
        5. recommendations: Key recommendations
        6. extracted_data: All relevant structured data
        
        Return ONLY valid JSON, no markdown formatting.
        """
    
    elif structure_type == "Product Information":
        prompt = f"""
        Extract product information from the following document.
        
        Document Content:
        {pdf_content}
        
        Create a JSON structure with:
        1. product_name: Name of the product
        2. description: Product description
        3. features: List of features
        4. specifications: Technical specifications
        5. pricing: Pricing information if available
        6. target_market: Target audience/market
        7. competitors: Competitive products mentioned
        
        Return ONLY valid JSON, no markdown formatting.
        """
    
    elif structure_type == "Financial Data":
        prompt = f"""
        Extract financial data from the following document.
        
        Document Content:
        {pdf_content}
        
        Create a JSON structure with:
        1. revenue: Revenue information
        2. costs: Cost breakdown
        3. profit_margins: Profit margins
        4. projections: Financial projections by year
        5. key_metrics: Important financial KPIs
        6. assumptions: Financial assumptions
        
        Return ONLY valid JSON, no markdown formatting.
        """
    
    else:  # Custom
        prompt = f"""
        {custom_prompt}
        
        Document Content:
        {pdf_content}
        
        Return ONLY valid JSON, no markdown formatting.
        """
    
    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured data from documents and returns valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8192
        )
        
        json_text = response.choices[0].message.content.strip().replace('```json', '').replace('```', '').strip()
        return json.loads(json_text)
    
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON from AI response: {e}")
        st.code(json_text)
        return {}
    except Exception as e:
        st.error(f"Error generating structured data: {e}")
        return {}

# Main UI
st.title("📄 PDF to Structured JSON Converter")
st.markdown("Upload a PDF and convert it to structured JSON using AI")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check API key status
    if OPENAI_API_KEY:
        st.success("✅ OpenAI API Key loaded")
    else:
        st.error("❌ OpenAI API Key not found")
        st.info("Please set OPENAI_API_KEY in your .env file")
    
    st.divider()
    
    # Structure type selection
    structure_type = st.selectbox(
        "Select JSON Structure Type",
        ["Business Analysis", "Product Information", "Financial Data", "Custom"]
    )
    
    # Custom prompt if selected
    custom_prompt = ""
    if structure_type == "Custom":
        custom_prompt = st.text_area(
            "Custom Prompt",
            placeholder="Describe what structured data you want to extract...",
            height=150
        )
    
    st.divider()
    
    # Download options
    st.header("📥 Download Options")
    pretty_print = st.checkbox("Pretty Print JSON", value=True)
    indent_size = st.slider("Indent Size", 2, 8, 2) if pretty_print else None

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📤 Upload PDF")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF document to extract structured data"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Display PDF info
        file_size = len(uploaded_file.getvalue()) / 1024  # KB
        st.info(f"📊 File size: {file_size:.2f} KB")
        
        # Extract text button
        if st.button("🔍 Extract Text from PDF", use_container_width=True):
            with st.spinner("Extracting text..."):
                pdf_text = read_pdf(uploaded_file)
                
                if pdf_text:
                    st.session_state.pdf_text = pdf_text
                    st.success(f"✅ Extracted {len(pdf_text)} characters")
                    
                    # Show preview
                    with st.expander("📝 Preview Extracted Text"):
                        st.text_area("Text Content", pdf_text, height=200)

with col2:
    st.header("🎯 Generate Structured JSON")
    
    if 'pdf_text' in st.session_state:
        if st.button("🚀 Generate JSON", use_container_width=True, type="primary"):
            with st.spinner("Generating structured JSON with AI..."):
                structured_data = generate_structured_json(
                    st.session_state.pdf_text,
                    structure_type,
                    custom_prompt
                )
                
                if structured_data:
                    st.session_state.json_output = structured_data
                    st.success("✅ JSON generated successfully!")
    else:
        st.info("👆 Please upload and extract text from a PDF first")

# Results section
if 'json_output' in st.session_state:
    st.divider()
    st.header("📊 Generated JSON Output")
    
    # Display JSON
    json_str = json.dumps(
        st.session_state.json_output,
        indent=indent_size if pretty_print else None,
        ensure_ascii=False
    )
    
    st.json(st.session_state.json_output)
    
    # Download button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"structured_output_{timestamp}.json"
        
        st.download_button(
            label="💾 Download JSON",
            data=json_str,
            file_name=filename,
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        if st.button("🗑️ Clear Results", use_container_width=True):
            if 'json_output' in st.session_state:
                del st.session_state.json_output
            if 'pdf_text' in st.session_state:
                del st.session_state.pdf_text
            st.rerun()
    
    # Show statistics
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("JSON Keys", len(st.session_state.json_output))
    
    with col2:
        json_size = len(json_str) / 1024
        st.metric("JSON Size", f"{json_size:.2f} KB")
    
    with col3:
        if 'pdf_text' in st.session_state:
            compression_ratio = (len(json_str) / len(st.session_state.pdf_text)) * 100
            st.metric("Compression Ratio", f"{compression_ratio:.1f}%")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Powered by OpenAI GPT-4o-mini | TUM-BMW Project</p>
</div>
""", unsafe_allow_html=True)
