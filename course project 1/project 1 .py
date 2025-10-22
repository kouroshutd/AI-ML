import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Generator
from dataclasses import dataclass, asdict
from enum import Enum

# ==================== EDUCATIONAL CONCEPTS ====================

# 1. DATACLASSES - Modern Python way to create data structures
@dataclass
class Expense:
    """
    Using dataclass instead of dictionaries provides:
    - Type safety
    - Automatic __init__, __repr__, __eq__ methods
    - Better IDE support and debugging
    - Cleaner code structure
    """
    date: str
    category: str
    amount: float
    description: str
    
    def __post_init__(self):
        """Validates data after initialization"""
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Validate date format
        try:
            datetime.strptime(self.date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for CSV writing"""
        return asdict(self)

# 2. ENUMS - Better than string constants
class MenuOption(Enum):
    """
    Enums prevent typos and make code more maintainable.
    Instead of magic numbers/strings, we use descriptive names.
    """
    ADD_EXPENSE = "1"
    VIEW_ALL = "2"
    VIEW_SORTED = "3"
    VIEW_BY_CATEGORY = "4"
    SET_BUDGET = "5"
    TRACK_BUDGET = "6"
    SAVE_EXIT = "7"

# 3. CONTEXT MANAGERS - Better file handling
class ExpenseFileManager:
    """
    Context manager for file operations ensures proper resource cleanup.
    Separates file operations from business logic (Single Responsibility Principle).
    """
    
    def __init__(self, expenses_file: str = "expenses.csv", config_file: str = "config.json"):
        self.expenses_file = expenses_file
        self.config_file = config_file
    
    def load_expenses(self) -> List[Expense]:
        """Load expenses with proper error handling"""
        expenses = []
        
        if not os.path.exists(self.expenses_file):
            return expenses
        
        try:
            with open(self.expenses_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        # Convert amount to float and create Expense object
                        expense = Expense(
                            date=row['date'],
                            category=row['category'],
                            amount=float(row['amount']),
                            description=row['description']
                        )
                        expenses.append(expense)
                    except (ValueError, KeyError) as e:
                        print(f"⚠️  Skipping invalid expense: {e}")
                        
        except Exception as e:
            print(f"❌ Error loading expenses: {e}")
        
        return expenses
    
    def save_expenses(self, expenses: List[Expense]) -> bool:
        """Save expenses to CSV file"""
        try:
            with open(self.expenses_file, 'w', newline='', encoding='utf-8') as file:
                if not expenses:
                    return True
                
                fieldnames = ['date', 'category', 'amount', 'description']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                
                for expense in expenses:
                    writer.writerow(expense.to_dict())
                
            return True
        except Exception as e:
            print(f"❌ Error saving expenses: {e}")
            return False
    
    def load_config(self) -> dict:
        """Load configuration (like budget) from JSON file"""
        if not os.path.exists(self.config_file):
            return {"monthly_budget": 0.0}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return {"monthly_budget": 0.0}
    
    def save_config(self, config: dict) -> bool:
        """Save configuration to JSON file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as file:
                json.dump(config, file, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            return False

# 4. CLASS-BASED ARCHITECTURE - Better organization
class ExpenseTracker:
    """
    Main application class following Object-Oriented Programming principles:
    - Encapsulation: Data and methods are bundled together
    - Single Responsibility: Each method has one clear purpose
    - Dependency Injection: FileManager is injected, making testing easier
    """
    
    def __init__(self, file_manager: ExpenseFileManager):
        self.file_manager = file_manager
        self.expenses: List[Expense] = []
        self.config = {"monthly_budget": 0.0}
        self.load_data()
    
    def load_data(self) -> None:
        """Load expenses and configuration on startup"""
        self.expenses = self.file_manager.load_expenses()
        self.config = self.file_manager.load_config()
        
        if self.expenses:
            print(f"✅ Loaded {len(self.expenses)} expenses")
        if self.config.get("monthly_budget", 0) > 0:
            print(f"✅ Monthly budget: ${self.config['monthly_budget']:.2f}")
    
    def save_data(self) -> bool:
        """Save expenses and configuration"""
        expenses_saved = self.file_manager.save_expenses(self.expenses)
        config_saved = self.file_manager.save_config(self.config)
        
        if expenses_saved and config_saved:
            print("✅ Data saved successfully")
            return True
        else:
            print("❌ Error saving data")
            return False
    
    # 5. INPUT VALIDATION - Separate concerns
    @staticmethod
    def get_valid_date() -> str:
        """Get and validate date input"""
        while True:
            date_str = input("📅 Enter date (YYYY-MM-DD) or 'today' for current date: ").strip()
            
            if date_str.lower() == 'today':
                return datetime.now().strftime('%Y-%m-%d')
            
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                print("❌ Invalid date format. Please use YYYY-MM-DD")
    
    @staticmethod
    def get_valid_amount() -> float:
        """Get and validate amount input"""
        while True:
            try:
                amount_str = input("💰 Enter amount: $").strip()
                amount = float(amount_str)
                if amount <= 0:
                    print("❌ Amount must be positive")
                    continue
                return amount
            except ValueError:
                print("❌ Please enter a valid number")
    
    @staticmethod
    def get_valid_category() -> str:
        """Get and validate category input"""
        common_categories = ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Health", "Other"]
        print(f"💡 Common categories: {', '.join(common_categories)}")
        
        while True:
            category = input("📂 Enter category: ").strip().title()
            if category:
                return category
            print("❌ Category cannot be empty")
    
    def add_expense(self) -> None:
        """Add new expense with comprehensive validation"""
        print("\n" + "="*50)
        print("💸 ADD NEW EXPENSE")
        print("="*50)
        
        try:
            date = self.get_valid_date()
            category = self.get_valid_category()
            amount = self.get_valid_amount()
            description = input("📝 Enter description (optional): ").strip()
            
            expense = Expense(date, category, amount, description)
            self.expenses.append(expense)
            
            print(f"✅ Expense added: ${amount:.2f} for {category}")
            
        except Exception as e:
            print(f"❌ Error adding expense: {e}")
    
    def view_all_expenses(self) -> None:
        """Display all expenses in a formatted table"""
        print("\n" + "="*80)
        print("📊 ALL EXPENSES")
        print("="*80)
        
        if not self.expenses:
            print("📝 No expenses recorded yet")
            return
        
        self._print_expense_table(self.expenses)
        
        # Summary statistics
        total = sum(exp.amount for exp in self.expenses)
        print(f"\n📈 Total Expenses: ${total:.2f}")
        print(f"📊 Number of Expenses: {len(self.expenses)}")
    
    def view_expenses_sorted(self) -> None:
        """
        EDUCATIONAL: Lambda functions and sorting
        Lambda is perfect for simple, one-line functions used as arguments
        """
        print("\n" + "="*80)
        print("📊 EXPENSES SORTED BY AMOUNT (Highest to Lowest)")
        print("="*80)
        
        if not self.expenses:
            print("📝 No expenses recorded yet")
            return
        
        # Lambda function explanation:
        # lambda expense: expense.amount creates an anonymous function
        # that takes an expense and returns its amount for sorting
        sorted_expenses = sorted(self.expenses, key=lambda expense: expense.amount, reverse=True)
        self._print_expense_table(sorted_expenses)
    
    def view_expenses_by_category(self) -> None:
        """
        EDUCATIONAL: Generator functions and yield
        Generators are memory-efficient for large datasets
        """
        print("\n" + "="*80)
        print("📂 EXPENSES BY CATEGORY")
        print("="*80)
        
        if not self.expenses:
            print("📝 No expenses recorded yet")
            return
        
        # Show available categories
        categories = set(exp.category for exp in self.expenses)
        print(f"📂 Available categories: {', '.join(sorted(categories))}")
        
        category = input("🔍 Enter category to filter: ").strip().title()
        
        # Using generator for memory efficiency
        filtered_expenses = list(self._get_expenses_by_category(category))
        
        if not filtered_expenses:
            print(f"❌ No expenses found for category '{category}'")
            return
        
        print(f"\n📂 Expenses in category: {category}")
        self._print_expense_table(filtered_expenses)
        
        # Category statistics
        total = sum(exp.amount for exp in filtered_expenses)
        print(f"\n📊 Total for {category}: ${total:.2f}")
    
    def _get_expenses_by_category(self, category: str) -> Generator[Expense, None, None]:
        """
        EDUCATIONAL: Generator function using yield
        
        Why use yield instead of return list?
        - Memory efficient: processes one item at a time
        - Lazy evaluation: only computes when needed
        - Can handle infinite sequences
        - Better for large datasets
        """
        for expense in self.expenses:
            if expense.category.lower() == category.lower():
                yield expense
    
    def set_budget(self) -> None:
        """Set or update monthly budget"""
        print("\n" + "="*50)
        print("💰 SET MONTHLY BUDGET")
        print("="*50)
        
        current_budget = self.config.get("monthly_budget", 0.0)
        print(f"Current budget: ${current_budget:.2f}")
        
        while True:
            try:
                budget_input = input("💰 Enter new monthly budget: $").strip()
                new_budget = float(budget_input)
                
                if new_budget < 0:
                    print("❌ Budget cannot be negative")
                    continue
                
                self.config["monthly_budget"] = new_budget
                print(f"✅ Monthly budget set to: ${new_budget:.2f}")
                break
                
            except ValueError:
                print("❌ Please enter a valid number")
    
    def track_budget(self) -> None:
        """
        EDUCATIONAL: Functional programming with map() and lambda
        Shows different ways to calculate totals
        """
        print("\n" + "="*60)
        print("📊 BUDGET TRACKING")
        print("="*60)
        
        budget = self.config.get("monthly_budget", 0.0)
        if budget == 0:
            print("❌ No budget set. Please set a budget first.")
            return
        
        # Method 1: Using map() with lambda (functional programming)
        total_expenses = sum(map(lambda exp: exp.amount, self.expenses))
        
        # Method 2: List comprehension (more Pythonic)
        # total_expenses = sum(exp.amount for exp in self.expenses)
        
        # Method 3: Traditional loop (most explicit)
        # total_expenses = 0
        # for expense in self.expenses:
        #     total_expenses += expense.amount
        
        remaining = budget - total_expenses
        percentage_used = (total_expenses / budget) * 100 if budget > 0 else 0
        
        print(f"💰 Monthly Budget:    ${budget:.2f}")
        print(f"💸 Total Expenses:    ${total_expenses:.2f}")
        print(f"📊 Budget Used:       {percentage_used:.1f}%")
        print("-" * 40)
        
        if remaining >= 0:
            print(f"✅ Remaining:         ${remaining:.2f}")
            if percentage_used > 80:
                print("⚠️  Warning: You've used over 80% of your budget!")
        else:
            print(f"❌ Over Budget:       ${abs(remaining):.2f}")
            print("🚨 WARNING: You have exceeded your budget!")
    
    def _print_expense_table(self, expenses: List[Expense]) -> None:
        """Helper method to print expenses in a formatted table"""
        print(f"{'Date':<12} | {'Category':<15} | {'Amount':<10} | {'Description':<25}")
        print("-" * 70)
        
        for expense in expenses:
            print(f"{expense.date:<12} | {expense.category:<15} | "
                  f"${expense.amount:<9.2f} | {expense.description:<25}")
    
    def display_menu(self) -> None:
        """Display the main menu"""
        print("\n" + "="*60)
        print("💰 PERSONAL EXPENSE TRACKER")
        print("="*60)
        print("1. 💸 Add Expense")
        print("2. 📊 View All Expenses")
        print("3. 📈 View Expenses Sorted by Amount")
        print("4. 📂 View Expenses by Category")
        print("5. 💰 Set Monthly Budget")
        print("6. 📊 Track Budget")
        print("7. 💾 Save and Exit")
        print("="*60)
    
    def run(self) -> None:
        """
        EDUCATIONAL: Main application loop with proper error handling
        Uses match-case (Python 3.10+) for cleaner code
        """
        print("🎉 Welcome to Personal Expense Tracker!")
        
        while True:
            self.display_menu()
            choice = input("🔢 Enter your choice (1-7): ").strip()
            
            # Using match-case (Python 3.10+) - more readable than if-elif chains
            match choice:
                case MenuOption.ADD_EXPENSE.value:
                    self.add_expense()
                case MenuOption.VIEW_ALL.value:
                    self.view_all_expenses()
                case MenuOption.VIEW_SORTED.value:
                    self.view_expenses_sorted()
                case MenuOption.VIEW_BY_CATEGORY.value:
                    self.view_expenses_by_category()
                case MenuOption.SET_BUDGET.value:
                    self.set_budget()
                case MenuOption.TRACK_BUDGET.value:
                    self.track_budget()
                case MenuOption.SAVE_EXIT.value:
                    print("\n💾 Saving data and exiting...")
                    if self.save_data():
                        print("👋 Thank you for using Personal Expense Tracker!")
                        break
                    else:
                        continue_anyway = input("❓ Save failed. Exit anyway? (y/n): ")
                        if continue_anyway.lower() == 'y':
                            break
                case _:  # Default case
                    print("❌ Invalid choice. Please select 1-7.")
            
            # Pause for user to read output
            input("\n⏯️  Press Enter to continue...")

# ==================== MAIN EXECUTION ====================
def main():
    """
    EDUCATIONAL: Dependency injection and separation of concerns
    - FileManager handles all file operations
    - ExpenseTracker handles business logic
    - Easy to test and maintain
    """
    file_manager = ExpenseFileManager()
    tracker = ExpenseTracker(file_manager)
    tracker.run()

if __name__ == "__main__":
    main()