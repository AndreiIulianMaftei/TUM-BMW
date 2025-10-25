from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class Variable(BaseModel):
    name: str
    value: str
    description: str


class Formula(BaseModel):
    name: str
    formula: str
    calculation: str


class IndustryExample(BaseModel):
    """Industry benchmark or comparable example"""
    name: str
    description: str
    link: Optional[str] = None
    metric_value: Optional[str] = None


class YearlyProjection(BaseModel):
    """Year-by-year numerical projections"""
    year_2024: Optional[float] = Field(None, alias="2024")
    year_2025: Optional[float] = Field(None, alias="2025")
    year_2026: Optional[float] = Field(None, alias="2026")
    year_2027: Optional[float] = Field(None, alias="2027")
    year_2028: Optional[float] = Field(None, alias="2028")
    year_2029: Optional[float] = Field(None, alias="2029")
    year_2030: Optional[float] = Field(None, alias="2030")
    
    class Config:
        populate_by_name = True


class TAMMetrics(BaseModel):
    description_of_public: str
    market_size: Optional[float] = None
    growth_rate: Optional[float] = None
    time_horizon: Optional[str] = None
    numbers: Optional[YearlyProjection] = None
    justification: str
    insight: str
    confidence: int = Field(ge=0, le=100)
    industry_example: Optional[IndustryExample] = None
    breakdown: Optional[Dict[str, float]] = None


class SAMMetrics(BaseModel):
    description_of_public: str
    region: Optional[str] = None
    target_segment: Optional[str] = None
    market_size: Optional[float] = None
    numbers: Optional[YearlyProjection] = None
    justification: str
    insight: str
    confidence: int = Field(ge=0, le=100)
    industry_example: Optional[IndustryExample] = None
    penetration_rate: Optional[float] = None


class SOMMetrics(BaseModel):
    description_of_public: str
    market_share: Optional[float] = None
    revenue_potential: Optional[float] = None
    capture_period: Optional[str] = None
    numbers: Optional[YearlyProjection] = None
    justification: str
    insight: str
    confidence: int = Field(ge=0, le=100)
    industry_example: Optional[IndustryExample] = None
    customer_acquisition_cost: Optional[float] = None


class ROIMetrics(BaseModel):
    revenue: Optional[float] = None
    cost: Optional[float] = None
    roi_percentage: Optional[float] = None
    numbers: Optional[YearlyProjection] = None
    payback_period_months: Optional[int] = None
    insight: str
    confidence: int = Field(ge=0, le=100)
    cost_breakdown: Optional[Dict[str, float]] = None


class TurnoverMetrics(BaseModel):
    year: Optional[int] = None
    total_revenue: Optional[float] = None
    yoy_growth: Optional[float] = None
    numbers: Optional[YearlyProjection] = None
    revenue_streams: Optional[Dict[str, float]] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class VolumeMetrics(BaseModel):
    units_sold: Optional[int] = None
    region: Optional[str] = None
    period: Optional[str] = None
    numbers: Optional[YearlyProjection] = None
    insight: str
    confidence: int = Field(ge=0, le=100)
    growth_drivers: Optional[List[str]] = None


class UnitEconomics(BaseModel):
    unit_revenue: Optional[float] = None
    unit_cost: Optional[float] = None
    margin: Optional[float] = None
    margin_percentage: Optional[float] = None
    ltv_cac_ratio: Optional[float] = None
    insight: str
    confidence: int = Field(ge=0, le=100)
    cost_components: Optional[Dict[str, float]] = None


class EBITMetrics(BaseModel):
    revenue: Optional[float] = None
    operating_expense: Optional[float] = None
    ebit_margin: Optional[float] = None
    ebit_percentage: Optional[float] = None
    numbers: Optional[YearlyProjection] = None
    insight: str
    confidence: int = Field(ge=0, le=100)
    opex_breakdown: Optional[Dict[str, float]] = None


class COGSMetrics(BaseModel):
    material: Optional[float] = None
    labor: Optional[float] = None
    overheads: Optional[float] = None
    total_cogs: Optional[float] = None
    cogs_percentage: Optional[float] = None
    numbers: Optional[YearlyProjection] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class MarketPotential(BaseModel):
    market_size: Optional[float] = None
    penetration: Optional[float] = None
    growth_rate: Optional[float] = None
    numbers: Optional[YearlyProjection] = None
    market_drivers: Optional[List[str]] = None
    barriers_to_entry: Optional[List[str]] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class ComprehensiveAnalysis(BaseModel):
    tam: TAMMetrics
    sam: SAMMetrics
    som: SOMMetrics
    roi: ROIMetrics
    turnover: TurnoverMetrics
    volume: VolumeMetrics
    unit_economics: UnitEconomics
    ebit: EBITMetrics
    cogs: COGSMetrics
    market_potential: MarketPotential
    identified_variables: List[Variable]
    formulas: List[Formula]
    business_assumptions: List[str]
    improvement_recommendations: List[str]
    value_market_potential_text: str
    executive_summary: str
    sources: Optional[List[str]] = None
    key_risks: Optional[List[str]] = None
    competitive_advantages: Optional[List[str]] = None


class AnalysisSettings(BaseModel):
    """Advanced settings for analysis customization"""
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    analysis_depth: str = Field(default="comprehensive")  # quick, standard, comprehensive
    industry_focus: Optional[str] = None  # automotive, tech, healthcare, etc.
    currency: str = Field(default="EUR")  # EUR, USD, GBP
    confidence_threshold: int = Field(default=60, ge=0, le=100)
    response_format: str = Field(default="detailed")  # concise, standard, detailed


class TextAnalysisRequest(BaseModel):
    """Request model for text-based analysis"""
    text: str = Field(..., min_length=50, max_length=50000)
    provider: str = Field(default="gemini")
    settings: Optional[AnalysisSettings] = None


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request for chat interaction"""
    message: str = Field(..., min_length=1, max_length=2000)
    document_id: Optional[str] = None  # Reference to analyzed document
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    provider: str = Field(default="gemini")


class ChatResponse(BaseModel):
    """Response from chat interaction"""
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tokens_used: Optional[int] = None
