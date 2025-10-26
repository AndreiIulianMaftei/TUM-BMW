from openai import OpenAI
from backend.config import get_settings
from backend.calculator import calculate_complete_analysis
from backend.models import ComprehensiveAnalysis
from datetime import datetime
from pathlib import Path
import json
import re
import spacy
import copy
from typing import Dict, Any, Tuple, List


def dump_pre_llm(content: str, name_prefix: str = "prompt") -> Path:
    """Write the given content to a timestamped .txt file inside PreLLM folder and return the path."""
    try:
        out_dir = Path("PreLLM")
        out_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name_prefix}_{timestamp}.txt"
        path = out_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Pre-LLM content dumped: {path}")
        return path
    except Exception as e:
        print(f"⚠️ Failed to dump pre-LLM content: {e}")
        return None


# Load multilingual spaCy model once at module import
try:
    nlp = spacy.load("xx_sent_ud_sm")
    print("✓ spaCy multilingual model 'xx_sent_ud_sm' loaded for sanitization")
except Exception as e:
    nlp = None
    print(f"⚠️ Could not load spaCy model 'xx_sent_ud_sm': {e}\n"+
          "Sanitization will be disabled. Run: python -m spacy download xx_sent_ud_sm")

# A small, configurable list of exact company names to redact (case-insensitive).
# Add more company names here if you want them always redacted.
COMPANY_NAMES = [
    "BMW",
]


def _sanitize_text_string(text: str) -> str:
    """Sanitize a plain text string using spaCy NER. Masks PERSON, ORG, and GPE.

    Returns the redacted text. If the spaCy model is not available, returns the input unchanged.
    """
    if not isinstance(text, str) or not text:
        return text

    # Collect spans to redact (start, end)
    spans: List[tuple] = []

    # spaCy NER spans
    if nlp:
        try:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in ("PERSON", "ORG", "GPE"):
                    spans.append((ent.start_char, ent.end_char))
        except Exception:
            # If spaCy fails for any reason, continue with regex-only redaction
            pass

    # Regex-based company and acronym patterns
    # Common company tokens and all-caps acronyms
    # First, redact specific company names (case-insensitive)
    company_name_patterns = [rf"\b{re.escape(name)}\b" for name in COMPANY_NAMES]
    for pattern in company_name_patterns:
        try:
            for m in re.finditer(pattern, text, flags=re.IGNORECASE):
                spans.append((m.start(), m.end()))
        except re.error:
            continue

    # Common company tokens (suffixes) to redact when present
    COMPANY_REGEXES = [
        r"\bGmbH\b",
        r"\bAG\b",
        r"\bInc\b",
        r"\bLLC\b",
        r"\bCorp(?:oration)?\b",
    ]

    for pattern in COMPANY_REGEXES:
        try:
            for m in re.finditer(pattern, text):
                spans.append((m.start(), m.end()))
        except re.error:
            continue

    # Merge overlapping/adjacent spans
    def _merge_spans(spans_list: List[tuple]) -> List[tuple]:
        if not spans_list:
            return []
        spans_sorted = sorted(spans_list, key=lambda x: x[0])
        merged: List[List[int]] = [list(spans_sorted[0])]
        for s, e in spans_sorted[1:]:
            if s > merged[-1][1]:
                merged.append([s, e])
            else:
                merged[-1][1] = max(merged[-1][1], e)
        return [(a, b) for a, b in merged]

    merged = _merge_spans(spans)
    if not merged:
        return text

    PLACEHOLDER = "[sanitized]"
    # Build redacted text by slicing
    out_parts: List[str] = []
    last = 0
    for s, e in merged:
        if s > last:
            out_parts.append(text[last:s])
        out_parts.append(PLACEHOLDER)
        last = e
    out_parts.append(text[last:])
    return "".join(out_parts)


def sanitize_extracted_data(extracted: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Iterate through an extracted dict and return (original_copy, sanitized_copy).

    - Recursively visits dicts and lists.
    - Runs spaCy NER on any string field and masks PERSON, ORG and GPE as [PERSON], [ORG], [PLACE].
    """
    def _sanitize_value(value: Any) -> Any:
        if isinstance(value, str):
            return _sanitize_text_string(value)
        elif isinstance(value, dict):
            return {k: _sanitize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_sanitize_value(v) for v in value]
        else:
            return value

    original_copy = copy.deepcopy(extracted)
    sanitized_copy = _sanitize_value(original_copy)
    return original_copy, sanitized_copy

def get_minimal_extraction_prompt(text: str) -> str:
    return f"""Extract ONLY these financial metrics from the business document. Return valid JSON only.

DOCUMENT:
{text}

EXTRACT (use null if not found):
1. project_name: Project title
2. project_type: Identify the business model:
   - "savings" if document mentions cost reduction/efficiency/avoiding costs
   - "one_time_sale" if selling products once (cars, hardware, equipment)
   - "subscription" if recurring revenue (SaaS, membership, monthly fees)
   - "royalty" if taking percentage of transactions (marketplace, licensing, platform)
   - "mixed" if combination
3. annual_revenue_or_savings: Total annual revenue OR savings in EUR (e.g., "€5 million p.a." → 5000000)
4. fleet_size_or_units: Number of units/customers/vehicles (null if savings project without units)
5. price_per_unit: Price or value per unit in EUR (null if savings project)
6. stream_values: Array of revenue/savings stream values [stream1, stream2, ...] in EUR (ANNUAL values)
7. development_cost: One-time development/setup/implementation cost in EUR (look for: feasibility studies, software dev, training costs)
8. growth_rate: Annual growth rate as percentage (default 5)
9. royalty_percentage: For royalty model - percentage taken (0-100, use 0 if not applicable)
10. take_rate: Customer adoption/conversion rate as percentage (default 10)
11. market_coverage: Market penetration percentage (default 50)

IMPORTANT INSTRUCTIONS:
- Stream values should be ANNUAL amounts (p.a. values), NOT one-time totals
- For development_cost: Add up any mentioned costs for studies, software, implementation, training
- If costs aren't specified but project needs implementation, estimate 10-20% of annual value
- Growth rate: Look for phrases like "5% annual growth", "CAGR", "year-over-year increase"

Return ONLY this JSON:
{{
  "project_name": "string or null",
  "project_type": "savings or one_time_sale or subscription or royalty or mixed",
  "annual_revenue_or_savings": number or null,
  "fleet_size_or_units": number or null,
  "price_per_unit": number or null,
  "stream_values": [number] or null,
  "development_cost": number or null,
  "growth_rate": number or null,
  "royalty_percentage": number or null,
  "take_rate": number or null,
  "market_coverage": number or null
}}"""

def analyze_document_fast(text: str) -> ComprehensiveAnalysis:
    print("\n" + "="*80)
    print("🚀 STARTING DOCUMENT ANALYSIS")
    print("="*80)
    
    try:
        settings = get_settings()
        print(f"✓ Config loaded - OpenAI Key: {settings.openai_api_key[:10]}...")
        
        client = OpenAI(api_key=settings.openai_api_key)
        
        print(f"📝 Document length: {len(text)} characters")
        print(f"📝 Document preview (first 200 chars): {text[:200]}...")

        # --- SANITIZE RAW DOCUMENT BEFORE SENDING TO LLM ---
        original_text = text
        sanitized_text = _sanitize_text_string(original_text)

        # Write both original and sanitized text files for audit
        prellm_dir = Path("PreLLM")
        prellm_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        orig_txt_path = prellm_dir / f"original_text_{ts}.txt"
        san_txt_path = prellm_dir / f"sanitized_text_{ts}.txt"
        try:
            with open(orig_txt_path, "w", encoding="utf-8") as f:
                f.write(original_text)
            with open(san_txt_path, "w", encoding="utf-8") as f:
                f.write(sanitized_text)
            print(f"✓ Wrote original and sanitized text to: {orig_txt_path}, {san_txt_path}")
        except Exception as e:
            print(f"⚠️ Failed to write sanitized/original text files: {e}")

        # Build prompt from the sanitized text only (ensures LLM never sees raw PII)
        prompt = get_minimal_extraction_prompt(sanitized_text)
        # Dump the prompt to disk before sending to the LLM for debugging/audit
        dump_pre_llm(prompt, name_prefix="extraction_prompt")
        print(f"📤 Sending SANITIZED prompt to LLM - Prompt length: {len(prompt)} chars")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=800
        )
        
        print(f"✓ LLM Response received")
        
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        print(f"📥 LLM Raw Response:\n{content}\n")
        
        try:
            extracted = json.loads(content)
            
            results_dir = Path("Json_Results")
            results_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            extraction_path = results_dir / f"extraction_{timestamp}.json"
            with open(extraction_path, "w", encoding="utf-8") as f:
                json.dump(extracted, f, indent=2, ensure_ascii=False)

            # Additionally sanitize the extracted dict (defense-in-depth) and save it
            try:
                orig_extracted, sanitized_extracted = sanitize_extracted_data(extracted)
                sanitized_path = results_dir / f"extraction_sanitized_{timestamp}.json"
                with open(sanitized_path, "w", encoding="utf-8") as f2:
                    json.dump(sanitized_extracted, f2, indent=2, ensure_ascii=False)
                print(f"✓ Sanitized extraction saved: {sanitized_path}")
            except Exception as e:
                print(f"⚠️ Failed to sanitize extracted data: {e}")

            print(f"✓ LLM Extraction saved: {extraction_path}")
            print(f"📊 Extracted Data:")
            for key, value in extracted.items():
                print(f"   {key}: {value}")
            print()
            
        except Exception as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Raw content causing error: {content[:500]}")
            extracted = {}
        
        print("🧮 Starting calculator with extracted data...")
        print(f"Input to calculator: {json.dumps(extracted, indent=2)}")
        
        full_analysis = calculate_complete_analysis(extracted)
        
        print(f"✓ Calculator completed successfully")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_path = results_dir / f"full_analysis_{timestamp}.json"
        
        analysis_dict = full_analysis.model_dump()
        with open(analysis_path, "w", encoding="utf-8") as f:
            json.dump(analysis_dict, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Full Analysis saved: {analysis_path}")
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"   TAM: €{full_analysis.tam.market_size:,.0f}")
        print(f"   SAM: €{full_analysis.sam.market_size:,.0f}")
        print(f"   SOM: €{full_analysis.som.revenue_potential:,.0f}")
        print(f"   ROI: {full_analysis.roi.roi_percentage:.1f}%")
        print(f"   Break-even: {full_analysis.roi.payback_period_months} months")
        print(f"   Units: {full_analysis.volume.units_sold:,.0f}")
        print("="*80 + "\n")
        
        return full_analysis
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR in analyze_document_fast:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        raise
