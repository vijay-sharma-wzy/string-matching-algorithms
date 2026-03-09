# Algorithms from Scratch

Practicing implementing well-known algorithms from scratch in Python.

## Algorithms

### 1. Generalized Suffix Tree (`gst.py`)
Ukkonen's algorithm for constructing a generalized suffix tree over multiple texts in linear time. Supports case-insensitive pattern matching and returns all occurrences across all input texts.

### 2. Modified Boyer-Moore (`modified_BoyerMoore.py`)
Boyer-Moore string matching with the good suffix rule (ASCII-conditioned variant), matched prefix fallback, and Galil's optimisation for O(n + m) time complexity.

## Requirements

- Python 3

## Usage

### Generalized Suffix Tree

```bash
python gst.py <run_spec_file>
```

The run spec file format:
```
<num_text_files>
1 <path_to_text1>
2 <path_to_text2>
<num_pattern_files>
1 <path_to_pattern1>
```

Output is written to `output_gst.txt`. Each line is: `<pattern_num> <text_num> <position>`.

### Modified Boyer-Moore

```bash
python modified_BoyerMoore.py <text_file> <pattern_file>
```

Output is written to `output_modified_BoyerMoore.txt`. Each line is a 1-indexed position where the pattern occurs in the text.

## License

MIT
