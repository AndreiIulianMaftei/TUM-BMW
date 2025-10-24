import json
import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Google AI API
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY environment variable in .env file")

genai.configure(api_key=API_KEY)

# System prompt with specifications
SYSTEM_PROMPT = """You are a data formatter.
Return ONLY valid JSON (no extra text).

Rules:
- For every metric, keep all fields NUMERIC except "Insight" (short text).
- "Insight" must be a concise sentence (≤ 25 words) extracted or paraphrased from the INPUT data. Do NOT invent facts.
- If the input lacks enough info, set "Insight" to "" and lower "Confidence (%)".
- "Confidence (%)" is 0–100 based on input completeness/clarity.
- Percentages are numbers (e.g., 15 for 15%). Periods can be numbers or short strings like "Q1 2025".
- No additional commentary, units, or formatting.

EXPECTED OUTPUT (exact JSON schema):
{
  "TAM": {
    "Market size": <number>,
    "Growth Rate": <number>,
    "Time Horizon": <number>,
    "Insight": "<short text from input notes or fields>",
    "Confidence (%)": <0-100>
  },
  "SAM": {
    "Region": "<short string>",
    "Target Segment": "<short string>",
    "Market size": <number>,
    "Insight": "<short text>",
    "Confidence (%)": <0-100>
  },
  "SOM": {
    "Market Share": <number>,
    "Revenue Potential": <number>,
    "Capture Period": <number>,
    "Insight": "<short text>",
    "Confidence (%)": <0-100>
  },
  "ROI": {
    "Revenue": <number>,
    "Cost": <number>,
    "ROI (%)": <number>,
    "Insight": "<short text>",
    "Confidence (%)": <0-100>
  },
  "Turnover": {
    "Year": <number>,
    "Total Revenue": <number>,
    "YoY Growth": <number>,
    "Insight": "<short text>",
    "Confidence (%)": <0-100>
  },
  "Volume": {
    "Units Sold": <number>,
    "Region": "<short string>",
    "Period": "<short string>",
    "Insight": "<short text>",
    "Confidence (%)": <0-100>
  },
  "Unit Economics": {
    "Unit Revenue": <number>,
    "Unit Cost": <number>,
    "Margin": <number>,
    "Insight": "<short text>",
    "Confidence (%)": <0-100>
  },
  "EBIT": {
    "Revenue": <number>,
    "Operating Expense": <number>,
    "EBIT Margin": <number>,
    "Insight": "<short text>",
    "Confidence (%)": <0-100>
  },
  "COGS": {
    "Material": <number>,
    "Labor": <number>,
    "Overheads": <number>,
    "Total COGS": <number>,
    "Insight": "<short text>",
    "Confidence (%)": <0-100>
  },
  "Market Potential": {
    "Market Size": <number>,
    "Penetration": <number>,
    "Growth Rate": <number>,
    "Insight": "<short text>",
    "Confidence (%)": <0-100>
  }
}"""

def load_input_data(file_path="business_data.json"):
    """Load input data from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        return None

def generate_formatted_json(input_data):
    """Use Gemini 2.5 Flash to format the input data according to specifications"""
    
    # Initialize the model
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash-exp',
        generation_config={
            "temperature": 0.1,  # Low temperature for consistent formatting
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
    )
    
    # Prepare the prompt
    user_prompt = f"""INPUT DATA:
{json.dumps(input_data, indent=2)}

Please format this data according to the specifications and return ONLY the JSON output."""
    
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
    
    try:
        print("Sending request to Gemini 2.5 Flash...")
        response = model.generate_content(full_prompt)
        
        # Extract the text response
        response_text = response.text.strip()
        
        # Try to parse as JSON
        # Remove potential markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        formatted_data = json.loads(response_text)
        return formatted_data
        
    except Exception as e:
        print(f"Error generating content: {e}")
        return None

def save_output(data, output_file="formatted_output.json"):
    """Save the formatted JSON to a file"""
    try:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Successfully saved formatted data to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving output: {e}")
        return False

def main():
    """Main function to run the script"""
    print("=" * 60)
    print("Google AI (Gemini 2.5 Flash) - JSON Data Formatter")
    print("=" * 60)
    
    # Load input data
    print("\n1. Loading input data...")
    input_data = load_input_data("business_data.json")
    
    if not input_data:
        print("Failed to load input data. Exiting.")
        return
    
    print("   ✓ Input data loaded successfully")
    
    # Generate formatted JSON using AI
    print("\n2. Generating formatted JSON with AI...")
    formatted_data = generate_formatted_json(input_data)
    
    if not formatted_data:
        print("Failed to generate formatted data. Exiting.")
        return
    
    print("   ✓ Formatted data generated successfully")
    
    # Display the result
    print("\n3. Generated JSON:")
    print("-" * 60)
    print(json.dumps(formatted_data, indent=2))
    print("-" * 60)
    
    # Save output
    print("\n4. Saving output...")
    if save_output(formatted_data, "formatted_output.json"):
        print("   ✓ Output saved successfully")
    
    print("\n" + "=" * 60)
    print("Process completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
