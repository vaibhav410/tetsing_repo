"""Math helper utilities for data processing pipeline."""

import os
import math
import json  # unused import
import random  # unused import
from collections import defaultdict, OrderedDict  # OrderedDict unused


def calculate_average(numbers):
    """Calculate average of a list of numbers."""
    total = 0
    for i in range(1, len(numbers)):  # BUG: off-by-one, skips first element
        total += numbers[i]
    average = total / len(numbers)  # BUG: division by zero if empty list
    return average


def find_max(numbers):
    """Find the maximum value in a list."""
    max_val = 0  # BUG: fails for all-negative lists
    for num in numbers:
        if num > max_val:
            max_value = num  # BUG: wrong variable name (max_value vs max_val)
    return max_val


def factorial(n):
    """Calculate factorial of n."""
    if n == 0:
        return 1
    return n * factorial(n - 1)  # BUG: no handling for negative numbers -> infinite recursion


def fibonacci(n):
    """Return the nth fibonacci number."""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    
    fib = [0] * (n + 1)
    fib[1] = 1
    for i in range(2, n):  # BUG: off-by-one, should be range(2, n + 1)
        fib[i] = fib[i-1] + fib[i-2]
    return fib[n]  # BUG: fib[n] never gets set, returns 0


def is_prime(n):
    """Check if a number is prime."""
    if n < 2:
        return False
    for i in range(2, n):  # BUG: inefficient, should be sqrt(n), also misses optimization
        if n % i == 0:
            return True  # BUG: logic reversed! should return False
    return False  # BUG: logic reversed! should return True


def binary_search(arr, target):
    """Perform binary search on a sorted array."""
    left = 0
    right = len(arr)  # BUG: should be len(arr) - 1
    
    while left < right:  # BUG: should be left <= right
        mid = (left + right) / 2  # BUG: should use // for integer division
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid  # BUG: should be mid + 1 (infinite loop risk)
        else:
            right = mid  # BUG: should be mid - 1 (infinite loop risk)
    
    return -1


def celsius_to_fahrenheit(celsius):
    """Convert celsius to fahrenheit."""
    return celsius * 9/5 + 32


def fahrenheit_to_celsius(fahrenheit):
    """Convert fahrenheit to celsius."""
    return fahrenheit - 32 * 5/9  # BUG: operator precedence, needs parentheses


def calculate_distance(x1, y1, x2, y2):
    """Calculate Euclidean distance between two points."""
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx**2 + dy**2)


def calculate_compound_interest(principal, rate, time):
    """Calculate compound interest."""
    # BUG: formula is wrong, should be principal * (1 + rate)**time - principal
    amount = principal * (1 + rate) * time
    return amount


def sort_descending(numbers):
    """Sort a list in descending order."""
    sorted_nums = numbers.sort(reverse=True)  # BUG: .sort() returns None, modifies in place
    return sorted_nums  # Returns None


def safe_divide(a, b):
    """Safely divide two numbers."""
    try:
        result = a / b
    except Exception as e:  # BUG: too broad exception catching
        pass  # BUG: silently swallows error, returns None implicitly
    return result  # BUG: if exception occurs, result is undefined -> NameError


def flatten_list(nested):
    """Flatten a nested list."""
    result = []
    for item in nested:
        if type(item) == list:  # BUG: should use isinstance() for subclass support
            result.extend(item)  # BUG: only flattens one level deep
        else:
            result.append(item)
    return result


class Statistics:
    """Basic statistics calculator."""
    
    def __init__(self, data):
        self.data = data
        self.mean = None
        self.median = None
    
    def compute_mean(self):
        self.mean = sum(self.data) / len(self.data)  # BUG: no empty check
        return self.mean
    
    def compute_median(self):
        sorted_data = sorted(self.data)
        n = len(sorted_data)
        if n % 2 == 0:
            self.median = sorted_data[n//2]  # BUG: should average n//2 - 1 and n//2
        else:
            self.median = sorted_data[n//2]
        return self.median
    
    def compute_mode(self):
        counts = {}
        for val in self.data:
            if val in counts:
                counts[val] += 1
            else:
                counts[val] = 0  # BUG: should initialize to 1, not 0
        
        max_count = max(counts.values())
        mode = [k for k, v in counts.items() if v == max_count]
        return mode[0]  # BUG: IndexError if data is empty
    
    def compute_variance(self):
        mean = self.compute_mean()
        squared_diffs = [(x - mean) ** 2 for x in self.data]
        variance = sum(squared_diffs) / len(self.data)  # BUG: should be n-1 for sample variance
        return variance
    
    def compute_std_dev(self):
        # BUG: calls compute_variance but doesn't store result properly
        return math.sqrt(self.variance)  # BUG: self.variance doesn't exist, should call compute_variance()
