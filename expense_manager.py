import csv
from datetime import datetime
import json

from expense import Expense

CATEGORY_KEYWORDS = {

    "Food": ["pizza", "burger","samosa","dosa","coffee","tea"],
    "Travel": ["uber","ola","bus","metro","flight"],
    "Entertainment": ["movie","netflix","game"],
    "Shopping": ["shirt","shoes","amazon"]
}

class ExpenseManager:
    def __init__(self):
        self.expenses=[]
        self.load_expenses()


    def add_expense(self):
        title = input("Enter expense name: ")

        try:
            amount = float(input("Enter amount: "))
        except ValueError:
            print("Invalid amount")
            return

        category = ExpenseManager.detect_category(title)
        expense = Expense(title,amount,category)
        self.expenses.append(expense)
        self.save_expenses()

    def view_expenses(self):
        if not self.expenses:
            print("No expenses found")
            return

        print("\n Expenses list:")

        for expense in self.expenses:
            print(expense)

    def show_total(self):
        total = sum( expense.get_amount() for expense in self.expenses)
        print(f" \n Total expenses: {total:.2f}")

    def save_expenses(self):

        with open('data.json', 'w') as file:
            expense_data =[expense.to_dict() for expense in self.expenses]
            json.dump(expense_data, file, indent=4)

    def load_expenses(self):
        try:
            with open('data.json', 'r') as file:
                expense_data = json.load(file)
                for expense in expense_data:
                    expense = Expense(expense["title"],expense["amount"],expense["category"],expense["date"])
                    self.expenses.append(expense)
        except (FileNotFoundError,json.JSONDecodeError):
            print("No expenses found")
            return []

    @staticmethod
    def detect_category(title):
        title_l=title.lower()
        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in title_l:
                    return category
        return "Others"

    def category_wise_expenses(self):
        category_report = {}

        for expense in self.expenses:
            category_report[expense.get_category()]=category_report.get(expense.get_category(),0) + expense.get_amount()

        print("\n ==== Category wise expenses ====")
        for cat, total in category_report.items():
            print(f"{cat:<15}: {total:.2f}") # {category:<15} left-align text keep width 15

    def date_wise_expenses(self):
        date_report = {}
        for expense in self.expenses:
            d=expense.get_date().split(" ")[0]
            date_report[d]=date_report.get(d,0)+expense.get_amount()

        print("\n ====== Date wise expenses =====")
        for date, total in date_report.items():
            day_name=datetime.strptime(date,"%Y-%m-%d").strftime("%A")
            print(f"{date} ({day_name}): {total:.2f}")

    def delete_expense(self):
        if not self.expenses:
            print("No expenses found")
            return

        print("\n ==== Expense ====")

        for index, expense in enumerate(self.expenses, start=1):
            print(f"{index:}. {expense}")

        try:
            choice = int(input("\n Enter choice: "))

            if choice < 1 or choice > len(self.expenses):
                print("Invalid expense number")
                return

            deleted_expense = self.expenses.pop(choice-1)
            self.save_expenses()
            print(f"\nDeleted: {deleted_expense}")

        except ValueError:
            print("Please enter a valid number")
            return

    def monthly_expenses(self):
        if not self.expenses:
            print("No expenses found")
            return

        monthly_report = {}

        for expense in self.expenses:
            date_string=expense.get_date().split(" ")[0]
            date_object=datetime.strptime(date_string,"%Y-%m-%d")
            month_name=date_object.strftime("%B")
            year_name=date_object.strftime("%Y")
            month_year=year_name+":"+month_name
            monthly_report[month_year]=monthly_report.get(month_year,0)+expense.get_amount()

        print("\n ==== Monthly expense ====")
        for month_year, total in monthly_report.items():
            print(f"{month_year:<15}: {total:.2f}")

    def search_expense(self,keyword):
        found_list=[]
        if not self.expenses:
            print("No expenses found")
            return

        if keyword.strip() =="":
            print("Please enter a valid keyword")
            return

        for expense in self.expenses:
            if keyword.lower() in expense.get_title().lower():
                found_list.append(expense)
        print("\n ==== Below are the Expenses with your search keywords ====")
        for index, expense in enumerate(found_list, start=1):
            print(f"{index}: {expense}")

    def edit_expense(self):
        if not self.expenses:
            print("No expenses found")
            return

        print("\n ==== Expense ====")

        for index, expense in enumerate(self.expenses, start=1):
            print(f"{index:}. {expense}")

        try:
            choice = int(input("\n Enter expense number which you want to edit: "))

            if choice < 1 or choice > len(self.expenses):
                print("Invalid expense number")
                return

            expense = self.expenses[choice - 1]
            print("\nLeave blank to keep old value\n")
            new_title = input(
                f"Enter new title "
                f"({expense.get_title()}): "
            )
            new_amount = input(
                f"Enter new amount "
                f"({expense.get_amount()}): "
            )
            if new_title.strip():
                expense.title = new_title
                expense.category = (self.detect_category(new_title))

            if new_amount.strip():
                expense.expense_amount = (float(new_amount))

            self.save_expenses()
            print("\nExpense updated successfully!")

        except ValueError:
            print("Please enter a valid number")

    def top_spending_category(self):
        if not self.expenses:
            print("No expenses found")
            return

        category_list={}
        for expense in self.expenses:
            category_list[expense.get_category()] =category_list.get(expense.get_category(),0)+expense.get_amount()

        top_category =max(category_list, key=category_list.get) # This is not python error
        top_amount =category_list[top_category]

        print("\n===== Top Spending Category =====\n")

        print(f"{top_category} : ₹{top_amount:.2f}")

    def export_csv_report(self):
        if not self.expenses:
            print("No expenses found")
            return

        with open("expense_report.csv","w",newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Amount", "Category", "Date"])
            for expense in self.expenses:
                writer.writerow([expense.get_title(), expense.get_amount(), expense.get_category(), expense.get_date()])

            print("\n==== CSV report created successfully! ====")

    def pie_chart_visualization(self):
        if not self.expenses:
            print("No expenses found")
            return

        import matplotlib.pyplot as plt

        category_total={}
        for expense in self.expenses:
            category_total[expense.get_category()]=category_total.get(expense.get_category(),0) + expense.get_amount()

        labels = category_total.keys()

        amounts = category_total.values()

        plt.pie(amounts,labels=labels,autopct="%1.1f%%")

        plt.savefig("expense_chart.png")

        plt.show()





















































