from datetime import datetime
class Expense:
    def __init__(self, title,amount,category='Others',created_at=None):
        self.title=title
        self.expense_amount=amount
        self.category=category
        if created_at:
            self._created_at = created_at
        else:
            self._created_at = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

    def get_title(self):
        return self.title

    def get_amount(self):
        return self.expense_amount

    def get_date(self):
        return self._created_at

    def get_item(self):
        return self.title, self.expense_amount

    def get_category(self):
        return self.category

    def __str__(self):
        return f"Title: {self.title}, Amount: {self.expense_amount}, Date: {self._created_at}, Category: {self.category}"

    def to_dict(self):
        return {"title":self.title, "amount":self.expense_amount, "date":self._created_at, "category":self.category}

