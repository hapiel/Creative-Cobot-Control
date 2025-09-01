#!/usr/bin/env python3
"""
Noisette JSON Normalizer

This script normalizes .noisette files by:
1. Sorting all dictionary keys recursively
2. Sorting arrays of objects by specific keys (niceName, type, controlAddress)
3. Maintaining consistent indentation and formatting
4. Preserving semantic order where it matters

This helps Git produce meaningful diffs by ensuring consistent JSON structure.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Union


def sort_array_by_keys(arr: List[Any], sort_keys: List[str]) -> List[Any]:
    """
    Sort array of objects by specified keys in priority order.
    Objects without these keys will be sorted last.
    """
    if not isinstance(arr, list) or not arr:
        return arr
    
    def get_sort_value(item):
        if not isinstance(item, dict):
            return (1, str(item))  # Non-dict items sorted last
        
        # Try each sort key in priority order
        for key in sort_keys:
            if key in item:
                value = item[key]
                if isinstance(value, (str, int, float)):
                    return (0, str(value).lower())
        
        # If no sort keys found, use string representation
        return (1, str(item))
    
    return sorted(arr, key=get_sort_value)


def normalize_json_structure(obj: Any, path: str = "") -> Any:
    """
    Recursively normalize JSON structure with context-aware sorting.
    """
    if isinstance(obj, dict):
        # Sort dictionary keys
        result = {}
        
        # Handle special cases where array order matters semantically
        for key in sorted(obj.keys()):
            value = obj[key]
            current_path = f"{path}.{key}" if path else key
            
            if isinstance(value, list):
                # Sort arrays of objects by meaningful keys
                if key in ['items', 'parameters', 'variables', 'processors', 'layers', 'cues', 'presets']:
                    # Sort by common identification keys
                    value = sort_array_by_keys(value, ['niceName', 'type', 'controlAddress', 'label'])
                elif key == 'modules':
                    # Sort modules by niceName and type
                    value = sort_array_by_keys(value, ['niceName', 'type'])
                elif key == 'states':
                    # Sort states by niceName
                    value = sort_array_by_keys(value, ['niceName', 'type'])
                elif key == 'sequences':
                    # Sort sequences by niceName
                    value = sort_array_by_keys(value, ['niceName', 'type'])
                elif key == 'customVariables':
                    # Sort custom variables by niceName
                    value = sort_array_by_keys(value, ['niceName', 'type'])
                
                # Recursively normalize array elements
                value = [normalize_json_structure(item, f"{current_path}[{i}]") 
                        for i, item in enumerate(value)]
            else:
                # Recursively normalize other values
                value = normalize_json_structure(value, current_path)
            
            result[key] = value
        
        return result
    
    elif isinstance(obj, list):
        # Recursively normalize list elements
        return [normalize_json_structure(item, f"{path}[{i}]") 
                for i, item in enumerate(obj)]
    
    else:
        # Return primitive values as-is
        return obj


def normalize_noisette_file(filepath: Union[str, Path]) -> bool:
    """
    Normalize a single .noisette file.
    Returns True if successful, False otherwise.
    """
    filepath = Path(filepath)
    
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Normalize the structure
        normalized_data = normalize_json_structure(data)
        
        # Write back with consistent formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(normalized_data, f, indent=2, ensure_ascii=False, sort_keys=False)
            f.write('\n')  # Add trailing newline
        
        print(f"✓ Normalized: {filepath}")
        return True
    
    except json.JSONDecodeError as e:
        print(f"✗ JSON Error in {filepath}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False


def find_noisette_files(directory: Union[str, Path] = '.') -> List[Path]:
    """Find all .noisette files in the given directory."""
    directory = Path(directory)
    return list(directory.glob('*.noisette'))


def main():
    """Main function - normalize all .noisette files in current directory."""
    if len(sys.argv) > 1:
        # Process specific files if provided
        files = [Path(arg) for arg in sys.argv[1:] if arg.endswith('.noisette')]
    else:
        # Process all .noisette files in current directory
        files = find_noisette_files()
    
    if not files:
        print("No .noisette files found.")
        return 0
    
    success_count = 0
    total_count = len(files)
    
    print(f"Normalizing {total_count} .noisette file(s)...")
    
    for filepath in files:
        if normalize_noisette_file(filepath):
            success_count += 1
    
    print(f"\nCompleted: {success_count}/{total_count} files normalized successfully.")
    
    if success_count == total_count:
        return 0  # Success
    else:
        return 1  # Some files failed


if __name__ == "__main__":
    sys.exit(main())
