import json
import os
from datetime import datetime

# Simple Expense Tracker Application
# The file where we will store the expense data
DATA_FILE = "expenses.json"

def load_data():
    """Loads expenses from the JSON file. Returns a list."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        return []

def save_data(expenses):
    """Saves the current list of expenses to the JSON file."""
    try:
        with open(DATA_FILE, 'w') as file:
            json.dump(expenses, file, indent=4)
        print("Data saved successfully.")
    except IOError as e:
        print(f"Error saving data: {e}")

def add_expense(expenses):
    """Prompts user for details and adds a new expense."""
    print("\n--- Add New Expense ---")
    try:
        amount = float(input("Enter amount: "))
        category = input("Enter category (e.g., Food, Travel, Rent): ").strip()
        description = input("Enter description: ").strip()
        
        # Get current date in YYYY-MM-DD format
        date = datetime.now().strftime("%Y-%m-%d")

        expense = {
            "amount": amount,
            "category": category,
            "description": description,
            "date": date
        }
        
        expenses.append(expense)
        save_data(expenses)
        print("Expense added!")
    except ValueError:
        print("Invalid input! Amount must be a number.")

def view_expenses(expenses):
    """Displays all stored expenses in a readable format."""
    print("\n--- Your Expenses ---")
    if not expenses:
        print("No expenses recorded yet.")
        return

    # Print header
    print(f"{'Date':<12} | {'Category':<15} | {'Amount':<10} | {'Description'}")
    print("-" * 60)

    for item in expenses:
        print(f"{item['date']:<12} | {item['category']:<15} | ${item['amount']:<9.2f} | {item['description']}")

def show_summary(expenses):
    """Calculates and shows total spending."""
    total = sum(item['amount'] for item in expenses)
    print(f"\nTotal Expenses: ${total:.2f}")
    
    # Optional: Breakdown by category
    print("\n--- Category Breakdown ---")
    breakdown = {}
    for item in expenses:
        cat = item['category']
        breakdown[cat] = breakdown.get(cat, 0) + item['amount']
    
    for cat, amt in breakdown.items():
        print(f"{cat}: ${amt:.2f}")

def delete_expense(expenses):
    """Deletes an expense by index."""
    print("\n--- Delete Expense ---")
    if not expenses:
        print("No expenses to delete.")
        return
    
    view_expenses(expenses)
    try:
        index = int(input("\nEnter the expense number to delete (1-based): ")) - 1
        if 0 <= index < len(expenses):
            deleted = expenses.pop(index)
            save_data(expenses)
            print(f"Deleted: {deleted['description']} (${deleted['amount']:.2f})")
        else:
            print("Invalid expense number.")
    except ValueError:
        print("Invalid input! Please enter a number.")

def edit_expense(expenses):
    """Edits an existing expense."""
    print("\n--- Edit Expense ---")
    if not expenses:
        print("No expenses to edit.")
        return
    
    view_expenses(expenses)
    try:
        index = int(input("\nEnter the expense number to edit (1-based): ")) - 1
        if 0 <= index < len(expenses):
            expense = expenses[index]
            print(f"\nCurrent: {expense['description']} - ${expense['amount']:.2f} ({expense['category']})")
            
            amount = input(f"New amount (press Enter to keep ${expense['amount']:.2f}): ").strip()
            category = input(f"New category (press Enter to keep '{expense['category']}'): ").strip()
            description = input(f"New description (press Enter to keep '{expense['description']}'): ").strip()
            
            if amount:
                expense['amount'] = float(amount)
            if category:
                expense['category'] = category
            if description:
                expense['description'] = description
            
            save_data(expenses)
            print("Expense updated!")
        else:
            print("Invalid expense number.")
    except ValueError:
        print("Invalid input!")

def filter_by_category(expenses):
    """Filters and displays expenses by category."""
    print("\n--- Filter by Category ---")
    if not expenses:
        print("No expenses recorded yet.")
        return
    
    category = input("Enter category to filter: ").strip()
    filtered = [exp for exp in expenses if exp['category'].lower() == category.lower()]
    
    if not filtered:
        print(f"No expenses found in category '{category}'.")
        return
    
    print(f"\n--- Expenses in '{category}' ---")
    print(f"{'Date':<12} | {'Amount':<10} | {'Description'}")
    print("-" * 45)
    
    total = 0
    for item in filtered:
        print(f"{item['date']:<12} | ${item['amount']:<9.2f} | {item['description']}")
        total += item['amount']
    
    print(f"\nTotal for {category}: ${total:.2f}")

def filter_by_date_range(expenses):
    """Filters expenses by date range."""
    print("\n--- Filter by Date Range ---")
    if not expenses:
        print("No expenses recorded yet.")
        return
    
    try:
        start_date = input("Enter start date (YYYY-MM-DD): ").strip()
        end_date = input("Enter end date (YYYY-MM-DD): ").strip()
        
        filtered = [exp for exp in expenses if start_date <= exp['date'] <= end_date]
        
        if not filtered:
            print("No expenses found in this date range.")
            return
        
        print(f"\n--- Expenses from {start_date} to {end_date} ---")
        print(f"{'Date':<12} | {'Category':<15} | {'Amount':<10} | {'Description'}")
        print("-" * 60)
        
        total = 0
        for item in filtered:
            print(f"{item['date']:<12} | {item['category']:<15} | ${item['amount']:<9.2f} | {item['description']}")
            total += item['amount']
        
        print(f"\nTotal for period: ${total:.2f}")
    except Exception as e:
        print(f"Error: {e}")

def export_to_csv(expenses):
    """Exports expenses to a CSV file."""
    print("\n--- Export to CSV ---")
    if not expenses:
        print("No expenses to export.")
        return
    
    filename = f"expenses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        with open(filename, 'w') as file:
            file.write("Date,Category,Amount,Description\n")
            for exp in expenses:
                file.write(f"{exp['date']},{exp['category']},{exp['amount']},\"{exp['description']}\"\n")
        print(f"Expenses exported to {filename}")
    except IOError as e:
        print(f"Error exporting data: {e}")

def monthly_report(expenses):
    """Shows expenses grouped by month."""
    print("\n--- Monthly Report ---")
    if not expenses:
        print("No expenses recorded yet.")
        return
    
    monthly = {}
    for exp in expenses:
        month = exp['date'][:7]  # YYYY-MM
        if month not in monthly:
            monthly[month] = []
        monthly[month].append(exp)
    
    for month in sorted(monthly.keys(), reverse=True):
        total = sum(exp['amount'] for exp in monthly[month])
        print(f"\n{month}: ${total:.2f} ({len(monthly[month])} expenses)")
        
        # Category breakdown
        breakdown = {}
        for exp in monthly[month]:
            cat = exp['category']
            breakdown[cat] = breakdown.get(cat, 0) + exp['amount']
        
        for cat, amt in breakdown.items():
            print(f"  - {cat}: ${amt:.2f}")

def set_budget(expenses):
    """Set and track monthly budget."""
    print("\n--- Budget Tracker ---")
    try:
        budget = float(input("Enter your monthly budget: $"))
        current_month = datetime.now().strftime("%Y-%m")
        
        month_expenses = [exp for exp in expenses if exp['date'].startswith(current_month)]
        spent = sum(exp['amount'] for exp in month_expenses)
        
        remaining = budget - spent
        percentage = (spent / budget * 100) if budget > 0 else 0
        
        print(f"\nBudget: ${budget:.2f}")
        print(f"Spent: ${spent:.2f} ({percentage:.1f}%)")
        print(f"Remaining: ${remaining:.2f}")
        
        if remaining < 0:
            print("⚠️  WARNING: You've exceeded your budget!")
        elif percentage > 80:
            print("⚠️  WARNING: You've used more than 80% of your budget!")
    except ValueError:
        print("Invalid budget amount.")

def main():
    """Main program loop."""
    expenses = load_data()
    
    while True:
        print("\n=== EXPENSE TRACKER MENU ===")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Show Summary")
        print("4. Delete Expense")
        print("5. Edit Expense")
        print("6. Filter by Category")
        print("7. Filter by Date Range")
        print("8. Monthly Report")
        print("9. Budget Tracker")
        print("10. Export to CSV")
        print("11. Exit")
        
        choice = input("Choose an option (1-11): ")

        if choice == '1':
            add_expense(expenses)
        elif choice == '2':
            view_expenses(expenses)
        elif choice == '3':
            show_summary(expenses)
        elif choice == '4':
            delete_expense(expenses)
        elif choice == '5':
            edit_expense(expenses)
        elif choice == '6':
            filter_by_category(expenses)
        elif choice == '7':
            filter_by_date_range(expenses)
        elif choice == '8':
            monthly_report(expenses)
        elif choice == '9':
            set_budget(expenses)
        elif choice == '10':
            export_to_csv(expenses)
        elif choice == '11':
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()