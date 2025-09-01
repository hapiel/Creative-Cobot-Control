# Noisette File Normalization

This repository includes a system to normalize `.noisette` files from Chataigne to ensure consistent Git diffs.

## Problem

Chataigne saves `.noisette` files with inconsistent JSON key ordering, making Git diffs hard to read and understand actual changes.

## Solution

### normalize_noisette.py

A Python script that:
- Recursively sorts all JSON dictionary keys
- Sorts arrays of objects by meaningful keys (`niceName`, `type`, `controlAddress`)
- Maintains consistent indentation and formatting
- Preserves semantic order where it matters

### Git Pre-commit Hook

Automatically normalizes `.noisette` files before each commit to ensure consistency.

## Usage

### Manual normalization:
```bash
# Normalize all .noisette files in current directory
python3 normalize_noisette.py

# Normalize specific files
python3 normalize_noisette.py ur3.noisette ur3_recovered.noisette
```

### Automatic normalization:
The pre-commit hook automatically normalizes any staged `.noisette` files before committing.

## Installation

The system is already set up in this repository. For new repositories:

1. Copy `normalize_noisette.py` to your repository root
2. Copy `.git/hooks/pre-commit` and make it executable:
   ```bash
   chmod +x .git/hooks/pre-commit
   ```

## How It Works

The normalizer:

1. **Sorts dictionary keys** alphabetically for consistent structure
2. **Sorts object arrays** by identifying keys:
   - `items`, `parameters`, `variables` → sorted by `niceName`, `type`, `controlAddress`
   - `modules`, `states`, `sequences` → sorted by `niceName`, `type`
3. **Maintains formatting** with 2-space indentation and trailing newlines
4. **Preserves semantic meaning** while improving diff readability

## Benefits

- **Cleaner Git diffs**: Only actual changes are highlighted
- **Better collaboration**: Easier to review changes from multiple contributors
- **Reduced merge conflicts**: Consistent formatting reduces spurious conflicts
- **Automatic**: No need to remember to run it manually
