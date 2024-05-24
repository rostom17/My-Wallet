import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import os
from tkcalendar import DateEntry

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("My Wallet")
        self.root.geometry("1600x1200")

        self.filename = "expenses.csv"
        self.load_expenses()

        self.selected_item = None

        self.setup_gui()

    def setup_gui(self):
        tk.Label(self.root, text="Date").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Category").grid(row=1, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Amount").grid(row=2, column=0, padx=10, pady=10)
        tk.Label(self.root, text="Description").grid(row=3, column=0, padx=10, pady=10)

        self.date_entry = DateEntry(self.root, date_pattern='yyyy-mm-dd')
        self.category_entry = ttk.Combobox(self.root, values=["Food","Rent","Supplies","Transport", "Utilities", "Entertainment","Education " ,"Other"])
        self.amount_entry = tk.Entry(self.root)
        self.description_entry = tk.Entry(self.root)

        self.date_entry.grid(row=0, column=1, padx=10, pady=10)
        self.category_entry.grid(row=1, column=1, padx=10, pady=10)
        self.amount_entry.grid(row=2, column=1, padx=10, pady=10)
        self.description_entry.grid(row=3, column=1, padx=10, pady=10)

        
        tk.Button(self.root, text="Add Expense", command=self.add_expense).grid(row=4, column=0, columnspan=2, pady=10)
        tk.Button(self.root, text="Update Expense", command=self.update_expense).grid(row=5, column=0, columnspan=2, pady=10)
        tk.Button(self.root, text="Delete Expense", command=self.delete_expense).grid(row=6, column=0, columnspan=2, pady=10)
        tk.Button(self.root, text="View Expenses", command=self.view_expenses).grid(row=7, column=0, columnspan=2, pady=10)
        tk.Button(self.root, text="Summary", command=self.show_summary).grid(row=8, column=0, columnspan=2, pady=10)

        
        self.tree = ttk.Treeview(self.root, columns=("Sl No","Date", "Category", "Amount", "Description"), show='headings')
        self.tree.heading("Sl No", text="Sl No")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Description", text="Description")
        self.tree.grid(row=0, column=2, rowspan=9, padx=10, pady=10)
        self.tree.bind("<ButtonRelease-1>", self.select_item)

    def load_expenses(self):
        if os.path.exists(self.filename):
            self.expenses = pd.read_csv(self.filename)
        else:
            self.expenses = pd.DataFrame(columns=["Sl No","Date", "Category", "Amount", "Description"])

    def save_expenses(self):
        self.expenses.to_csv(self.filename, index=False)

    def add_expense(self):
        date = self.date_entry.get()
        category = self.category_entry.get()
        amount = self.amount_entry.get()
        description = self.description_entry.get()

        print(f"Debug: date={date}, category={category}, amount={amount}, description={description}")

        if date and category and amount and description:
            try:
                amount = float(amount)
                print(f"Debug: Converted amount={amount}")
                new_expense = pd.DataFrame([{"Date": date, "Category": category, "Amount": amount, "Description": description}])
                self.expenses = pd.concat([self.expenses, new_expense], ignore_index=True)
                self.save_expenses()
                messagebox.showinfo("Success", "Expense added successfully!")
                self.clear_entries()  
                self.view_expenses()
            except ValueError as ve:
                print(f"Debug: ValueError={ve}")
                #messagebox.showerror("Error", "Please enter a valid amount.")
        else:
            messagebox.showerror("Error", "Please fill all the fields.")

    def update_expense(self):
        if self.selected_item:
            date = self.date_entry.get()
            category = self.category_entry.get()
            amount = self.amount_entry.get()
            description = self.description_entry.get()

            if date and category and amount and description:
                try:
                    amount = float(amount)
                    selected_index = int(self.tree.item(self.selected_item)["values"][0])
                    self.expenses.loc[selected_index, ["Date", "Category", "Amount", "Description"]] = [date, category, amount, description]
                    self.save_expenses()
                    messagebox.showinfo("Success", "Expense updated successfully!")
                    self.clear_entries()
                    self.view_expenses()
                except ValueError:
                    #messagebox.showerror("Error", "Please enter a valid amount.")
                    print("Successfull")
            else:
                messagebox.showerror("Error", "Please fill all the fields.")
        else:
            messagebox.showerror("Error", "Please select an expense to update.")

    def delete_expense(self):
        if self.selected_item:
            selected_index = int(self.tree.item(self.selected_item)["values"][0])
            self.expenses = self.expenses.drop(selected_index).reset_index(drop=True)
            self.save_expenses()
            messagebox.showinfo("Success", "Expense deleted successfully!")
            self.clear_entries()
            self.view_expenses()
        else:
            messagebox.showerror("Error", "Please select an expense to delete.")

    def view_expenses(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for index, row in self.expenses.iterrows():
            self.tree.insert("", "end", iid=index, values=(index, row["Date"], row["Category"], row["Amount"], row["Description"]))

    def select_item(self, event):
        selected = self.tree.focus()
        if selected:
            self.selected_item = selected
            values = self.tree.item(selected, 'values')
            self.date_entry.set_date(values[1])
            self.category_entry.set(values[2])
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, values[3])
            self.description_entry.delete(0, tk.END)
            self.description_entry.insert(0, values[4])

    def show_summary(self):
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Expense Summary")
        summary_window.geometry("400x300")

        summary = self.expenses.groupby("Category")["Amount"].sum()
        total = self.expenses["Amount"].sum()

        tk.Label(summary_window, text="Category-wise Summary", font=("Arial", 14)).pack(pady=10)
        for category, amount in summary.items():
            tk.Label(summary_window, text=f"{category}: ${amount:.2f}", font=("Arial", 12)).pack()

        tk.Label(summary_window, text=f"\nTotal: ${total:.2f}", font=("Arial", 14)).pack(pady=10)

    def clear_entries(self):
        self.date_entry.set_date("0000-00-00")
        self.category_entry.set("")
        self.amount_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.selected_item = None

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
