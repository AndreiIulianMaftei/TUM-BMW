"""
Chat Modifier Module
Handles natural language modification requests for dashboard data
"""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any, List
import copy

# Load environment variables
load_dotenv()

# Configure OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None


def parse_modification_request(user_message: str, current_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse natural language modification request using OpenAI.
    
    Args:
        user_message: User's natural language request
        current_data: Current dashboard data for context
        
    Returns:
        Dict with modification plan including target, old/new values, affected items
    """
    
    if not client:
        return {"error": "OpenAI API key not configured"}
    
    # Build context about available data
    data_context = build_data_context(current_data)
    
    prompt = f"""
Parse this data modification request and extract structured information.

USER REQUEST: "{user_message}"

AVAILABLE DATA TO MODIFY:
{data_context}

Your task:
1. Understand the user's intent - they may describe a scenario or directly request changes
2. Translate scenarios into concrete data modifications
   - "aluminum price increased by 50%" → increase price by 50%
   - "costs doubled" → increase costs by 100%
   - "sales dropped" → decrease units
3. Identify which data type to modify (income, cost, or market)
4. Identify the specific variable/field (price, cost, units, etc.)
5. Extract the new value (number or percentage change)
6. Determine which years are affected (if mentioned, otherwise "all")
7. If the request is too vague or not about modifying data, return confidence: "low" with interpretation explaining what's unclear

Return ONLY valid JSON in this exact format:
{{
    "data_type": "income" | "cost" | "market" | "unknown",
    "variable": "field_name",
    "operation": "set" | "increase" | "decrease",
    "value": <number>,
    "is_percentage": true | false,
    "years": ["2024", "2025"] | "all",
    "confidence": "high" | "medium" | "low",
    "interpretation": "Brief explanation of what will be modified"
}}

Examples:
- "Change royalty rate to 12%" → {{"data_type": "income", "variable": "royalty_percentage", "operation": "set", "value": 12, "years": "all", "confidence": "high"}}
- "Increase price by 10% for 2025" → {{"data_type": "income", "variable": "price_per_piece", "operation": "increase", "value": 10, "is_percentage": true, "years": ["2025"], "confidence": "high"}}
- "Aluminum price increased by 50%" → {{"data_type": "income", "variable": "price_per_piece", "operation": "increase", "value": 50, "is_percentage": true, "years": "all", "confidence": "high", "interpretation": "Increasing product price by 50% to reflect aluminum cost increase"}}
- "Costs went up 30% in 2026" → {{"data_type": "cost", "variable": "one_time_development", "operation": "increase", "value": 30, "is_percentage": true, "years": ["2026"], "confidence": "medium", "interpretation": "Increasing development costs by 30% for 2026"}}
- "What if revenue doubles?" → {{"data_type": "unknown", "confidence": "low", "interpretation": "Please specify which income variable to modify (price, units, royalty rate, etc.)"}}

CRITICAL: 
- If request mentions price changes, material costs, or inflation → modify relevant price/cost variables
- If unclear which specific variable, set confidence to "low" and explain in interpretation
- Always return valid JSON

Return ONLY the JSON, no markdown or extra text.
"""
    
    try:
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": "You are a data modification parser. Extract structured modification requests from natural language. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=500
        )
        
        json_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if '```json' in json_text:
            json_text = json_text.split('```json')[1].split('```')[0].strip()
        elif '```' in json_text:
            json_text = json_text.split('```')[1].split('```')[0].strip()
        
        result = json.loads(json_text)
        return result
        
    except Exception as e:
        return {"error": f"Failed to parse request: {str(e)}"}


def build_data_context(current_data: Dict[str, Any]) -> str:
    """Build a description of available data for the AI"""
    
    context = []
    
    # Income data
    if "income_analysis" in current_data and current_data["income_analysis"]:
        income_type = current_data.get("selected_income_strategy", "Unknown")
        context.append(f"\nINCOME DATA (Strategy: {income_type}):")
        
        if income_type == "Royalties":
            context.append("  - royalty_percentage: Royalty rate per sale (%)")
            context.append("  - price_per_piece: Price per unit (EUR)")
            context.append("  - number_of_units: Units sold per year")
        elif income_type == "Subscription":
            context.append("  - monthly_cost: Subscription price per month (EUR)")
            context.append("  - number_of_subscribers: Subscriber count per year")
            context.append("  - churn_rate: Customer churn rate (%)")
        else:  # Single Buy
            context.append("  - price: Product price (EUR)")
            context.append("  - number_of_units: Units sold per year")
    
    # Cost data
    if "cost_analysis" in current_data and current_data["cost_analysis"]:
        context.append("\nCOST DATA:")
        context.append("  - one_time_development: Development costs (EUR)")
        context.append("  - customer_acquisition: Customer acquisition costs (EUR)")
        context.append("  - distribution_operations: Distribution & operations costs (EUR)")
        context.append("  - after_sales: After-sales support costs (EUR)")
        context.append("  - total_cogs: Cost of goods sold (EUR)")
        context.append("  - cogs_per_unit: COGS per unit (EUR)")
    
    # Market data
    if "tam_sam_som" in current_data and current_data["tam_sam_som"]:
        context.append("\nMARKET DATA:")
        context.append("  - TAM: Total Addressable Market (EUR)")
        context.append("  - SAM: Serviceable Addressable Market (EUR)")
        context.append("  - SOM: Serviceable Obtainable Market (EUR)")
    
    return "\n".join(context)


def preview_modifications(modification_plan: Dict[str, Any], current_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate preview of what will change with proposed modifications.
    
    Args:
        modification_plan: Parsed modification from parse_modification_request
        current_data: Current dashboard data
        
    Returns:
        Dict with preview information (old values, new values, impact)
    """
    
    if "error" in modification_plan:
        return modification_plan
    
    data_type = modification_plan["data_type"]
    variable = modification_plan["variable"]
    operation = modification_plan["operation"]
    value = modification_plan["value"]
    is_percentage = modification_plan.get("is_percentage", False)
    years = modification_plan["years"]
    
    preview = {
        "data_type": data_type,
        "variable": variable,
        "operation": operation,
        "changes": [],
        "summary": {}
    }
    
    try:
        if data_type == "income":
            preview = preview_income_modifications(
                modification_plan, 
                current_data.get("income_analysis"),
                current_data.get("selected_income_strategy")
            )
        elif data_type == "cost":
            preview = preview_cost_modifications(
                modification_plan,
                current_data.get("cost_analysis")
            )
        elif data_type == "market":
            preview = preview_market_modifications(
                modification_plan,
                current_data.get("tam_sam_som")
            )
        
        return preview
        
    except Exception as e:
        return {"error": f"Failed to preview modifications: {str(e)}"}


def preview_income_modifications(plan: Dict, income_data: Dict, strategy: str) -> Dict:
    """Preview income data modifications"""
    
    if not income_data or "yearly_projections" not in income_data:
        return {"error": "No income data available"}
    
    variable = plan["variable"]
    operation = plan["operation"]
    value = plan["value"]
    is_percentage = plan.get("is_percentage", False)
    years = plan["years"]
    
    projections = income_data["yearly_projections"]
    changes = []
    old_total_income = 0
    new_total_income = 0
    
    for proj in projections:
        if not isinstance(proj, dict):
            continue
            
        year = str(proj.get("year", ""))
        
        # Check if this year should be modified
        if years != "all" and year not in years:
            continue
        
        old_value = proj.get(variable, 0)
        
        # Calculate new value
        if operation == "set":
            new_value = value
        elif operation == "increase":
            if is_percentage:
                new_value = old_value * (1 + value / 100)
            else:
                new_value = old_value + value
        elif operation == "decrease":
            if is_percentage:
                new_value = old_value * (1 - value / 100)
            else:
                new_value = old_value - value
        else:
            new_value = old_value
        
        # Calculate impact on yearly income
        old_yearly_income = proj.get("yearly_income", 0)
        new_yearly_income = calculate_new_income(proj, variable, new_value, strategy)
        
        changes.append({
            "year": year,
            "old_value": old_value,
            "new_value": new_value,
            "old_income": old_yearly_income,
            "new_income": new_yearly_income,
            "income_change": new_yearly_income - old_yearly_income
        })
        
        old_total_income += old_yearly_income
        new_total_income += new_yearly_income
    
    return {
        "data_type": "income",
        "variable": variable,
        "changes": changes,
        "summary": {
            "old_total_income": old_total_income,
            "new_total_income": new_total_income,
            "total_change": new_total_income - old_total_income,
            "change_percentage": ((new_total_income - old_total_income) / old_total_income * 100) if old_total_income > 0 else 0
        }
    }


def calculate_new_income(projection: Dict, modified_variable: str, new_value: float, strategy: str) -> float:
    """Calculate new yearly income based on modified variable"""
    
    # Create a copy and update the variable
    proj = projection.copy()
    proj[modified_variable] = new_value
    
    if strategy == "Royalties":
        royalty_pct = proj.get("royalty_percentage", 0)
        price = proj.get("price_per_piece", 0)
        units = proj.get("number_of_units", 0)
        return (price * royalty_pct / 100) * units
        
    elif strategy == "Subscription":
        monthly = proj.get("monthly_cost", 0)
        subscribers = proj.get("number_of_subscribers", 0)
        return monthly * 12 * subscribers
        
    else:  # Single Buy
        price = proj.get("price", 0)
        units = proj.get("number_of_units", 0)
        return price * units


def preview_cost_modifications(plan: Dict, cost_data: Dict) -> Dict:
    """Preview cost data modifications"""
    
    if not cost_data or "yearly_cost_breakdown" not in cost_data:
        return {"error": "No cost data available"}
    
    variable = plan["variable"]
    operation = plan["operation"]
    value = plan["value"]
    is_percentage = plan.get("is_percentage", False)
    years = plan["years"]
    
    breakdown = cost_data["yearly_cost_breakdown"]
    changes = []
    old_total_cost = 0
    new_total_cost = 0
    
    for year, year_data in breakdown.items():
        if years != "all" and year not in years:
            continue
        
        old_value = year_data.get(variable, 0)
        
        # Calculate new value
        if operation == "set":
            new_value = value
        elif operation == "increase":
            if is_percentage:
                new_value = old_value * (1 + value / 100)
            else:
                new_value = old_value + value
        elif operation == "decrease":
            if is_percentage:
                new_value = old_value * (1 - value / 100)
            else:
                new_value = old_value - value
        else:
            new_value = old_value
        
        # Get all cost components
        dev = year_data.get("one_time_development", 0)
        cac = year_data.get("customer_acquisition", 0)
        dist = year_data.get("distribution_operations", 0)
        after = year_data.get("after_sales", 0)
        total_cogs = year_data.get("total_cogs", 0)
        cogs_per_unit = year_data.get("cogs_per_unit", 0)
        volume = year_data.get("projected_volume", 0)
        
        # Update the modified component
        if variable == "one_time_development":
            dev = new_value
        elif variable == "customer_acquisition":
            cac = new_value
        elif variable == "distribution_operations":
            dist = new_value
        elif variable == "after_sales":
            after = new_value
        elif variable == "cogs_per_unit":
            cogs_per_unit = new_value
            total_cogs = round(new_value * volume, 2)
        elif variable == "total_cogs":
            total_cogs = new_value
        
        # Recalculate total cost from components
        old_year_total = year_data.get("total_cost", 0)
        new_year_total = round(dev + cac + dist + after + total_cogs, 2)
        
        changes.append({
            "year": year,
            "variable": variable,
            "old_value": old_value,
            "new_value": new_value,
            "old_total": old_year_total,
            "new_total": new_year_total,
            "total_change": new_year_total - old_year_total,
            "components": {
                "development": dev,
                "customer_acquisition": cac,
                "distribution_operations": dist,
                "after_sales": after,
                "total_cogs": total_cogs
            }
        })
        
        old_total_cost += old_year_total
        new_total_cost += new_year_total
    
    return {
        "data_type": "cost",
        "variable": variable,
        "changes": changes,
        "summary": {
            "old_total_cost": old_total_cost,
            "new_total_cost": new_total_cost,
            "total_change": new_total_cost - old_total_cost,
            "change_percentage": ((new_total_cost - old_total_cost) / old_total_cost * 100) if old_total_cost > 0 else 0
        }
    }


def preview_market_modifications(plan: Dict, market_data: Dict) -> Dict:
    """Preview TAM/SAM/SOM modifications"""
    
    if not market_data:
        return {"error": "No market data available"}
    
    variable = plan["variable"]
    operation = plan["operation"]
    value = plan["value"]
    is_percentage = plan.get("is_percentage", False)
    
    old_value = market_data.get(variable, 0)
    
    # Calculate new value
    if operation == "set":
        new_value = value
    elif operation == "increase":
        if is_percentage:
            new_value = old_value * (1 + value / 100)
        else:
            new_value = old_value + value
    elif operation == "decrease":
        if is_percentage:
            new_value = old_value * (1 - value / 100)
        else:
            new_value = old_value - value
    else:
        new_value = old_value
    
    return {
        "data_type": "market",
        "variable": variable,
        "changes": [{
            "old_value": old_value,
            "new_value": new_value,
            "change": new_value - old_value
        }],
        "summary": {
            "old_value": old_value,
            "new_value": new_value,
            "change": new_value - old_value,
            "change_percentage": ((new_value - old_value) / old_value * 100) if old_value > 0 else 0
        }
    }


def apply_modifications(modification_plan: Dict[str, Any], preview_data: Dict[str, Any], session_state: Any) -> bool:
    """
    Apply confirmed modifications to session state.
    
    Args:
        modification_plan: Original parsed plan
        preview_data: Preview calculations
        session_state: Streamlit session state
        
    Returns:
        True if successful, False otherwise
    """
    
    try:
        data_type = modification_plan["data_type"]
        variable = modification_plan["variable"]
        
        if data_type == "income":
            income_data = session_state.income_analysis
            
            for change in preview_data["changes"]:
                year = change["year"]
                new_value = change["new_value"]
                new_income = change["new_income"]
                
                # Find and update the projection
                for proj in income_data["yearly_projections"]:
                    if str(proj.get("year")) == year:
                        proj[variable] = new_value
                        proj["yearly_income"] = new_income
            
            # Recalculate total income
            total_income = sum(proj.get("yearly_income", 0) for proj in income_data["yearly_projections"])
            income_data["total_income"] = total_income
            
        elif data_type == "cost":
            cost_data = session_state.cost_analysis
            
            for change in preview_data["changes"]:
                year = change["year"]
                new_value = change["new_value"]
                
                # Update the cost breakdown
                if year in cost_data["yearly_cost_breakdown"]:
                    year_data = cost_data["yearly_cost_breakdown"][year]
                    
                    # Update the modified variable
                    year_data[variable] = new_value
                    
                    # Recalculate dependent fields
                    # If cogs_per_unit changed, recalculate total_cogs
                    if variable == "cogs_per_unit":
                        volume = year_data.get("projected_volume", 0)
                        year_data["total_cogs"] = round(new_value * volume, 2)
                        # Also update the base cost_data
                        cost_data["average_cogs_per_bundle"] = new_value
                    
                    # If any component cost changed, update the base totals
                    if variable == "customer_acquisition":
                        cost_data["total_customer_acquisition_cost"] = new_value
                    elif variable == "distribution_operations":
                        cost_data["total_distribution_operations_cost"] = new_value
                    elif variable == "after_sales":
                        cost_data["total_after_sales_cost"] = new_value
                    elif variable == "one_time_development":
                        cost_data["total_development_cost"] = new_value
                    
                    # Recalculate total_cost for this year
                    year_data["total_cost"] = round(
                        year_data.get("one_time_development", 0) +
                        year_data.get("customer_acquisition", 0) +
                        year_data.get("distribution_operations", 0) +
                        year_data.get("after_sales", 0) +
                        year_data.get("total_cogs", 0),
                        2
                    )
            
            # Recalculate seven_year_summary
            yearly_breakdown = cost_data["yearly_cost_breakdown"]
            available_years = sorted(yearly_breakdown.keys())
            
            total_all_years = sum(yearly_breakdown[year]["total_cost"] for year in available_years if year in yearly_breakdown)
            total_volume_all_years = sum(yearly_breakdown[year].get("projected_volume", 0) for year in available_years if year in yearly_breakdown)
            
            first_year = available_years[0] if available_years else "2024"
            last_year = available_years[-1] if available_years else "2030"
            
            cost_data["seven_year_summary"] = {
                "total_cost": round(total_all_years, 2),
                "total_volume": total_volume_all_years,
                "average_cost_per_unit": round(total_all_years / total_volume_all_years, 2) if total_volume_all_years > 0 else 0,
                "period": f"{first_year}-{last_year}"
            }
        
        elif data_type == "market":
            market_data = session_state.tam_sam_som
            market_data[variable] = preview_data["changes"][0]["new_value"]
        
        return True
        
    except Exception as e:
        print(f"Error applying modifications: {e}")
        return False
