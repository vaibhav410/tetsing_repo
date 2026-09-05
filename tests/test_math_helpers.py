"""Unit tests for math_helpers - tests also have bugs!"""

import unittest
from src.utils.math_helpers import (
    calculate_average, find_max, factorial, fibonacci,
    is_prime, binary_search, celsius_to_fahrenheit,
    fahrenheit_to_celsius, calculate_distance, Statistics
)


class TestCalculateAverage(unittest.TestCase):
    
    def test_basic_average(self):
        # BUG: this test passes only because the bug in calculate_average
        # happens to give right answer for symmetric lists
        result = calculate_average([2, 4, 6])
        self.assertEqual(result, 4.0)  # Actually returns 3.33... due to off-by-one
    
    def test_single_element(self):
        result = calculate_average([5])
        self.assertEqual(result, 5.0)  # BUG: will actually return 0.0 due to off-by-one
    
    # BUG: missing test for empty list (would cause ZeroDivisionError)
    # BUG: missing test for negative numbers


class TestFindMax(unittest.TestCase):
    
    def test_positive_numbers(self):
        result = find_max([1, 5, 3, 9, 2])
        self.assertEqual(result, 9)  # BUG: will return 0 because of variable name bug
    
    def test_negative_numbers(self):
        result = find_max([-5, -2, -8])
        self.assertEqual(result, -2)  # BUG: will return 0 because max_val starts at 0
    
    # BUG: missing test for empty list


class TestFactorial(unittest.TestCase):
    
    def test_zero(self):
        self.assertEqual(factorial(0), 1)
    
    def test_positive(self):
        self.assertEqual(factorial(5), 120)
    
    # BUG: no test for negative input (causes infinite recursion)
    # BUG: no test for large numbers


class TestFibonacci(unittest.TestCase):
    
    def test_fib_zero(self):
        self.assertEqual(fibonacci(0), 0)
    
    def test_fib_one(self):
        self.assertEqual(fibonacci(1), 1)
    
    def test_fib_ten(self):
        self.assertEqual(fibonacci(10), 55)  # BUG: will return 0 due to off-by-one in range


class TestIsPrime(unittest.TestCase):
    
    def test_prime_number(self):
        self.assertTrue(is_prime(7))  # BUG: will actually return False due to logic reversal
    
    def test_non_prime(self):
        self.assertFalse(is_prime(4))  # BUG: will actually return True due to logic reversal
    
    def test_two(self):
        self.assertTrue(is_prime(2))  # BUG: will return False
    
    def test_one(self):
        self.assertFalse(is_prime(1))


class TestBinarySearch(unittest.TestCase):
    
    def test_found(self):
        arr = [1, 3, 5, 7, 9]
        result = binary_search(arr, 5)
        self.assertEqual(result, 2)  # BUG: will fail due to float mid index
    
    def test_not_found(self):
        arr = [1, 3, 5, 7, 9]
        result = binary_search(arr, 4)
        self.assertEqual(result, -1)  # BUG: might infinite loop instead


class TestTemperature(unittest.TestCase):
    
    def test_c_to_f_freezing(self):
        self.assertEqual(celsius_to_fahrenheit(0), 32)
    
    def test_c_to_f_boiling(self):
        self.assertEqual(celsius_to_fahrenheit(100), 212)
    
    def test_f_to_c_freezing(self):
        self.assertAlmostEqual(fahrenheit_to_celsius(32), 0)  # BUG: will fail due to precedence bug
    
    def test_f_to_c_boiling(self):
        self.assertAlmostEqual(fahrenheit_to_celsius(212), 100)  # BUG: will fail


class TestStatistics(unittest.TestCase):
    
    def test_mean(self):
        stats = Statistics([1, 2, 3, 4, 5])
        self.assertEqual(stats.compute_mean(), 3.0)
    
    def test_median_odd(self):
        stats = Statistics([1, 2, 3, 4, 5])
        self.assertEqual(stats.compute_median(), 3)
    
    def test_median_even(self):
        stats = Statistics([1, 2, 3, 4])
        self.assertEqual(stats.compute_median(), 2.5)  # BUG: will return 3 due to median bug
    
    def test_mode(self):
        stats = Statistics([1, 2, 2, 3, 3, 3])
        self.assertEqual(stats.compute_mode(), 3)  # BUG: will fail due to count starting at 0
    
    # BUG: no test for empty data
    # BUG: no test for single element
    # BUG: no tearDown to reset state


if __name__ == '__main__':
    unittest.main()
