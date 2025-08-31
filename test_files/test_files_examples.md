# Sample Python files for testing the Code Review Application

## test_simple.py
```python
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
```

## test_complex.py  
```python
import os
import sys
from typing import List, Dict, Optional

class DataProcessor:
    def __init__(self, data_source: str):
        self.data_source = data_source
        self.processed_data = []
    
    def load_data(self) -> List[Dict]:
        """Load data from source with potential issues for review."""
        data = []
        # Potential issue: no error handling for file operations
        with open(self.data_source, 'r') as f:
            for line in f:
                # Potential issue: assuming specific format without validation
                parts = line.strip().split(',')
                data.append({
                    'id': parts[0],
                    'name': parts[1], 
                    'value': int(parts[2])  # Potential issue: no type checking
                })
        return data
    
    def process_data(self, data: List[Dict]) -> None:
        """Process the loaded data."""
        for item in data:
            # Potential issue: inefficient string concatenation
            result = ""
            for i in range(len(item['name'])):
                result += item['name'][i].upper()
            
            # Potential issue: modifying during iteration
            if item['value'] < 0:
                data.remove(item)
            
            self.processed_data.append({
                'processed_name': result,
                'squared_value': item['value'] ** 2
            })
    
    def save_results(self, filename: str) -> None:
        """Save processed results."""
        # Potential issue: no error handling or path validation
        with open(filename, 'w') as f:
            for item in self.processed_data:
                f.write(f"{item['processed_name']},{item['squared_value']}\n")

# Usage with potential issues
if __name__ == "__main__":
    # Potential issue: hardcoded paths
    processor = DataProcessor("data.csv")
    
    # Potential issue: no error handling for the main workflow
    raw_data = processor.load_data()
    processor.process_data(raw_data)
    processor.save_results("output.csv")
    
    print("Processing completed!")
```

## test_with_bugs.py
```python
def calculate_average(numbers):
    # Bug: division by zero not handled
    total = sum(numbers)
    return total / len(numbers)

def find_max_value(data_list):
    # Bug: empty list not handled
    max_val = data_list[0]
    for item in data_list:
        if item > max_val:
            max_val = item
    return max_val

class BankAccount:
    def __init__(self, initial_balance):
        # Bug: negative balance allowed
        self.balance = initial_balance
    
    def withdraw(self, amount):
        # Bug: overdraft not prevented
        self.balance -= amount
        return self.balance
    
    def deposit(self, amount):
        # Bug: negative deposits allowed
        self.balance += amount
        return self.balance

# Bug: global variable modification in function
counter = 0

def increment_counter():
    global counter
    counter += 1
    # Bug: potential race condition in multi-threaded environment
    return counter

# Usage examples with various issues
if __name__ == "__main__":
    # This will cause division by zero
    print(calculate_average([]))
    
    # This will cause index error
    print(find_max_value([]))
    
    # This allows negative balance
    account = BankAccount(-100)
    account.withdraw(50)
    account.deposit(-25)
```

Place these test files in the `test_files/` directory to experiment with the Code Review Application!