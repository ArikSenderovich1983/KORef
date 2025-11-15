# KORef Problem Instances

This directory contains KORef (KO-plan Refinement) problem instances in YAML format.

## Directory Structure

- `small/` - Small instances (3-5 activities) for testing and validation
- `medium/` - Medium instances (6-10 activities) for performance evaluation
- `large/` - Large instances (11+ activities) for scalability testing

## Instance Naming Convention

Format: `{structure}_{size}_{variant}.yaml`

- `structure`: chain, parallel, mixed, dag
- `size`: number of activities
- `variant`: optional descriptor (e.g., low_risk, high_risk, varied_durations)

## Instance Properties

Each instance specifies:
- Activities with durations and KO probabilities
- Initial precedence constraints
- Metadata about complexity and structure

## Usage

```bash
python koref_domain.py problems/small/chain_3.yaml --config Optimal
```
