import csv
import os
from datetime import datetime

# File name for storing expenses
file_name = "expenses.csv"

# Ensure the CSV file exists with headers
if not os.path.exists(file_name):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Category", "Amount", "Description"])

# Function to add an expense
def add_expense():
    date = input("Enter date (YYYY-MM-DD): ")
    category = input("Enter category (e.g., Food, Transport): ")
    amount = input("Enter amount: ")
    description = input("Enter description: ")
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, category, amount, description])
    print("Expense added successfully!\n")

# Function to view all expenses
def view_expenses():
    print("\nAll Expenses:")
    with open(file_name, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            print(", ".join(row))
    print("\n")

# Function to display summary by category
def summary_by_category():
    category_totals = {}
    with open(file_name, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            category = row["Category"]
            amount = float(row["Amount"])
            category_totals[category] = category_totals.get(category, 0) + amount

    print("\nExpense Summary by Category:")
    for category, total in category_totals.items():
        print(f"{category}: ${total:.2f}")
    print("\n")

# Function to delete an expense
def delete_expense():
    view_expenses()
    try:
        row_num = int(input("Enter row number to delete (1 for first expense, 2 for second, etc.): "))
        rows = []
        with open(file_name, mode='r') as file:
            reader = csv.reader(file)
            rows = list(reader)
        
        if row_num < 1 or row_num >= len(rows):
            print("Invalid row number!\n")
            return
        
        deleted_row = rows.pop(row_num)
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        print(f"Deleted expense: {', '.join(deleted_row)}\n")
    except ValueError:
        print("Invalid input!\n")

# Function to search expenses by category
def search_by_category():
    category = input("Enter category to search: ")
    print(f"\nExpenses in '{category}' category:")
    found = False
    with open(file_name, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Category"].lower() == category.lower():
                print(f"{row['Date']}, {row['Category']}, ${row['Amount']}, {row['Description']}")
                found = True
    if not found:
        print(f"No expenses found in '{category}' category.")
    print("\n")

# Function to search expenses by date range
def search_by_date_range():
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")
    print(f"\nExpenses from {start_date} to {end_date}:")
    total = 0
    found = False
    with open(file_name, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if start_date <= row["Date"] <= end_date:
                print(f"{row['Date']}, {row['Category']}, ${row['Amount']}, {row['Description']}")
                total += float(row["Amount"])
                found = True
    if found:
        print(f"Total for this period: ${total:.2f}")
    else:
        print("No expenses found in this date range.")
    print("\n")

# Function to get total expenses
def total_expenses():
    total = 0
    with open(file_name, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            total += float(row["Amount"])
    print(f"\nTotal Expenses: ${total:.2f}\n")

# Function to get monthly summary
def monthly_summary():
    month = input("Enter month (YYYY-MM): ")
    monthly_total = 0
    category_totals = {}
    
    with open(file_name, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Date"].startswith(month):
                amount = float(row["Amount"])
                monthly_total += amount
                category = row["Category"]
                category_totals[category] = category_totals.get(category, 0) + amount
    
    print(f"\nSummary for {month}:")
    print(f"Total: ${monthly_total:.2f}")
    if category_totals:
        print("\nBreakdown by category:")
        for category, total in category_totals.items():
            print(f"  {category}: ${total:.2f}")
    else:
        print("No expenses found for this month.")
    print("\n")

# Function to export expenses to a report
def export_report():
    report_name = f"expense_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_name, 'w') as report:
        report.write("EXPENSE REPORT\n")
        report.write("=" * 50 + "\n\n")
        
        # Total expenses
        total = 0
        with open(file_name, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                total += float(row["Amount"])
        report.write(f"Total Expenses: ${total:.2f}\n\n")
        
        # Category summary
        category_totals = {}
        with open(file_name, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category = row["Category"]
                amount = float(row["Amount"])
                category_totals[category] = category_totals.get(category, 0) + amount
        
        report.write("Summary by Category:\n")
        for category, cat_total in category_totals.items():
            report.write(f"  {category}: ${cat_total:.2f}\n")
        
        report.write("\n" + "=" * 50 + "\n\n")
        
        # All expenses
        report.write("All Expenses:\n")
        with open(file_name, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                report.write(", ".join(row) + "\n")
    
    print(f"Report exported to {report_name}\n")

# Menu-driven interface
def menu():
    while True:
        print("Expense Tracker Menu:")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. View Summary by Category")
        print("4. Delete Expense")
        print("5. Search by Category")
        print("6. Search by Date Range")
        print("7. View Total Expenses")
        print("8. Monthly Summary")
        print("9. Export Report")
        print("10. Exit")
        choice = input("Enter your choice (1-10): ")

        if choice == '1':
            add_expense()
        elif choice == '2':
            view_expenses()
        elif choice == '3':
            summary_by_category()
        elif choice == '4':
            delete_expense()
        elif choice == '5':
            search_by_category()
        elif choice == '6':
            search_by_date_range()
        elif choice == '7':
            total_expenses()
        elif choice == '8':
            monthly_summary()
        elif choice == '9':
            export_report()
        elif choice == '10':
            print("Exiting Expense Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.\n")

# Run the menu
# Uncomment the line below when running locally.
#menu()
if __name__ == "__main__":
    menu()