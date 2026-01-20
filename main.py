from flask import Flask, request
import json
import os
from datetime import datetime

app = Flask(__name__)

# File to store expenses
EXPENSES_FILE = 'expenses.json'
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Other"]

def load_expenses():
    """Load expenses from file"""
    try:
        if os.path.exists(EXPENSES_FILE):
            with open(EXPENSES_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_expenses(expenses):
    """Save expenses to file"""
    with open(EXPENSES_FILE, 'w') as f:
        json.dump(expenses, f, indent=2)

# HTML template
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>💰 Expenses Tracker</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        .tab-btn {
            padding: 12px 25px;
            background: #f0f0f0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        .tab-btn:hover {
            background: #ddd;
        }
        .tab-btn.active {
            background: #4CAF50;
            color: white;
        }
        .tab-content {
            display: none;
            padding: 20px;
            border-radius: 10px;
            background: #f9f9f9;
            margin-top: 20px;
        }
        .tab-content.active {
            display: block;
        }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #4CAF50;
        }
        button {
            background: #4CAF50;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
            transition: background 0.3s;
        }
        button:hover {
            background: #45a049;
        }
        .expense-item {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 5px solid #4CAF50;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .expense-details {
            flex: 1;
        }
        .expense-amount {
            font-weight: bold;
            font-size: 1.2em;
            color: #333;
        }
        .expense-category {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .delete-btn {
            background: #ff4444;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .stats-box {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .category-bar {
            background: #f0f0f0;
            border-radius: 10px;
            margin: 10px 0;
            overflow: hidden;
        }
        .category-fill {
            background: #4CAF50;
            height: 30px;
            border-radius: 10px;
            color: white;
            display: flex;
            align-items: center;
            padding-left: 15px;
            font-weight: bold;
            transition: width 0.5s;
        }
        .message {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: center;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>💰 Expenses Tracker</h1>

        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('add')">➕ Add Expense</button>
            <button class="tab-btn" onclick="showTab('view')">📋 View All</button>
            <button class="tab-btn" onclick="showTab('summary')">📊 Summary</button>
        </div>

        <!-- Add Expense Tab -->
        <div id="add-tab" class="tab-content active">
            <form method="POST" action="/add">
                <input type="number" name="amount" step="0.01" min="0.01" placeholder="Amount ($)" required>

                <select name="category" required>
                    <option value="">Select Category</option>
                    <option value="Food">🍎 Food</option>
                    <option value="Transport">🚗 Transport</option>
                    <option value="Shopping">🛍️ Shopping</option>
                    <option value="Bills">📄 Bills</option>
                    <option value="Entertainment">🎬 Entertainment</option>
                    <option value="Other">📦 Other</option>
                </select>

                <textarea name="description" placeholder="Description (optional)" rows="3"></textarea>

                <input type="date" name="date" value="{{ today }}">

                <button type="submit">💾 Save Expense</button>
            </form>

            {% if add_message %}
            <div class="message {{ add_message_type }}">
                {{ add_message }}
            </div>
            {% endif %}
        </div>

        <!-- View Expenses Tab -->
        <div id="view-tab" class="tab-content">
            <h3>📋 All Expenses ({{ total_expenses }})</h3>
            <p>Total: ${{ total_amount }}</p>

            {% if not expenses %}
            <div class="message" style="text-align: center; padding: 40px;">
                📭 No expenses recorded yet!
            </div>
            {% else %}
                {% for expense in expenses %}
                <div class="expense-item">
                    <div class="expense-details">
                        <div class="expense-amount">${{ expense.amount }}</div>
                        <div>{{ expense.description }}</div>
                        <div style="color: #666; font-size: 0.9em;">
                            {{ expense.date }}
                            <span class="expense-category">{{ expense.category }}</span>
                        </div>
                    </div>
                    <form method="POST" action="/delete" style="display: inline;">
                        <input type="hidden" name="expense_id" value="{{ loop.index0 }}">
                        <button type="submit" class="delete-btn" onclick="return confirm('Delete this expense?')">
                            🗑️
                        </button>
                    </form>
                </div>
                {% endfor %}
            {% endif %}
        </div>

        <!-- Summary Tab -->
        <div id="summary-tab" class="tab-content">
            <h3>📊 Expense Summary</h3>

            {% if not expenses %}
            <div class="message" style="text-align: center; padding: 40px;">
                📭 No expenses to summarize!
            </div>
            {% else %}
            <div class="stats-box">
                <h4>Total: ${{ total_amount }}</h4>

                {% for category, data in summary.items() %}
                <div style="margin: 15px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>{{ category }}: ${{ data.amount }}</span>
                        <span>{{ data.percentage }}%</span>
                    </div>
                    <div class="category-bar">
                        <div class="category-fill" style="width: {{ data.percentage }}%">
                            {{ data.percentage }}%
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });

            // Remove active class from all buttons
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });

            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');

            // Set active button
            event.target.classList.add('active');
        }

        // Set today's date as default
        document.addEventListener('DOMContentLoaded', function() {
            const today = new Date().toISOString().split('T')[0];
            const dateInput = document.querySelector('input[name="date"]');
            if (dateInput && !dateInput.value) {
                dateInput.value = today;
            }
        });
    </script>
</body>
</html>"""

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page"""
    expenses = load_expenses()
    today = datetime.now().strftime('%Y-%m-%d')

    # Calculate totals
    total_amount = sum(expense['amount'] for expense in expenses)
    total_expenses = len(expenses)

    # Calculate summary
    summary = {}
    if expenses:
        for expense in expenses:
            category = expense['category']
            if category not in summary:
                summary[category] = {'amount': 0, 'percentage': 0}
            summary[category]['amount'] += expense['amount']

        # Calculate percentages
        for category in summary:
            summary[category]['amount'] = round(summary[category]['amount'], 2)
            summary[category]['percentage'] = round((summary[category]['amount'] / total_amount) * 100, 1)

    # Replace template variables
    html = HTML_TEMPLATE
    html = html.replace('{{ today }}', today)
    html = html.replace('{{ total_expenses }}', str(total_expenses))
    html = html.replace('{{ total_amount }}', f"{total_amount:.2f}")

    # Replace expenses list
    if expenses:
        expenses_html = ""
        for i, expense in enumerate(expenses):
            exp_html = f"""
            <div class="expense-item">
                <div class="expense-details">
                    <div class="expense-amount">${expense['amount']:.2f}</div>
                    <div>{expense['description']}</div>
                    <div style="color: #666; font-size: 0.9em;">
                        {expense.get('date', 'Today')}
                        <span class="expense-category">{expense['category']}</span>
                    </div>
                </div>
                <form method="POST" action="/delete" style="display: inline;">
                    <input type="hidden" name="expense_id" value="{i}">
                    <button type="submit" class="delete-btn" onclick="return confirm('Delete this expense?')">
                        🗑️
                    </button>
                </form>
            </div>
            """
            expenses_html += exp_html
        html = html.replace('{% for expense in expenses %}', '').replace('{% endfor %}', '')
        html = html.replace('{{ expense.amount }}', '').replace('{{ expense.description }}', '')
        html = html.replace('{{ expense.date }}', '').replace('{{ expense.category }}', '')
        html = html.replace('{{ loop.index0 }}', '')
        html = html.replace('{% if not expenses %}', '').replace('{% else %}', '')
        html = html.replace('{% endif %}', '')
        html = html.replace('📭 No expenses recorded yet!', '')
        html = html.replace('{% for expense in expenses %}{% endfor %}', expenses_html)
    else:
        # Handle empty expenses
        html = html.replace('{% if not expenses %}', '').replace('{% else %}', '')
        html = html.replace('{% endif %}', '')
        html = html.replace('{% for expense in expenses %}', '')
        html = html.replace('{% endfor %}', '')
        html = html.replace('{{ expense.amount }}', '').replace('{{ expense.description }}', '')
        html = html.replace('{{ expense.date }}', '').replace('{{ expense.category }}', '')
        html = html.replace('{{ loop.index0 }}', '')

    # Replace summary
    if summary:
        summary_html = ""
        for category, data in summary.items():
            sum_html = f"""
            <div style="margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span>{category}: ${data['amount']:.2f}</span>
                    <span>{data['percentage']}%</span>
                </div>
                <div class="category-bar">
                    <div class="category-fill" style="width: {data['percentage']}%">
                        {data['percentage']}%
                    </div>
                </div>
            </div>
            """
            summary_html += sum_html

        html = html.replace('{% for category, data in summary.items() %}', '')
        html = html.replace('{% endfor %}', '')
        html = html.replace('{{ category }}', '').replace('{{ data.amount }}', '')
        html = html.replace('{{ data.percentage }}', '')
        html = html.replace('{{ data.percentage }}%', '')
        html = html.replace('{% for category, data in summary.items() %}{% endfor %}', summary_html)
    else:
        html = html.replace('{% for category, data in summary.items() %}', '')
        html = html.replace('{% endfor %}', '')
        html = html.replace('{{ category }}', '').replace('{{ data.amount }}', '')
        html = html.replace('{{ data.percentage }}', '')

    # Remove message placeholders
    html = html.replace('{% if add_message %}', '')
    html = html.replace('{{ add_message }}', '')
    html = html.replace('{{ add_message_type }}', '')
    html = html.replace('{% endif %}', '')

    return html

@app.route('/add', methods=['POST'])
def add_expense():
    """Add a new expense"""
    try:
        amount = float(request.form['amount'])
        if amount <= 0:
            return index_with_message("❌ Amount must be positive!", "error")

        category = request.form['category']
        if category not in CATEGORIES:
            return index_with_message("❌ Invalid category!", "error")

        description = request.form.get('description', 'No description').strip()
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d')).strip()

        expenses = load_expenses()
        expenses.append({
            'amount': round(amount, 2),
            'category': category,
            'description': description if description else 'No description',
            'date': date
        })
        save_expenses(expenses)

        return index_with_message(f"✅ Expense added: ${amount:.2f} for {category}", "success")

    except ValueError:
        return index_with_message("❌ Please enter a valid amount!", "error")
    except Exception as e:
        return index_with_message(f"❌ Error: {str(e)}", "error")

@app.route('/delete', methods=['POST'])
def delete_expense():
    """Delete an expense"""
    try:
        expense_id = int(request.form['expense_id'])
        expenses = load_expenses()

        if 0 <= expense_id < len(expenses):
            deleted = expenses.pop(expense_id)
            save_expenses(expenses)
            return index_with_message(f"🗑️ Deleted: ${deleted['amount']:.2f} for {deleted['category']}", "success")
        else:
            return index_with_message("❌ Invalid expense ID!", "error")
    except Exception as e:
        return index_with_message(f"❌ Error: {str(e)}", "error")

def index_with_message(message, message_type):
    """Render index with a message"""
    expenses = load_expenses()
    today = datetime.now().strftime('%Y-%m-%d')

    total_amount = sum(expense['amount'] for expense in expenses)
    total_expenses = len(expenses)

    html = HTML_TEMPLATE
    html = html.replace('{{ today }}', today)
    html = html.replace('{{ total_expenses }}', str(total_expenses))
    html = html.replace('{{ total_amount }}', f"{total_amount:.2f}")

    # Add message
    html = html.replace('{% if add_message %}', 'has_message')
    html = html.replace('{{ add_message }}', message)
    html = html.replace('{{ add_message_type }}', message_type)
    html = html.replace('{% endif %}', '')

    # Clean up other template tags
    html = clean_template_tags(html, expenses)

    return html

def clean_template_tags(html, expenses):
    """Clean up all template tags"""
    tags_to_clean = [
        '{% if not expenses %}', '{% else %}', '{% endif %}',
        '{% for expense in expenses %}', '{% endfor %}',
        '{{ expense.amount }}', '{{ expense.description }}',
        '{{ expense.date }}', '{{ expense.category }}',
        '{{ loop.index0 }}', '📭 No expenses recorded yet!',
        '{% for category, data in summary.items() %}',
        '{{ category }}', '{{ data.amount }}', '{{ data.percentage }}'
    ]

    for tag in tags_to_clean:
        html = html.replace(tag, '')

    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)