async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (body) options.body = JSON.stringify(body);

    const response = await fetch(endpoint, options);
    const data = await response.json();
    if (!response.ok) {
        const detail = typeof data.detail === 'string' ? data.detail : response.statusText;
        throw new Error(detail || `Request failed (${response.status})`);
    }
    return data;
}

async function submitExpense() {
    const input = document.getElementById('expenseInput');
    const replyDiv = document.getElementById('aiReply');
    const message = input.value;

    if (!message) return;

    replyDiv.innerText = "Money Mentor is thinking...";

    try {
        // FastAPI expects query param 'message' for simple strings
        const data = await apiCall(`/expense?message=${encodeURIComponent(message)}`, 'POST');
        if (typeof data.reply !== 'string') {
            throw new Error('The server response did not include an expense reply.');
        }
        replyDiv.innerText = data.reply;
        input.value = '';
        loadDashboard();
    } catch (e) {
        replyDiv.innerText = `Error logging expense: ${e.message}`;
    }
}

async function loadDashboard() {
    // Load Expenses
    const expenses = await apiCall('/expenses');
    const list = document.getElementById('expenseList');
    list.innerHTML = expenses.map(e =>
        `<li><span>${e.category}</span> <strong>₹${e.amount}</strong></li>`
    ).join('');

    // Load Budgets
    const budgets = await apiCall('/budget');
    const container = document.getElementById('budgetContainer');
    container.innerHTML = budgets.map(b => {
        const percent = Math.min((b.spent / b.monthly_limit) * 100, 100);
        const isOver = b.remaining < 0;
        return `
            <div class="budget-item">
                <div>${b.category} (₹${b.spent} / ₹${b.monthly_limit})</div>
                <div class="progress-bar">
                    <div class="progress-fill ${isOver ? 'over-budget' : ''}" style="width: ${percent}%"></div>
                </div>
            </div>
        `;
    }).join('');
}

async function getReport() {
    const container = document.getElementById('reportContainer');
    container.classList.remove('hidden');
    container.innerHTML = "Generating AI report...";

    try {
        const r = await apiCall('/report');
        container.innerHTML = `
            <div class="score-circle">${r.score}/100</div>
            <h3>Status: ${r.status}</h3>
            <p><strong>Biggest Expense:</strong> ${r.biggest_expense_category}</p>
            <p><strong>AI Tip:</strong> ${r.saving_tip}</p>
        `;
    } catch (e) {
        container.innerText = `Error generating report: ${e.message}`;
    }
}

// Initial load
window.onload = loadDashboard;
