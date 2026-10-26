from typing import List
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel
from langchain_core.tools import tool
from langchain.agents import create_agent
from .schemas import ExpenseCreate, HealthCheckResponse
from sqlalchemy.orm import Session
from .models import Expense, Budget

llm = ChatOllama(
    model="qwen2.5:1.5b",
    temperature=0,
)

# --- Step 1: Extraction Chain ---
expense_prompt = ChatPromptTemplate.from_messages([
    ("system", "You extract expense details from casual messages. Category must be one of: food, travel, shopping, entertainment, others."),
    ("human", "{message}"),
])
expense_chain = expense_prompt | llm.with_structured_output(ExpenseCreate)

# --- Step 2: DB Tools for Agent ---
def get_db_tools(db: Session):
    @tool
    def log_expense(amount: float, category: str) -> str:
        '''Save an expense into the database.'''
        new_expense = Expense(amount=amount, category=category.lower())
        db.add(new_expense)
        db.commit()
        return f"✅ Logged ₹{amount} under '{category}'"

    @tool
    def check_budget(category: str) -> str:
        '''Check budget remaining for a category.'''
        cat = category.lower()
        budget = db.query(Budget).filter(Budget.category == cat).first()
        limit = budget.monthly_limit if budget else 1000.0
        spent = db.query(Expense).filter(Expense.category == cat).with_entities(Expense.amount).all()
        total_spent = sum(item[0] for item in spent)
        left = limit - total_spent
        if left >= 0:
            return f"{cat}: spent ₹{total_spent} of ₹{limit} -> ₹{left} left ✅"
        return f"{cat}: OVER budget by ₹{-left}! 🚨"

    @tool
    def total_spent() -> str:
        '''Get total money spent across all categories.'''
        total = db.query(Expense).with_entities(Expense.amount).all()
        t = sum(item[0] for item in total)
        return f"Total spent so far: ₹{t}"

    return [log_expense, check_budget, total_spent]

def run_money_agent(message: str, db: Session):
    tools = get_db_tools(db)
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="You are Money Mentor's accountant. Whenever the user reports an expense: 1) log it, 2) check budget, 3) reply in one short line.",
    )
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    return result["messages"][-1].content

# --- Step 3: Expert Opinions ---
def expert(name: str, role: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are {name}. {role} Reply in max 2 short sentences."),
        ("human", "This month's expenses:\n{ledger}"),
    ])
    return prompt | llm | StrOutputParser()

experts_chain = RunnableParallel(
    analyst=expert("Analyst Ravi 📊", "Find which category eats the most money."),
    coach=expert("Savings Coach Meena 🏦", "Give ONE practical tip to save more."),
    guard=expert("Budget Guard Vikram 🚨", "Warn about any overspending danger."),
)

# --- Step 4: Health Check Report ---
report_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Money Mentor writing the month-end report. Combine expert opinions into a verdict. Keep 'saving_tip' under 20 words."),
    ("human", "EXPENSES:\n{ledger}\n\nEXPERTS' OPINIONS:\n{opinions}"),
])
report_chain = report_prompt | llm.with_structured_output(HealthCheckResponse)

def generate_report(db: Session):
    expenses = db.query(Expense).all()
    ledger_text = "\n".join([f"- ₹{e.amount} on {e.category}" for e in expenses])

    opinions = experts_chain.invoke({"ledger": ledger_text})
    opinions_text = "\n".join([f"{k}: {v}" for k, v in opinions.items()])

    report = report_chain.invoke({
        "ledger": ledger_text,
        "opinions": opinions_text
    })
    return report
