"""
Enhanced Chatbot for analyzing business cases and modifying simulation parameters
"""
import os
import json
import re
from typing import Dict, Any, Optional, List, Tuple
from openai import OpenAI
import google.generativeai as genai
from backend.config import get_settings

# Get settings
settings = get_settings()

# Initialize clients
openai_client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


def chat_with_analysis(
    message: str,
    analysis_context: Dict[str, Any],
    provider: str = "gemini",
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """
    Chat with AI about the analysis and potentially extract parameter modifications
    
    Returns:
        Tuple of (response_text, parameter_modifications)
        parameter_modifications is None if no modifications were requested
    """
    print("\n" + "="*100)
    print("💬 CHAT ANALYZER: Processing message")
    print("="*100)
    print(f"📝 User Message: {message}")
    print(f"🤖 Provider: {provider}")
    print(f"📊 Analysis Context Available: {bool(analysis_context)}")
    
    if conversation_history:
        print(f"💭 Conversation History: {len(conversation_history)} messages")
    
    # Build context summary from analysis
    context_summary = _build_context_summary(analysis_context)
    print(f"\n📋 Context Summary Generated ({len(context_summary)} chars)")
    
    # Create system prompt
    system_prompt = _create_chat_system_prompt(context_summary)
    print(f"🎯 System Prompt Created ({len(system_prompt)} chars)")
    
    # Build messages for API
    messages = _build_message_history(system_prompt, message, conversation_history)
    print(f"📨 Total Messages: {len(messages)}")
    
    try:
        # Get AI response
        print(f"\n🚀 Calling {provider.upper()} API...")
        if provider == "openai":
            response_text = _call_openai_chat(messages)
        else:
            response_text = _call_gemini_chat(messages)
        
        print(f"✓ Response Received ({len(response_text)} chars)")
        print(f"📄 Response Preview: {response_text[:200]}...")
        
        # Parse for parameter modifications
        print(f"\n🔍 Parsing for parameter modifications...")
        modifications = _extract_parameter_modifications(message, response_text, analysis_context)
        
        if modifications:
            print(f"✓ PARAMETER MODIFICATIONS DETECTED:")
            for key, value in modifications.items():
                print(f"   {key}: {value}")
        else:
            print(f"ℹ️  No parameter modifications detected")
        
        print(f"\n✅ Chat processing complete")
        print("="*100 + "\n")
        
        return response_text, modifications
        
    except Exception as e:
        print(f"\n❌ CHAT ERROR:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        print(f"   Traceback:\n{traceback.format_exc()}")
        print("="*100 + "\n")
        raise


def _build_context_summary(analysis_context: Dict[str, Any]) -> str:
    """Build a concise summary of the analysis for the chatbot"""
    print("   Building context summary...")
    
    summary_parts = []
    
    # Project basics
    if 'project_name' in analysis_context:
        summary_parts.append(f"Project: {analysis_context['project_name']}")
    
    # TAM/SAM/SOM
    if 'tam' in analysis_context:
        tam = analysis_context['tam']
        summary_parts.append(f"TAM: €{tam.get('market_size', 0):,.0f}")
        if 'description_of_public' in tam:
            summary_parts.append(f"Target Market: {tam['description_of_public'][:100]}")
    
    if 'sam' in analysis_context:
        sam = analysis_context['sam']
        summary_parts.append(f"SAM: €{sam.get('market_size', 0):,.0f}")
    
    if 'som' in analysis_context:
        som = analysis_context['som']
        summary_parts.append(f"SOM: €{som.get('revenue_potential', 0):,.0f}")
    
    # Financial metrics
    if 'roi' in analysis_context:
        roi = analysis_context['roi']
        summary_parts.append(f"ROI: {roi.get('roi_percentage', 0):.1f}%")
        summary_parts.append(f"Payback Period: {roi.get('payback_period_months', 0)} months")
    
    # Cost summary
    if 'total_estimated_cost_summary' in analysis_context:
        cost = analysis_context['total_estimated_cost_summary']
        summary_parts.append(f"Total Revenue (5Y): €{cost.get('total_revenue_5_years', 0):,.0f}")
        summary_parts.append(f"Total Cost (5Y): €{cost.get('total_cost_5_years', 0):,.0f}")
        summary_parts.append(f"Net Profit (5Y): €{cost.get('net_profit_5_years', 0):,.0f}")
    
    # Revenue streams
    if 'revenue_streams' in analysis_context:
        streams = analysis_context['revenue_streams']
        summary_parts.append(f"Revenue Streams: {len(streams)} identified")
        for stream in streams[:3]:  # First 3 streams
            summary_parts.append(f"  - {stream.get('name', 'Unknown')}: €{stream.get('value', 0):,.0f}")
    
    result = "\n".join(summary_parts)
    print(f"   ✓ Summary has {len(summary_parts)} components")
    return result


def _create_chat_system_prompt(context_summary: str) -> str:
    """Create the system prompt for the chatbot"""
    return f"""You are an expert business analyst assistant helping users understand and optimize their business case analysis.

CURRENT ANALYSIS CONTEXT:
{context_summary}

YOUR CAPABILITIES:
1. Answer questions about the current analysis
2. Explain financial metrics (TAM, SAM, SOM, ROI, etc.)
3. Provide insights and recommendations
4. Help users modify parameters to simulate different scenarios

PARAMETER MODIFICATION:
When a user wants to change parameters for simulation, respond with your explanation AND include a JSON block at the end of your response in this EXACT format:

```json
{{
  "modifications": {{
    "parameter_name": new_value,
    "another_parameter": new_value
  }}
}}
```

AVAILABLE PARAMETERS TO MODIFY:
- growth_rate: Annual growth rate percentage (e.g., 5.0 for 5%)
- development_cost: Initial development/implementation cost in euros
- royalty_percentage: Royalty percentage if applicable (e.g., 10.0 for 10%)
- take_rate: Platform take rate percentage (e.g., 15.0 for 15%)
- market_coverage: Market coverage percentage (e.g., 50.0 for 50%)
- annual_revenue_or_savings: Annual revenue or savings amount in euros
- fleet_size_or_units: Number of units or fleet size
- price_per_unit: Price per unit in euros

EXAMPLE USER REQUESTS:
- "What if we increase the growth rate to 10%?" → Modify growth_rate to 10.0
- "Try with 20% higher development cost" → Modify development_cost accordingly
- "Set market coverage to 75%" → Modify market_coverage to 75.0
- "What if we reduce the take rate to 12%?" → Modify take_rate to 12.0

GUIDELINES:
- Be conversational and helpful
- Explain financial concepts clearly
- When suggesting modifications, explain why they might be interesting
- Always validate that modifications make business sense
- Use the analysis context to provide relevant insights
- If you suggest a parameter change, include the JSON modification block
"""


def _build_message_history(
    system_prompt: str,
    current_message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> List[Dict[str, str]]:
    """Build the message array for the API call"""
    messages = [{"role": "system", "content": system_prompt}]
    
    if conversation_history:
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
    
    messages.append({"role": "user", "content": current_message})
    
    return messages


def _call_openai_chat(messages: List[Dict[str, str]]) -> str:
    """Call OpenAI Chat API"""
    print("   📡 Calling OpenAI API...")
    
    if not openai_client:
        raise ValueError("OpenAI API key not configured")
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=1500
    )
    
    result = response.choices[0].message.content.strip()
    print(f"   ✓ OpenAI response received")
    return result


def _call_gemini_chat(messages: List[Dict[str, str]]) -> str:
    """Call Gemini Chat API"""
    print("   📡 Calling Gemini API...")
    
    if not settings.gemini_api_key:
        raise ValueError("Gemini API key not configured")
    
    # Convert messages to Gemini format
    gemini_messages = []
    system_instruction = None
    
    for msg in messages:
        if msg["role"] == "system":
            system_instruction = msg["content"]
        else:
            gemini_messages.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]]
            })
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction
    )
    
    chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
    response = chat.send_message(gemini_messages[-1]["parts"][0])
    
    result = response.text.strip()
    print(f"   ✓ Gemini response received")
    return result


def _extract_parameter_modifications(
    user_message: str,
    ai_response: str,
    analysis_context: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Extract parameter modifications from the AI response or infer from user message
    """
    print("   🔍 Extracting parameter modifications...")
    
    modifications = {}
    
    # First, try to extract JSON block from AI response
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', ai_response, re.DOTALL)
    if json_match:
        print("   ✓ Found JSON modification block in AI response")
        try:
            parsed = json.loads(json_match.group(1))
            if "modifications" in parsed:
                modifications = parsed["modifications"]
                print(f"   ✓ Parsed {len(modifications)} modifications from JSON")
        except json.JSONDecodeError as e:
            print(f"   ⚠️  JSON parse error: {e}")
    
    # Also try to infer from user message using pattern matching
    inferred = _infer_modifications_from_message(user_message, analysis_context)
    if inferred:
        print(f"   ✓ Inferred {len(inferred)} modifications from user message")
        modifications.update(inferred)
    
    # Validate modifications
    if modifications:
        modifications = _validate_modifications(modifications, analysis_context)
        print(f"   ✓ Validated modifications: {len(modifications)} parameters")
    
    return modifications if modifications else None


def _infer_modifications_from_message(
    message: str,
    analysis_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Infer parameter modifications from natural language"""
    print("   🧠 Inferring modifications from message...")
    
    modifications = {}
    message_lower = message.lower()
    
    # Growth rate patterns
    growth_patterns = [
        r'growth.*?(\d+(?:\.\d+)?)\s*%',
        r'increase.*?growth.*?(\d+(?:\.\d+)?)',
        r'grow.*?(\d+(?:\.\d+)?)\s*percent'
    ]
    for pattern in growth_patterns:
        match = re.search(pattern, message_lower)
        if match:
            modifications['growth_rate'] = float(match.group(1))
            print(f"   ✓ Detected growth_rate: {modifications['growth_rate']}")
            break
    
    # Development cost patterns
    cost_patterns = [
        r'development cost.*?€?(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|m)?',
        r'(?:increase|decrease).*?cost.*?(\d+)\s*%',
        r'cost.*?€?(\d+(?:,\d{3})*)'
    ]
    for pattern in cost_patterns:
        match = re.search(pattern, message_lower)
        if match:
            value_str = match.group(1).replace(',', '')
            value = float(value_str)
            
            # Check if it's a percentage change
            if '%' in message or 'percent' in message_lower:
                current_cost = analysis_context.get('total_estimated_cost_summary', {}).get('development_cost', 0)
                if 'increase' in message_lower:
                    value = current_cost * (1 + value / 100)
                elif 'decrease' in message_lower:
                    value = current_cost * (1 - value / 100)
            
            # Check for million
            if 'million' in message_lower or ' m' in message_lower:
                value *= 1_000_000
            
            modifications['development_cost'] = value
            print(f"   ✓ Detected development_cost: {modifications['development_cost']}")
            break
    
    # Market coverage patterns
    coverage_patterns = [
        r'market coverage.*?(\d+(?:\.\d+)?)\s*%',
        r'coverage.*?(\d+(?:\.\d+)?)\s*percent',
        r'cover.*?(\d+(?:\.\d+)?)\s*%'
    ]
    for pattern in coverage_patterns:
        match = re.search(pattern, message_lower)
        if match:
            modifications['market_coverage'] = float(match.group(1))
            print(f"   ✓ Detected market_coverage: {modifications['market_coverage']}")
            break
    
    # Take rate patterns
    take_patterns = [
        r'take rate.*?(\d+(?:\.\d+)?)\s*%',
        r'commission.*?(\d+(?:\.\d+)?)\s*%',
        r'fee.*?(\d+(?:\.\d+)?)\s*percent'
    ]
    for pattern in take_patterns:
        match = re.search(pattern, message_lower)
        if match:
            modifications['take_rate'] = float(match.group(1))
            print(f"   ✓ Detected take_rate: {modifications['take_rate']}")
            break
    
    # Royalty patterns
    royalty_patterns = [
        r'royalty.*?(\d+(?:\.\d+)?)\s*%',
        r'royalties.*?(\d+(?:\.\d+)?)\s*percent'
    ]
    for pattern in royalty_patterns:
        match = re.search(pattern, message_lower)
        if match:
            modifications['royalty_percentage'] = float(match.group(1))
            print(f"   ✓ Detected royalty_percentage: {modifications['royalty_percentage']}")
            break
    
    return modifications


def _validate_modifications(
    modifications: Dict[str, Any],
    analysis_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate and sanitize parameter modifications"""
    print("   ✓ Validating modifications...")
    
    valid = {}
    
    for key, value in modifications.items():
        # Ensure numeric values
        try:
            value = float(value)
        except (TypeError, ValueError):
            print(f"   ⚠️  Skipping {key}: invalid numeric value")
            continue
        
        # Validate ranges
        if key == 'growth_rate' and 0 <= value <= 100:
            valid[key] = value
        elif key == 'development_cost' and value >= 0:
            valid[key] = value
        elif key == 'royalty_percentage' and 0 <= value <= 100:
            valid[key] = value
        elif key == 'take_rate' and 0 <= value <= 100:
            valid[key] = value
        elif key == 'market_coverage' and 0 <= value <= 100:
            valid[key] = value
        elif key == 'annual_revenue_or_savings' and value >= 0:
            valid[key] = value
        elif key == 'fleet_size_or_units' and value >= 0:
            valid[key] = int(value)
        elif key == 'price_per_unit' and value >= 0:
            valid[key] = value
        else:
            print(f"   ⚠️  Skipping {key}: out of valid range or unknown parameter")
    
    return valid
