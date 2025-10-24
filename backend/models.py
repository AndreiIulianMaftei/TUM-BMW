from pydantic import BaseModel
from typing import List


class Variable(BaseModel):
    name: str
    value: str
    description: str


class Formula(BaseModel):
    name: str
    formula: str
    calculation: str


class AnalysisResult(BaseModel):
    identified_variables: List[Variable]
    formulas: List[Formula]
    market_size: str = None
    revenue_potential: str = None
    addressable_market: str = None
    serviceable_market: str = None
    target_market_share: str = None
    unit_economics: str = None
    roi_estimate: str = None
    business_assumptions: List[str]
    value_market_potential_text: str
