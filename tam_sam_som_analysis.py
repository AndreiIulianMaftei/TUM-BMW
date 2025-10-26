"""
TAM/SAM/SOM Analysis Module
Extracts market analysis from PDF and generates structured JSON with industry examples
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Configure OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None


def generate_tam_sam_som_analysis(pdf_content: str) -> Dict[str, Any]:
    """
    Generate TAM/SAM/SOM analysis with industry examples using OpenAI.
    """
    
    prompt = f"""
    Based on the following document, create a comprehensive TAM/SAM/SOM (Total Addressable Market, Serviceable Available Market, Serviceable Obtainable Market) analysis.
    
    Document Content:
    {pdf_content}
    
    IMPORTANT: Search online for real  industry examples and include actual URLs to support each market segment.
    CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE GUIDELINES:

1. DATA DERIVATION & CALCULATION:
   - DO NOT use mock or placeholder data
   - DERIVE all estimates from real industry benchmarks, competitor data, and market research
   - CALCULATE projections based on logical assumptions and growth models
   - RESEARCH online for supporting evidence including company examples, industry reports, and market data
   - VALIDATE your estimates against similar projects/companies in the automotive, motorcycle, or related industries

2. SOURCE VALIDATION & EVIDENCE:
   - For EVERY cost estimate, provide real company examples with actual project costs
   - Include reference_links to credible sources (annual reports, press releases, industry publications)
   - Cite specific companies (BMW competitors like Mercedes-Benz, Audi, Porsche, Harley-Davidson, Ducati, etc.)
   - Use market_comparison fields to show how your estimates compare to real-world examples
   - Sources must be verifiable and recent (prefer 2020-2024 data)
    3. Create a JSON structure with the following EXACT format:
    FOR THESE. ONLY SELECT NUMBERS THAT REFER TO PEOPLE.
    {{
      "TAM": {{
        "description_of_public": "Clear description of the total addressable market - who are ALL potential users/beneficiaries",
        "numbers": {{
          "2024": <number>,
          "2025": <number>,
          "2026": <number>,
          "2027": <number>,
          "2028": <number>,
          "2029": <number>,
          "2030": <number>
        }},
        "justification": "Detailed explanation of how these numbers were calculated, what assumptions were made, and why they make sense for this market. Include reasoning about market size and growth.",
        "industry_example": {{
          "name": "Real Company Name",
          "description": "Real example of how this company operates in a similar TAM space with concrete details",
          "link": "https://actual-real-url.com/news-article"
        }}
      }},
      "SAM": {{
        "description_of_public": "Clear description of the serviceable available market - who can realistically be reached/served",
        "numbers": {{
          "2024": <number>,
          "2025": <number>,
          "2026": <number>,
          "2027": <number>,
          "2028": <number>,
          "2029": <number>,
          "2030": <number>
        }},
        "justification": "Detailed explanation of how SAM relates to TAM, what percentage it represents, growth assumptions, and why certain segments are included or excluded.",
        "industry_example": {{
          "name": "Real Company Name",
          "description": "Real example of a company operating in a similar SAM with specific details about their approach",
          "link": "https://actual-real-url.com/case-study"
        }}
      }},
      "SOM": {{
        "description_of_public": "Clear description of the serviceable obtainable market - who can realistically be captured in the near term",
        "numbers": {{
          "2024": <number>,
          "2025": <number>,
          "2026": <number>,
          "2027": <number>,
          "2028": <number>,
          "2029": <number>,
          "2030": <number>
        }},
        "justification": "Detailed explanation of realistic market capture, growth trajectory, competitive factors, and adoption assumptions.",
        "industry_example": {{
          "name": "Real Company Name",
          "description": "Real example of a company that successfully captured their initial market share with specific strategies",
          "link": "https://actual-real-url.com/success-story"
        }}
      }},
      "sources": [
        "https://url1.com",
        "https://url2.com",
        "https://url3.com"
      ]
    }}
    
    Guidelines:
    1. Numbers should be realistic and based on the document content and market research
    2. SAM should be smaller than TAM (typically 30-60% of TAM)
    3. SOM should be smaller than SAM (typically 20-50% of SAM initially, growing over time)
    4. Show realistic growth patterns year over year
    5. Industry examples MUST be real companies (Ford, BMW, Volkswagen, Toyota, Tesla, Mercedes, etc.)
    6. Links MUST be actual URLs that could exist (news articles, press releases, case studies)
    7. Justifications should be detailed and explain the logic clearly
    8. All numbers should align with the document's context (automotive, development, parts reuse, etc.)
    9. Include specific assumptions in the justification
    10. Search online for similar automotive industry examples and use real data where possible
    
    Return ONLY valid JSON, no markdown formatting or extra text.
    """
    
    try:
        print("🤖 [SERVER] Starting TAM/SAM/SOM analysis with OpenAI...")
        print("   [SERVER] Searching for industry examples online...")
        
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "system", "content": "You are a market analysis expert that generates comprehensive TAM/SAM/SOM analyses with real industry examples. Return only valid JSON without markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8192
        )
        
        json_text = response.choices[0].message.content.strip().replace('```json', '').replace('```', '').strip()
        
        result = json.loads(json_text)
        print("✅ [SERVER] LLM finished generating analysis successfully!")
        print(f"   [SERVER] Generated {len(result)} top-level fields")
        
        return result
    
    except json.JSONDecodeError as e:
        print(f"✗ [SERVER ERROR] Failed to parse JSON response: {e}")
        print("\n[SERVER] Raw response:")
        print(json_text)
        return {}
    except Exception as e:
        print(f"✗ [SERVER ERROR] Error generating analysis: {e}")
        import traceback
        traceback.print_exc()
        return {}


# CLI interface when run directly
def main():
    """Main execution function for CLI usage."""
    import PyPDF2
    
    print("=" * 70)
    print("TAM/SAM/SOM Analysis Generator")
    print("Using OpenAI GPT-4o-mini API with Online Research")
    print("=" * 70)
    print()
    
    # Check API key
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        return
    
    # PDF path - adjust this to your needs
    pdf_path = '../input/Motorrad_Accessory_Bundles_1-Pager_missing_section.pdf'
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        print("\nPlease provide the correct path to your PDF file.")
        return
    
    # Read PDF
    print(f"📄 Reading PDF: {pdf_path}")
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            pdf_content = ""
            for page in pdf_reader.pages:
                pdf_content += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return
    
    if not pdf_content:
        print("Error: Could not extract content from PDF")
        return
    
    print(f"✓ Successfully extracted {len(pdf_content)} characters from PDF")
    print()
    
    # Generate TAM/SAM/SOM analysis
    print("=" * 70)
    print("Generating Market Analysis...")
    print("=" * 70)
    print()
    
    analysis = generate_tam_sam_som_analysis(pdf_content)
    
    if analysis:
        # Save to JSON file
        output_file = 'tam_sam_som_analysis.json'
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"✓ Successfully saved: {output_file}")
        except Exception as e:
            print(f"✗ Error saving {output_file}: {e}")
        print()
        
        # Display summary
        print("=" * 70)
        print("✅ Analysis Generated Successfully!")
        print("=" * 70)
        print()
        
        # Show quick summary
        print("📊 Market Size Summary:")
        print("-" * 70)
        
        if 'TAM' in analysis and 'numbers' in analysis['TAM']:
            tam_2024 = analysis['TAM']['numbers'].get('2024', 0)
            tam_2030 = analysis['TAM']['numbers'].get('2030', 0)
            print(f"TAM (Total Addressable Market):")
            print(f"  2024: {tam_2024:,}")
            print(f"  2030: {tam_2030:,}")
            print()
        
        if 'SAM' in analysis and 'numbers' in analysis['SAM']:
            sam_2024 = analysis['SAM']['numbers'].get('2024', 0)
            sam_2030 = analysis['SAM']['numbers'].get('2030', 0)
            print(f"SAM (Serviceable Available Market):")
            print(f"  2024: {sam_2024:,}")
            print(f"  2030: {sam_2030:,}")
            print()
        
        if 'SOM' in analysis and 'numbers' in analysis['SOM']:
            som_2024 = analysis['SOM']['numbers'].get('2024', 0)
            som_2030 = analysis['SOM']['numbers'].get('2030', 0)
            print(f"SOM (Serviceable Obtainable Market):")
            print(f"  2024: {som_2024:,}")
            print(f"  2030: {som_2030:,}")
            print()
        
        # Show industry examples
        if 'sources' in analysis and analysis['sources']:
            print("🔗 Industry Sources:")
            print("-" * 70)
            for i, source in enumerate(analysis['sources'], 1):
                print(f"{i}. {source}")
            print()
        
        print(f"📁 Full analysis saved to: {output_file}")
        print()
    else:
        print("✗ Failed to generate analysis")


if __name__ == "__main__":
    main()
