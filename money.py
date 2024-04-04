import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QWidget, QScrollArea, QLabel, QLineEdit, QPushButton, QHBoxLayout, QComboBox, QDialog, QMessageBox
import sqlite3
from PySide6.QtCore import Signal
###############################################
class BudgetEditWindow(QDialog):
    def __init__(self, budget_type, value, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit {budget_type} Budget")

        layout = QVBoxLayout()

        # Add input field for editing budget value
        self.value_input = QLineEdit(str(value))
        layout.addWidget(QLabel("Value:"))
        layout.addWidget(self.value_input)

        # Add a button to submit changes
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_changes)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def submit_changes(self):
        # Get the updated budget value
        updated_value = float(self.value_input.text())

        # Update the budget value in the database
        update_budget_value_in_database(updated_value, self.parent().budget_type)

        # Close the edit window
        self.accept()


def update_budget_value_in_database(updated_value, budget_type):
    # Connect to the SQLite database
    conn = sqlite3.connect('money.db')
    cursor = conn.cursor()

    # Execute the SQL command to update the budget value
    cursor.execute("UPDATE maximum SET value=? WHERE id=?", (updated_value, budget_type))

    # Commit the transaction
    conn.commit()

    # Close the cursor and the connection
    cursor.close()
    conn.close()


def edit_budget(item):
    row = item.row()
    budget_type = row + 1  # Budget types are indexed starting from 1 in the database
    value = float(table.item(row, 1).text())  # Assuming value is in the second column

    edit_window = BudgetEditWindow(get_budget_type_name(budget_type), value, parent=window)
    edit_window.exec()


def get_budget_type_name(budget_type):
    if budget_type == 1:
        return "Daily"
    elif budget_type == 2:
        return "Weekly"
    elif budget_type == 3:
        return "Monthly"
    else:
        return "Unknown"



###################################
def edit_expense(item):
    # Get the row index of the double-clicked item
    row = item.row()

    # Retrieve data from the double-clicked row
    expense_id = int(table.item(row, 0).text())
    date = table.item(row, 1).text()
    price = table.item(row, 2).text()
    category = table.item(row, 3).text()
    comments = table.item(row, 4).text()

    # Create a new window for editing the expense
    edit_window = EditExpenseWindow(expense_id, date, price, category, comments)
    edit_window.exec()

class EditExpenseWindow(QDialog):
    def __init__(self, expense_id, date, price, category, comments, parent=None):
        super().__init__(parent)
        self.expense_id = expense_id
        self.setWindowTitle("Edit Expense")

        layout = QVBoxLayout()

        # Add input fields for editing expense data
        self.date_input = QLineEdit(date)
        layout.addWidget(QLabel("Date:"))
        layout.addWidget(self.date_input)

        self.price_input = QLineEdit(price)
        layout.addWidget(QLabel("Price:"))
        layout.addWidget(self.price_input)

        # Add a combo box for selecting the category
        self.category_combo = QComboBox()
        layout.addWidget(QLabel("Category:"))
        layout.addWidget(self.category_combo)

        self.comments_input = QLineEdit(comments)
        layout.addWidget(QLabel("Comments:"))
        layout.addWidget(self.comments_input)

        # Add a button to submit changes
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submit_changes)
        layout.addWidget(submit_button)

        self.setLayout(layout)

        # Populate the category combo box
        self.populate_category_combo(category)

    def populate_category_combo(self, selected_category):
        conn = sqlite3.connect('money.db')
        cursor = conn.cursor()

        # Retrieve categories from the 'category' table
        cursor.execute("SELECT id, name FROM category")
        categories = cursor.fetchall()

        # Populate the category combo box
        for category_id, category_name in categories:
            self.category_combo.addItem(category_name, userData=category_id)

        # Set the selected category
        index = self.category_combo.findText(selected_category)
        if index != -1:
            self.category_combo.setCurrentIndex(index)

        # Close the cursor and the connection
        cursor.close()
        conn.close()

    def submit_changes(self):
        # Get the updated expense data
        updated_date = self.date_input.text()
        updated_price = self.price_input.text()
        updated_comments = self.comments_input.text()

        # Get the selected category ID from the combo box
        selected_category_id = self.category_combo.currentData()

        # Update the expense in the database
        update_expense_in_database(self.expense_id, updated_date, updated_price, selected_category_id, updated_comments)
        refresh_table(table)
        # Close the edit window
        self.accept()

def update_expense_in_database(expense_id, updated_date, updated_price, updated_category_id, updated_comments):
    # Connect to the SQLite database
    conn = sqlite3.connect('money.db')
    cursor = conn.cursor()

    # Execute the SQL command to update the expense record in the 'expense' table
    cursor.execute("UPDATE expense SET date=?, price=?, category_id=?, comments=? WHERE id=?", 
                   (updated_date, updated_price, updated_category_id, updated_comments, expense_id))

    # Commit the transaction
    conn.commit()

    # Close the cursor and the connection
    cursor.close()
    conn.close()
    






class AddCategoryDialog(QDialog):

    categoryAdded = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Category")

        layout = QVBoxLayout()

        self.category_name_input = QLineEdit()
        layout.addWidget(QLabel("Category Name:"))
        layout.addWidget(self.category_name_input)

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_category)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def add_category(self):
        category_name = self.category_name_input.text().strip()
        conn = sqlite3.connect('money.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM category")
        existing_categories = {row[0] for row in cursor.fetchall()}
        conn.close()
        if category_name:
            # Check if the category already exists
            if category_name in existing_categories:
                QMessageBox.warning(self, "Warning", "Category already exists.")
            else:
                # Add the category to the database
                add_category_to_database(category_name)
                QMessageBox.information(self, "Success", "Category added successfully.")
                self.categoryAdded.emit()
                refresh_add_expense(category_combo)
                self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Category name cannot be empty.")

def add_category_to_database(category_name):
    conn = sqlite3.connect('money.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO category (name) VALUES (?)", (category_name,))
    conn.commit()
    conn.close()

    # Update existing_categories list after adding a new category
    update_existing_categories()

def update_existing_categories():
    global existing_categories
    conn = sqlite3.connect('money.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM category")
    existing_categories = {row[0] for row in cursor.fetchall()}
    conn.close()


def main():
    global window
    # Connect to the SQLite database
    conn = sqlite3.connect('money.db')
    cursor = conn.cursor()
    
    # Retrieve data from the 'category' table
    cursor.execute("SELECT name FROM category")
    category_rows = cursor.fetchall()
    cursor.execute("SELECT name FROM category")
    existing_categories = {row[0] for row in cursor.fetchall()}

    # Retrieve data from the 'expense' table
    cursor.execute("SELECT expense.id, expense.date, expense.price, category.name, expense.comments FROM expense INNER JOIN category ON expense.category_id = category.id")
    expense_rows = cursor.fetchall()
    cursor.execute("SELECT maximum.value from maximum")
    budget_rows=cursor.fetchall()
    # Close the cursor and the connection
    cursor.close()
    conn.close()
    
    # Create the application object
    app = QApplication(sys.argv)

    # Create the main window
    window = QMainWindow()
    window.setWindowTitle("The bookeeper App")

    # Create a widget to contain the table and add a layout to it
    table_widget = QWidget()
    table_layout = QVBoxLayout(table_widget)

    # Create a table widget
    global table
    table = QTableWidget()

    # Set the row and column count for the table
    table.setRowCount(len(expense_rows))
    table.setColumnCount(len(expense_rows[0]))  # Assuming all rows have the same number of columns

    # Set headers for the table columns in Russian
    headers = ["ID","Date", "Expense", "Category", "Comment"]
    table.setHorizontalHeaderLabels(headers)
    table.hideColumn(0)
    # Populate the table with data
    for row_idx, row_data in enumerate(expense_rows):
        for col_idx, col_data in enumerate(row_data):  # Skip the first column (ID)
            item = QTableWidgetItem(str(col_data))
            table.setItem(row_idx, col_idx, item)

    # Set the table width to take 100% of the window's width
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.itemDoubleClicked.connect(edit_expense)
######################################################
    global day_sum_label#, week_sum_label, month_sum_label
    day_sum_label = QLabel("Total: $4.00")
    conn = sqlite3.connect('money.db')
    cursor = conn.cursor()

    # Calculate the daily expense
    cursor.execute("SELECT SUM(price) FROM expense WHERE date = date('now')")
    daily_expense = cursor.fetchone()[0] or 0.0  # If no expense for today, set daily expense to 0.0

    # Close the cursor and the connection
    cursor.close()
    conn.close()

    # Update the day_sum_label text with the calculated daily expense
    day_sum_label.setText(f"Total: {daily_expense:.2f}")

    # Add labels to the layout
    table_layout.addWidget(day_sum_label)

    # Create a widget to contain the budget table and add a layout to it
    budget_widget = QWidget()
    budget_layout = QVBoxLayout(budget_widget)

    # Create a budget table widget
    global budget_table
    budget_table = QTableWidget()

    # Set the row and column count for the budget table
    budget_table.setRowCount(len(budget_rows))
    budget_table.setColumnCount(len(budget_rows[0]))  # Assuming all rows have the same number of columns

    # Set headers for the budget table columns
    budget_headers = ["Daily Budget", "Weekly Budget", "Monthly Budget"]
    budget_table.setFixedHeight(92)  # Adjust height as needed
    budget_table.setFixedWidth(200)   # Adjust width as needed
    budget_table.setVerticalHeaderLabels(budget_headers)
    budget_table.horizontalHeader().setVisible(False)
    # Populate the budget table with data
    for row_idx, row_data in enumerate(budget_rows):
        for col_idx, col_data in enumerate(row_data):
            item = QTableWidgetItem(str(col_data))
            budget_table.setItem(row_idx, col_idx, item)
    budget_table.itemChanged.connect(update_budget)
    
    # Add the budget table to the layout
    budget_layout.addWidget(budget_table)
    budget_widget.setLayout(budget_layout)
    interval_combo = QComboBox()
    interval_combo.addItems(["Daily", "Weekly", "Monthly"])
    interval_combo.currentIndexChanged.connect(lambda: update_expense_display(interval_combo.currentText(), existing_categories))
    #interval_combo.setFixedWidth(100)
    # Add interval selection widget to the layout
    table_layout.addWidget(interval_combo)
    # Add the budget widget to the main layout
    table_layout.addWidget(budget_widget)

    # Create widgets for selecting time interval

    ########################################################
    # Add the table to the layout
    table_layout.addWidget(table)

    # Create widgets for adding expense
    add_expense_layout = QHBoxLayout()
    price_label = QLabel("Price:")
    price_input = QLineEdit()
    add_expense_layout.addWidget(price_label)
    add_expense_layout.addWidget(price_input)

    comments_label = QLabel("Comments:")
    comments_input = QLineEdit()
    add_expense_layout.addWidget(comments_label)
    add_expense_layout.addWidget(comments_input)

    category_label = QLabel("Category:")
    global category_combo
    category_combo = QComboBox()
    for category in category_rows:
        category_combo.addItem(category[0])
    add_expense_layout.addWidget(category_label)
    add_expense_layout.addWidget(category_combo)

    add_expense_button = QPushButton("Add Expense")
    add_expense_button.clicked.connect(lambda: add_expense(price_input.text(), comments_input.text(), category_combo.currentText(), table))
    add_expense_layout.addWidget(add_expense_button)

    # Add expense layout to the main layout
    table_layout.addLayout(add_expense_layout)

    # Create a button to add category
    add_category_button = QPushButton("Add Category")
    add_category_button.clicked.connect(show_add_category_dialog)
    table_layout.addWidget(add_category_button)

    # Create a scroll area and set the table widget as its widget
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(table_widget)

    # Set the scroll area as the central widget of the main window
    window.setCentralWidget(scroll_area)

    # Show the main window
    window.show()

    # Start the event loop
    sys.exit(app.exec())


def update_budget(item):
    # Get the new value from the QTableWidgetItem
    new_value = item.text()
    # Get the row and column indices of the clicked cell
    row = item.row()
    col = item.column()
    # Map column index to budget type ID
    if row == 0:
        budget_type_id = 1  # Daily budget
    elif row == 1:
        budget_type_id = 2  # Weekly budget
    elif row == 2:
        budget_type_id = 3  # Monthly budget
    else:
        return  # Ignore other columns
    # Update the database with the new budget value
    conn = sqlite3.connect('money.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE maximum SET value = ? WHERE id = ?", (new_value, budget_type_id))
    conn.commit()
    conn.close()


def update_expense_display(interval, existing_categories):
    global table
    global category_combo
    global day_sum_label
    global week_sum_label
    global month_sum_label

    # Connect to the SQLite database
    conn = sqlite3.connect('money.db')
    cursor = conn.cursor()

    # Determine the time interval for querying expenses
    if interval == "Daily":
        query = "SELECT expense.id, expense.date, expense.price, category.name, expense.comments FROM expense INNER JOIN category ON expense.category_id = category.id WHERE expense.date = date('now')"
    elif interval == "Weekly":
        query = "SELECT expense.id, expense.date, expense.price, category.name, expense.comments FROM expense INNER JOIN category ON expense.category_id = category.id WHERE strftime('%W', expense.date) = strftime('%W', 'now')"
    elif interval == "Monthly":
        query = "SELECT expense.id, expense.date, expense.price, category.name, expense.comments FROM expense INNER JOIN category ON expense.category_id = category.id WHERE strftime('%Y-%m', expense.date) = strftime('%Y-%m', 'now')"

    # Execute the query
    cursor.execute(query)

    # Fetch the results
    expense_rows = cursor.fetchall()

    # Calculate total expenses for the day, week, and month
    day_sum = sum(float(row[2]) for row in expense_rows)
    # week_sum = day_sum
    # month_sum = day_sum

    # Close the cursor and the connection
    cursor.close()
    conn.close()

    # Update labels to display total expenses
    day_sum_label.setText(f"Total: {day_sum:.2f}")
    # week_sum_label.setText(f"Week's Total: ${week_sum:.2f}")
    # month_sum_label.setText(f"Month's Total: ${month_sum:.2f}")

    # Clear the table
    table.clearContents()

    # Populate the table with updated data
    table.setRowCount(len(expense_rows))
    for row_idx, row_data in enumerate(expense_rows):
        for col_idx, col_data in enumerate(row_data):
            item = QTableWidgetItem(str(col_data))
            table.setItem(row_idx, col_idx, item)

    # Clear and re-populate the category combo box
    category_combo.clear()
    for category in existing_categories:
        category_combo.addItem(category)








def show_add_category_dialog():
    dialog = AddCategoryDialog()
    dialog.exec()

def add_expense(price, comments, category,table):
    # Connect to the SQLite database
    conn = sqlite3.connect('money.db')
    cursor = conn.cursor()

    # Retrieve category_id for the selected category
    cursor.execute("SELECT id FROM category WHERE name=?", (category,))
    category_id = cursor.fetchone()[0]

    # Insert the new expense into the database
    cursor.execute("INSERT INTO expense (date, price, category_id, comments) VALUES (date('now'), ?, ?, ?)", (price, category_id, comments))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    # Refresh the table with updated data
    refresh_table(table)

def refresh_add_expense(category_combo):
    # # Connect to the SQLite database
    # conn = sqlite3.connect('money.db')
    # cursor = conn.cursor()

    # # Retrieve data from the 'expense' table
    # cursor.execute("SELECT expense.date, expense.price, category.name, expense.comments FROM expense INNER JOIN category ON expense.category_id = category.id")
    # expense_rows = cursor.fetchall()

    # # Close the cursor and the connection
    # cursor.close()
    # conn.close()

    # # Clear the table
    # table.setRowCount(0)

    # # Populate the table with updated data
    # for row_data in expense_rows:
    #     row_position = table.rowCount()
    #     table.insertRow(row_position)
    #     for col_idx, col_data in enumerate(row_data[1:]):  # Skip the first column (ID)
    #         item = QTableWidgetItem(str(col_data))
    #         table.setItem(row_position, col_idx, item)

    # Clear and re-populate the category combo box
    category_combo.clear()
    for category in existing_categories:
        category_combo.addItem(category)



def refresh_table(table):
    # Connect to the SQLite database
    conn = sqlite3.connect('money.db')
    cursor = conn.cursor()

    # Retrieve data from the 'expense' table
    cursor.execute("SELECT expense.id, expense.date, expense.price, category.name, expense.comments FROM expense INNER JOIN category ON expense.category_id = category.id")
    expense_rows = cursor.fetchall()

    # Close the cursor and the connection
    cursor.close()
    conn.close()

    # Clear the table
    table.setRowCount(0)

    # Populate the table with updated data
    for row_data in expense_rows:
        row_position = table.rowCount()
        table.insertRow(row_position)
        for col_idx, col_data in enumerate(row_data):  # Skip the first column (ID)
            item = QTableWidgetItem(str(col_data))
            table.setItem(row_position, col_idx, item)
if __name__ == "__main__":
    
    main()
