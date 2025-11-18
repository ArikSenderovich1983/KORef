# Runtime & Problem Difficulty Analysis for KORef

This document discusses what factors make KORef instances computationally difficult, based on theoretical analysis and empirical observations from our benchmarks.

---

## Overview

The KORef problem involves finding an optimal precedence relation that minimizes expected makespan under stochastic knockout events. The computational difficulty depends on both the **search space size** (how many solutions exist) and the **landscape complexity** (how hard it is to find the optimum).

---

## Factors Affecting Computational Difficulty

### 1. **Number of Activities (n)** - PRIMARY DRIVER

**Impact**: Exponential growth in search space

**Why it matters**:
- Unresolved pairs: `k = n(n-1)/2` for empty initial precedence
- Search space: `2^k` possible refinements
- Terminal states: Up to `n!` total orderings

**Concrete examples**:
```
n=3:  3 unresolved pairs → 8 search states, 6 orderings
n=5:  10 unresolved pairs → 1,024 search states, 120 orderings
n=10: 45 unresolved pairs → 2^45 search states, 3.6M orderings
n=15: 105 unresolved pairs → 2^105 search states, 1.3×10^12 orderings
n=20: 190 unresolved pairs → 2^190 search states, 2.4×10^18 orderings
```

**Benchmark evidence**:
- Small (n=3-5): Avg runtime 0.008s
- Medium (n=6-10): Avg runtime 0.031s (4× slower)
- Large (n=11-15): Avg runtime 0.173s (5.6× slower)

**Conclusion**: **n is the dominant factor**. Even small increases cause dramatic slowdowns.

---

### 2. **Initial Precedence Density** - REDUCES DIFFICULTY

**Impact**: More initial constraints = smaller search space

**Why it matters**:
- Initial constraints reduce unresolved pairs
- Fewer decisions to make
- Pruning via cycle detection is more effective

**Examples**:
```
Empty precedence (n=10):
  Unresolved pairs: 45
  Search space: 2^45

DAG precedence (n=10, 20 constraints):
  Unresolved pairs: ~25
  Search space: 2^25 (much smaller!)

Chain precedence (n=10):
  Unresolved pairs: 0
  Search space: 1 (trivial!)
```

**Benchmark evidence**:
- Empty constraints: 9.6% show improvement (more freedom to optimize)
- Non-empty constraints: 5.4% show improvement (less freedom, but faster)

**Conclusion**: **More initial constraints make problems easier** (smaller search space), but may limit optimization potential.

---

### 3. **Risk Profile: Proportion & Distribution** - COMPLEX INTERACTION

**Impact**: Affects optimization landscape, not just search space size

#### 3.1. Overall Risk Level

**Low risk** (all p(i) ≈ 0):
- Expected makespan ≈ deterministic makespan
- Optimal solution: parallelize everything (CPM-like)
- **Easy to optimize**: Clear objective, simple landscape

**Medium risk** (p(i) ≈ 0.1-0.3):
- Significant but not dominant knockout probability
- Trade-off between parallelism and risk management
- **Moderately difficult**: Multiple local optima possible

**High risk** (p(i) ≈ 0.5-0.7):
- Knockouts are likely
- Strategic sequencing can significantly reduce expected makespan
- **Most interesting**: Large improvement potential (we see up to 52% improvement!)

**Very high risk** (all p(i) ≈ 0.9):
- Almost certain knockout
- Optimal: execute highest-risk activities first (greedy)
- **Easy to optimize**: Clear strategy emerges

**Benchmark evidence**:
- High risk: 9.9% of problems improved, avg improvement 12.7% when improved
- Very high risk: Only 4.2% improved, avg 0.9% (already near-optimal?)
- Medium risk: 6.2% improved, avg 6.2%

**Interpretation**: High risk (not very high) creates the most interesting optimization landscape with significant improvement potential.

#### 3.2. Risk Heterogeneity

**Homogeneous risk** (all p(i) similar):
- Activities are interchangeable from risk perspective
- Ordering matters less
- **Easier**: Fewer strategic choices

**Heterogeneous risk** (p(i) varies widely):
- Clear high-risk vs low-risk activities
- Strategic ordering: high-risk first or last?
- **More difficult**: Complex interactions between activities

**Example**:
```
Homogeneous: [0.3, 0.3, 0.3, 0.3]
  → All orderings relatively similar in expected makespan
  → Flat landscape, easy to optimize

Heterogeneous: [0.8, 0.1, 0.7, 0.05]
  → Ordering 0,2 first vs last makes huge difference
  → Rugged landscape, more local optima
```

---

### 4. **Duration Variance** - MODERATE IMPACT

**Impact**: Affects overlap calculations and abort times

**Why it matters**:
- Large duration variance → more potential for overlaps
- Overlaps determine abort times, which affect expected makespan
- Strategic sequencing becomes more important

**Short durations (all d(i) ≈ 1)**:
- Activities complete quickly
- Less overlap in parallel execution
- Knockouts affect fewer activities
- **Easier**: Less complex overlap calculations

**Long durations (all d(i) ≈ 10)**:
- More overlap potential
- Knockouts affect many activities
- Sequencing choices matter more
- **Moderate difficulty**: More strategic depth

**Heterogeneous durations** (d varies widely):
- Long activities create "bottlenecks"
- Short activities can overlap with long ones
- Complex abort time calculations
- **More difficult**: Intricate interactions

**Example**:
```
Uniform durations [2, 2, 2]:
  → Simple overlap structure
  
Varied durations [1, 10, 1]:
  → Activity 1 (long) creates complex overlaps
  → Strategic placement of activity 1 critical
```

---

### 5. **Risk-Duration Correlation** - MOST COMPLEX

**Impact**: Creates strategic trade-offs

#### Scenario 1: High risk, short duration
```
Activities: [d=1, p=0.8]
Strategy: Execute early (fails fast, cuts off early)
Result: Can significantly reduce expected makespan
```

#### Scenario 2: High risk, long duration
```
Activities: [d=10, p=0.8]
Strategy: Unclear! 
  - Early execution: Fails fast BUT wastes 10 time units
  - Late execution: Maximizes work done before knockout
Result: Complex optimization, multiple local optima
```

#### Scenario 3: Low risk, long duration
```
Activities: [d=10, p=0.1]
Strategy: Execute in parallel (unlikely to knockout, maximize throughput)
Result: Relatively simple
```

**Most difficult instances**:
- **Negative correlation**: High-risk activities have long durations
  - Creates painful trade-offs
  - "Should we risk wasting 10 time units for potential early cutoff?"
  - Multiple competing strategies

- **Positive correlation**: High-risk activities have short durations
  - More straightforward: fail fast
  - Clear optimal strategy emerges
  - Easier to optimize

---

### 6. **Structure Type** - MODERATE IMPACT

**DAG (Directed Acyclic Graph)**:
- Partial ordering already established
- Reduces unresolved pairs
- Cycle detection is more constraining
- **Easier**: Smaller effective search space

**Mixed constraints**:
- Some chains, some parallel opportunities
- Moderate flexibility
- **Moderate difficulty**

**Parallel (mostly independent)**:
- Maximum unresolved pairs
- Most freedom to reorder
- BUT: Often optimal is just parallel execution (no improvement)
- **Moderate difficulty**: Large space but often trivial optimum

**Chain (total order)**:
- No unresolved pairs
- Only one valid ordering
- **Trivial**: No optimization possible

---

## Predicted "Hardest" Instance Characteristics

Based on the above analysis, the **most computationally difficult** instances would have:

### 1. **Large n** (15-20 activities)
- Exponential explosion in search space
- Exhaustive search becomes infeasible

### 2. **Empty or sparse initial precedence**
- Maximum unresolved pairs
- No pruning from existing constraints

### 3. **Heterogeneous, medium-high risk** (p ∈ [0.3, 0.7], varying)
- Not too low (would be trivial - parallel optimal)
- Not too high (greedy strategy works)
- Varied enough to create strategic choices

### 4. **Heterogeneous durations with negative risk correlation**
- High-risk activities have long durations
- Creates painful strategic trade-offs
- Multiple local optima

### 5. **Moderate overlap potential**
- Durations that allow significant overlaps
- Makes abort time calculations complex
- Strategic sequencing critical

---

## Example "Hard" Instance

```yaml
n: 18
durations: [12, 2, 15, 3, 20, 1, 18, 4, 10, 8, 14, 5, 16, 3, 11, 6, 13, 2]
probabilities: [0.6, 0.1, 0.7, 0.2, 0.8, 0.05, 0.65, 0.15, 0.5, 0.3, 0.55, 0.2, 0.7, 0.1, 0.6, 0.25, 0.65, 0.08]
precedence: []  # Empty

Properties:
- Large n (18) → 153 unresolved pairs, 2^153 search space
- Empty precedence → maximum freedom
- Negative risk-duration correlation: 
  - Activities 4 (d=20, p=0.8), 2 (d=15, p=0.7) are painful
  - Short activities have low risk
- Heterogeneous in both dimensions
- Many opportunities for overlaps
```

**Why this is hard**:
1. **Huge search space**: Cannot exhaustively explore in reasonable time
2. **Complex landscape**: Multiple local optima due to risk-duration trade-offs
3. **Strategic depth**: Many different orderings could be near-optimal
4. **No clear heuristic**: Neither "high-risk first" nor "long-duration last" is clearly optimal

---

## Example "Easy" Instance

```yaml
n: 5
durations: [2, 2, 2, 2, 2]
probabilities: [0.9, 0.9, 0.9, 0.9, 0.9]
precedence: [(0,1), (1,2), (2,3), (3,4)]  # Chain

Properties:
- Small n (5)
- Already a total order (chain)
- Homogeneous durations
- Very high risk (greedy strategy: doesn't matter, already serialized)
```

**Why this is easy**:
1. **Tiny search space**: Already fully ordered
2. **Trivial optimization**: No decisions to make
3. **Clear objective**: Expected makespan is deterministic given the chain

---

## What Our Benchmarks Reveal

### Surprising Findings

1. **Small is hard (sometimes)**:
   - Small n=4 problems showed 52% improvement
   - Why? With few activities, strategic sequencing makes huge difference
   - High-risk, empty precedence, small n → very sensitive to ordering

2. **Large is not always harder**:
   - Large n with dense precedence can be easier than small n with sparse precedence
   - Search space size matters more than n alone

3. **High risk (not very high) is the sweet spot**:
   - Very high risk: already optimal (fail fast)
   - High risk: significant strategic potential
   - Medium risk: moderate potential
   - Low risk: parallel is optimal (trivial)

4. **Empty precedence problems improve more often**:
   - 9.6% vs 5.4% for non-empty
   - More freedom → more optimization potential
   - But also larger search space → longer runtime

### Runtime Predictors (in order of importance)

1. **Number of unresolved pairs** (function of n and initial precedence density)
2. **Risk heterogeneity** (variance in probabilities)
3. **Duration heterogeneity** (variance in durations)
4. **Risk-duration correlation** (negative correlation is harder)
5. **Overall risk level** (medium-high is hardest)

---

## Implications for Algorithm Design

### For Exact Methods (DFBB):

**Tractable** (n ≤ 15):
- Exhaustive search feasible
- Proven optimal solutions
- Reasonable runtimes (<1 minute)

**Borderline** (n = 16-20):
- Time limits necessary
- May need early termination
- Best solution found may not be proven optimal

**Intractable** (n > 20):
- Exponential explosion
- Need heuristic approaches
- Focus on good solutions, not optimality

### For Heuristic Methods:

**Key challenge**: Complex landscape with multiple local optima

**Promising approaches**:
1. **Greedy by risk**: Sequence high-risk activities first (or last)
2. **Critical path**: Consider duration-based scheduling
3. **Hybrid**: Balance risk and duration in priority function
4. **Local search**: Start with heuristic, improve iteratively
5. **Decomposition**: Break into independent sub-problems when possible

### For Instance Generation:

**To create challenging benchmarks**:
1. Use n ∈ [15, 25] (large but not impossibly large)
2. Use sparse precedence (empty or DAG with low density)
3. Use heterogeneous, medium-high risk (0.3-0.7 range)
4. Use negative risk-duration correlation
5. Use varied durations to create overlap complexity

---

## Future Work

### Theoretical Questions

1. **Can we bound the improvement potential?**
   - Given n, risk profile, durations, what's the maximum possible improvement?
   - This could help detect when optimal is reached early

2. **Are there problem classes with polynomial algorithms?**
   - Homogeneous risk + uniform durations?
   - Chain precedence + any risk profile?

3. **What's the approximation complexity?**
   - Can we guarantee (1+ε)-approximation in polynomial time?

### Empirical Questions

1. **Does risk-duration correlation predict runtime?**
   - Need controlled experiments varying only correlation
   
2. **What's the phase transition?**
   - At what n does exhaustive search become infeasible?
   - How does this depend on other parameters?

3. **How good are simple heuristics?**
   - Test "high-risk first", "long-duration last", etc.
   - Compare against optimal on small instances

---

## Conclusion

**The KORef problem difficulty is primarily driven by**:

1. **Search space size** → Number of activities and initial precedence density
2. **Landscape complexity** → Risk heterogeneity and risk-duration interaction
3. **Computational complexity** → Overlap calculations and abort time determination

**Most difficult instances combine**:
- Large n (15-20)
- Sparse initial precedence
- Heterogeneous medium-high risk
- Negative risk-duration correlation

**Most interesting instances** (high improvement potential):
- Small-medium n (4-10)
- Empty precedence
- High (not very high) risk
- Strategic trade-offs between risk and duration

**For practical solving**:
- n ≤ 15: Exhaustive search (DFBB) is feasible and guarantees optimality
- n > 15: Need heuristics or bounded search with early termination
- Focus optimization efforts on high-risk, heterogeneous instances where improvement potential is largest

