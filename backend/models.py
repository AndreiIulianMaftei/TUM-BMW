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
    metric_value: Optional[float] = None  # Changed from str to float to accept numeric values


# New detailed cost analysis models
class CostFigure(BaseModel):
    """Industry cost comparison figure"""
    company: str
    project: Optional[str] = None  # For development/ops costs
    product: Optional[str] = None  # For COGS items
    amount: Optional[float] = None  # General cost amount
    retail_price: Optional[float] = None  # For COGS retail price
    cogs: Optional[float] = None  # For COGS per item
    margin: Optional[float] = None  # For COGS margin percentage
    currency: str
    year: int


class MarketComparison(BaseModel):
    """Market comparison with industry examples"""
    similar_case: str
    comparison_details: str
    cost_figures: Optional[List[CostFigure]] = None
    source: Optional[str] = None
    reference_links: Optional[List[str]] = None


class DevelopmentCost(BaseModel):
    """Development cost item with detailed justification"""
    category: str
    estimated_amount: float
    currency: str = "EUR"
    reasoning: str
    market_comparison: Optional[MarketComparison] = None


class CustomerAcquisitionCost(BaseModel):
    """Customer acquisition cost item"""
    category: str
    estimated_amount_per_customer: Optional[float] = None
    estimated_annual_budget: float
    currency: str = "EUR"
    reasoning: str
    market_comparison: Optional[MarketComparison] = None


class DistributionOperationsCost(BaseModel):
    """Distribution and operations cost item"""
    category: str
    estimated_amount: float
    currency: str = "EUR"
    reasoning: str
    market_comparison: Optional[MarketComparison] = None


class AfterSalesCost(BaseModel):
    """After-sales cost item"""
    category: str
    estimated_amount: float
    currency: str = "EUR"
    reasoning: str
    market_comparison: Optional[MarketComparison] = None


class COGSItem(BaseModel):
    """Cost of goods sold item"""
    product_category: str
    price_per_item: float
    cogs_per_item: float
    gross_margin_percentage: float
    currency: str = "EUR"
    reasoning: str
    market_comparison: Optional[MarketComparison] = None


class YearlyCostBreakdown(BaseModel):
    """Yearly cost breakdown"""
    projected_volume: int
    one_time_development: float
    customer_acquisition: float
    distribution_operations: float
    after_sales: float
    total_cogs: float
    cogs_per_unit: float
    total_cost: float
    currency: str = "EUR"


class SevenYearSummary(BaseModel):
    """Seven-year summary metrics"""
    total_cost_2024_2030: float
    total_volume_2024_2030: int
    average_cost_per_unit: float
    currency: str = "EUR"


class KeyRisk(BaseModel):
    """Individual risk assessment"""
    risk: str
    probability: Optional[str] = None
    mitigation: Optional[str] = None
    impact: Optional[str] = None


class CompetitiveAdvantage(BaseModel):
    """Competitive advantage description"""
    advantage: str
    market_validation: Optional[str] = None
    sustainability_assessment: Optional[str] = None


class TAMMetrics(BaseModel):
    description_of_public: str
    market_size: Optional[float] = None
    growth_rate: Optional[float] = None
    time_horizon: Optional[str] = None
    numbers: Optional[Dict[str, float]] = None  # {"2024": 1000000, "2025": 1200000, ...}
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
    numbers: Optional[Dict[str, float]] = None
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
    numbers: Optional[Dict[str, float]] = None
    justification: str
    insight: str
    confidence: int = Field(ge=0, le=100)
    industry_example: Optional[IndustryExample] = None
    customer_acquisition_cost: Optional[float] = None


class ROIMetrics(BaseModel):
    revenue: Optional[float] = None
    cost: Optional[float] = None
    roi_percentage: Optional[float] = None
    numbers: Optional[Dict[str, float]] = None
    payback_period_months: Optional[int] = None
    insight: str
    confidence: int = Field(ge=0, le=100)
    cost_breakdown: Optional[Dict[str, float]] = None


class TurnoverMetrics(BaseModel):
    year: Optional[int] = None
    total_revenue: Optional[float] = None
    yoy_growth: Optional[float] = None
    numbers: Optional[Dict[str, float]] = None
    revenue_streams: Optional[Dict[str, float]] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class VolumeMetrics(BaseModel):
    units_sold: Optional[int] = None
    region: Optional[str] = None
    period: Optional[str] = None
    numbers: Optional[Dict[str, float]] = None
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
    numbers: Optional[Dict[str, float]] = None
    insight: str
    confidence: int = Field(ge=0, le=100)
    opex_breakdown: Optional[Dict[str, float]] = None


class COGSMetrics(BaseModel):
    material: Optional[float] = None
    labor: Optional[float] = None
    overheads: Optional[float] = None
    total_cogs: Optional[float] = None
    cogs_percentage: Optional[float] = None
    numbers: Optional[Dict[str, float]] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class MarketPotential(BaseModel):
    market_size: Optional[float] = None
    penetration: Optional[float] = None
    growth_rate: Optional[float] = None
    numbers: Optional[Dict[str, float]] = None
    market_drivers: Optional[List[str]] = None
    barriers_to_entry: Optional[List[str]] = None
    insight: str
    confidence: int = Field(ge=0, le=100)


class ComprehensiveAnalysis(BaseModel):
    # Original market metrics
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
    
    # New detailed cost analysis
    development_costs: Optional[List[DevelopmentCost]] = None
    total_development_cost: Optional[float] = None
    customer_acquisition_costs: Optional[List[CustomerAcquisitionCost]] = None
    total_customer_acquisition_cost: Optional[float] = None
    distribution_and_operations_costs: Optional[List[DistributionOperationsCost]] = None
    total_distribution_operations_cost: Optional[float] = None
    after_sales_costs: Optional[List[AfterSalesCost]] = None
    total_after_sales_cost: Optional[float] = None
    cost_of_goods_sold: Optional[List[COGSItem]] = None
    average_cogs_per_bundle: Optional[float] = None
    
    # Volume projections and summaries
    volume_projections: Optional[Dict[str, int]] = None  # {"2024": 5000, "2025": 12000, ...}
    yearly_cost_breakdown: Optional[Dict[str, YearlyCostBreakdown]] = None  # {"2024": {...}, "2025": {...}, ...}
    seven_year_summary: Optional[SevenYearSummary] = None
    
    # Summary fields
    total_estimated_cost_summary: Optional[Dict[str, float]] = None
    confidence_level: Optional[str] = None
    additional_notes: Optional[str] = None
    
    # Original summary fields
    identified_variables: List[Variable]
    formulas: List[Formula]
    business_assumptions: List[str]
    improvement_recommendations: List[str]
    value_market_potential_text: str
    executive_summary: str
    sources: Optional[List[str]] = None
    key_risks: Optional[List[KeyRisk]] = None
    competitive_advantages: Optional[List[CompetitiveAdvantage]] = None


class AnalysisSettings(BaseModel):
    """Advanced settings for analysis customization"""
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    industry_focus: Optional[str] = None  # automotive, tech, healthcare, etc.
    currency: str = Field(default="EUR")  # EUR, USD, GBP


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
