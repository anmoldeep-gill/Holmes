import csv
import os

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

# Menu-driven interface
def menu():
    while True:
        print("Expense Tracker Menu:")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. View Summary by Category")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            add_expense()
        elif choice == '2':
            view_expenses()
        elif choice == '3':
            summary_by_category()
        elif choice == '4':
            print("Exiting Expense Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.\n")

# Run the menu
# Uncomment the line below when running locally.
#menu()
if __name__ == "__menu__":
    menu()