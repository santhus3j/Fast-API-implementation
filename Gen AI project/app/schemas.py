from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0, description="Amount spent in rupees")
    category: str = Field(description="One of: food, travel, shopping, entertainment, others")
    payment_mode: Optional[str] = Field(default=None, description="e.g. cash, upi, credit card")

class ExpenseResponse(ExpenseCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class BudgetResponse(BaseModel):
    category: str
    monthly_limit: float
    spent: float
    remaining: float

class HealthCheckResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    status: str
    biggest_expense_category: str
    saving_tip: str
