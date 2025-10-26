from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Body
from fastapi.responses import FileResponse
from datetime import datetime
from backend.processor import process_file
from backend.analyzer import analyze_bmw_1pager, analyze_bmw_1pager_with_extraction
from backend.database import Database
from backend.models import (
    TextAnalysisRequest, AnalysisSettings, ComprehensiveAnalysis, ChatRequest, ChatResponse
)
from backend.calculator import calculate_complete_analysis
from backend.chat_analyzer import chat_with_analysis
from backend.excel_exporter import ExcelExporter
from typing import Optional, Dict, Any, List
import json
import re

router = APIRouter(prefix="/api", tags=["documents"])


def generate_analysis_title(analysis: ComprehensiveAnalysis, filename: str) -> str:
    """Generate a meaningful title from the analysis"""
    # Try to extract a business concept from the executive summary or filename
    if hasattr(analysis, 'executive_summary') and analysis.executive_summary:
        # Take first sentence or first 50 characters
        summary = analysis.executive_summary.split('.')[0]
        if len(summary) > 60:
            summary = summary[:57] + "..."
        return summary
    
    # Try to extract from TAM description
    if hasattr(analysis, 'tam') and analysis.tam and hasattr(analysis.tam, 'description_of_public'):
        desc = analysis.tam.description_of_public.split('.')[0]
        if len(desc) > 60:
            desc = desc[:57] + "..."
        return desc
    
    # Fallback to filename
    clean_name = re.sub(r'\.(pdf|docx|txt)$', '', filename, flags=re.IGNORECASE)
    clean_name = clean_name.replace('_', ' ').replace('-', ' ')
    if len(clean_name) > 60:
        clean_name = clean_name[:57] + "..."
    return clean_name


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    provider: Optional[str] = Form("gemini"),
    settings_json: Optional[str] = Form(None)
):
    print("\n" + "="*100)
    print("🌐 API: UPLOAD REQUEST RECEIVED")
    print("="*100)
    
    try:
        print(f"📁 File: {file.filename}")
        print(f"🤖 Provider: {provider}")
        
        if not file.filename.endswith(('.pdf', '.docx')):
            print(f"❌ Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")
        
        if provider not in ["gemini", "openai"]:
            print(f"❌ Invalid provider: {provider}")
            raise HTTPException(status_code=400, detail="Provider must be 'gemini' or 'openai'")
        
        settings = None
        if settings_json:
            try:
                settings_dict = json.loads(settings_json)
                settings = AnalysisSettings(**settings_dict)
                print(f"⚙️  Settings loaded: {settings_dict}")
            except Exception as e:
                print(f"❌ Settings parse error: {e}")
                raise HTTPException(status_code=400, detail=f"Invalid settings: {str(e)}")
        
        print(f"📤 Reading file content...")
        file_content = await file.read()
        file_type = "pdf" if file.filename.endswith('.pdf') else "docx"
        print(f"✓ File read: {len(file_content)} bytes")
        
        print(f"\n📝 Processing file ({file_type})...")
        text = process_file(file_content, file_type)
        print(f"✓ Text extracted: {len(text)} characters")
        print(f"   Preview: {text[:200]}...")
        
        print(f"\n🧠 Starting analysis...")
        analysis, extraction_data = analyze_bmw_1pager_with_extraction(text, provider=provider, settings=settings)
        print(f"✓ Analysis completed")
        
        print(f"\n📊 Generating title...")
        title = generate_analysis_title(analysis, file.filename)
        print(f"✓ Title: {title}")
        
        print(f"\n💾 Saving to database...")
        db = Database.get_db()
        document_record = {
            "title": title,
            "filename": file.filename,
            "file_type": file_type,
            "input_type": "file",
            "llm_provider": provider,
            "upload_date": datetime.utcnow(),
            "settings": settings.model_dump() if settings else None,
            "analysis": analysis.model_dump(),
            "extraction_data": extraction_data  # Store original LLM extraction for auto-scaling
        }
        
        result = db.documents.insert_one(document_record)
        doc_id = str(result.inserted_id)
        print(f"✓ Saved to database: ID={doc_id}")
        
        print(f"\n✅ SUCCESS - Returning response to frontend")
        print(f"   TAM: €{analysis.tam.market_size:,.0f}")
        print(f"   SOM: €{analysis.som.revenue_potential:,.0f}")
        print(f"   ROI: {analysis.roi.roi_percentage:.1f}%")
        print("="*100 + "\n")
        
        return {
            "success": True,
            "document_id": doc_id,
            "filename": file.filename,
            "provider": provider,
            "analysis": analysis
        }
    
    except Exception as e:
        print(f"\n❌ UPLOAD ERROR:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        print(f"   Traceback:\n{traceback.format_exc()}")
        print("="*100 + "\n")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.post("/analyze-text")
async def analyze_text(request: TextAnalysisRequest):
    if request.provider not in ["gemini", "openai"]:
        raise HTTPException(status_code=400, detail="Provider must be 'gemini' or 'openai'")
    
    try:
        analysis, extraction_data = analyze_bmw_1pager_with_extraction(
            text=request.text,
            provider=request.provider,
            settings=request.settings
        )
        
        # Generate a title from the analysis
        title = generate_analysis_title(analysis, "Text Input Analysis")
        
        db = Database.get_db()
        document_record = {
            "title": title,
            "filename": "text_input",
            "file_type": "text",
            "input_type": "text",
            "llm_provider": request.provider,
            "upload_date": datetime.utcnow(),
            "input_text": request.text[:500],  # Store first 500 chars for reference
            "settings": request.settings.model_dump() if request.settings else None,
            "analysis": analysis.model_dump(),
            "extraction_data": extraction_data  # Store for auto-scaling
        }
        
        result = db.documents.insert_one(document_record)
        
        return {
            "success": True,
            "document_id": str(result.inserted_id),
            "provider": request.provider,
            "analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing text: {str(e)}")


@router.get("/documents")
async def get_documents():
    """Get all documents - full details"""
    db = Database.get_db()
    documents = list(db.documents.find().sort("upload_date", -1).limit(50))
    
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    
    return {"documents": documents}


@router.get("/history")
async def get_history():
    """Get analysis history for sidebar - lightweight with only essential fields"""
    db = Database.get_db()
    documents = list(db.documents.find(
        {},
        {
            "_id": 1,
            "title": 1,
            "filename": 1,
            "upload_date": 1,
            "llm_provider": 1,
            "file_type": 1
        }
    ).sort("upload_date", -1).limit(100))
    
    history_items = []
    for doc in documents:
        history_items.append({
            "id": str(doc["_id"]),
            "title": doc.get("title", doc.get("filename", "Untitled Analysis")),
            "date": doc["upload_date"].isoformat() if doc.get("upload_date") else None,
            "provider": doc.get("llm_provider", "unknown"),
            "file_type": doc.get("file_type", "unknown")
        })
    
    return {"history": history_items}


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    from bson import ObjectId
    
    db = Database.get_db()
    document = db.documents.find_one({"_id": ObjectId(document_id)})
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document["_id"] = str(document["_id"])
    return document


@router.post("/simulate-income")
async def simulate_income(
    document_id: Optional[str] = Body(None),
    parameters: Dict[str, Any] = Body(...)
):
    """
    Simulate income with modified parameters
    Allows users to adjust key variables and see updated projections
    """
    print("\n" + "="*100)
    print("🎯 API: INCOME SIMULATION REQUEST")
    print("="*100)
    
    try:
        print(f"📄 Document ID: {document_id}")
        print(f"🔧 Modified Parameters:")
        for key, value in parameters.items():
            print(f"   {key}: {value}")
        
        from bson import ObjectId
        db = Database.get_db()
        
        original_analysis = None
        if document_id:
            print(f"\n📥 Loading original analysis from database...")
            document = db.documents.find_one({"_id": ObjectId(document_id)})
            if document and "analysis" in document:
                original_analysis = document["analysis"]
                print(f"✓ Original analysis loaded")
        
        print(f"\n🧮 Recalculating with new parameters...")
        
        extracted_params = {
            "project_name": parameters.get("project_name", "Income Simulation"),
            "project_type": parameters.get("project_type", "savings"),
            "annual_revenue_or_savings": parameters.get("annual_revenue_or_savings"),
            "fleet_size_or_units": parameters.get("fleet_size_or_units"),
            "price_per_unit": parameters.get("price_per_unit"),
            "stream_values": parameters.get("stream_values"),
            "development_cost": parameters.get("development_cost"),
            "growth_rate": parameters.get("growth_rate", 5.0),
            "royalty_percentage": parameters.get("royalty_percentage", 0.0),
            "take_rate": parameters.get("take_rate", 10.0),
            "market_coverage": parameters.get("market_coverage", 50.0)
        }

        # ----- AUTO-SCALING LOGIC FOR DEPENDENT METRICS -----
        # Remove internal tracking metadata before processing
        explicit_mods = extracted_params.pop('_explicit_mods', set())
        
        # If only volume/fleet size changed for savings project, scale annual_revenue_or_savings proportionally
        # IMPORTANT: Use original EXTRACTION values, not derived analysis values
        try:
            if original_analysis and extracted_params["project_type"] in ["savings", "cost_savings", "efficiency"]:
                # Get original EXTRACTED fleet size (not derived units_sold)
                orig_extraction = original_analysis.get("extraction_data", {})
                orig_fleet = orig_extraction.get("fleet_size_or_units")
                orig_annual = orig_extraction.get("annual_revenue_or_savings")
                new_fleet = extracted_params.get("fleet_size_or_units")
                
                # Check if user explicitly modified annual_revenue_or_savings (via _explicit_mods set from chat)
                user_overrode_annual = 'annual_revenue_or_savings' in explicit_mods
                
                # Only scale if original baseline exists, new fleet provided, annual not explicitly overridden
                if orig_fleet and new_fleet and orig_fleet > 0 and new_fleet != orig_fleet:
                    if not user_overrode_annual and orig_annual:
                        per_unit = orig_annual / orig_fleet
                        scaled = per_unit * new_fleet
                        extracted_params["annual_revenue_or_savings"] = scaled
                        print(f"   🔁 Auto-scaled annual savings: baseline per-unit=€{per_unit:.2f} → new annual=€{scaled:,.0f} (fleet {orig_fleet:,}→{new_fleet:,})")
        except Exception as e:
            print(f"   ⚠️ Auto-scale skipped (error: {e})")
        
        new_analysis = calculate_complete_analysis(extracted_params)
        print(f"✓ Simulation completed")
        
        print(f"\n📊 Simulation Results:")
        print(f"   TAM: €{new_analysis.tam.market_size:,.0f}")
        print(f"   SAM: €{new_analysis.sam.market_size:,.0f}")
        print(f"   SOM: €{new_analysis.som.revenue_potential:,.0f}")
        print(f"   ROI: {new_analysis.roi.roi_percentage:.1f}%")
        print(f"   Break-even: {new_analysis.roi.payback_period_months} months")
        
        print(f"\n💾 Saving simulation scenario to database...")
        
        # Clean internal metadata from parameters before saving
        clean_parameters = {k: v for k, v in parameters.items() if k != '_explicit_mods'}
        
        simulation_record = {
            "original_document_id": document_id,
            "simulation_date": datetime.utcnow(),
            "modified_parameters": clean_parameters,
            "simulation_results": new_analysis.model_dump(),
            "scenario_type": parameters.get("scenario_type", "custom")
        }
        
        result = db.simulations.insert_one(simulation_record)
        simulation_id = str(result.inserted_id)
        print(f"✓ Simulation saved: ID={simulation_id}")
        
        comparison = None
        if original_analysis:
            print(f"\n📈 Generating comparison with original...")
            comparison = {
                "tam_change": new_analysis.tam.market_size - original_analysis.get("tam", {}).get("market_size", 0),
                "som_change": new_analysis.som.revenue_potential - original_analysis.get("som", {}).get("revenue_potential", 0),
                "roi_change": new_analysis.roi.roi_percentage - original_analysis.get("roi", {}).get("roi_percentage", 0),
                "tam_change_pct": ((new_analysis.tam.market_size / original_analysis.get("tam", {}).get("market_size", 1) - 1) * 100) if original_analysis.get("tam", {}).get("market_size", 0) > 0 else 0,
                "som_change_pct": ((new_analysis.som.revenue_potential / original_analysis.get("som", {}).get("revenue_potential", 1) - 1) * 100) if original_analysis.get("som", {}).get("revenue_potential", 0) > 0 else 0,
            }
            print(f"✓ Comparison generated:")
            print(f"   TAM Change: {comparison['tam_change_pct']:.1f}%")
            print(f"   SOM Change: {comparison['som_change_pct']:.1f}%")
            print(f"   ROI Change: {comparison['roi_change']:.1f}%")
        
        print(f"\n✅ SUCCESS - Returning simulation results")
        print("="*100 + "\n")
        
        return {
            "success": True,
            "simulation_id": simulation_id,
            "analysis": new_analysis,
            "comparison": comparison,
            "modified_parameters": clean_parameters
        }
    
    except Exception as e:
        print(f"\n❌ SIMULATION ERROR:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        print(f"   Traceback:\n{traceback.format_exc()}")
        print("="*100 + "\n")
        raise HTTPException(status_code=500, detail=f"Error simulating income: {str(e)}")


@router.get("/simulations/{document_id}")
async def get_simulations(document_id: str):
    """Get all simulation scenarios for a document"""
    from bson import ObjectId
    
    db = Database.get_db()
    simulations = list(db.simulations.find(
        {"original_document_id": document_id}
    ).sort("simulation_date", -1).limit(20))
    
    for sim in simulations:
        sim["_id"] = str(sim["_id"])
    
    return {"simulations": simulations}


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Chat with AI about the analysis and potentially modify simulation parameters
    """
    print("\n" + "="*100)
    print("💬 API: CHAT REQUEST RECEIVED")
    print("="*100)
    
    try:
        print(f"📝 Message: {request.message}")
        print(f"🤖 Provider: {request.provider}")
        print(f"📊 Analysis Context: {bool(request.analysis_context)}")
        print(f"💭 Conversation History: {len(request.conversation_history)} messages")
        
        if not request.analysis_context:
            print("⚠️  No analysis context provided")
            raise HTTPException(
                status_code=400, 
                detail="Analysis context is required for chat"
            )
        
        print(f"\n🧠 Processing chat message...")
        response_text, modifications = chat_with_analysis(
            message=request.message,
            analysis_context=request.analysis_context,
            provider=request.provider,
            conversation_history=[msg.model_dump() for msg in request.conversation_history]
        )
        
        print(f"✓ Chat response generated")
        print(f"   Response length: {len(response_text)} chars")
        print(f"   Modifications detected: {bool(modifications)}")
        
        result = {
            "success": True,
            "response": response_text,
            "modifications": modifications
        }
        
        # Handle revert request
        if modifications and modifications.get('__revert'):
            print("\n↩️ Revert requested - returning original analysis without simulation")
            # Remove special key from modifications before returning
            result['modifications'] = None
            result['revert'] = True
            # Embed original analysis for frontend to restore
            result['simulation'] = {"analysis": request.analysis_context}
        # If modifications were detected (non-revert), run simulation automatically
        elif modifications:
            print(f"\n🎯 Auto-running simulation with modifications...")
            print(f"   Modified parameters: {list(modifications.keys())}")
            
            # Get current parameters from analysis context
            current_params = _extract_current_parameters(request.analysis_context)
            
            # Track which parameters were explicitly modified by user
            explicit_modifications = set(modifications.keys())
            
            # Apply modifications
            current_params.update(modifications)
            
            # Pass explicit modification info for auto-scaling detection
            current_params['_explicit_mods'] = explicit_modifications
            
            print(f"   Running simulation...")
            simulation_result = await simulate_income(
                document_id=request.analysis_context.get('document_id'),
                parameters=current_params
            )
            
            result['simulation'] = simulation_result
            print(f"   ✓ Simulation completed")
            print(f"   New SOM: €{simulation_result['analysis'].som.revenue_potential:,.0f}")
            print(f"   New ROI: {simulation_result['analysis'].roi.roi_percentage:.1f}%")
        
        print(f"\n✅ SUCCESS - Returning chat response")
        print("="*100 + "\n")
        
        return ChatResponse(**result)
        
    except Exception as e:
        print(f"\n❌ CHAT ERROR:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        import traceback
        print(f"   Traceback:\n{traceback.format_exc()}")
        print("="*100 + "\n")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


def _extract_current_parameters(analysis_context: Dict[str, Any]) -> Dict[str, Any]:
    """Extract current parameters from analysis context for simulation"""
    params = {
        "project_name": analysis_context.get("project_name", "Chat Simulation"),
        "project_type": analysis_context.get("project_type", "savings"),
    }
    
    # Extract from cost summary if available
    if "total_estimated_cost_summary" in analysis_context:
        cost_summary = analysis_context["total_estimated_cost_summary"]
        params["development_cost"] = cost_summary.get("development_cost", 0)
        params["growth_rate"] = cost_summary.get("growth_rate", 5.0)
    
    # Extract revenue streams
    if "revenue_streams" in analysis_context:
        streams = analysis_context["revenue_streams"]
        params["stream_values"] = {
            stream.get("name", f"Stream {i+1}"): stream.get("value", 0)
            for i, stream in enumerate(streams)
        }
    
    # Extract market data
    project_type = analysis_context.get("project_type")
    # For savings projects: annual value already represents realized annual savings → no division
    if project_type in ["savings", "cost_savings", "efficiency"]:
        if "som" in analysis_context and isinstance(analysis_context["som"], dict):
            params["annual_revenue_or_savings"] = analysis_context["som"].get("revenue_potential", 0)
        elif "tam" in analysis_context and isinstance(analysis_context["tam"], dict):
            params["annual_revenue_or_savings"] = analysis_context["tam"].get("market_size", 0)
    else:
        # Non-savings: keep conservative original behavior (divide to approximate Year1 if total used)
        if "som" in analysis_context and isinstance(analysis_context["som"], dict):
            params["annual_revenue_or_savings"] = analysis_context["som"].get("revenue_potential", 0) / 5
        elif "tam" in analysis_context and isinstance(analysis_context["tam"], dict):
            params["annual_revenue_or_savings"] = analysis_context["tam"].get("market_size", 0) / 5
    
    # Extract fleet size & price if available (ensure downstream scaling context)
    if "volume" in analysis_context and isinstance(analysis_context["volume"], dict):
        params["fleet_size_or_units"] = analysis_context["volume"].get("units_sold")
    if "unit_economics" in analysis_context and isinstance(analysis_context["unit_economics"], dict):
        params["price_per_unit"] = analysis_context["unit_economics"].get("unit_revenue")

    # Extract percentages
    params["royalty_percentage"] = analysis_context.get("royalty_percentage", 0.0)
    params["take_rate"] = analysis_context.get("take_rate", 10.0)
    params["market_coverage"] = analysis_context.get("market_coverage", 50.0)
    
    return params


@router.post("/export")
async def export_to_excel(analysis_data: Dict[str, Any] = Body(...)):
    """
    Export comprehensive analysis to professionally formatted Excel file
    """
    try:
        exporter = ExcelExporter()
        filepath = exporter.generate_excel(analysis_data)
        
        return FileResponse(
            path=filepath,
            filename=filepath.split("/")[-1],
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        print(f"❌ Export error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
