# KORef Benchmark Results: Main Takeaways

## Executive Summary

- **Total Problems**: 364
- **Problems with Improvement**: 32 (8.8%)
- **Average Improvement** (for improved problems): 10.51%
- **Maximum Improvement**: 52.43%
- **All Problems Solved to Optimality**: 100%
- **Average Runtime**: 0.003s

## Key Finding: High-Risk Scenarios Benefit More from Refinement

### Risk Level Analysis (Empty Problems)

| Risk Level | Total | Improved | Improvement Rate | Avg Improvement | Max Improvement |
|------------|-------|----------|------------------|----------------|-----------------|
| high | 208 | 22 | 10.6% | 13.08% | 52.43% |
| medium | 64 | 4 | 6.2% | 3.41% | 5.79% |

### High vs Medium Risk Comparison

- **High Risk**: 10.6% improvement rate (22/208 problems)
  - Average improvement: 13.08%
- **Medium Risk**: 6.2% improvement rate (4/64 problems)
  - Average improvement: 3.41%

**Conclusion**: High-risk scenarios show **1.69x** higher improvement rate and **3.84x** larger average improvement magnitude.

## Main Takeaways

### 1. Refinement is Selective but Powerful

- Only 8.8% of problems benefit from refinement
- However, when refinement helps, the improvements can be substantial (up to 52.43%)
- This suggests that refinement is most valuable for specific problem configurations

### 2. High-Risk Scenarios Are Prime Candidates for Refinement

- High-risk problems show significantly higher improvement rates
- The top 6 improvements all come from high-risk scenarios:
  - n4_high_012: 52.43%
  - n4_high_018: 52.43%
  - n5_high_015: 29.63%
  - n5_high_030: 29.63%
  - n5_high_010: 22.00%
  - n5_high_016: 22.00%

- **Why?** High knockout probabilities create more opportunities for strategic ordering:
  - Placing risky activities early can lead to early termination
  - Strategic serialization can reduce expected makespan when knockouts are likely
  - The trade-off between parallelism and fail-fast becomes more pronounced

### 3. Problem Size Influences Refinement Success

| Size | Improvement Rate | Avg Improvement |
|------|------------------|-----------------|
| small | 11.8% (12/102) | 18.83% |
| medium | 5.4% (8/149) | 6.34% |
| large | 10.6% (12/113) | 4.98% |

- Smaller problems show higher improvement rates (more opportunities for optimization)
- However, larger problems can still benefit significantly (e.g., n13_high instances)

### 4. Empty Precedence vs Non-Empty Precedence

- **Empty**: 9.6% improvement rate (26/272)
- **Non-Empty**: 6.5% improvement rate (6/92)

- Empty precedence problems have more degrees of freedom for refinement
- Non-empty problems are often already well-structured

### 5. Computational Efficiency

- **100% optimality**: All problems solved to proven optimality
- **Fast runtime**: Average 0.003s per problem
- **No timeouts**: All problems solved within 30s budget
- DIDP with DFBB is highly effective for KORef problems up to 15 activities

### 6. Structure-Specific Insights (Non-Empty Problems)

| Structure | Improvement Rate | Avg Improvement |
|-----------|------------------|-----------------|
| chain | 0.0% (0/23) | 0.00% |
| parallel | 8.7% (2/23) | 14.88% |
| mixed | 8.0% (2/25) | 2.42% |
| dag | 9.5% (2/21) | 0.15% |

- Parallel structures show notable improvements (e.g., parallel_6_medium: 17.27%)
- Mixed structures also benefit from strategic refinement

## Implications for Practice

1. **When to Apply Refinement**: Focus on high-risk scenarios with empty or sparse precedence constraints
2. **Expected Benefits**: While not universal, refinement can yield substantial improvements (10-50%+) when applicable
3. **Computational Feasibility**: Optimal refinement is computationally tractable for problems up to 15 activities
4. **Problem Characteristics**: The combination of high risk, small-medium size, and empty precedence is most promising

## Top 10 Improvements

| Rank | Instance | Risk | Size | Improvement % |
|------|----------|------|------|---------------|
| 1 | n4_high_012 | high | small | 52.43% |
| 2 | n4_high_018 | high | small | 52.43% |
| 3 | n5_high_015 | high | small | 29.63% |
| 4 | n5_high_030 | high | small | 29.63% |
| 5 | n5_high_010 | high | small | 22.00% |
| 6 | n5_high_016 | high | small | 22.00% |
| 7 | parallel_6_medium | medium | medium | 17.27% |
| 8 | n13_high_011 | high | large | 13.92% |
| 9 | n13_high_017 | high | large | 13.92% |
| 10 | parallel_13 | unknown | large | 12.50% |
