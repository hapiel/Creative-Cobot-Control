# Noisette JSON Normalization for Git

This solution addresses Chataigne's non-deterministic JSON serialization that causes messy Git diffs in `.noisette` files.

## Problem

Chataigne saves `.noisette` files as JSON, but the key ordering varies between saves, making Git diffs nearly impossible to read. This happens because:

1. **JavaScript objects** (which JSON is based on) don't guarantee key order
2. **Chataigne's serialization** doesn't enforce consistent ordering
3. **Minor changes** result in massive, unreadable diffs when keys are reordered

## Solution

### 1. Normalization Script (`normalize_noisette.py`)

A comprehensive Python script that:

- **Recursively sorts** all dictionary keys for consistent ordering
- **Intelligently sorts arrays** by meaningful keys (`niceName`, `type`, `controlAddress`)
- **Preserves semantic order** where it matters (like parameter arrays)
- **Maintains proper formatting** with 2-space indentation
- **Handles errors gracefully** with detailed reporting

#### Usage:

```bash
# Normalize all .noisette files in current directory
python3 normalize_noisette.py

# Normalize specific files
python3 normalize_noisette.py file1.noisette file2.noisette
```

### 2. Git Pre-Commit Hook

Automatically normalizes staged `.noisette` files before each commit:

- **Located at**: `.git/hooks/pre-commit`
- **Automatically runs** when you `git commit`
- **Only processes** staged `.noisette` files
- **Re-stages** normalized files
- **Fails commit** if normalization fails
- **Colorized output** for clear feedback

#### Features:
- ✅ Only processes staged `.noisette` files
- ✅ Validates Python 3 and script availability
- ✅ Provides clear error messages
- ✅ Re-stages normalized files automatically
- ✅ Aborts commit on normalization failure

### 3. Chataigne JSON Structure

The script understands the complete Chataigne `.noisette` structure:

```json
{
  "metaData": { ... },
  "projectSettings": { ... },
  "dashboardManager": { ... },
  "parrots": { ... },
  "layout": { ... },
  "modules": { ... },
  "customVariables": { ... },
  "states": { ... },
  "sequences": { ... },
  "routers": { ... }
}
```

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

## Recent Updates

**September 1, 2025**: Enhanced normalization with semantic array preservation and deep structure normalization:
- **Deep normalization**: Now applies comprehensive normalization to all nested levels of JSON structure
- **Semantic array preservation**: Preserves order of arrays where sequence matters (coordinates, colors, viewOffset, etc.)
- **Isolated changes**: Individual value changes now result in minimal, focused Git diffs
- **Intelligent sorting**: Only sorts arrays that benefit from consistent ordering (objects with niceName, type, etc.)
- **Enhanced pre-commit hook**: Simple, reliable hook that normalizes ur3.noisette without complex branching
- **Comprehensive testing**: Verified that single property changes (like TEST LUCIFER → TEST LUCIFER2) show as exactly 1 line changed

### Key Improvements:
- **Problem solved**: Changes to individual values in Chataigne no longer cause wholesale JSON restructuring
- **Minimal diffs**: Git diffs now show only actual changes, not formatting artifacts
- **Semantic awareness**: Arrays like `[x, y]` coordinates and `[r, g, b, a]` colors maintain their meaningful order
- **Robust normalization**: Handles complex nested structures while preventing infinite recursion
