"""
TAM/SAM/SOM Analysis Dashboard
Professional dashboard for market analysis visualization
"""

import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd

# Import custom modules
from tam_sam_som_analysis import generate_tam_sam_som_analysis
from costs_analysis import generate_cost_analysis
from income import generate_income_analysis
from utils import read_pdf_upload, save_json, format_large_number, format_number
from visualizations import (
    create_market_funnel_chart,
    create_growth_chart,
    create_comparison_chart,
    create_growth_rate_chart,
    create_cost_breakdown_chart,
    create_cost_per_unit_chart,
    create_total_cost_chart,
    create_income_chart,
    create_income_comparison_chart,
    create_cumulative_profit_chart
)
from chat_modifier import (
    parse_modification_request,
    preview_modifications,
    apply_modifications
)

# Load environment variables
load_dotenv()

# Check API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Create results directory if it doesn't exist
RESULTS_DIR = "analysis_results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Initialize session state for editable mode
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'original_analysis' not in st.session_state:
    st.session_state.original_analysis = None
if 'sales_volume_percentage' not in st.session_state:
    st.session_state.sales_volume_percentage = 50.0  # Default 50% of SOM
if 'sam_percentage' not in st.session_state:
    st.session_state.sam_percentage = 50.0  # Default SAM as 50% of TAM
if 'som_percentage' not in st.session_state:
    st.session_state.som_percentage = 50.0  # Default SOM as 50% of SAM

# Initialize chat-related session state
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'pending_modifications' not in st.session_state:
    st.session_state.pending_modifications = None
if 'modification_preview' not in st.session_state:
    st.session_state.modification_preview = None
if 'modification_history' not in st.session_state:
    st.session_state.modification_history = []
if 'use_percentages' not in st.session_state:
    st.session_state.use_percentages = False  # Toggle between absolute values and percentages
if 'analysis_end_year' not in st.session_state:
    st.session_state.analysis_end_year = 2030
if 'selected_sales_model' not in st.session_state:
    st.session_state.selected_sales_model = None
if 'sales_model_data' not in st.session_state:
    st.session_state.sales_model_data = {}
if 'cost_analysis' not in st.session_state:
    st.session_state.cost_analysis = None
if 'cost_analysis_done' not in st.session_state:
    st.session_state.cost_analysis_done = False
if 'cost_edit_mode' not in st.session_state:
    st.session_state.cost_edit_mode = False
if 'original_cost_analysis' not in st.session_state:
    st.session_state.original_cost_analysis = None
if 'income_analysis' not in st.session_state:
    st.session_state.income_analysis = None
if 'income_analysis_done' not in st.session_state:
    st.session_state.income_analysis_done = False
if 'selected_income_strategy' not in st.session_state:
    st.session_state.selected_income_strategy = None

# Page configuration
st.set_page_config(
    page_title="BMW Motorrad • Market Analysis Dashboard",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for BMW-style professional look
st.markdown("""
    <style>
    /* BMW Brand Colors */
    :root {
        --bmw-blue: #1C69D4;
        --bmw-dark-blue: #0E3B6F;
        --bmw-light-blue: #4A9EFF;
        --bmw-gray: #262626;
        --bmw-light-gray: #F4F4F4;
        --bmw-silver: #E8E8E8;
    }
    
    /* Main container */
    .main {
        padding: 0rem 2rem;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    }
    
    /* Header styling */
    .bmw-header {
        background: linear-gradient(135deg, var(--bmw-dark-blue) 0%, var(--bmw-blue) 100%);
        padding: 2rem 2rem 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(28, 105, 212, 0.15);
    }
    
    .bmw-header h1 {
        color: white;
        font-weight: 700;
        font-size: 2.5rem;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .bmw-header .subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Metrics styling */
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid var(--bmw-blue);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(28, 105, 212, 0.2);
    }
    
    .stMetric label {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--bmw-gray);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: var(--bmw-blue);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        font-weight: 600;
        color: var(--bmw-dark-blue);
        transition: all 0.2s;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--bmw-light-gray);
        border-color: var(--bmw-blue);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        overflow: hidden;
    }
    
    div[data-testid="stDataFrame"] table {
        font-size: 0.9rem;
    }
    
    div[data-testid="stDataFrame"] thead tr th {
        background: var(--bmw-dark-blue) !important;
        color: white !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.5px;
        padding: 1rem 0.5rem;
    }
    
    div[data-testid="stDataFrame"] tbody tr:nth-child(even) {
        background: var(--bmw-light-gray);
    }
    
    div[data-testid="stDataFrame"] tbody tr:hover {
        background: rgba(28, 105, 212, 0.05);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        border-right: 1px solid #e0e0e0;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: var(--bmw-dark-blue);
    }
    
    /* Button styling */
    .stButton button {
        background: var(--bmw-blue);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        background: var(--bmw-dark-blue);
        box-shadow: 0 4px 12px rgba(28, 105, 212, 0.3);
        transform: translateY(-1px);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid var(--bmw-blue);
    }
    
    /* Section headers */
    h1 {
        color: var(--bmw-dark-blue);
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h2 {
        color: var(--bmw-blue);
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid var(--bmw-silver);
        padding-bottom: 0.5rem;
    }
    
    h3 {
        color: var(--bmw-gray);
        font-weight: 600;
        margin-top: 1.5rem;
    }
    
    /* Dividers */
    hr {
        border: none;
        border-top: 2px solid var(--bmw-silver);
        margin: 2rem 0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: var(--bmw-gray);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--bmw-blue);
        color: white;
    }
    
    /* Cards for cost structure */
    .cost-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin: 1rem 0;
        border-left: 4px solid var(--bmw-light-blue);
    }
    
    .cost-card h4 {
        color: var(--bmw-dark-blue);
        margin-top: 0;
        font-weight: 700;
    }
    
    /* Success/Info/Warning boxes */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #c3e6cb;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 8px;
        color: #155724;
        font-weight: 500;
    }
    
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 1px solid #bee5eb;
        border-left: 4px solid var(--bmw-blue);
        padding: 1rem;
        border-radius: 8px;
        color: #0c5460;
        font-weight: 500;
    }
    
    /* Footer */
    .dashboard-footer {
        text-align: center;
        padding: 2rem;
        color: #6c757d;
        font-size: 0.9rem;
        border-top: 1px solid var(--bmw-silver);
        margin-top: 3rem;
    }
    </style>
""", unsafe_allow_html=True)


def recalculate_costs(cost_data, sales_volume_data):
    """
    Recalculate all cost metrics dynamically based on current values.
    """
    if not cost_data or 'yearly_cost_breakdown' not in cost_data:
        return cost_data
    
    # Get base cost components
    one_time_dev = cost_data.get('total_development_cost', 0)
    annual_cac = cost_data.get('total_customer_acquisition_cost', 0)
    annual_ops = cost_data.get('total_distribution_operations_cost', 0)
    annual_after_sales = cost_data.get('total_after_sales_cost', 0)
    cogs_per_unit = cost_data.get('average_cogs_per_bundle', 0)
    
    yearly_breakdown = cost_data.get('yearly_cost_breakdown', {})
    
    # Get available years from sales_volume_data
    available_years = sorted(sales_volume_data.keys())
    
    for year in available_years:
        if year not in yearly_breakdown:
            # Initialize if doesn't exist
            yearly_breakdown[year] = {}
            
        volume = sales_volume_data.get(year, 0)
        
        # First year includes one-time development cost
        dev_cost = one_time_dev if year == available_years[0] else 0
        
        # Calculate total COGS based on actual volume
        total_cogs = volume * cogs_per_unit
        
        # Total cost for the year
        total_cost = dev_cost + annual_cac + annual_ops + annual_after_sales + total_cogs
        
        # Update yearly breakdown
        yearly_breakdown[year].update({
            "projected_volume": volume,
            "one_time_development": dev_cost,
            "customer_acquisition": annual_cac,
            "distribution_operations": annual_ops,
            "after_sales": annual_after_sales,
            "total_cogs": round(total_cogs, 2),
            "cogs_per_unit": cogs_per_unit,
            "total_cost": round(total_cost, 2),
        })
    
    # Update seven year summary with available years
    total_all_years = sum(yearly_breakdown[year]["total_cost"] for year in available_years if year in yearly_breakdown)
    total_volume_all_years = sum(sales_volume_data[year] for year in available_years if year in sales_volume_data)
    
    first_year = available_years[0] if available_years else "2024"
    last_year = available_years[-1] if available_years else "2030"
    
    cost_data["seven_year_summary"] = {
        f"total_cost_{first_year}_{last_year}": round(total_all_years, 2),
        f"total_volume_{first_year}_{last_year}": total_volume_all_years,
        "average_cost_per_unit": round(total_all_years / total_volume_all_years, 2) if total_volume_all_years > 0 else 0,
        "currency": "EUR"
    }
    
    return cost_data


# Main Dashboard
st.markdown("""
    <div class="bmw-header">
        <h1>🏍️ BMW MOTORRAD</h1>
        <div class="subtitle">Market Analysis & Financial Dashboard • TAM/SAM/SOM Strategy</div>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📁 Upload Document")
    
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=['pdf'],
        help="Upload your market analysis document"
    )
    
    st.divider()
    
    # API Status
    if OPENAI_API_KEY:
        st.success("✅ API Connected")
    else:
        st.error("❌ API Key Missing")
        st.info("Set OPENAI_API_KEY in .env")
    
    st.divider()
    
    # Generate button
    if uploaded_file:
        if st.button("🚀 Generate Analysis", use_container_width=True, type="primary"):
            with st.spinner("Analyzing document..."):
                pdf_text = read_pdf_upload(uploaded_file)
                
                if pdf_text:
                    st.session_state.pdf_text = pdf_text
                    
                    with st.spinner("🤖 Generating market analysis with AI..."):
                        analysis = generate_tam_sam_som_analysis(pdf_text)
                        
                        if analysis:
                            st.session_state.analysis = analysis
                            st.session_state.original_analysis = json.loads(json.dumps(analysis))
                            st.session_state.edit_mode = False
                            
                            # Save LLM result to analysis_results folder
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{RESULTS_DIR}/tam_sam_som_{timestamp}.json"
                            
                            if save_json(analysis, filename):
                                print(f"✅ [SERVER] Analysis saved to: {filename}")
                                st.session_state.last_saved_file = filename
                            
                            st.success("✅ Analysis Complete!")
                            st.balloons()
                            print("✅ [SERVER] LLM Analysis completed successfully!")
                            st.rerun()
    
    st.divider()
    
    # Analysis Year Range
    if 'analysis' in st.session_state:
        st.header("📅 Analysis Period")
        
        end_year = st.selectbox(
            "End Year",
            options=[2025, 2026, 2027, 2028, 2029, 2030],
            index=[2025, 2026, 2027, 2028, 2029, 2030].index(st.session_state.analysis_end_year),
            help="Select the final year for your analysis"
        )
        
        if end_year != st.session_state.analysis_end_year:
            st.session_state.analysis_end_year = end_year
            st.rerun()
        
        st.caption(f"Analyzing 2024 - {end_year}")
    
    st.divider()
    
    # Market Percentages Configuration
    if 'analysis' in st.session_state:
        st.header("� Market Percentages")
        
        use_pct = st.toggle(
            "Use Percentage Mode",
            value=st.session_state.use_percentages,
            help="Toggle between absolute values and percentage-based calculations"
        )
        
        if use_pct != st.session_state.use_percentages:
            st.session_state.use_percentages = use_pct
            st.rerun()
        
        if st.session_state.use_percentages:
            st.markdown("**Set market relationships:**")
            
            sam_pct = st.slider(
                "SAM (% of TAM)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.sam_percentage,
                step=1.0,
                help="SAM as percentage of TAM",
                key="sam_pct_slider"
            )
            if sam_pct != st.session_state.sam_percentage:
                st.session_state.sam_percentage = sam_pct
                # Force recalculation by triggering rerun
                st.rerun()
            
            som_pct = st.slider(
                "SOM (% of SAM)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.som_percentage,
                step=1.0,
                help="SOM as percentage of SAM",
                key="som_pct_slider"
            )
            if som_pct != st.session_state.som_percentage:
                st.session_state.som_percentage = som_pct
                # Force recalculation by triggering rerun
                st.rerun()
            
            volume_pct = st.slider(
                "Sales Volume (% of SOM)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.sales_volume_percentage,
                step=1.0,
                help="Sales Volume as percentage of SOM",
                key="volume_pct_slider_pct"
            )
            if volume_pct != st.session_state.sales_volume_percentage:
                st.session_state.sales_volume_percentage = volume_pct
                # Force recalculation by triggering rerun
                st.rerun()
            
            # Show the cascade
            st.info(f"""
            📊 **Current Settings:**
            - SAM: {sam_pct:.0f}% of TAM
            - SOM: {som_pct:.0f}% of SAM ({(sam_pct * som_pct / 100):.1f}% of TAM)
            - Volume: {volume_pct:.0f}% of SOM ({(sam_pct * som_pct * volume_pct / 10000):.2f}% of TAM)
            """)
        else:
            volume_pct = st.slider(
                "Sales Volume (% of SOM)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.sales_volume_percentage,
                step=5.0,
                help="Percentage of SOM that represents actual sales volume",
                key="volume_pct_slider_manual"
            )
            
            if volume_pct != st.session_state.sales_volume_percentage:
                st.session_state.sales_volume_percentage = volume_pct
                # Force recalculation
                st.rerun()
            
            st.info(f"📊 Sales Volume: {volume_pct:.0f}% of SOM")
    
    st.divider()
    
    # Sales Model Selection
    if 'analysis' in st.session_state:
        st.header("🎯 Sales Model")
        
        sales_model = st.radio(
            "Select Sales Model",
            ["Single Buy", "Subscription", "Royalties"],
            index=0 if st.session_state.selected_sales_model is None 
                  else ["Single Buy", "Subscription", "Royalties"].index(st.session_state.selected_sales_model) 
                  if st.session_state.selected_sales_model in ["Single Buy", "Subscription", "Royalties"] else 0,
            help="Choose your preferred sales model"
        )
        
        if sales_model != st.session_state.selected_sales_model:
            st.session_state.selected_sales_model = sales_model
        
        # Show selected model info
        if sales_model == "Single Buy":
            st.success("💵 One-time purchase model selected")
        elif sales_model == "Subscription":
            st.success("📅 Recurring subscription model selected")
        else:
            st.success("💎 Royalty-based model selected")
    
    st.divider()
    
    # Edit Mode Toggle
    if 'analysis' in st.session_state:
        st.header("✏️ Edit Mode")
        
        edit_mode = st.toggle("Enable Editing", value=st.session_state.edit_mode)
        if edit_mode != st.session_state.edit_mode:
            st.session_state.edit_mode = edit_mode
            st.rerun()
        
        if st.session_state.edit_mode:
            st.info("📝 Edit values below. Charts update automatically!")
        
        st.divider()
    
    # Cost Edit Mode Toggle (only show if cost analysis exists)
    if 'cost_analysis' in st.session_state and st.session_state.cost_analysis_done:
        st.header("✏️ Edit Costs")
        
        cost_edit_mode = st.toggle("Enable Cost Editing", value=st.session_state.cost_edit_mode)
        if cost_edit_mode != st.session_state.cost_edit_mode:
            st.session_state.cost_edit_mode = cost_edit_mode
            st.rerun()
        
        if st.session_state.cost_edit_mode:
            st.info("📝 Edit cost values below. All calculations update automatically!")
        
        # Show data flow
        with st.expander("🔗 Data Flow"):
            st.markdown("""
            **Automatic Calculations:**
            
            1️⃣ **TAM/SAM/SOM** → Changes update **Sales Volume**
            
            2️⃣ **Volume %** slider → Changes update **Sales Volume**
            
            3️⃣ **Sales Volume** → Auto-updates **Total COGS**
            - `Total COGS = Volume × COGS per Unit`
            
            4️⃣ **Total COGS + Other Costs** → Auto-updates **Total Cost**
            - `Total = Dev + CAC + Dist + After Sales + COGS`
            
            5️⃣ All yearly costs → Auto-updates **7-Year Summary**
            
            💡 **Edit any base value and watch everything recalculate!**
            """)
        
        st.divider()
    
    # Download results
    if 'analysis' in st.session_state:
        st.header("💾 Export")
        
        # Show last saved file info
        if 'last_saved_file' in st.session_state:
            st.caption(f"📁 Auto-saved: {st.session_state.last_saved_file}")
        
        json_str = json.dumps(st.session_state.analysis, indent=2, ensure_ascii=False)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f"tam_sam_som_{timestamp}.json",
            mime="application/json",
            use_container_width=True
        )
        
        if st.button("🔄 Reset to Original", use_container_width=True):
            if st.session_state.original_analysis:
                st.session_state.analysis = json.loads(json.dumps(st.session_state.original_analysis))
                st.session_state.sales_volume_percentage = 50.0
                st.success("Reset market analysis to original values!")
                st.rerun()
        
        # Reset costs button (if cost analysis exists)
        if 'cost_analysis' in st.session_state and st.session_state.original_cost_analysis:
            if st.button("🔄 Reset Costs to Original", use_container_width=True):
                st.session_state.cost_analysis = json.loads(json.dumps(st.session_state.original_cost_analysis))
                st.success("Reset costs to original values!")
                st.rerun()
        
        # Save current configuration
        if st.button("💾 Save Configuration", use_container_width=True):
            config_data = {
                'analysis': st.session_state.analysis,
                'sales_model': st.session_state.selected_sales_model,
                'volume_percentage': st.session_state.sales_volume_percentage,
                'sales_model_data': st.session_state.sales_model_data,
                'cost_analysis': st.session_state.cost_analysis if 'cost_analysis' in st.session_state else None,
                'cost_analysis_done': st.session_state.cost_analysis_done,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to analysis_results folder
            config_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            config_filename = f"{RESULTS_DIR}/config_{config_timestamp}.json"
            
            if save_json(config_data, config_filename):
                st.success(f"✅ Saved to: {config_filename}")
    
    # ============= CHAT MODIFIER INTERFACE =============
    # Only show if any analysis has been generated
    if 'analysis' in st.session_state or 'cost_analysis' in st.session_state or 'income_analysis' in st.session_state:
        st.divider()
        st.header("💬 AI Assistant")
        st.caption("Modify data with natural language")
        
        # Show examples in expander
        with st.expander("💡 Example Commands"):
            st.markdown("""
            **Income Modifications:**
            - "Change royalty rate to 12%"
            - "Increase price by 10%"
            - "Set subscription price to €75/month"
            
            **Cost Modifications:**
            - "Reduce development costs by 20%"
            - "Set customer acquisition to €500K"
            - "Decrease all costs by 15%"
            
            **Market Modifications:**
            - "Set TAM to 50 million"
            - "Increase SAM by 10%"
            """)
        
        # Chat input
        if prompt := st.chat_input("e.g., 'Increase royalty rate to 12%'", key="chat_input"):
            # Add user message to history
            st.session_state.chat_messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Build current data context
            current_data = {
                "income_analysis": st.session_state.get('income_analysis'),
                "cost_analysis": st.session_state.get('cost_analysis'),
                "tam_sam_som": st.session_state.get('analysis'),
                "selected_income_strategy": st.session_state.get('selected_income_strategy')
            }
            
            # Parse the modification request
            with st.spinner("🤖 Understanding your request..."):
                modification_plan = parse_modification_request(prompt, current_data)
            
            if "error" in modification_plan:
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": f"❌ {modification_plan['error']}"
                })
            elif modification_plan.get('confidence') == 'low' or modification_plan.get('data_type') == 'unknown':
                # Handle unclear requests
                interpretation = modification_plan.get('interpretation', 'Could not understand the request')
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": f"❓ I'm not sure how to interpret that.\n\n{interpretation}\n\nPlease try:\n- 'Increase price by 50%'\n- 'Set development costs to €1M for 2026'\n- 'Reduce all costs by 20%'"
                })
            else:
                # Generate preview
                with st.spinner("📊 Calculating impact..."):
                    preview = preview_modifications(modification_plan, current_data)
                
                if "error" in preview:
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": f"❌ {preview['error']}"
                    })
                else:
                    # Store pending modifications
                    st.session_state.pending_modifications = modification_plan
                    st.session_state.modification_preview = preview
                    
                    # Add assistant response
                    interpretation = modification_plan.get('interpretation', 'Modification parsed')
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": f"✅ {interpretation}\n\nReview the preview below and click Apply to confirm."
                    })
            
            st.rerun()
        
        # Display chat history (last 5 messages)
        if st.session_state.chat_messages:
            st.markdown("**Recent Activity:**")
            for msg in st.session_state.chat_messages[-5:]:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
        
        # Show modification preview if pending
        if st.session_state.pending_modifications and st.session_state.modification_preview:
            st.markdown("---")
            st.markdown("### 🔍 Preview Changes")
            
            preview = st.session_state.modification_preview
            plan = st.session_state.pending_modifications
            
            # Show what will change
            st.info(f"**Modifying:** {plan.get('variable', 'Unknown')}")
            
            if preview.get("data_type") == "income" and "summary" in preview:
                summary = preview["summary"]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Current Total Income",
                        f"€{summary['old_total_income']:,.0f}"
                    )
                with col2:
                    change_pct = summary['change_percentage']
                    st.metric(
                        "New Total Income",
                        f"€{summary['new_total_income']:,.0f}",
                        delta=f"{change_pct:+.1f}%"
                    )
                
                # Show per-year changes
                if len(preview.get("changes", [])) <= 7:
                    with st.expander("📅 Yearly Changes"):
                        for change in preview["changes"]:
                            st.write(f"**{change['year']}:** {change['old_value']} → {change['new_value']}")
            
            elif preview.get("data_type") == "cost" and "summary" in preview:
                summary = preview["summary"]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Current Total Cost",
                        f"€{summary['old_total_cost']:,.0f}"
                    )
                with col2:
                    change_pct = summary['change_percentage']
                    st.metric(
                        "New Total Cost",
                        f"€{summary['new_total_cost']:,.0f}",
                        delta=f"{change_pct:+.1f}%"
                    )
            
            elif preview.get("data_type") == "market" and "summary" in preview:
                summary = preview["summary"]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        "Current Value",
                        f"€{summary['old_value']:,.0f}"
                    )
                with col2:
                    change_pct = summary['change_percentage']
                    st.metric(
                        "New Value",
                        f"€{summary['new_value']:,.0f}",
                        delta=f"{change_pct:+.1f}%"
                    )
            
            # Confirmation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Apply Changes", use_container_width=True, type="primary"):
                    success = apply_modifications(
                        st.session_state.pending_modifications,
                        st.session_state.modification_preview,
                        st.session_state
                    )
                    
                    if success:
                        # Add to history
                        st.session_state.modification_history.append({
                            "timestamp": datetime.now().isoformat(),
                            "modification": st.session_state.pending_modifications,
                            "preview": st.session_state.modification_preview
                        })
                        
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": "✅ Changes applied successfully!"
                        })
                        
                        # Clear pending
                        st.session_state.pending_modifications = None
                        st.session_state.modification_preview = None
                        st.success("✅ Modifications applied!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to apply modifications")
            
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.pending_modifications = None
                    st.session_state.modification_preview = None
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": "❌ Modification cancelled"
                    })
                    st.rerun()
        
        # Clear chat history button
        if st.session_state.chat_messages:
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()

# Main Content
if 'analysis' not in st.session_state:
    # Welcome screen
    st.info("👈 Upload a PDF document in the sidebar to get started")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📄 Upload")
        st.write("Upload your market analysis document")
    
    with col2:
        st.markdown("### 🤖 Analyze")
        st.write("AI extracts market insights")
    
    with col3:
        st.markdown("### 📊 Visualize")
        st.write("Beautiful charts & metrics")

else:
    analysis = st.session_state.analysis
    
    # Executive Summary Section
    st.markdown("## 📊 Executive Summary")
    
    # Show configuration info with BMW styling
    if st.session_state.use_percentages:
        st.markdown(f"""
        <div class="info-box">
            <strong>🎯 Percentage Mode Active</strong> • <strong>📅 Analysis Period:</strong> 2024-{st.session_state.analysis_end_year}<br><br>
            <strong>Market Relationships:</strong><br>
            • SAM = <strong>{st.session_state.sam_percentage:.0f}%</strong> of TAM<br>
            • SOM = <strong>{st.session_state.som_percentage:.0f}%</strong> of SAM<br>  
            • Volume = <strong>{st.session_state.sales_volume_percentage:.0f}%</strong> of SOM<br><br>
            💡 <em>Adjust percentages in the Control Center to see real-time updates</em>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="info-box">
            <strong>📅 Analysis Period:</strong> 2024-{st.session_state.analysis_end_year} • 
            <strong>📊 Target Volume:</strong> {st.session_state.sales_volume_percentage:.0f}% of SOM
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")  # Spacing
    
    # Get year range
    years = list(range(2024, st.session_state.analysis_end_year + 1))
    
    # Apply percentage mode if enabled
    if st.session_state.use_percentages:
        for year in years:
            year_str = str(year)
            tam_val = analysis['TAM']['numbers'].get(year_str, 0)
            
            # Calculate SAM as percentage of TAM
            sam_val = tam_val * (st.session_state.sam_percentage / 100)
            analysis['SAM']['numbers'][year_str] = int(sam_val)
            
            # Calculate SOM as percentage of SAM
            som_val = sam_val * (st.session_state.som_percentage / 100)
            analysis['SOM']['numbers'][year_str] = int(som_val)
    
    # Calculate Sales Volume for each year
    def calculate_sales_volume(year: str) -> int:
        som_value = analysis['SOM']['numbers'].get(year, 0)
        volume = int(som_value * (st.session_state.sales_volume_percentage / 100))
        return volume
    
    # Store sales volume data
    sales_volume_data = {}
    for year in years:
        sales_volume_data[str(year)] = calculate_sales_volume(str(year))
    
    # Check if volume has changed and we need to recalculate costs
    previous_volume = st.session_state.sales_model_data.get('sales_volume_by_year', {})
    volume_changed = previous_volume != sales_volume_data
    
    # Save to session state
    st.session_state.sales_model_data = {
        'model_type': st.session_state.selected_sales_model,
        'volume_percentage': st.session_state.sales_volume_percentage,
        'sales_volume_by_year': sales_volume_data
    }
    
    # If volume changed and cost analysis was done, automatically recalculate
    if volume_changed and st.session_state.cost_analysis_done:
        st.session_state.cost_analysis = recalculate_costs(
            st.session_state.cost_analysis,
            sales_volume_data
        )
        
    # Key Performance Indicators Section
    first_year = str(years[0])
    last_year = str(years[-1])
    
    tam_first = analysis['TAM']['numbers'].get(first_year, 0)
    tam_last = analysis['TAM']['numbers'].get(last_year, 0)
    tam_growth = ((tam_last - tam_first) / tam_first) * 100 if tam_first > 0 else 0
    
    sam_first = analysis['SAM']['numbers'].get(first_year, 0)
    sam_last = analysis['SAM']['numbers'].get(last_year, 0)
    sam_growth = ((sam_last - sam_first) / sam_first) * 100 if sam_first > 0 else 0
    
    som_first = analysis['SOM']['numbers'].get(first_year, 0)
    som_last = analysis['SOM']['numbers'].get(last_year, 0)
    som_growth = ((som_last - som_first) / som_first) * 100 if som_first > 0 else 0
    
    vol_first = sales_volume_data.get(first_year, 0)
    vol_last = sales_volume_data.get(last_year, 0)
    vol_growth = ((vol_last - vol_first) / vol_first) * 100 if vol_first > 0 else 0
    
    # Display KPIs in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="TOTAL ADDRESSABLE MARKET",
            value=format_number(tam_last, " customers"),
            delta=f"{tam_growth:+.1f}% from {first_year}",
            help=f"Total potential customers in {last_year}"
        )
    
    with col2:
        st.metric(
            label="SERVICEABLE ADDRESSABLE MARKET",
            value=format_number(sam_last, " customers"),
            delta=f"{sam_growth:+.1f}% from {first_year}",
            help=f"Serviceable customers in {last_year}"
        )
    
    with col3:
        st.metric(
            label="SERVICEABLE OBTAINABLE MARKET",
            value=format_number(som_last, " customers"),
            delta=f"{som_growth:+.1f}% from {first_year}",
            help=f"Obtainable customers in {last_year}"
        )
    
    with col4:
        st.metric(
            label="PROJECTED SALES VOLUME",
            value=format_number(vol_last, " units"),
            delta=f"{vol_growth:+.1f}% from {first_year}",
            help=f"Expected sales volume in {last_year}"
        )
    
    st.markdown("---")
    st.markdown("")  # Spacing
    
    # Interactive Editor Section (if edit mode is on)
    if st.session_state.edit_mode:
        with st.expander("✏️ **EDIT MARKET DATA**", expanded=True):
            st.markdown("### Modify Values by Year")
            st.info("💡 **Note:** TAM/SAM/SOM values represent **number of customers/people**, not currency. When you edit a value, the trend will be applied proportionally to all years.")
            
            # Create tabs for each year in range
            year_tabs = st.tabs([str(year) for year in years])
            
            for idx, year in enumerate(years):
                with year_tabs[idx]:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"**TAM - {year}** (customers)")
                        current_tam = analysis['TAM']['numbers'].get(str(year), 0)
                        new_tam = st.number_input(
                            f"TAM Value",
                            min_value=0,
                            value=current_tam,
                            step=1000,
                            key=f"tam_{year}",
                            label_visibility="collapsed"
                        )
                        if new_tam != current_tam:
                            # Calculate the change ratio
                            ratio = new_tam / current_tam if current_tam > 0 else 1.0
                            
                            # Apply the ratio to all years to maintain the trend
                            for y in years:
                                old_val = analysis['TAM']['numbers'].get(str(y), 0)
                                analysis['TAM']['numbers'][str(y)] = int(old_val * ratio)
                            
                            # Recalculate if percentage mode
                            if st.session_state.use_percentages:
                                st.rerun()
                    
                    with col2:
                        st.markdown(f"**SAM - {year}** (customers)")
                        if st.session_state.use_percentages:
                            sam_val = analysis['SAM']['numbers'].get(str(year), 0)
                            st.metric("SAM (Auto)", f"{sam_val:,}", 
                                     help=f"Calculated as {st.session_state.sam_percentage:.0f}% of TAM")
                        else:
                            current_sam = analysis['SAM']['numbers'].get(str(year), 0)
                            new_sam = st.number_input(
                                f"SAM Value",
                                min_value=0,
                                value=current_sam,
                                step=1000,
                                key=f"sam_{year}",
                                label_visibility="collapsed"
                            )
                            if new_sam != current_sam:
                                # Calculate the change ratio
                                ratio = new_sam / current_sam if current_sam > 0 else 1.0
                                
                                # Apply the ratio to all years to maintain the trend
                                for y in years:
                                    old_val = analysis['SAM']['numbers'].get(str(y), 0)
                                    analysis['SAM']['numbers'][str(y)] = int(old_val * ratio)
                    
                    with col3:
                        st.markdown(f"**SOM - {year}** (customers)")
                        if st.session_state.use_percentages:
                            som_val = analysis['SOM']['numbers'].get(str(year), 0)
                            st.metric("SOM (Auto)", f"{som_val:,}",
                                     help=f"Calculated as {st.session_state.som_percentage:.0f}% of SAM")
                        else:
                            current_som = analysis['SOM']['numbers'].get(str(year), 0)
                            new_som = st.number_input(
                                f"SOM Value",
                                min_value=0,
                                value=current_som,
                                step=1000,
                                key=f"som_{year}",
                                label_visibility="collapsed"
                            )
                            if new_som != current_som:
                                # Calculate the change ratio
                                ratio = new_som / current_som if current_som > 0 else 1.0
                                
                                # Apply the ratio to all years to maintain the trend
                                for y in years:
                                    old_val = analysis['SOM']['numbers'].get(str(y), 0)
                                    analysis['SOM']['numbers'][str(y)] = int(old_val * ratio)
                    
                    with col4:
                        st.markdown(f"**Volume - {year}**")
                        sales_vol = sales_volume_data.get(str(year), 0)
                        st.metric("Volume (Auto)", f"{sales_vol:,}",
                                 help=f"Calculated as {st.session_state.sales_volume_percentage:.0f}% of SOM")
                    
                    # Show percentages and relationships
                    st.markdown("---")
                    col_a, col_b, col_c, col_d = st.columns(4)
                    with col_a:
                        tam_val = analysis['TAM']['numbers'].get(str(year), 0)
                        st.info(f"� TAM: {tam_val:,} customers")
                    with col_b:
                        sam_val = analysis['SAM']['numbers'].get(str(year), 0)
                        sam_pct = (sam_val / tam_val * 100) if tam_val > 0 else 0
                        st.success(f"� SAM: {sam_val:,} customers ({sam_pct:.1f}% of TAM)")
                    with col_c:
                        som_val = analysis['SOM']['numbers'].get(str(year), 0)
                        som_pct = (som_val / sam_val * 100) if sam_val > 0 else 0
                        st.warning(f"� SOM: {som_val:,} customers ({som_pct:.1f}% of SAM)")
                    with col_d:
                        sales_vol = sales_volume_data.get(str(year), 0)
                        vol_pct = (sales_vol / som_val * 100) if som_val > 0 else 0
                        st.caption(f"📦 Volume: {sales_vol:,} units ({vol_pct:.1f}% of SOM)")
    
    # Market Visualizations Section
    st.markdown("## 📊 Market Analysis & Visualizations")
    
    with st.expander("� **MARKET FUNNEL & TRENDS**", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(create_market_funnel_chart(analysis), use_container_width=True)
        
        with col2:
            st.plotly_chart(create_comparison_chart(analysis), use_container_width=True)
        
        # Growth chart (full width)
        st.plotly_chart(create_growth_chart(analysis), use_container_width=True)
    
    # Growth rate in separate expander
    with st.expander("📈 **GROWTH RATE ANALYSIS**"):
        st.plotly_chart(create_growth_rate_chart(analysis), use_container_width=True)
    
    # Market Definitions (editable if in edit mode)
    st.markdown("## 🎯 Market Definitions & Strategy")
    with st.expander("**MARKET DESCRIPTIONS & JUSTIFICATIONS**"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### TAM")
            if st.session_state.edit_mode:
                new_tam_desc = st.text_area(
                    "Description",
                    analysis['TAM']['description_of_public'],
                    key="tam_desc",
                    height=100
                )
                analysis['TAM']['description_of_public'] = new_tam_desc
                
                st.markdown("**Justification:**")
                new_tam_just = st.text_area(
                    "Justification",
                    analysis['TAM']['justification'],
                    key="tam_just",
                    height=150
                )
                analysis['TAM']['justification'] = new_tam_just
            else:
                st.info(analysis['TAM']['description_of_public'])
                with st.expander("View Justification"):
                    st.write(analysis['TAM']['justification'])
        
        with col2:
            st.markdown("### SAM")
            if st.session_state.edit_mode:
                new_sam_desc = st.text_area(
                    "Description",
                    analysis['SAM']['description_of_public'],
                    key="sam_desc",
                    height=100
                )
                analysis['SAM']['description_of_public'] = new_sam_desc
                
                st.markdown("**Justification:**")
                new_sam_just = st.text_area(
                    "Justification",
                    analysis['SAM']['justification'],
                    key="sam_just",
                    height=150
                )
                analysis['SAM']['justification'] = new_sam_just
            else:
                st.success(analysis['SAM']['description_of_public'])
                with st.expander("View Justification"):
                    st.write(analysis['SAM']['justification'])
        
        with col3:
            st.markdown("### SOM")
            if st.session_state.edit_mode:
                new_som_desc = st.text_area(
                    "Description",
                    analysis['SOM']['description_of_public'],
                    key="som_desc",
                    height=100
                )
                analysis['SOM']['description_of_public'] = new_som_desc
                
                st.markdown("**Justification:**")
                new_som_just = st.text_area(
                    "Justification",
                    analysis['SOM']['justification'],
                    key="som_just",
                    height=150
                )
                analysis['SOM']['justification'] = new_som_just
            else:
                st.warning(analysis['SOM']['description_of_public'])
                with st.expander("View Justification"):
                    st.write(analysis['SOM']['justification'])
    
    # Industry Examples in collapsible section
    with st.expander("🏢 Industry Examples & Case Studies"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### TAM Example")
            st.markdown(f"**{analysis['TAM']['industry_example']['name']}**")
            st.write(analysis['TAM']['industry_example']['description'])
            st.markdown(f"[🔗 Read More]({analysis['TAM']['industry_example']['link']})")
        
        with col2:
            st.markdown("### SAM Example")
            st.markdown(f"**{analysis['SAM']['industry_example']['name']}**")
            st.write(analysis['SAM']['industry_example']['description'])
            st.markdown(f"[🔗 Read More]({analysis['SAM']['industry_example']['link']})")
        
        with col3:
            st.markdown("### SOM Example")
            st.markdown(f"**{analysis['SOM']['industry_example']['name']}**")
            st.write(analysis['SOM']['industry_example']['description'])
            st.markdown(f"[🔗 Read More]({analysis['SOM']['industry_example']['link']})")
    
    # Sources in collapsible section
    with st.expander("📚 Sources & References"):
        for i, source in enumerate(analysis.get('sources', []), 1):
            st.markdown(f"{i}. [{source}]({source})")
    
    st.divider()
    
    # Cost Analysis Button (appears after TAM/SAM/SOM is complete)
    st.markdown("---")
    st.markdown("## 💰 Financial Analysis & Cost Structure")
    
    if not st.session_state.cost_analysis_done:
        st.markdown("""
        <div class="info-box">
            <strong>📊 Next Step:</strong> Generate comprehensive cost analysis including development, 
            customer acquisition, distribution, and COGS calculations based on your sales projections.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")
        
        if st.button("**GENERATE COST ANALYSIS**", use_container_width=True, type="primary"):
            with st.spinner("🤖 Analyzing costs with AI..."):
                # Get sales volume data
                sales_volume = st.session_state.sales_model_data.get('sales_volume_by_year', {})
                
                # Generate cost analysis
                cost_analysis = generate_cost_analysis(
                    st.session_state.pdf_text,
                    sales_volume
                )
                
                if cost_analysis and "error" not in cost_analysis:
                    st.session_state.cost_analysis = cost_analysis
                    st.session_state.original_cost_analysis = json.loads(json.dumps(cost_analysis))
                    st.session_state.cost_analysis_done = True
                    
                    # Save cost analysis
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    cost_filename = f"{RESULTS_DIR}/cost_analysis_{timestamp}.json"
                    
                    if save_json(cost_analysis, cost_filename):
                        print(f"✅ [SERVER] Cost analysis saved to: {cost_filename}")
                    
                    st.success("✅ Cost Analysis Complete!")
                    st.balloons()
                    print("✅ [SERVER] Cost analysis completed successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to generate cost analysis")
    else:
        st.markdown('<div class="success-box">✓ Cost Analysis Completed Successfully</div>', unsafe_allow_html=True)
        st.markdown("")
        
        if st.button("🔄 Regenerate Cost Analysis", use_container_width=True):
            st.session_state.cost_analysis_done = False
            st.session_state.cost_analysis = None
            st.rerun()
        
        # Display Cost Analysis Results
        if st.session_state.cost_analysis:
            cost_data = st.session_state.cost_analysis
            
            # Editable Base Cost Components (if edit mode enabled)
            if st.session_state.cost_edit_mode:
                with st.expander("✏️ Edit Base Cost Components", expanded=True):
                    st.markdown("### Annual Cost Components")
                    st.caption("Edit these values to recalculate all yearly costs")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_cac = st.number_input(
                            "Annual Customer Acquisition Cost (€)",
                            min_value=0,
                            value=int(cost_data.get('total_customer_acquisition_cost', 0)),
                            step=1000,
                            key="edit_cac"
                        )
                        cost_data['total_customer_acquisition_cost'] = new_cac
                        
                        new_ops = st.number_input(
                            "Annual Distribution & Operations Cost (€)",
                            min_value=0,
                            value=int(cost_data.get('total_distribution_operations_cost', 0)),
                            step=1000,
                            key="edit_ops"
                        )
                        cost_data['total_distribution_operations_cost'] = new_ops
                    
                    with col2:
                        new_after_sales = st.number_input(
                            "Annual After Sales Cost (€)",
                            min_value=0,
                            value=int(cost_data.get('total_after_sales_cost', 0)),
                            step=1000,
                            key="edit_after_sales"
                        )
                        cost_data['total_after_sales_cost'] = new_after_sales
                        
                        new_cogs_per_unit = st.number_input(
                            "COGS per Unit (€)",
                            min_value=0.0,
                            value=float(cost_data.get('average_cogs_per_bundle', 0)),
                            step=0.1,
                            format="%.2f",
                            key="edit_cogs_unit"
                        )
                        cost_data['average_cogs_per_bundle'] = new_cogs_per_unit
                    
                    st.markdown("### One-Time Costs")
                    new_dev = st.number_input(
                        "One-Time Development Cost (€) - Applied in 2024 only",
                        min_value=0,
                        value=int(cost_data.get('total_development_cost', 0)),
                        step=5000,
                        key="edit_dev"
                    )
                    cost_data['total_development_cost'] = new_dev
                    
                    # Recalculate with new values
                    cost_data = recalculate_costs(cost_data, sales_volume_data)
                    st.success("✅ Costs recalculated automatically!")
            
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_dev = cost_data.get('total_development_cost', 0)
                st.metric("💻 Total Development", f"${total_dev:,.0f}")
            with col2:
                total_cac = cost_data.get('total_customer_acquisition_cost', 0)
                st.metric("📢 Annual CAC", f"${total_cac:,.0f}")
            with col3:
                total_dist = cost_data.get('total_distribution_operations_cost', 0)
                st.metric("🚚 Annual Distribution", f"${total_dist:,.0f}")
            with col4:
                total_after_sales = cost_data.get('total_after_sales_cost', 0)
                st.metric("🛠️ Annual After Sales", f"${total_after_sales:,.0f}")
            
            # Show COGS per unit and summary
            col1, col2, col3 = st.columns(3)
            with col1:
                cogs_unit = cost_data.get('average_cogs_per_bundle', 0)
                st.metric("💰 COGS per Unit", f"${cogs_unit:.2f}")
            with col2:
                if 'seven_year_summary' in cost_data:
                    # Get the key dynamically
                    summary_keys = [k for k in cost_data['seven_year_summary'].keys() if k.startswith('total_cost_')]
                    if summary_keys:
                        total_period = cost_data['seven_year_summary'].get(summary_keys[0], 0)
                        st.metric(f"📊 Total Cost ({first_year}-{last_year})", f"${total_period:,.0f}")
            with col3:
                if 'seven_year_summary' in cost_data:
                    avg_cost_unit = cost_data['seven_year_summary'].get('average_cost_per_unit', 0)
                    st.metric(f"📈 Avg Cost/Unit ({first_year}-{last_year})", f"${avg_cost_unit:.2f}")
            
            # Yearly breakdown - cleaner compact view
            with st.expander("📊 Yearly Cost Breakdown"):
                st.caption("💡 These values automatically update when you change TAM/SAM/SOM or sales volume percentage!")
                
                yearly_breakdown = cost_data.get('yearly_cost_breakdown', {})
                
                # Create a table view for cleaner display
                import pandas as pd
                
                table_data = []
                for year_str in [str(y) for y in years]:
                    if year_str not in yearly_breakdown:
                        continue
                    year_data = yearly_breakdown[year_str]
                    table_data.append({
                        'Year': year_str,
                        'Volume': f"{year_data['projected_volume']:,}",
                        'Development': format_large_number(year_data['one_time_development']),
                        'CAC': format_large_number(year_data['customer_acquisition']),
                        'Distribution': format_large_number(year_data['distribution_operations']),
                        'After Sales': format_large_number(year_data['after_sales']),
                        'COGS': format_large_number(year_data['total_cogs']),
                        'COGS/Unit': format_large_number(year_data['cogs_per_unit']),
                        'Total Cost': format_large_number(year_data['total_cost'])
                    })
                
                if table_data:
                    df = pd.DataFrame(table_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Detailed view for selected year (if edit mode)
                if st.session_state.cost_edit_mode:
                    st.markdown("---")
                    st.markdown("### 📐 Detailed Breakdown by Year")
                    
                    for year_str in [str(y) for y in years]:
                        if year_str not in yearly_breakdown:
                            continue
                        year_data = yearly_breakdown[year_str]
                        
                        with st.expander(f"Year {year_str} Details"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("📦 Sales Volume", f"{year_data['projected_volume']:,}",
                                         help="Auto-calculated from SOM × Volume %")
                                st.metric("💻 Development", format_large_number(year_data['one_time_development']),
                                         help="One-time cost in first year only")
                                st.metric("📢 CAC", format_large_number(year_data['customer_acquisition']),
                                         help="Annual customer acquisition cost")
                            with col2:
                                st.metric("🚚 Distribution", format_large_number(year_data['distribution_operations']),
                                         help="Annual distribution & operations cost")
                                st.metric("🛠️ After Sales", format_large_number(year_data['after_sales']),
                                         help="Annual after sales cost")
                                st.metric("💰 Total COGS", format_large_number(year_data['total_cogs']),
                                         help="Auto-calculated: Volume × COGS per unit")
                            
                            st.divider()
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("🔢 COGS per Unit", format_large_number(year_data['cogs_per_unit']))
                            with col_b:
                                st.metric("💵 Total Cost", format_large_number(year_data['total_cost']),
                                         help="Sum of all costs for this year")
                            
                            # Show calculation breakdown
                            st.markdown(f"""
                            **Calculation Breakdown:**
                            \`\`\`
                            Development:     {format_large_number(year_data['one_time_development']):>15}
                            CAC:            {format_large_number(year_data['customer_acquisition']):>15}
                            Distribution:   {format_large_number(year_data['distribution_operations']):>15}
                            After Sales:    {format_large_number(year_data['after_sales']):>15}
                            COGS:           {format_large_number(year_data['total_cogs']):>15}
                                            ({year_data['projected_volume']:,} × {format_large_number(year_data['cogs_per_unit'])})
                            ────────────────────────────────
                            Total:          {format_large_number(year_data['total_cost']):>15}
                            \`\`\`
                            """)
            
            # Cost structure details with sources and examples
            with st.expander("🔍 Detailed Cost Structure & Market Comparisons"):
                if 'development_costs' in cost_data:
                    st.markdown("### 💻 Development Costs")
                    for cost_item in cost_data['development_costs']:
                        with st.container():
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.markdown(f"**{cost_item['category']}**")
                                st.write(cost_item['reasoning'])
                            with col2:
                                st.metric("Estimated Cost", format_large_number(cost_item['estimated_amount']))
                            
                            # Market comparison
                            if 'market_comparison' in cost_item:
                                mc = cost_item['market_comparison']
                                st.markdown(f"**📊 Market Comparison:** {mc.get('similar_case', 'N/A')}")
                                st.caption(mc.get('comparison_details', ''))
                                
                                if 'cost_figures' in mc and mc['cost_figures']:
                                    st.markdown("**Industry Examples:**")
                                    for fig in mc['cost_figures']:
                                        st.text(f"• {fig['company']} - {fig['project']}: {format_large_number(fig['amount'])} ({fig['year']})")
                                
                                if 'reference_links' in mc and mc['reference_links']:
                                    with st.expander("📚 Sources"):
                                        for link in mc['reference_links']:
                                            st.markdown(f"- [{link}]({link})")
                            st.divider()
                
                if 'customer_acquisition_costs' in cost_data:
                    st.markdown("### 📢 Customer Acquisition Costs")
                    for cost_item in cost_data['customer_acquisition_costs']:
                        with st.container():
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.markdown(f"**{cost_item['category']}**")
                                st.write(cost_item['reasoning'])
                            with col2:
                                st.metric("Annual Budget", format_large_number(cost_item.get('estimated_annual_budget', 0)))
                                if 'estimated_amount_per_customer' in cost_item:
                                    st.metric("Cost per Customer", format_large_number(cost_item['estimated_amount_per_customer']))
                            
                            # Market comparison
                            if 'market_comparison' in cost_item:
                                mc = cost_item['market_comparison']
                                st.markdown(f"**📊 Market Comparison:** {mc.get('similar_case', 'N/A')}")
                                st.caption(mc.get('comparison_details', ''))
                                
                                if 'cost_figures' in mc and mc['cost_figures']:
                                    st.markdown("**Industry Examples:**")
                                    for fig in mc['cost_figures']:
                                        st.text(f"• {fig['company']} - {fig['project']}: {format_large_number(fig['amount'])} ({fig['year']})")
                                
                                if 'reference_links' in mc and mc['reference_links']:
                                    with st.expander("📚 Sources"):
                                        for link in mc['reference_links']:
                                            st.markdown(f"- [{link}]({link})")
                            st.divider()
                
                if 'distribution_and_operations_costs' in cost_data:
                    st.markdown("### 🚚 Distribution & Operations Costs")
                    for cost_item in cost_data['distribution_and_operations_costs']:
                        with st.container():
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.markdown(f"**{cost_item['category']}**")
                                st.write(cost_item['reasoning'])
                            with col2:
                                st.metric("Estimated Cost", format_large_number(cost_item['estimated_amount']))
                            
                            # Market comparison
                            if 'market_comparison' in cost_item:
                                mc = cost_item['market_comparison']
                                st.markdown(f"**📊 Market Comparison:** {mc.get('similar_case', 'N/A')}")
                                st.caption(mc.get('comparison_details', ''))
                                
                                if 'cost_figures' in mc and mc['cost_figures']:
                                    st.markdown("**Industry Examples:**")
                                    for fig in mc['cost_figures']:
                                        st.text(f"• {fig['company']} - {fig['project']}: {format_large_number(fig['amount'])} ({fig['year']})")
                                
                                if 'reference_links' in mc and mc['reference_links']:
                                    with st.expander("📚 Sources"):
                                        for link in mc['reference_links']:
                                            st.markdown(f"- [{link}]({link})")
                            st.divider()
                
                if 'after_sales_costs' in cost_data:
                    st.markdown("### 🛠️ After Sales Costs")
                    for cost_item in cost_data['after_sales_costs']:
                        with st.container():
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.markdown(f"**{cost_item['category']}**")
                                st.write(cost_item['reasoning'])
                            with col2:
                                st.metric("Estimated Cost", format_large_number(cost_item['estimated_amount']))
                            
                            # Market comparison
                            if 'market_comparison' in cost_item:
                                mc = cost_item['market_comparison']
                                st.markdown(f"**📊 Market Comparison:** {mc.get('similar_case', 'N/A')}")
                                st.caption(mc.get('comparison_details', ''))
                                
                                if 'cost_figures' in mc and mc['cost_figures']:
                                    st.markdown("**Industry Examples:**")
                                    for fig in mc['cost_figures']:
                                        st.text(f"• {fig['company']} - {fig['project']}: {format_large_number(fig['amount'])} ({fig['year']})")
                                
                                if 'reference_links' in mc and mc['reference_links']:
                                    with st.expander("📚 Sources"):
                                        for link in mc['reference_links']:
                                            st.markdown(f"- [{link}]({link})")
                            st.divider()
                
                if 'cost_of_goods_sold' in cost_data:
                    st.markdown("### 💰 Cost of Goods Sold (COGS)")
                    for cost_item in cost_data['cost_of_goods_sold']:
                        with st.container():
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.markdown(f"**{cost_item.get('product_category', 'Product')}**")
                                st.write(cost_item.get('reasoning', ''))
                            with col2:
                                st.metric("Price per Item", format_large_number(cost_item.get('price_per_item', 0)))
                                st.metric("COGS per Item", format_large_number(cost_item.get('cogs_per_item', 0)))
                            with col3:
                                st.metric("Gross Margin", f"{cost_item.get('gross_margin_percentage', 0)}%")
                            
                            # Market comparison
                            if 'market_comparison' in cost_item:
                                mc = cost_item['market_comparison']
                                st.markdown(f"**📊 Market Comparison:** {mc.get('similar_case', 'N/A')}")
                                st.caption(mc.get('comparison_details', ''))
                                
                                if 'cost_figures' in mc and mc['cost_figures']:
                                    st.markdown("**Industry Examples:**")
                                    for fig in mc['cost_figures']:
                                        st.text(f"• {fig['company']} - {fig['project']}: {format_large_number(fig['amount'])} ({fig['year']})")
                                
                                if 'reference_links' in mc and mc['reference_links']:
                                    with st.expander("📚 Sources"):
                                        for link in mc['reference_links']:
                                            st.markdown(f"- [{link}]({link})")
                            st.divider()
                
                # Show confidence level and notes
                if 'confidence_level' in cost_data:
                    st.info(f"**Confidence Level:** {cost_data['confidence_level']}")
                if 'additional_notes' in cost_data:
                    st.markdown("**Additional Notes:**")
                    st.write(cost_data['additional_notes'])
            
            # Cost Visualizations
            with st.expander("📈 Cost Visualizations", expanded=True):
                yearly_breakdown = cost_data.get('yearly_cost_breakdown', {})
                if yearly_breakdown:
                    # Convert dict to list format for visualization
                    yearly_list = []
                    for year in ["2024", "2025", "2026", "2027", "2028", "2029", "2030"]:
                        if year in yearly_breakdown:
                            data = yearly_breakdown[year].copy()
                            data['year'] = year
                            yearly_list.append(data)
                    
                    if yearly_list:
                        st.plotly_chart(create_cost_breakdown_chart(yearly_list), 
                                       use_container_width=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.plotly_chart(create_cost_per_unit_chart(yearly_list), 
                                           use_container_width=True)
                        with col2:
                            st.plotly_chart(create_total_cost_chart(yearly_list), 
                                           use_container_width=True)
    
    # ==================== INCOME ANALYSIS SECTION ====================
    # Only show after cost analysis is complete
    if st.session_state.cost_analysis_done:
        st.divider()
        st.markdown("---")
        st.markdown("## 💰 Income Analysis & Revenue Projections")
        
        if not st.session_state.income_analysis_done:
            st.markdown("""
            <div class="info-box">
                <strong>📊 Next Step:</strong> Select your income strategy and generate revenue projections 
                based on your sales volume and market analysis.
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")
            
            # Income Strategy Selector
            st.markdown("### 🎯 Select Income Strategy")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💎 **Royalties Model**", use_container_width=True, 
                            type="primary" if st.session_state.selected_income_strategy == "Royalties" else "secondary"):
                    st.session_state.selected_income_strategy = "Royalties"
                    st.rerun()
                st.caption("Percentage-based revenue per sale")
            
            with col2:
                if st.button("📅 **Subscription Model**", use_container_width=True,
                            type="primary" if st.session_state.selected_income_strategy == "Subscription" else "secondary"):
                    st.session_state.selected_income_strategy = "Subscription"
                    st.rerun()
                st.caption("Recurring monthly revenue")
            
            with col3:
                if st.button("💵 **One-Time Sale**", use_container_width=True,
                            type="primary" if st.session_state.selected_income_strategy == "Single Buy" else "secondary"):
                    st.session_state.selected_income_strategy = "Single Buy"
                    st.rerun()
                st.caption("Single purchase per customer")
            
            st.markdown("")
            
            # Show selected strategy
            if st.session_state.selected_income_strategy:
                st.success(f"✅ Selected Strategy: **{st.session_state.selected_income_strategy}**")
                st.markdown("")
                
                # Generate button
                if st.button("**🚀 GENERATE INCOME ANALYSIS**", use_container_width=True, type="primary"):
                    with st.spinner(f"🤖 Generating {st.session_state.selected_income_strategy} income model with AI..."):
                        # Get sales volume data
                        sales_volume = st.session_state.sales_model_data.get('sales_volume_by_year', {})
                    
                    # Generate income analysis
                    income_analysis = generate_income_analysis(
                        st.session_state.pdf_text,
                        sales_volume,
                        st.session_state.selected_income_strategy
                    )
                    
                    if income_analysis and "error" not in income_analysis:
                        st.session_state.income_analysis = income_analysis
                        st.session_state.income_analysis_done = True
                        
                        # Save income analysis
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        strategy_name = st.session_state.selected_income_strategy.lower().replace(" ", "_")
                        income_filename = f"{RESULTS_DIR}/income_{strategy_name}_{timestamp}.json"
                        
                        if save_json(income_analysis, income_filename):
                            print(f"✅ [SERVER] Income analysis saved to: {income_filename}")
                        
                        st.success("✅ Income Analysis Complete!")
                        st.balloons()
                        print(f"✅ [SERVER] {st.session_state.selected_income_strategy} income analysis completed successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to generate income analysis: {income_analysis.get('error', 'Unknown error')}")
            else:
                st.info("👆 Please select an income strategy above")
        
        else:
            st.markdown('<div class="success-box">✓ Income Analysis Completed Successfully</div>', unsafe_allow_html=True)
            st.markdown("")
            
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Current Strategy:** {st.session_state.selected_income_strategy}")
            with col2:
                if st.button("🔄 Change Strategy", use_container_width=True):
                    st.session_state.income_analysis_done = False
                    st.session_state.income_analysis = None
                    st.session_state.selected_income_strategy = None
                    st.rerun()
            
            # Display Income Analysis Results
            if st.session_state.income_analysis:
                income_data = st.session_state.income_analysis
                
                # Calculate totals
                total_income = income_data.get('total_income', 0)
                
                # Get yearly projections
                yearly_projections = income_data.get('yearly_projections', [])
                
                if yearly_projections:
                    # ============ BIG PROFIT CALCULATION SECTION ============
                    # Calculate total costs if cost analysis exists
                    if st.session_state.cost_analysis and 'yearly_cost_breakdown' in st.session_state.cost_analysis:
                        cost_breakdown = st.session_state.cost_analysis['yearly_cost_breakdown']
                        
                        # Ensure yearly_projections contains dictionaries
                        valid_projections = [proj for proj in yearly_projections if isinstance(proj, dict)]
                        
                        if valid_projections:
                            years = [str(proj.get('year', '')) for proj in valid_projections]
                            incomes = [proj.get('yearly_income', 0) for proj in valid_projections]
                            
                            # For Royalties model, exclude distribution, operations, and COGS
                            if st.session_state.selected_income_strategy == "Royalties":
                                costs = []
                                for year in years:
                                    year_costs = cost_breakdown.get(year, {})
                                    # Only include development, customer acquisition, and after-sales
                                    cost = (year_costs.get('one_time_development', 0) + 
                                           year_costs.get('customer_acquisition', 0) + 
                                           year_costs.get('after_sales', 0))
                                    costs.append(cost)
                            else:
                                # For other models, use total cost (includes all categories)
                                costs = [cost_breakdown.get(year, {}).get('total_cost', 0) for year in years]
                        else:
                            years = []
                            incomes = []
                            costs = []
                        
                        # Only show profit banner if we have valid data
                        if years and incomes and costs:
                            total_income_calc = sum(incomes)
                            total_costs = sum(costs)
                            total_profit = total_income_calc - total_costs
                            profit_margin = (total_profit / total_income_calc * 100) if total_income_calc > 0 else 0
                            roi = (total_profit / total_costs * 100) if total_costs > 0 else 0
                            
                            # Determine profit status
                            is_profitable = total_profit > 0
                            profit_color = "#27ae60" if is_profitable else "#e74c3c"
                            status_emoji = "✅" if is_profitable else "❌"
                            status_text = "PROFITABLE" if is_profitable else "NOT PROFITABLE"
                            
                            # Format numbers
                            profit_formatted = format_large_number(abs(total_profit))
                            income_formatted = format_large_number(total_income_calc)
                            costs_formatted = format_large_number(total_costs)
                            
                            # BIG PROFIT BANNER (Compact Version)
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, {'#27ae60' if is_profitable else '#e74c3c'} 0%, {'#229954' if is_profitable else '#c0392b'} 100%);
                                padding: 1.5rem 2rem;
                                border-radius: 12px;
                                text-align: center;
                                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
                                margin: 1.5rem 0;
                                border: 2px solid {'#1e8449' if is_profitable else '#922b21'};
                            ">
                                <h1 style="color: white; font-size: 2rem; margin: 0; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                                    {status_emoji} {status_text}
                                </h1>
                                <h2 style="color: white; font-size: 3rem; margin: 0.5rem 0; font-weight: 900; text-shadow: 3px 3px 6px rgba(0,0,0,0.4);">
                                    {profit_formatted if is_profitable else '-' + profit_formatted.replace('€', '€')}
                                </h2>
                                <p style="color: rgba(255, 255, 255, 0.95); font-size: 1rem; margin: 0.3rem 0; font-weight: 600;">
                                    {'Net Profit' if is_profitable else 'Net Loss'} • {profit_margin:+.1f}% Margin • {roi:+.1f}% ROI
                                </p>
                                <p style="color: rgba(255, 255, 255, 0.85); font-size: 0.9rem; margin: 0.3rem 0;">
                                    Income: {income_formatted} | Costs: {costs_formatted} | {years[0]}-{years[-1]} ({len(years)} years)
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ Unable to calculate profit: Invalid data in income projections.")
                        
                        # Visual breakdown of the calculation (Compact Version) - only show if we have valid data
                        if years and incomes and costs:
                            st.markdown("### 🧮 Breakdown")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown("""
                                <div style="background: linear-gradient(135deg, #27ae60 0%, #229954 100%); 
                                            padding: 1rem; border-radius: 8px; text-align: center; 
                                            box-shadow: 0 3px 10px rgba(39, 174, 96, 0.3);">
                                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 0.75rem; font-weight: 600; 
                                                text-transform: uppercase; letter-spacing: 0.5px;">Total Income</div>
                                    <div style="color: white; font-size: 1.8rem; font-weight: 800; margin: 0.3rem 0;">
                                        {}
                                    </div>
                                    <div style="color: rgba(255, 255, 255, 0.8); font-size: 0.7rem;">
                                        {}
                                    </div>
                                </div>
                                """.format(income_formatted, st.session_state.selected_income_strategy), unsafe_allow_html=True)
                            
                            with col2:
                                cost_description = "Dev + Acquisition + Support" if st.session_state.selected_income_strategy == "Royalties" else "All Operations"
                                st.markdown("""
                                <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); 
                                                padding: 1rem; border-radius: 8px; text-align: center; 
                                            box-shadow: 0 3px 10px rgba(231, 76, 60, 0.3);">
                                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 0.75rem; font-weight: 600; 
                                                text-transform: uppercase; letter-spacing: 0.5px;">Total Costs</div>
                                    <div style="color: white; font-size: 1.8rem; font-weight: 800; margin: 0.3rem 0;">
                                        {}
                                    </div>
                                    <div style="color: rgba(255, 255, 255, 0.8); font-size: 0.7rem;">
                                        {}
                                    </div>
                                </div>
                                """.format(costs_formatted, cost_description), unsafe_allow_html=True)
                            
                            with col3:
                                st.markdown("""
                                <div style="background: linear-gradient(135deg, {} 0%, {} 100%); 
                                            padding: 1rem; border-radius: 8px; text-align: center; 
                                            box-shadow: 0 3px 10px rgba({}, 0.3);
                                            border: 2px solid {};">
                                    <div style="color: rgba(255, 255, 255, 0.9); font-size: 0.75rem; font-weight: 600; 
                                                text-transform: uppercase; letter-spacing: 0.5px;">{}</div>
                                    <div style="color: white; font-size: 1.8rem; font-weight: 800; margin: 0.3rem 0;">
                                        {}{}
                                    </div>
                                    <div style="color: rgba(255, 255, 255, 0.8); font-size: 0.7rem;">
                                        {:.1f}% Margin
                                    </div>
                                </div>
                                """.format(
                                    profit_color, profit_color.replace('7', '5'),
                                    "39, 174, 96" if is_profitable else "231, 76, 60",
                                    profit_color.replace('7', '4'),
                                    "NET PROFIT" if is_profitable else "NET LOSS",
                                    "+" if is_profitable else "-",
                                    profit_formatted.replace('€', ''),
                                    profit_margin
                                ), unsafe_allow_html=True)
                            
                            st.markdown("")  # Spacing
                            
                            # Add informational note for Royalties model
                            if st.session_state.selected_income_strategy == "Royalties":
                                st.info("ℹ️ **Royalties Model**: Costs exclude distribution, operations, and COGS since these are handled by the licensee. Only development, customer acquisition, and after-sales support costs are included.")
                    
                    # Overview metrics
                    st.markdown("### 📊 Revenue Overview")
                    
                    # Only show metrics if we have valid projection data
                    if yearly_projections and len(yearly_projections) > 0 and all(isinstance(proj, dict) for proj in yearly_projections):
                        # Show different metrics based on model type
                        if st.session_state.selected_income_strategy == "Royalties":
                            first_year_data = yearly_projections[0]
                            last_year_data = yearly_projections[-1]
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("💎 Royalty Rate", f"{first_year_data.get('royalty_percentage', 0)}%")
                            with col2:
                                price_per_unit = first_year_data.get('price_per_piece', 0)
                                st.metric("💰 Price per Unit", format_large_number(price_per_unit))
                            with col3:
                                total_units = sum(year.get('number_of_units', 0) for year in yearly_projections)
                                st.metric("📦 Total Units", f"{total_units:,}")
                            with col4:
                                st.metric("💵 Total Income", format_large_number(total_income), 
                                         help=f"Total revenue from {len(yearly_projections)} years")
                        
                        elif st.session_state.selected_income_strategy == "Subscription":
                            first_year_data = yearly_projections[0]
                            last_year_data = yearly_projections[-1]
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                monthly_cost = first_year_data.get('monthly_cost', 0)
                                st.metric("📅 Monthly Cost", format_large_number(monthly_cost))
                            with col2:
                                annual_rev = first_year_data.get('monthly_cost', 0) * 12
                                st.metric("📈 Annual Revenue", format_large_number(annual_rev),
                                         help="Per subscriber")
                            with col3:
                                total_subs = sum(year.get('number_of_subscribers', 0) for year in yearly_projections)
                                avg_subs = total_subs / len(yearly_projections) if yearly_projections else 0
                                st.metric("👥 Avg Subscribers", f"{avg_subs:,.0f}")
                            with col4:
                                st.metric("💵 Total Income", format_large_number(total_income),
                                         help=f"Total revenue from {len(yearly_projections)} years")
                        
                        else:  # Single Buy
                            first_year_data = yearly_projections[0]
                            last_year_data = yearly_projections[-1]
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                avg_price = sum(year.get('price', 0) for year in yearly_projections) / len(yearly_projections)
                                st.metric("💰 Avg Price", format_large_number(avg_price))
                            with col2:
                                first_price = first_year_data.get('price', 0)
                                last_price = last_year_data.get('price', 0)
                                price_change = ((last_price - first_price) / first_price * 100) if first_price > 0 else 0
                                st.metric("📊 Price Trend", f"{price_change:+.1f}%",
                                         help="Price change from first to last year")
                            with col3:
                                total_units = sum(year.get('number_of_units', 0) for year in yearly_projections)
                                st.metric("📦 Total Units", f"{total_units:,}")
                            with col4:
                                st.metric("💵 Total Income", format_large_number(total_income),
                                         help=f"Total revenue from {len(yearly_projections)} years")
                        
                        # Yearly breakdown table
                        with st.expander("📊 Yearly Revenue Breakdown", expanded=True):
                            import pandas as pd
                            
                            table_data = []
                            for year_data in yearly_projections:
                                year = year_data.get('year', 'N/A')
                                
                                if st.session_state.selected_income_strategy == "Royalties":
                                    table_data.append({
                                        'Year': year,
                                        'Units Sold': f"{year_data.get('number_of_units', 0):,}",
                                        'Price/Unit': format_large_number(year_data.get('price_per_piece', 0)),
                                        'Royalty %': f"{year_data.get('royalty_percentage', 0)}%",
                                        'Yearly Income': format_large_number(year_data.get('yearly_income', 0))
                                    })
                                elif st.session_state.selected_income_strategy == "Subscription":
                                    table_data.append({
                                        'Year': year,
                                        'Subscribers': f"{year_data.get('number_of_subscribers', 0):,}",
                                        'Monthly Cost': format_large_number(year_data.get('monthly_cost', 0)),
                                        'Churn Rate': f"{year_data.get('churn_rate', 0)}%",
                                        'Yearly Income': format_large_number(year_data.get('yearly_income', 0))
                                    })
                                else:  # Single Buy
                                    table_data.append({
                                        'Year': year,
                                        'Units Sold': f"{year_data.get('number_of_units', 0):,}",
                                        'Price': format_large_number(year_data.get('price', 0)),
                                        'Yearly Income': format_large_number(year_data.get('yearly_income', 0))
                                    })
                            
                            if table_data:
                                df = pd.DataFrame(table_data)
                                st.dataframe(df, use_container_width=True, hide_index=True)
                    else:
                        st.warning("⚠️ No valid projection data available to display revenue overview.")
                    
                    # Summary and methodology
                    with st.expander("📋 Strategy Summary & Methodology"):
                        if 'summary' in income_data:
                            st.markdown("### 📝 Summary")
                            st.write(income_data['summary'])
                        
                        if 'methodology' in income_data:
                            st.markdown("### 🔬 Methodology")
                            st.write(income_data['methodology'])
                    
                    # Income Visualizations - only show if we have valid data
                    if yearly_projections and len(yearly_projections) > 0 and all(isinstance(proj, dict) for proj in yearly_projections):
                        with st.expander("📈 Income & Profit Visualizations", expanded=True):
                            # Income over time
                            st.plotly_chart(
                                create_income_chart(yearly_projections, st.session_state.selected_income_strategy),
                                use_container_width=True
                            )
                            
                            # Income vs Costs comparison (if cost analysis exists)
                            if st.session_state.cost_analysis and 'yearly_cost_breakdown' in st.session_state.cost_analysis:
                                cost_breakdown = st.session_state.cost_analysis['yearly_cost_breakdown']
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.plotly_chart(
                                        create_income_comparison_chart(
                                            yearly_projections, 
                                            cost_breakdown,
                                            st.session_state.selected_income_strategy
                                        ),
                                        use_container_width=True
                                    )
                                with col2:
                                    st.plotly_chart(
                                        create_cumulative_profit_chart(yearly_projections, cost_breakdown),
                                        use_container_width=True
                                    )
                                
                                # Profit Analysis Summary
                                st.markdown("### 💰 Profit Analysis Summary")
                                
                                # Ensure yearly_projections contains dictionaries
                                valid_projections = [proj for proj in yearly_projections if isinstance(proj, dict)]
                                
                                if valid_projections:
                                    years = [str(proj.get('year', '')) for proj in valid_projections]
                                    incomes = [proj.get('yearly_income', 0) for proj in valid_projections]
                                    
                                    # For Royalties model, exclude distribution, operations, and COGS
                                    if st.session_state.selected_income_strategy == "Royalties":
                                        costs = []
                                        for year in years:
                                            year_costs = cost_breakdown.get(year, {})
                                            # Only include development, customer acquisition, and after-sales
                                            cost = (year_costs.get('one_time_development', 0) + 
                                                   year_costs.get('customer_acquisition', 0) + 
                                                   year_costs.get('after_sales', 0))
                                            costs.append(cost)
                                    else:
                                        # For other models, use total cost (includes all categories)
                                        costs = [cost_breakdown.get(year, {}).get('total_cost', 0) for year in years]
                                else:
                                    years = []
                                    incomes = []
                                    costs = []
                                
                                total_income = sum(incomes)
                                total_costs = sum(costs)
                                total_profit = total_income - total_costs
                                profit_margin = (total_profit / total_income * 100) if total_income > 0 else 0
                                
                                # Find break-even year
                                cumulative = 0
                                break_even_year = None
                                for year, inc, cost in zip(years, incomes, costs):
                                    cumulative += (inc - cost)
                                    if cumulative >= 0 and break_even_year is None:
                                        break_even_year = year
                                
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("💰 Total Income", format_large_number(total_income))
                                with col2:
                                    st.metric("💸 Total Costs", format_large_number(total_costs))
                                with col3:
                                    st.metric("📈 Net Profit", format_large_number(total_profit),
                                             delta=f"{profit_margin:.1f}% margin")
                                with col4:
                                    if break_even_year:
                                        st.metric("⚖️ Break-even Year", break_even_year)
                                    else:
                                        st.metric("⚖️ Break-even", "Not reached", delta="Review strategy")
                    
                    # Comparable projects
                    if 'comparable_projects' in income_data:
                        with st.expander("🏢 Comparable Projects & Market Research"):
                            st.markdown("### 📊 Industry Comparisons")
                            
                            comparables = income_data['comparable_projects']
                            if isinstance(comparables, list):
                                for idx, comp in enumerate(comparables, 1):
                                    st.markdown(f"#### {idx}. {comp.get('name', 'Unnamed Project')}")
                                    st.write(comp.get('description', 'No description available'))
                                    
                                    if 'details' in comp:
                                        st.info(comp['details'])
                                    
                                    if 'link' in comp and comp['link']:
                                        st.markdown(f"[🔗 Learn More]({comp['link']})")
                                    
                                    st.divider()
                            else:
                                st.write(comparables)
                    
                    # Download income analysis
                    st.markdown("### 💾 Export Income Analysis")
                    income_json = json.dumps(income_data, indent=2, ensure_ascii=False)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    strategy_name = st.session_state.selected_income_strategy.lower().replace(" ", "_")
                    
                    st.download_button(
                        label="📥 Download Income Analysis JSON",
                        data=income_json,
                        file_name=f"income_{strategy_name}_{timestamp}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                else:
                    st.warning("No yearly projections found in the income analysis.")
            
            else:
                st.warning("⚠️ Income analysis completed but no data available. Please regenerate.")

# Dashboard Footer
st.markdown("---")
st.markdown("""
    <div class="dashboard-footer">
        <strong>BMW MOTORRAD • Market Intelligence Dashboard</strong><br>
        Powered by AI-Driven Market Analysis | © 2024-2025<br>
        <small>Confidential & Proprietary Information</small>
    </div>
""", unsafe_allow_html=True)
