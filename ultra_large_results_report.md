# Ultra-Large, Ultra-Risky Problems: Benchmark Results

## Configuration

- **Problem Size**: 100-200 activities
- **Precedence**: Empty
- **Durations**: All unit (1.0)
- **Risk Levels**: high, medium, low
- **Instances**: 10 of each risk level (30 total)
- **Matching**: All parameters match except risk level
- **Solver**: DIDP with DFBB
- **Time Limit**: 30 seconds per problem

## Summary Statistics

- **Total Problems**: 30
- **Completed**: 30/30 (100.0%)
- **Proven Optimal**: 30/30 (100.0%)
- **Problems with Improvement**: 0/30 (0.0%)
- **Average Runtime**: 2.913s
- **Max Runtime**: 6.609s
- **Min Runtime**: 0.905s

## Results by Risk Level

### HIGH Risk

- **Total**: 10
- **Completed**: 10/10 (100.0%)
- **Proven Optimal**: 10/10 (100.0%)
- **Problems with Improvement**: 0/10 (0.0%)
- **Average Runtime**: 2.931s
- **Max Runtime**: 5.749s

### MEDIUM Risk

- **Total**: 10
- **Completed**: 10/10 (100.0%)
- **Proven Optimal**: 10/10 (100.0%)
- **Problems with Improvement**: 0/10 (0.0%)
- **Average Runtime**: 2.848s
- **Max Runtime**: 6.609s

### LOW Risk

- **Total**: 10
- **Completed**: 10/10 (100.0%)
- **Proven Optimal**: 10/10 (100.0%)
- **Problems with Improvement**: 0/10 (0.0%)
- **Average Runtime**: 2.961s
- **Max Runtime**: 4.966s

## Detailed Results

| Instance | N | Risk | Original | Refined | Improvement % | Runtime (s) | Optimal | Status |
|----------|---|------|----------|---------|---------------|-------------|---------|--------|
| ultra_102_high_07 | 102 | high | 9.790 | 9.790 | 0.00% | 0.905 | [YES] | OK |
| ultra_102_low_07 | 102 | low | 9.790 | 9.790 | 0.00% | 1.353 | [YES] | OK |
| ultra_102_medium_07 | 102 | medium | 9.790 | 9.790 | 0.00% | 0.959 | [YES] | OK |
| ultra_118_high_01 | 118 | high | 9.970 | 9.970 | 0.00% | 1.534 | [YES] | OK |
| ultra_118_low_01 | 118 | low | 9.970 | 9.970 | 0.00% | 1.457 | [YES] | OK |
| ultra_118_medium_01 | 118 | medium | 9.970 | 9.970 | 0.00% | 1.386 | [YES] | OK |
| ultra_119_high_08 | 119 | high | 9.970 | 9.970 | 0.00% | 1.550 | [YES] | OK |
| ultra_119_low_08 | 119 | low | 9.970 | 9.970 | 0.00% | 2.282 | [YES] | OK |
| ultra_119_medium_08 | 119 | medium | 9.970 | 9.970 | 0.00% | 1.371 | [YES] | OK |
| ultra_120_high_09 | 120 | high | 9.890 | 9.890 | 0.00% | 1.453 | [YES] | OK |
| ultra_120_low_09 | 120 | low | 9.890 | 9.890 | 0.00% | 2.008 | [YES] | OK |
| ultra_120_medium_09 | 120 | medium | 9.890 | 9.890 | 0.00% | 1.405 | [YES] | OK |
| ultra_126_high_04 | 126 | high | 9.980 | 9.980 | 0.00% | 1.608 | [YES] | OK |
| ultra_126_low_04 | 126 | low | 9.980 | 9.980 | 0.00% | 1.695 | [YES] | OK |
| ultra_126_medium_04 | 126 | medium | 9.980 | 9.980 | 0.00% | 2.346 | [YES] | OK |
| ultra_144_high_02 | 144 | high | 9.930 | 9.930 | 0.00% | 3.549 | [YES] | OK |
| ultra_144_low_02 | 144 | low | 9.930 | 9.930 | 0.00% | 4.180 | [YES] | OK |
| ultra_144_medium_02 | 144 | medium | 9.930 | 9.930 | 0.00% | 4.031 | [YES] | OK |
| ultra_146_high_10 | 146 | high | 10.000 | 10.000 | 0.00% | 3.880 | [YES] | OK |
| ultra_146_low_10 | 146 | low | 10.000 | 10.000 | 0.00% | 3.035 | [YES] | OK |
| ultra_146_medium_10 | 146 | medium | 10.000 | 10.000 | 0.00% | 3.411 | [YES] | OK |
| ultra_156_high_06 | 156 | high | 10.000 | 10.000 | 0.00% | 4.079 | [YES] | OK |
| ultra_156_low_06 | 156 | low | 10.000 | 10.000 | 0.00% | 3.922 | [YES] | OK |
| ultra_156_medium_06 | 156 | medium | 10.000 | 10.000 | 0.00% | 3.645 | [YES] | OK |
| ultra_161_high_03 | 161 | high | 9.960 | 9.960 | 0.00% | 5.000 | [YES] | OK |
| ultra_161_low_03 | 161 | low | 9.960 | 9.960 | 0.00% | 4.966 | [YES] | OK |
| ultra_161_medium_03 | 161 | medium | 9.960 | 9.960 | 0.00% | 6.609 | [YES] | OK |
| ultra_169_high_05 | 169 | high | 10.000 | 10.000 | 0.00% | 5.749 | [YES] | OK |
| ultra_169_low_05 | 169 | low | 10.000 | 10.000 | 0.00% | 4.716 | [YES] | OK |
| ultra_169_medium_05 | 169 | medium | 10.000 | 10.000 | 0.00% | 3.317 | [YES] | OK |

## Comparison: Matching Instances

For each instance ID, compare high vs medium vs low risk:

| Instance ID | N | High Risk | Medium Risk | Low Risk |
|-------------|---|-----------|-------------|----------|
| 01 | 118 | 0.00% | 0.00% | 0.00% |
| 02 | 144 | 0.00% | 0.00% | 0.00% |
| 03 | 161 | 0.00% | 0.00% | 0.00% |
| 04 | 126 | 0.00% | 0.00% | 0.00% |
| 05 | 169 | 0.00% | 0.00% | 0.00% |
| 06 | 156 | 0.00% | 0.00% | 0.00% |
| 07 | 102 | 0.00% | 0.00% | 0.00% |
| 08 | 119 | 0.00% | 0.00% | 0.00% |
| 09 | 120 | 0.00% | 0.00% | 0.00% |
| 10 | 146 | 0.00% | 0.00% | 0.00% |
