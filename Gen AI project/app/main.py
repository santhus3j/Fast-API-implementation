from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List

from .database import engine, Base, get_db
from .models import Expense, Budget
from .schemas import ExpenseResponse, BudgetResponse, HealthCheckResponse
from .ai_engine import run_money_agent, generate_report

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Money Mentor AI")

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.post("/expense")
async def add_expense(message: str, db: Session = Depends(get_db)):
    """Process a natural language expense message."""
    try:
        reply = run_money_agent(message, db)
        return {"status": "success", "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/expenses", response_model=List[ExpenseResponse])
async def get_expenses(db: Session = Depends(get_db)):
    """Get all logged expenses."""
    return db.query(Expense).all()

@app.get("/budget", response_model=List[BudgetResponse])
async def get_budget_status(db: Session = Depends(get_db)):
    """Get budget status for all categories."""
    budgets = db.query(Budget).all()
    results = []
    for b in budgets:
        spent = sum(e.amount for e in db.query(Expense).filter(Expense.category == b.category).all())
        results.append(BudgetResponse(
            category=b.category,
            monthly_limit=b.monthly_limit,
            spent=spent,
            remaining=b.monthly_limit - spent
        ))
    return results

@app.get("/report", response_model=HealthCheckResponse)
async def get_financial_report(db: Session = Depends(get_db)):
    """Generate AI financial health report."""
    try:
        return generate_report(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Initialize default budgets if empty
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    if not db.query(Budget).first():
        default_budgets = [
            Budget(category="food", monthly_limit=3000),
            Budget(category="travel", monthly_limit=1500),
            Budget(category="shopping", monthly_limit=2000),
            Budget(category="entertainment", monthly_limit=1000),
            Budget(category="others", monthly_limit=1000),
        ]
        db.add_all(default_budgets)
        db.commit()
