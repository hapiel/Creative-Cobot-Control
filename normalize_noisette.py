#!/usr/bin/env python3
"""
Enhanced Chataigne .noisette File Normalizer with Deep Structure Normalization

This script applies comprehensive normalization to ensure that changes to individual
values in Chataigne result in minimal, focused Git diffs rather than wholesale
restructuring of the JSON file.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Union


def normalize_array_intelligently(arr: List[Any], parent_key: str = "", depth: int = 0) -> List[Any]:
    """
    Sort arrays using intelligent key detection, but preserve semantic order
    for arrays where order matters (like coordinates, colors, etc.)
    """
    if not arr:
        return arr
    
    # Arrays where order has semantic meaning - do NOT sort these
    semantic_order_keys = {
        'color', 'position', 'viewuiposition', 'viewuisize', 'value',
        'viewoffset', 'rotation', 'scale', 'bounds', 'range',
        'controladdress', 'inputrange', 'outputrange', 'coefficients',
        'vertices', 'points', 'coordinates', 'offset'
    }
    
    # Check if this array should preserve its order
    if parent_key.lower() in semantic_order_keys:
        # For semantic arrays, just normalize the contents without reordering
        return [deep_normalize_json(item, parent_key, depth + 1) for item in arr]
    
    # Handle primitive arrays
    if not all(isinstance(item, dict) for item in arr):
        # Only sort if not a semantic array
        try:
            return sorted(arr, key=str)
        except TypeError:
            return arr
    
    # Find the best sorting key from priority list for object arrays
    semantic_keys = ['niceName', 'name', 'controlAddress', 'type', 'shortName', 'id', 'label']
    
    for key in semantic_keys:
        if all(key in item and item[key] is not None for item in arr):
            return sorted(arr, key=lambda x: str(x[key]).lower())
    
    # Fallback: sort by JSON string representation
    try:
        return sorted(arr, key=lambda x: json.dumps(x, sort_keys=True))
    except (TypeError, ValueError):
        return arr


def deep_normalize_json(obj: Any, parent_key: str = "", depth: int = 0) -> Any:
    """
    Recursively normalize JSON with comprehensive structure sorting.
    Uses depth limiting and semantic awareness to prevent unwanted reordering.
    """
    # Prevent excessive recursion depth
    if depth > 100:
        return obj
    
    if isinstance(obj, dict):
        # Sort keys and recursively normalize values
        result = {}
        for key in sorted(obj.keys()):
            result[key] = deep_normalize_json(obj[key], key, depth + 1)
        return result
    
    elif isinstance(obj, list):
        # Use parent_key context to decide whether to sort this array
        return normalize_array_intelligently(obj, parent_key, depth)
    
    else:
        # Primitive value - return unchanged
        return obj


def normalize_noisette_file(filepath: Union[str, Path]) -> bool:
    """Normalize a single .noisette file with comprehensive deep normalization."""
    filepath = Path(filepath)
    
    try:
        print(f"Processing {filepath}...")
        
        # Read and parse JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"  Applying deep normalization...")
        # Apply comprehensive normalization
        normalized_data = deep_normalize_json(data)
        
        print(f"  Writing normalized data...")
        # Write back with consistent formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(normalized_data, f, indent=2, ensure_ascii=False, sort_keys=False)
            f.write('\n')
        
        return True
        
    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False


def main():
    """Main function."""
    if len(sys.argv) > 1:
        files = [Path(arg) for arg in sys.argv[1:]]
    else:
        files = list(Path('.').glob('*.noisette'))
    
    if not files:
        print("No .noisette files found.")
        return 1
    
    print(f"Normalizing {len(files)} .noisette file(s)...")
    
    successful = 0
    for filepath in files:
        if filepath.exists() and normalize_noisette_file(filepath):
            print(f"✓ Normalized: {filepath}")
            successful += 1
        else:
            print(f"✗ Failed: {filepath}")
    
    print(f"\nCompleted: {successful}/{len(files)} files normalized successfully.")
    return 0 if successful == len(files) else 1


if __name__ == '__main__':
    sys.exit(main())
