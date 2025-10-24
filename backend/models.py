from pydantic import BaseModel, Field
from typing import List, Optional


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
