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

You may also accept HIGH-LEVEL metric overrides:
 - TAM: Will be interpreted as new annual_revenue_or_savings baseline (no double reduction)
 - SAM: Will adjust market_coverage relative to current TAM
 - SOM: Will adjust take_rate relative to current SAM
If user supplies TAM + SAM + SOM together, compute coverage and take sequentially.

AUTO-SCALING RULE (Savings projects):
If user changes fleet_size_or_units WITHOUT explicitly changing annual_revenue_or_savings, the system will assume per-unit savings remain constant and will proportionally scale the annual total. To override this behavior, explicitly set a new annual_revenue_or_savings value.

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

    # Early detection of revert/reset intent
    if re.search(r'\b(revert|reset|undo|original)\b', user_message.lower()) and not re.search(r'(increase|decrease)', user_message.lower()):
        print("   ↩️ Revert command detected in user message")
        return {"__revert": True}
    
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
        # Map high-level semantic keys (TAM/SAM/SOM) to underlying parameters first
        modifications = _map_semantic_modifications(modifications, analysis_context)
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
    
    # Development cost patterns - must match million/m suffix to avoid false matches
    cost_patterns = [
        r'(?:development\s+)?cost\s+(?:was|is|at|=)?\s*€?(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|m)\b',  # "cost was 10m"
        r'development cost.*?€?(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|m)\b',  # "development cost 50m"
        r'(?:increase|decrease).*?cost.*?(\d+)\s*%',
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
            
            # Check for million (group 2 in first/second pattern, or word in message)
            if len(match.groups()) > 1 and match.group(2) in ['million', 'm']:
                value *= 1_000_000
            elif 'million' in message_lower:
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

    # Income / revenue direct value (e.g., "income was 5 million", "revenue 3.2m", "total income was 1m")
    income_patterns = [
        r'(?:total\s+)?(?:income|revenue|savings)\s+(?:was|is|at|=)?\s*€?(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|m)\b',  # "income was 1m"
        r'(?:total\s+)?(?:income|revenue|savings)\s*(?:was|is|at|=)?\s*(?:always\s+)?€?(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|m)?\b',
        r'(?:income|revenue|savings).*?€\s*(\d+(?:,\d{3})*)'
    ]
    for pattern in income_patterns:
        match = re.search(pattern, message_lower)
        if match:
            raw = match.group(1).replace(',', '')
            val = float(raw)
            # Check if million/m suffix captured in group 2, or anywhere in message
            if (len(match.groups()) > 1 and match.group(2) in ['million', 'm']) or 'million' in message_lower:
                val *= 1_000_000
            modifications.setdefault('annual_revenue_or_savings', val)
            print(f"   ✓ Detected income/revenue value: {val}")
            break

    # Generic parameter override & delta parsing
    generic = _parse_generic_parameter_adjustments(message, analysis_context)
    if generic:
        modifications.update(generic)
        print(f"   ✓ Generic adjustments parsed: {list(generic.keys())}")
    
    return modifications


def _parse_generic_parameter_adjustments(message: str, analysis_context: Dict[str, Any]) -> Dict[str, Any]:
    """Parse generic 'set', '=', 'increase/decrease' patterns for any known parameter.
    Supports:
      - set growth_rate to 7%
      - change market coverage to 65%
      - take_rate = 12%
      - increase development cost by 15%
      - decrease annual revenue by 2 million
      - increase annual_revenue_or_savings by 500000
      - set TAM to 10 million (handled later by semantic mapper)
    Returns raw modifications (semantic mapping handled separately).
    """
    known_params = [
        'growth_rate', 'development_cost', 'royalty_percentage', 'take_rate', 'market_coverage',
        'annual_revenue_or_savings', 'fleet_size_or_units', 'price_per_unit', 'TAM', 'SAM', 'SOM',
        'volume', 'fleet', 'units'  # Aliases for fleet_size_or_units
    ]
    msg = message.lower()
    mods: Dict[str, Any] = {}

    def parse_number(token: str) -> Optional[float]:
        token = token.replace(',', '').strip()
        mult = 1.0
        if token.endswith('m'):  # 5m shorthand
            mult = 1_000_000
            token = token[:-1]
        if token.endswith('k'):  # 500k shorthand
            mult = 1_000
            token = token[:-1]
        try:
            val = float(token)
            return val * mult
        except ValueError:
            return None

    # Normalize aliases to canonical param names
    def normalize_param(param: str) -> str:
        param = param.strip().replace(' ', '_')
        if param in ['volume', 'fleet', 'units', 'fleet_size']:
            return 'fleet_size_or_units'
        return param
    
    # SET / CHANGE / UPDATE patterns
    set_pattern = re.compile(r'(set|change|update)\s+([a-z_ ]+)\s+(?:to|=|to\s+be)\s*([\d.,]+(?:\s*million|\s*m|\s*k|%|))', re.IGNORECASE)
    for verb, param_raw, value_raw in set_pattern.findall(message):
        param = normalize_param(param_raw.strip())
        if param in known_params or param == 'fleet_size_or_units':
            value = value_raw.strip()
            is_percent = value.endswith('%')
            value = value.rstrip('%').strip()
            if 'million' in value:
                value = value.replace('million', '').strip()
                parsed = parse_number(value)
                if parsed is not None:
                    parsed *= 1_000_000
            else:
                parsed = parse_number(value)
            if parsed is not None:
                if is_percent:
                    mods[param] = parsed  # percent kept as raw value
                else:
                    mods[param] = parsed
                print(f"   → Parsed SET for {param} = {mods[param]}")
    
    # Contextual "now X" pattern for volume/fleet (e.g., "now 50k")
    # Only apply if previous message context suggests volume modification
    now_pattern = re.compile(r'\bnow\s+([\d.,]+(?:k|m)?)\b', re.IGNORECASE)
    now_match = now_pattern.search(message)
    if now_match and len(message.split()) <= 3:  # Short message like "now 50k"
        # Assume continuing volume conversation
        value_raw = now_match.group(1)
        parsed = parse_number(value_raw)
        if parsed and 'fleet_size_or_units' not in mods:
            mods['fleet_size_or_units'] = int(parsed)
            print(f"   → Parsed contextual NOW for fleet_size_or_units = {mods['fleet_size_or_units']}")

    # DIRECT assignment pattern e.g., market_coverage = 70%
    assign_pattern = re.compile(r'\b([a-z_]{3,})\s*=\s*([\d.,]+(?:\s*million|\s*m|\s*k|%|))', re.IGNORECASE)
    for param_raw, value_raw in assign_pattern.findall(message):
        param = normalize_param(param_raw.strip())
        if param in known_params or param == 'fleet_size_or_units':
            value = value_raw.strip()
            is_percent = value.endswith('%')
            value = value.rstrip('%').strip()
            if 'million' in value:
                value = value.replace('million', '').strip()
                parsed = parse_number(value)
                if parsed is not None:
                    parsed *= 1_000_000
            else:
                parsed = parse_number(value)
            if parsed is not None:
                if is_percent:
                    mods[param] = parsed
                else:
                    mods[param] = parsed
                print(f"   → Parsed DIRECT assignment for {param} = {mods[param]}")
    
    # Volume/fleet specific patterns (e.g., "volume was 20", "if fleet was 100")
    volume_patterns = [
        r'\b(?:volume|fleet|units?)\s+(?:was|is|of|at)\s+([\d.,]+(?:k|m)?)\b',  # "volume was 20", "fleet is 100k"
        r'\bif\s+(?:volume|fleet|units?)\s+(?:was|were|is)\s+([\d.,]+(?:k|m)?)\b',  # "if volume was 20"
    ]
    for pattern in volume_patterns:
        match = re.search(pattern, msg)
        if match and 'fleet_size_or_units' not in mods:
            value_raw = match.group(1)
            parsed = parse_number(value_raw)
            if parsed is not None:
                mods['fleet_size_or_units'] = int(parsed)
                print(f"   → Parsed volume/fleet pattern: fleet_size_or_units = {mods['fleet_size_or_units']}")
                break
            if parsed is not None:
                mods[param] = parsed
                print(f"   → Parsed ASSIGN for {param} = {mods[param]}")

    # INCREASE / DECREASE patterns
    incdec_pattern = re.compile(r'(increase|decrease)\s+([a-z_ ]+)\s+by\s+([\d.,]+(?:\s*million|\s*m|\s*k|%|))', re.IGNORECASE)
    for action, param_raw, value_raw in incdec_pattern.findall(message):
        param = param_raw.strip().replace(' ', '_')
        if param in known_params:
            value = value_raw.strip()
            is_percent = value.endswith('%')
            value = value.rstrip('%').strip()
            base_current = None
            # Try to derive current value from context
            if param in analysis_context:
                base_current = analysis_context.get(param)
            elif param == 'annual_revenue_or_savings':
                base_current = analysis_context.get('som', {}).get('revenue_potential') or analysis_context.get('tam', {}).get('market_size')
            elif param == 'market_coverage':
                base_current = analysis_context.get('market_coverage') or analysis_context.get('sam', {}).get('penetration_rate')
            elif param == 'take_rate':
                base_current = analysis_context.get('take_rate')
            elif param == 'growth_rate':
                base_current = analysis_context.get('tam', {}).get('growth_rate')

            if 'million' in value:
                value = value.replace('million', '').strip()
                parsed = parse_number(value)
                if parsed is not None:
                    parsed *= 1_000_000
            else:
                parsed = parse_number(value)
            if parsed is None:
                continue

            if is_percent and base_current is not None:
                delta_ratio = parsed / 100.0
                if action.lower() == 'increase':
                    mods[param] = base_current * (1 + delta_ratio)
                else:
                    mods[param] = base_current * (1 - delta_ratio)
            else:
                # Absolute delta
                if base_current is not None:
                    if action.lower() == 'increase':
                        mods[param] = base_current + parsed
                    else:
                        mods[param] = max(0, base_current - parsed)
                else:
                    # If no base, treat as direct value
                    mods[param] = parsed if action.lower() == 'increase' else max(0, parsed)
            print(f"   → Parsed {action.upper()} for {param} -> {mods[param]}")

    return mods


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


def _map_semantic_modifications(mods: Dict[str, Any], analysis_context: Dict[str, Any]) -> Dict[str, Any]:
    """Translate high-level metric overrides (TAM/SAM/SOM) into concrete simulator parameters.

    Rules:
    - TAM: sets annual_revenue_or_savings directly (treated as realized baseline for savings; as new theoretical market for revenue/royalty)
    - SAM: adjusts market_coverage = SAM / TAM * 100 if TAM available (from override or context)
    - SOM: adjusts take_rate = SOM / SAM * 100 if SAM available (from override or context)
    If only SOM provided and TAM exists, infer SAM = existing SAM or TAM * existing market_coverage.
    Edge cases handled conservatively (skip divide-by-zero).
    """
    if not mods:
        return mods

    # Fetch existing context metrics
    ctx_tam = None
    ctx_sam = None
    try:
        if 'tam' in analysis_context and isinstance(analysis_context['tam'], dict):
            ctx_tam = analysis_context['tam'].get('market_size')
        if 'sam' in analysis_context and isinstance(analysis_context['sam'], dict):
            ctx_sam = analysis_context['sam'].get('market_size')
    except Exception:
        pass

    # Work on a copy
    mapped = dict(mods)

    # Handle TAM override
    if 'TAM' in mapped:
        tam_val = mapped.pop('TAM')
        if isinstance(tam_val, (int, float)) and tam_val >= 0:
            mapped['annual_revenue_or_savings'] = tam_val
            ctx_tam = tam_val  # Update for subsequent SAM/SOM mapping
            print(f"   🔁 Mapped TAM -> annual_revenue_or_savings = {tam_val}")

    # Handle SAM override
    if 'SAM' in mapped:
        sam_val = mapped.pop('SAM')
        if isinstance(sam_val, (int, float)) and sam_val >= 0:
            if ctx_tam and ctx_tam > 0:
                coverage = (sam_val / ctx_tam) * 100.0
                mapped['market_coverage'] = coverage
                ctx_sam = sam_val
                print(f"   🔁 Mapped SAM -> market_coverage = {coverage:.2f}% (SAM {sam_val} / TAM {ctx_tam})")
            else:
                # Fallback: treat SAM as annual value if TAM unknown
                mapped['annual_revenue_or_savings'] = sam_val
                ctx_sam = sam_val
                print(f"   ⚠️ No TAM context; SAM treated as annual_revenue_or_savings = {sam_val}")

    # Handle SOM override
    if 'SOM' in mapped:
        som_val = mapped.pop('SOM')
        if isinstance(som_val, (int, float)) and som_val >= 0:
            # Need SAM for take_rate calculation
            if not ctx_sam and ctx_tam:
                # Reconstruct SAM using existing market_coverage in context if available
                existing_cov = analysis_context.get('market_coverage') or analysis_context.get('sam', {}).get('penetration_rate')
                if existing_cov:
                    ctx_sam = ctx_tam * (existing_cov / 100.0)
            if ctx_sam and ctx_sam > 0:
                take_rate = (som_val / ctx_sam) * 100.0
                mapped['take_rate'] = take_rate
                print(f"   🔁 Mapped SOM -> take_rate = {take_rate:.2f}% (SOM {som_val} / SAM {ctx_sam})")
            else:
                # If no SAM context, treat SOM as annual_revenue_or_savings directly
                mapped['annual_revenue_or_savings'] = som_val
                print(f"   ⚠️ No SAM context; SOM treated as annual_revenue_or_savings = {som_val}")

    return mapped
