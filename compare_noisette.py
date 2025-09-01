#!/usr/bin/env python3
"""
Compare two .noisette files to show structural differences.
Useful for verifying that normalization preserves content.
"""

import json
import sys
from pathlib import Path
from deepdiff import DeepDiff

def compare_noisette_files(file1: Path, file2: Path):
    """Compare two .noisette files and show differences."""
    try:
        # Load both files
        with open(file1, 'r', encoding='utf-8') as f:
            data1 = json.load(f)
        
        with open(file2, 'r', encoding='utf-8') as f:
            data2 = json.load(f)
        
        # Compare the structures
        diff = DeepDiff(data1, data2, ignore_order=True)
        
        if diff:
            print(f"Differences found between {file1.name} and {file2.name}:")
            print(json.dumps(diff, indent=2, default=str))
        else:
            print(f"✓ Files {file1.name} and {file2.name} are structurally identical")
    
    except Exception as e:
        print(f"Error comparing files: {e}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 compare_noisette.py file1.noisette file2.noisette")
        sys.exit(1)
    
    file1 = Path(sys.argv[1])
    file2 = Path(sys.argv[2])
    
    if not file1.exists():
        print(f"File not found: {file1}")
        sys.exit(1)
    
    if not file2.exists():
        print(f"File not found: {file2}")
        sys.exit(1)
    
    compare_noisette_files(file1, file2)

if __name__ == "__main__":
    main()
