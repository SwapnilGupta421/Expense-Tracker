from expense_manager import ExpenseManager

def main():
    manager = ExpenseManager()

    while True:

        print("\n===== Expense Tracker =====")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Show Total Expenses")
        print("4. Category wise expenses")
        print("5. Date wise expenses")
        print("6. Delete expense")
        print("7. Month wise expenses")
        print("8. Search expense")
        print("9. Edit Expense")
        print("10. Top Spending Category")
        print("11. Pie Chart Visualization")
        print("12. Export CSV Report")
        print("13. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            manager.add_expense()

        elif choice == "2":
            manager.view_expenses()

        elif choice == "3":
            manager.show_total()

        elif choice == "4":
            manager.category_wise_expenses()

        elif choice == "5":
            manager.date_wise_expenses()

        elif choice == "6":
            manager.delete_expense()

        elif choice == "7":
            manager.monthly_expenses()

        elif choice == "8":
            search_keyword=input("Enter your search keyword: ")
            manager.search_expense(search_keyword)
        elif choice == "9":
            manager.edit_expense()

        elif choice == "10":
            manager.top_spending_category()

        elif choice == "11":
            manager.pie_chart_visualization()

        elif choice == "12":
            manager.export_csv_report()

        elif choice == "13":
            print("Thank you for using this program. See you next time!")
            break
        else:
            print("Please enter a valid choice.")

if __name__ == "__main__":
    main()






