# KORef Benchmark Results

Comparison of original vs refined solutions for all problem instances.

## Results Summary

| Instance | Original Makespan | Refined Makespan | Improvement | Improvement % | Runtime (s) | Status |
|----------|-------------------|------------------|-------------|--------------|-------------|--------|
| chain_12.yaml | 4.692158 | 4.692158 | 0.000000 | 0.00% | 0.00 | ✓ |
| chain_50.yaml | 9.640736 | 9.640736 | 0.000000 | 0.00% | 0.02 | ✓ |
| dag_50.yaml | 7.600106 | 7.600106 | 0.000000 | 0.00% | 0.10 | ✓ |
| mixed_20.yaml | 6.000001 | 6.000001 | 0.000000 | 0.00% | 0.01 | ✓ |
| mixed_50.yaml | 7.816057 | 7.816057 | 0.000000 | 0.00% | 0.10 | ✓ |
| parallel_15.yaml | 6.000000 | 6.000000 | 0.000000 | 0.00% | 0.00 | ✓ |
| parallel_50.yaml | 8.000000 | 8.000000 | 0.000000 | 0.00% | 0.10 | ✓ |
| chain_6.yaml | 7.478757 | 7.478757 | 0.000000 | 0.00% | 0.00 | ✓ |
| dag_7.yaml | 3.547143 | 3.547143 | 0.000000 | 0.00% | 0.00 | ✓ |
| mixed_8.yaml | 10.005016 | 10.005016 | 0.000000 | 0.00% | 0.00 | ✓ |
| parallel_6.yaml | 6.000000 | 6.000000 | 0.000000 | 0.00% | 0.00 | ✓ |
| sparse_10.yaml | 6.010859 | 6.010859 | 0.000000 | 0.00% | 0.00 | ✓ |
| chain_3.yaml | 5.948600 | 5.948600 | 0.000000 | 0.00% | 0.00 | ✓ |
| chain_4.yaml | 6.240234 | 6.240234 | 0.000000 | 0.00% | 0.00 | ✓ |
| high_risk_4.yaml | 5.000000 | 5.000000 | 0.000000 | 0.00% | 0.00 | ✓ |
| mixed_4.yaml | 5.510000 | 4.550000 | 0.960000 | 17.42% | 0.00 | ✓ |
| parallel_3.yaml | 5.000000 | 5.000000 | 0.000000 | 0.00% | 0.00 | ✓ |
| varied_durations_5.yaml | 15.000000 | 15.000000 | 0.000000 | 0.00% | 0.00 | ✓ |

## Summary Statistics

- **Successfully solved**: 18/18
- **Optimal solutions**: 18/18
- **Average improvement**: 0.97%
- **Total runtime**: 0.35s (0.01 minutes)

## Notes

- All problems use knockout-heavy probabilities (0.3-0.8 range)
- Original makespan: Expected makespan of the original precedence
- Refined makespan: Optimal expected makespan after refinement
- Improvement: Difference between original and refined makespan
- Status: OK = Optimal solution found, FAIL = Failed to find solution
