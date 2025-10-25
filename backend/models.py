from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Variable(BaseModel):
    name: str
    value: str
    description: str


class Formula(BaseModel):
    name: str
    formula: str
    calculation: str


class TAMMetrics(BaseModel):
    market_size: Optional[float] = None
    growth_rate: Optional[float] = None
    time_horizon: Optional[str] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class SAMMetrics(BaseModel):
    region: Optional[str] = None
    target_segment: Optional[str] = None
    market_size: Optional[float] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class SOMMetrics(BaseModel):
    market_share: Optional[float] = None
    revenue_potential: Optional[float] = None
    capture_period: Optional[str] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class ROIMetrics(BaseModel):
    revenue: Optional[float] = None
    cost: Optional[float] = None
    roi_percentage: Optional[float] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class TurnoverMetrics(BaseModel):
    year: Optional[int] = None
    total_revenue: Optional[float] = None
    yoy_growth: Optional[float] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class VolumeMetrics(BaseModel):
    units_sold: Optional[int] = None
    region: Optional[str] = None
    period: Optional[str] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class UnitEconomics(BaseModel):
    unit_revenue: Optional[float] = None
    unit_cost: Optional[float] = None
    margin: Optional[float] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class EBITMetrics(BaseModel):
    revenue: Optional[float] = None
    operating_expense: Optional[float] = None
    ebit_margin: Optional[float] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class COGSMetrics(BaseModel):
    material: Optional[float] = None
    labor: Optional[float] = None
    overheads: Optional[float] = None
    total_cogs: Optional[float] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class MarketPotential(BaseModel):
    market_size: Optional[float] = None
    penetration: Optional[float] = None
    growth_rate: Optional[float] = None
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
