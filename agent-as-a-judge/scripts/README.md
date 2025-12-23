## Demo scripts

### Ask Anything

1. Ask any questions about the given workspace

```python 

PYTHONPATH=. python scripts/run_ask.py \
  --workspace $(pwd)/benchmark/workspaces/OpenHands/39_Drug_Response_Prediction_SVM_GDSC_ML \
  --question "What does this workspace contain?"
```

### Agent-as-a-Judge

2. Using the collected trajectories or development logs (gray-box setting)

```python
PYTHONPATH=. python scripts/run_aaaj.py \
  --developer_agent "OpenHands" \
  --setting "gray_box" \
  --planning "comprehensive (no planning)" \
  --benchmark_dir $(pwd)/benchmark
```

3. Do not have trajectories or development logs (black-box setting)

```python
PYTHONPATH=. python scripts/run_aaaj.py \
  --developer_agent "OpenHands" \
  --setting "black_box" \
  --planning "efficient (no planning)" \
  --benchmark_dir $(pwd)/benchmark
```

4. Do not have trajectories or development logs and using planning to decide the actions of Agent-as-a-Judge (black-box setting)

```python
PYTHONPATH=. python scripts/run_aaaj.py \
  --developer_agent "OpenHands" \
  --setting "gray_box" \
  --planning "planning" \
  --benchmark_dir $(pwd)/benchmark
```

### Statistics

5. Get the statistics of the projects

```python
PYTHONPATH=. python scripts/run_statistics.py \
    --benchmark_dir $(pwd)/benchmark \
    --developer_agent OpenHands
```

# Agent-as-a-Judge Scripts

This directory contains executable scripts for Agent-as-a-Judge.

## Available Scripts

### run_ask.py
Run the AaaJ agent in ask mode to query repositories.

### run_aaaj.py
Run the AaaJ agent for evaluation tasks.

### run_statistics.py
Generate statistics about repositories.

### run_wiki.py
Generate interactive guidance documentation for repositories.

## run_wiki.py

The `run_wiki.py` script generates comprehensive interactive documentation for any code repository, focusing on creating useful guidance rather than just basic statistics.

### Features

- Automatically analyzes repository structure and architecture
- Extracts key components and their relationships
- Generates in-depth documentation through intelligent Q&A
- Detects the most important files in the repository
- Creates a clean, information-rich HTML guide
- Provides best practices and recommendations
- Visualizes the codebase architecture with flowcharts
- Shows code snippets from key files

### Usage

```bash
# Generate HTML documentation for any repository
PYTHONPATH=. python scripts/run_wiki.py --repo /path/to/repository --out-dir ./output
```

### Options

- `--repo`: Path to the repository (required)
- `--out-dir`: Output directory for documentation (default: "./output")
- `--templates-dir`: Directory containing custom templates (optional)

### Dependencies

This script requires the following packages:
- jinja2 (for HTML template rendering)

This dependency is included in the pyproject.toml file.

### Custom Templates

You can provide custom templates by specifying a templates directory with `--templates-dir`. The directory structure should be:

```
templates/
└── html/
    ├── index.html
    └── assets/
        ├── css/
        └── js/
```

The default template is located in the `scripts/templates/html` directory.

### Documentation Structure

The generated documentation contains:

1. **Overview** - High-level understanding of the repository
2. **Purpose and Scope** - What the repository is designed to do
3. **Architecture** - Visual representation of components and their relationships
4. **Key Components** - Detailed explanation of main modules
5. **Installation and Setup** - How to set up the project
6. **Usage Guide** - How to use the codebase
7. **FAQ** - Common questions and answers
8. **Code References** - Snippets from key files with explanations

This comprehensive documentation helps new developers quickly understand the codebase structure, purpose, and best practices.