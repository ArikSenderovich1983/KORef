# KORef Instance Guide

## Instance Categories

### Small Instances (3-5 activities)
- **chain_3.yaml**: Simple 3-activity chain - good for testing
- **parallel_3.yaml**: 3 parallel activities - tests parallel scheduling
- **mixed_4.yaml**: Mixed structure with 4 activities
- **chain_4.yaml**: Fully specified chain (no refinement needed)
- **high_risk_4.yaml**: High KO probabilities - tests risk management
- **varied_durations_5.yaml**: Highly varied durations - tests duration impact

### Medium Instances (6-10 activities)
- **chain_6.yaml**: 6-activity chain
- **parallel_6.yaml**: 6 parallel activities (15 unresolved pairs)
- **dag_7.yaml**: DAG structure with branching
- **mixed_8.yaml**: Mixed structure with varied properties
- **sparse_10.yaml**: Sparse precedence (43 unresolved pairs)

### Large Instances (11+ activities)
- **chain_12.yaml**: 12-activity chain (fully specified)
- **parallel_15.yaml**: 15 parallel activities (105 unresolved pairs - extreme)
- **mixed_20.yaml**: 20 activities with mixed structure (185 unresolved pairs)

## Complexity Metrics

### Search Space Size
The number of possible refinements is approximately `2^(n_unresolved_pairs)`.
- Small: 2^2 to 2^9 = 4 to 512 refinements
- Medium: 2^17 to 2^43 = 131K to 8.8T refinements
- Large: 2^105 to 2^185 = astronomical

### Difficulty Factors

1. **Number of unresolved pairs**: Primary driver of complexity
   - 0 pairs: Trivial (already fully specified)
   - 1-5 pairs: Easy (exhaustive search feasible)
   - 6-15 pairs: Medium (may need heuristics)
   - 16+ pairs: Hard (requires efficient search)

2. **KO probability distribution**:
   - Low risk (<0.1): Less impact on makespan
   - Medium risk (0.1-0.3): Moderate impact
   - High risk (>0.3): Significant impact, risk-averse strategies important

3. **Duration distribution**:
   - Uniform: Predictable schedules
   - Varied: More complex overlap calculations
   - Highly varied: Long tasks dominate makespan

4. **Graph structure**:
   - Chain: Simple, linear dependencies
   - Parallel: Maximum concurrency, maximum risk
   - Mixed/DAG: Balanced complexity

## Recommended Testing Order

1. **Validation**: Start with `chain_3.yaml` and `parallel_3.yaml`
2. **Small scale**: Test all small instances
3. **Medium scale**: Progress to medium instances
4. **Large scale**: Use large instances for scalability testing

## Expected Solve Times (Optimal Exhaustive)

- Small (3-5 activities): < 1 second
- Medium (6-8 activities): 1 second to 1 minute
- Medium (9-10 activities): 1 minute to 1 hour (depends on unresolved pairs)
- Large (11+ activities): Hours to days (may need time limits)

## Usage Examples

```bash
# Quick validation
python koref_domain.py problems/small/chain_3.yaml --config Optimal

# Medium instance with time limit
python koref_domain.py problems/medium/parallel_6.yaml --config Optimal --time-out 300

# Large instance (may not complete)
python koref_domain.py problems/large/parallel_15.yaml --config Optimal --time-out 3600
```
