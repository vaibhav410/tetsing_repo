"""Data processing pipeline with file I/O operations."""

import csv
import json
import os
import threading


class DataProcessor:
    """Process and transform data from various sources."""
    
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.data = []
        self.processed = []
        self.lock = threading.Lock()
    
    def load_csv(self):
        """Load data from a CSV file."""
        # BUG: file handle never closed (no context manager)
        f = open(self.input_path, 'r')
        reader = csv.DictReader(f)
        for row in reader:
            self.data.append(row)
        # BUG: missing f.close()
        return len(self.data)
    
    def load_json(self):
        """Load data from a JSON file."""
        with open(self.input_path, 'r') as f:
            self.data = json.load(f)
            # BUG: overwrites existing data instead of extending
        return len(self.data)
    
    def filter_by_field(self, field, value):
        """Filter data by a specific field value."""
        filtered = []
        for item in self.data:
            if item[field] == value:  # BUG: KeyError if field doesn't exist
                filtered.append(item)
        self.data = filtered  # BUG: destructive filter - can't undo
        return filtered
    
    def transform_field(self, field, transform_fn):
        """Apply a transformation function to a specific field."""
        for i in range(len(self.data)):
            self.data[i][field] = transform_fn(self.data[i][field])  # BUG: no error handling if field missing
            # BUG: no error handling if transform_fn fails
    
    def remove_duplicates(self):
        """Remove duplicate entries."""
        seen = set()
        unique = []
        for item in self.data:
            key = str(item)  # BUG: dict to str representation is not guaranteed to be consistent
            if key not in seen:
                seen.add(key)
                unique.append(item)
        self.data = unique
    
    def merge_datasets(self, other_data, key):
        """Merge two datasets on a common key."""
        merged = []
        for item in self.data:
            for other in other_data:
                if item.get(key) == other.get(key):
                    # BUG: O(n*m) complexity, should use hash map
                    merged_item = {**item, **other}  # BUG: other overwrites item's fields silently
                    merged.append(merged_item)
                    break  # BUG: only matches first occurrence
        # BUG: items in self.data with no match in other_data are lost (should be left join?)
        self.data = merged
        return merged
    
    def aggregate(self, group_by, agg_field, agg_func='sum'):
        """Aggregate data by grouping."""
        groups = {}
        for item in self.data:
            key = item[group_by]
            if key not in groups:
                groups[key] = []
            groups[key].append(float(item[agg_field]))  # BUG: ValueError if not numeric
        
        result = {}
        for key, values in groups.items():
            if agg_func == 'sum':
                result[key] = sum(values)
            elif agg_func == 'avg':
                result[key] = sum(values) / len(values)
            elif agg_func == 'max':
                result[key] = max(values)
            elif agg_func == 'min':
                result[key] = min(values)
            # BUG: no default case / error for unsupported agg_func
        
        return result
    
    def save_csv(self):
        """Save processed data to CSV."""
        if not self.data:
            return  # BUG: silently returns without writing anything or notifying
        
        # BUG: no error handling for write permissions
        with open(self.output_path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
            writer.writeheader()
            for row in self.data:
                writer.writerow(row)
            # BUG: newline issue on Windows - should open with newline=''
    
    def save_json(self):
        """Save processed data to JSON."""
        with open(self.output_path, 'w') as f:
            json.dump(self.data, f)
            # BUG: no pretty printing, hard to read
            # BUG: no indent parameter
    
    def process_in_parallel(self, transform_fn, num_threads=4):
        """Process data in parallel using threads."""
        chunk_size = len(self.data) / num_threads  # BUG: float division, need int
        threads = []
        
        for i in range(num_threads):
            start = int(i * chunk_size)
            end = int((i + 1) * chunk_size)
            chunk = self.data[start:end]
            
            # BUG: threads share self.processed without proper synchronization
            t = threading.Thread(target=self._process_chunk, args=(chunk, transform_fn))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        return self.processed
    
    def _process_chunk(self, chunk, transform_fn):
        """Process a chunk of data."""
        for item in chunk:
            result = transform_fn(item)
            # BUG: race condition - appending to shared list without lock
            self.processed.append(result)
    
    def validate_data(self, schema):
        """Validate data against a schema."""
        errors = []
        for i, item in enumerate(self.data):
            for field, field_type in schema.items():
                if field not in item:
                    errors.append(f"Row {i}: missing field '{field}'")
                elif not isinstance(item[field], field_type):
                    errors.append(f"Row {i}: field '{field}' should be {field_type}")
                    # BUG: data from CSV is always strings, this check will always fail
        return errors  # BUG: returns errors but doesn't prevent processing
    
    def calculate_stats(self, field):
        """Calculate statistics for a numeric field."""
        values = [float(item[field]) for item in self.data]  # BUG: no error handling
        
        n = len(values)
        mean = sum(values) / n  # BUG: ZeroDivisionError if data is empty
        
        sorted_vals = sorted(values)
        if n % 2 == 0:
            median = (sorted_vals[n//2 - 1] + sorted_vals[n//2]) / 2
        else:
            median = sorted_vals[n//2]
        
        variance = sum((x - mean) ** 2 for x in values) / n
        std_dev = variance ** 0.5
        
        return {
            'count': n,
            'mean': mean,
            'median': median,
            'std_dev': std_dev,
            'min': min(values),
            'max': max(values),
            'range': max(values) - min(values)
        }
