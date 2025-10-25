import json
import csv
import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Google AI API
GEMINI_API_KEY = os.getenv("gemini_api_key")
GEMINI_MODEL_NAME = os.getenv("gemini_model_name")

if not GEMINI_API_KEY:
    raise ValueError("Please set gemini_api_key environment variable in .env file")
if not GEMINI_MODEL_NAME:
    raise ValueError("Please set gemini_model_name environment variable in .env file")

genai.configure(api_key=GEMINI_API_KEY)

# System prompt for question generation
SYSTEM_PROMPT = """You are a business analyst expert who creates specific, targeted questions to gather missing information from human experts.

Analyze the business plan data provided and generate 3-4 VERY SPECIFIC questions that:
1. Reference actual numbers, metrics, or details from the data
2. Ask for expert judgment on concrete aspects of the business
3. Are directly relevant to the specific business context (not generic questions)
4. Require domain expertise to answer

For each question:
- Make it SPECIFIC to the actual data provided (reference actual numbers, markets, or business details)
- Ask for expert input on a concrete decision or clarification
- Provide exactly 2 suggested answers that are VERY SHORT (3-4 words maximum each)
- Answers should be realistic options an expert would choose between

Return ONLY valid JSON in this exact format (no extra text):
{
  "questions": [
    {
      "question": "Given your $30M revenue target, which pricing model fits best?",
      "reason": "Pricing strategy not specified for revenue projections",
      "suggested_answers": [
        "Subscription-based SaaS model",
        "Transaction-based fees"
      ]
    }
  ]
}

Requirements:
- Generate 3-4 questions that reference SPECIFIC data points from the input
- Each question must be concrete and contextual (not "What is your market?" but "Is your $500M SOM targeting enterprise or SMB?")
- Questions should require expert judgment, not research
- Suggested answers MUST be 3-4 words maximum
- Make questions highly relevant to the specific business scenario provided
- Return ONLY the JSON object"""


def load_business_data(file_path="business_data.json"):
    """Load business plan data from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        return None


def analyze_data_completeness(data):
    """Analyze the business data to identify what might be missing"""
    analysis = {
        "provided_metrics": [],
        "confidence_levels": {},
        "missing_details": []
    }
    
    if "metrics" in data:
        for metric_name, metric_data in data["metrics"].items():
            analysis["provided_metrics"].append(metric_name)
            if isinstance(metric_data, dict) and "confidence" in metric_data:
                analysis["confidence_levels"][metric_name] = metric_data.get("confidence", 0)
    
    return analysis


def generate_questions(business_data):
    """Use Gemini to generate questions about missing or unclear information"""
    
    # Initialize the model
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL_NAME,
        generation_config={
            "temperature": 0.7,  # Moderate temperature for creative but focused questions
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 4096,
        }
    )
    
    # Analyze data completeness
    analysis = analyze_data_completeness(business_data)
    
    # Prepare the prompt
    user_prompt = f"""BUSINESS PLAN DATA:
{json.dumps(business_data, indent=2)}

DATA ANALYSIS:
- Provided metrics: {', '.join(analysis['provided_metrics'])}
- Confidence levels: {json.dumps(analysis['confidence_levels'], indent=2)}

Please generate 3-4 critical questions about missing, incomplete, or low-confidence information that would help improve this business plan. Focus on what's needed for better decision-making.

Return ONLY the JSON output."""
    
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
    
    try:
        print("Generating questions with Gemini AI...")
        response = model.generate_content(full_prompt)
        
        # Extract the text response
        response_text = response.text.strip()
        
        # Remove potential markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        questions_data = json.loads(response_text)
        return questions_data
        
    except Exception as e:
        print(f"Error generating questions: {e}")
        print(f"Response text: {response_text if 'response_text' in locals() else 'N/A'}")
        return None


def save_to_csv(questions_data, output_file="generated_questions.csv"):
    """Save the questions and suggested answers to a CSV file"""
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                "Question Number",
                "Question",
                "Reason",
                "Suggested Answer 1",
                "Suggested Answer 2"
            ])
            
            # Write data
            questions = questions_data.get("questions", [])
            for idx, q in enumerate(questions, start=1):
                question = q.get("question", "")
                reason = q.get("reason", "")
                suggested_answers = q.get("suggested_answers", [])
                
                # Ensure we have at least 2 suggested answers
                answer1 = suggested_answers[0] if len(suggested_answers) > 0 else ""
                answer2 = suggested_answers[1] if len(suggested_answers) > 1 else ""
                
                writer.writerow([
                    idx,
                    question,
                    reason,
                    answer1,
                    answer2
                ])
        
        print(f"✓ Questions saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False


def display_questions(questions_data):
    """Display the generated questions in a readable format"""
    questions = questions_data.get("questions", [])
    
    print("\n" + "=" * 80)
    print("GENERATED QUESTIONS")
    print("=" * 80)
    
    for idx, q in enumerate(questions, start=1):
        print(f"\nQuestion {idx}:")
        print(f"  {q.get('question', '')}")
        print(f"\n  Reason: {q.get('reason', '')}")
        print(f"\n  Suggested Answers:")
        for ans_idx, answer in enumerate(q.get('suggested_answers', []), start=1):
            print(f"    {ans_idx}. {answer}")
        print("-" * 80)


def main():
    """Main function to run the script"""
    print("=" * 80)
    print("Business Plan Question Generator")
    print("Using Google AI (Gemini) to identify missing information")
    print("=" * 80)
    
    # Load business data
    print("\n1. Loading business plan data...")
    business_data = load_business_data("business_data.json")
    
    if not business_data:
        print("Failed to load business data. Exiting.")
        return
    
    print("   ✓ Business data loaded successfully")
    
    # Generate questions using AI
    print("\n2. Analyzing data and generating questions...")
    questions_data = generate_questions(business_data)
    
    if not questions_data or "questions" not in questions_data:
        print("Failed to generate questions. Exiting.")
        return
    
    print(f"   ✓ Generated {len(questions_data['questions'])} questions")
    
    # Display questions
    display_questions(questions_data)
    
    # Save to CSV
    print("\n3. Saving questions to CSV...")
    if save_to_csv(questions_data, "generated_questions.csv"):
        print("   ✓ Successfully saved to generated_questions.csv")
    
    # Also save as JSON for reference
    print("\n4. Saving JSON backup...")
    try:
        with open("generated_questions.json", 'w') as f:
            json.dump(questions_data, f, indent=2)
        print("   ✓ JSON backup saved to generated_questions.json")
    except Exception as e:
        print(f"   ✗ Error saving JSON: {e}")
    
    print("\n" + "=" * 80)
    print("Process completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
