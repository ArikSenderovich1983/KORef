# KORef Problem Instances

This directory contains KORef (KO-plan Refinement) problem instances in YAML format.

## Directory Structure

Problems are organized by constraint type, size, and structure:

```
problems/
├── empty/              # Problems with empty initial precedence constraints
│   ├── small/          # 3-5 activities (all YAML files directly here)
│   ├── medium/         # 6-10 activities (all YAML files directly here)
│   └── large/          # 11-15 activities (all YAML files directly here)
└── non_empty/          # Problems with existing precedence constraints
    ├── small/          # 3-5 activities
    │   ├── chain/      # Chain structures (linear sequences)
    │   ├── parallel/   # Parallel structures (minimal constraints)
    │   ├── mixed/      # Mixed structures (combination of chains and parallel)
    │   └── dag/        # DAG structures (directed acyclic graphs)
    ├── medium/         # 6-10 activities
    │   ├── chain/
    │   ├── parallel/
    │   ├── mixed/
    │   └── dag/
    └── large/          # 11-15 activities
        ├── chain/
        ├── parallel/
        ├── mixed/
        └── dag/
```

**Note:** Empty constraint problems don't have structure subdirectories because they all start with `precedence: []` (no constraints). The structure labels in filenames (e.g., `chain_3_high.yaml`) are just naming conventions and don't reflect actual precedence structure.

## Instance Naming Convention

### Empty Constraint Problems
Format: `n{size}_{risk_level}_{counter}.yaml`

- `n{size}`: number of activities (e.g., `n3`, `n11`)
- `risk_level`: medium, high, very_high (KO probability ranges)
- `counter`: 3-digit sequential number (001, 002, ...) to handle multiple instances with same size/risk

Examples:
- `n3_high_001.yaml` - 3 activities, high risk, first instance
- `n11_very_high_015.yaml` - 11 activities, very high risk, 15th instance

**Note:** Structure labels (chain/dag/parallel/mixed) are not used since empty problems have no precedence structure.

### Non-Empty Constraint Problems
Format: `{structure}_{size}_{risk_level}[_variant].yaml`

- `structure`: chain, parallel, mixed, dag
- `size`: number of activities
- `risk_level`: medium, high, very_high (KO probability ranges)
- `variant`: optional variant identifier (e.g., `_v1`)

Examples:
- `chain_5_high.yaml` - Chain structure with 5 activities, high risk
- `dag_12_very_high.yaml` - DAG structure with 12 activities, very high risk
- `parallel_8_medium_v1.yaml` - Parallel structure variant

## Instance Properties

Each instance specifies:
- **Activities**: List of activities with:
  - `id`: Activity identifier (0-indexed)
  - `name`: Human-readable name
  - `duration`: Activity duration (positive float)
  - `ko_probability`: Knockout probability (float in [0,1])
- **Precedence**: List of precedence constraints `[predecessor, successor]`
  - Empty constraint problems have `precedence: []`
  - Non-empty constraint problems have partial precedence relations
- **Metadata**: Problem metadata including:
  - `category`: Structure type (chain, parallel, mixed, dag)
  - `difficulty`: Size category (small, medium, large)
  - `n_activities`: Number of activities
  - `n_precedence`: Number of initial precedence constraints
  - `graph_structure`: Graph structure type
  - `ko_probability_distribution`: Risk level

## Problem Categories

### Empty Constraint Problems
- Start with **no precedence constraints** (`precedence: []`)
- All activities can execute in parallel initially
- Refinement adds precedence constraints from scratch
- Useful for testing when parallel execution is optimal vs. when ordering helps
- **Note:** These problems are organized only by size (small/medium/large), not by structure type, since they have no precedence structure initially

### Non-Empty Constraint Problems
- Start with **partial precedence constraints**
- Refinement extends existing constraints
- More realistic scenarios where some ordering is already required
- Tests refinement of suboptimal initial constraints

## Usage

```bash
# Solve a single instance
python koref_domain.py problems/non_empty/small/chain/chain_3.yaml --config Optimal

# Benchmark all problems
python benchmark.py --type all --time-limit 1800

# Benchmark only empty constraint problems
python benchmark.py --type empty --time-limit 30
```

## Statistics

- **Empty constraint problems**: 136 instances
  - Small: 36 (9 per structure type × 4 structures)
  - Medium: 60 (15 per structure type × 4 structures)
  - Large: 40 (10 per structure type × 4 structures)

- **Non-empty constraint problems**: 92+ instances
  - Organized by size and structure type
  - Various risk levels and variants
