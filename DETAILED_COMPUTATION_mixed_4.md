# Detailed Pen-and-Paper Computation: mixed_4 Problem

## Problem Specification

**Activities:**
- Activity 0 (Start): duration = 2.0, KO probability = 0.05
- Activity 1 (Parallel_A): duration = 4.0, KO probability = 0.20
- Activity 2 (Parallel_B): duration = 3.0, KO probability = 0.15
- Activity 3 (End): duration = 5.0, KO probability = 0.10

**Initial Precedence Constraints:**
- 0 → 1 (Start must precede Parallel_A)
- 0 → 2 (Start must precede Parallel_B)

**Unresolved Pairs:** {(0,3), (1,2), (1,3), (2,3)}

---

## Part 1: Canonical Schedule Expected Makespan

### Step 1: Compute Earliest-Start Schedule

Given initial precedence: {0→1, 0→2}

**Topological Order:**
- Activity 0 has no predecessors → start at 0.0
- Activities 1 and 2 depend on 0 → start after 0 finishes
- Activity 3 has no constraints → can start at 0.0

**Schedule Computation:**
```
s(0) = 0.0  (no predecessors)
f(0) = 0.0 + 2.0 = 2.0

s(1) = max{f(0)} = max{2.0} = 2.0  (must wait for 0)
f(1) = 2.0 + 4.0 = 6.0

s(2) = max{f(0)} = max{2.0} = 2.0  (must wait for 0)
f(2) = 2.0 + 3.0 = 5.0

s(3) = 0.0  (no constraints)
f(3) = 0.0 + 5.0 = 5.0
```

**Canonical Schedule:**
- Activity 0: start = 0.0, finish = 2.0
- Activity 1: start = 2.0, finish = 6.0
- Activity 2: start = 2.0, finish = 5.0
- Activity 3: start = 0.0, finish = 5.0

**Deterministic Makespan:** T = max{2.0, 6.0, 5.0, 5.0} = 6.0

### Step 2: Overlap Analysis

Check which activities overlap:

**Activity 0 [0.0, 2.0):**
- Overlaps with 3? [0.0, 2.0) ∩ [0.0, 5.0) = [0.0, 2.0) ≠ ∅ → YES
- Overlaps with 1? [0.0, 2.0) ∩ [2.0, 6.0) = ∅ → NO
- Overlaps with 2? [0.0, 2.0) ∩ [2.0, 5.0) = ∅ → NO

**Activity 1 [2.0, 6.0):**
- Overlaps with 2? [2.0, 6.0) ∩ [2.0, 5.0) = [2.0, 5.0) ≠ ∅ → YES
- Overlaps with 3? [2.0, 6.0) ∩ [0.0, 5.0) = [2.0, 5.0) ≠ ∅ → YES

**Activity 2 [2.0, 5.0):**
- Overlaps with 1? [2.0, 5.0) ∩ [2.0, 6.0) = [2.0, 5.0) ≠ ∅ → YES
- Overlaps with 3? [2.0, 5.0) ∩ [0.0, 5.0) = [2.0, 5.0) ≠ ∅ → YES

**Activity 3 [0.0, 5.0):**
- Overlaps with 0? [0.0, 5.0) ∩ [0.0, 2.0) = [0.0, 2.0) ≠ ∅ → YES
- Overlaps with 1? [0.0, 5.0) ∩ [2.0, 6.0) = [2.0, 5.0) ≠ ∅ → YES
- Overlaps with 2? [0.0, 5.0) ∩ [2.0, 5.0) = [2.0, 5.0) ≠ ∅ → YES

### Step 3: Compute Abort Times

For each activity, abort time = max finish time of all overlapping activities:

```
τ(0) = max{f(0), f(3)} = max{2.0, 5.0} = 5.0
τ(1) = max{f(1), f(2), f(3)} = max{6.0, 5.0, 5.0} = 6.0
τ(2) = max{f(1), f(2), f(3)} = max{6.0, 5.0, 5.0} = 6.0
τ(3) = max{f(0), f(1), f(2), f(3)} = max{2.0, 6.0, 5.0, 5.0} = 6.0
```

### Step 4: Group into Buckets by Abort Time

Distinct abort times: {5.0, 6.0}

**Bucket 1 (t₁ = 5.0):** S₁ = {0}
**Bucket 2 (t₂ = 6.0):** S₂ = {1, 2, 3}

### Step 5: Compute Survival Probabilities

**Bucket 1:**
Q₁ = (1 - p(0)) = (1 - 0.05) = 0.95

**Bucket 2:**
Q₂ = (1 - p(1)) × (1 - p(2)) × (1 - p(3))
   = (1 - 0.20) × (1 - 0.15) × (1 - 0.10)
   = 0.80 × 0.85 × 0.90
   = 0.612

### Step 6: Compute Cumulative Probabilities

P₀ = 1.0
P₁ = P₀ × Q₁ = 1.0 × 0.95 = 0.95
P₂ = P₁ × Q₂ = 0.95 × 0.612 = 0.5814

### Step 7: Compute Expected Makespan

E[M] = Σ(t_j × P_{j-1} × (1 - Q_j)) + T × P_k

E[M] = t₁ × P₀ × (1 - Q₁) + t₂ × P₁ × (1 - Q₂) + T × P₂
     = 5.0 × 1.0 × (1 - 0.95) + 6.0 × 0.95 × (1 - 0.612) + 6.0 × 0.5814
     = 5.0 × 0.05 + 6.0 × 0.95 × 0.388 + 3.4884
     = 0.25 + 2.2116 + 3.4884
     = **5.95**

**Canonical Expected Makespan: 5.95**

---

## Part 2: Refinement DP Computation

### DP State Space

**State:** S = (precedence_relation, unresolved_pairs)

**Initial State S₀:**
- Precedence: {0→1, 0→2}
- Unresolved: {(0,3), (1,2), (1,3), (2,3)}

### Bellman Equation

For terminal states:
```
V(S_terminal) = ExpectedMakespan(S_terminal)
```

For non-terminal states:
```
V(S) = min_{unresolved pair (a,b)} [V(S + a<b), V(S + b<a)]
```

### Enumeration of All Valid Refinements

We have 4 unresolved pairs, so 2⁴ = 16 possible combinations.
After filtering cycles, we get 8 valid refinements.

#### Refinement 1: {0→3, 1→2, 1→3, 2→3}

**Precedence:** {0→1, 0→2, 0→3, 1→2, 1→3, 2→3}

**Schedule:**
```
s(0) = 0.0
f(0) = 2.0

s(1) = max{f(0)} = 2.0
f(1) = 6.0

s(2) = max{f(0), f(1)} = max{2.0, 6.0} = 6.0
f(2) = 9.0

s(3) = max{f(0), f(1), f(2)} = max{2.0, 6.0, 9.0} = 9.0
f(3) = 14.0
```

**Schedule:** {0: 0.0, 1: 2.0, 2: 6.0, 3: 9.0}
**T = 14.0**

**Overlap Analysis:**
- No overlaps (sequential execution)

**Abort Times:**
```
τ(0) = f(0) = 2.0
τ(1) = f(1) = 6.0
τ(2) = f(2) = 9.0
τ(3) = f(3) = 14.0
```

**Buckets:**
- Bucket 1 (t₁ = 2.0): S₁ = {0}, Q₁ = 0.95
- Bucket 2 (t₂ = 6.0): S₂ = {1}, Q₂ = 0.80
- Bucket 3 (t₃ = 9.0): S₃ = {2}, Q₃ = 0.85
- Bucket 4 (t₄ = 14.0): S₄ = {3}, Q₄ = 0.90

**Cumulative Probabilities:**
P₀ = 1.0
P₁ = 0.95
P₂ = 0.95 × 0.80 = 0.76
P₃ = 0.76 × 0.85 = 0.646
P₄ = 0.646 × 0.90 = 0.5814

**Expected Makespan:**
E[M] = 2.0×1.0×(1-0.95) + 6.0×0.95×(1-0.80) + 9.0×0.76×(1-0.85) + 14.0×0.646×(1-0.90) + 14.0×0.5814
     = 2.0×0.05 + 6.0×0.19 + 9.0×0.114 + 14.0×0.0646 + 8.1396
     = 0.1 + 1.14 + 1.026 + 0.9044 + 8.1396
     = **11.31**

#### Refinement 2: {0→3, 2→1, 1→3, 2→3}

**Precedence:** {0→1, 0→2, 0→3, 2→1, 1→3, 2→3}

**Schedule:**
```
s(0) = 0.0, f(0) = 2.0
s(2) = max{f(0)} = 2.0, f(2) = 5.0
s(1) = max{f(0), f(2)} = max{2.0, 5.0} = 5.0, f(1) = 9.0
s(3) = max{f(0), f(1), f(2)} = max{2.0, 9.0, 5.0} = 9.0, f(3) = 14.0
```

**Schedule:** {0: 0.0, 2: 2.0, 1: 5.0, 3: 9.0}
**T = 14.0**

**Abort Times:** (sequential, no overlaps)
τ(0) = 2.0, τ(2) = 5.0, τ(1) = 9.0, τ(3) = 14.0

**Buckets:**
- Bucket 1 (t₁ = 2.0): {0}, Q₁ = 0.95
- Bucket 2 (t₂ = 5.0): {2}, Q₂ = 0.85
- Bucket 3 (t₃ = 9.0): {1}, Q₃ = 0.80
- Bucket 4 (t₄ = 14.0): {3}, Q₄ = 0.90

**Cumulative Probabilities:**
P₀ = 1.0, P₁ = 0.95, P₂ = 0.8075, P₃ = 0.646, P₄ = 0.5814

**Expected Makespan:**
E[M] = 2.0×1.0×0.05 + 5.0×0.95×0.15 + 9.0×0.8075×0.20 + 14.0×0.646×0.10 + 14.0×0.5814
     = 0.1 + 0.7125 + 1.4535 + 0.9044 + 8.1396
     = **11.31**

#### Refinement 3: {0→3, 1→2, 1→3, 3→2}

**Precedence:** {0→1, 0→2, 0→3, 1→2, 1→3, 3→2}

**Schedule:**
```
s(0) = 0.0, f(0) = 2.0
s(1) = 2.0, f(1) = 6.0
s(3) = max{f(0), f(1)} = max{2.0, 6.0} = 6.0, f(3) = 11.0
s(2) = max{f(0), f(1), f(3)} = max{2.0, 6.0, 11.0} = 11.0, f(2) = 14.0
```

**Schedule:** {0: 0.0, 1: 2.0, 3: 6.0, 2: 11.0}
**T = 14.0**

**Abort Times:** (sequential)
τ(0) = 2.0, τ(1) = 6.0, τ(3) = 11.0, τ(2) = 14.0

**Buckets:**
- Bucket 1 (t₁ = 2.0): {0}, Q₁ = 0.95
- Bucket 2 (t₂ = 6.0): {1}, Q₂ = 0.80
- Bucket 3 (t₃ = 11.0): {3}, Q₃ = 0.90
- Bucket 4 (t₄ = 14.0): {2}, Q₄ = 0.85

**Cumulative Probabilities:**
P₀ = 1.0, P₁ = 0.95, P₂ = 0.76, P₃ = 0.684, P₄ = 0.5814

**Expected Makespan:**
E[M] = 2.0×0.05 + 6.0×0.19 + 11.0×0.76×0.10 + 14.0×0.684×0.15 + 14.0×0.5814
     = 0.1 + 1.14 + 0.836 + 1.4364 + 8.1396
     = **11.652**

#### Refinement 4: {0→3, 2→1, 3→1, 2→3}

**Precedence:** {0→1, 0→2, 0→3, 2→1, 3→1, 2→3}

**Schedule:**
```
s(0) = 0.0, f(0) = 2.0
s(2) = 2.0, f(2) = 5.0
s(3) = max{f(0), f(2)} = max{2.0, 5.0} = 5.0, f(3) = 10.0
s(1) = max{f(0), f(2), f(3)} = max{2.0, 5.0, 10.0} = 10.0, f(1) = 14.0
```

**Schedule:** {0: 0.0, 2: 2.0, 3: 5.0, 1: 10.0}
**T = 14.0**

**Abort Times:** (sequential)
τ(0) = 2.0, τ(2) = 5.0, τ(3) = 10.0, τ(1) = 14.0

**Buckets:**
- Bucket 1 (t₁ = 2.0): {0}, Q₁ = 0.95
- Bucket 2 (t₂ = 5.0): {2}, Q₂ = 0.85
- Bucket 3 (t₃ = 10.0): {3}, Q₃ = 0.90
- Bucket 4 (t₄ = 14.0): {1}, Q₄ = 0.80

**Cumulative Probabilities:**
P₀ = 1.0, P₁ = 0.95, P₂ = 0.8075, P₃ = 0.72675, P₄ = 0.5814

**Expected Makespan:**
E[M] = 2.0×0.05 + 5.0×0.95×0.15 + 10.0×0.8075×0.10 + 14.0×0.72675×0.20 + 14.0×0.5814
     = 0.1 + 0.7125 + 0.8075 + 2.0349 + 8.1396
     = **11.795**

#### Refinements 5-8: (Similar computation, higher makespans)

**Refinement 5:** {0→3, 1→2, 3→1, 3→2} → E[M] = 12.222
**Refinement 6:** {0→3, 2→1, 3→1, 3→2} → E[M] = 12.222
**Refinement 7:** {3→0, 2→1, 3→1, 3→2} → E[M] = 12.272
**Refinement 8:** {3→0, 1→2, 3→1, 3→2} → E[M] = 12.272

### Optimal Solution via DP

**Bellman Optimality:**
```
V(S₀) = min{V(S_canonical), V(S_terminal₁), V(S_terminal₂), ..., V(S_terminal₈)}
       = min{5.95, 11.31, 11.31, 11.652, 11.795, 12.222, 12.222, 12.272, 12.272}
       = 5.95
```

**Optimal Solution:**
- Type: Canonical schedule (empty refinement)
- Constraints Added: [] (none - using original precedence only)
- Expected Makespan: **5.95**

---

## Comparison: Canonical vs Complete Refinements

| Schedule Type | Expected Makespan | Schedule Structure |
|--------------|------------------|-------------------|
| **Canonical** (empty refinement) | **5.95** ⭐ OPTIMAL | Parallel: 0&3 together, then 1&2 together |
| **Best Complete Refinement** | **11.31** | Sequential: 0→1→2→3 |

### Key Insight

The canonical schedule has **lower expected makespan** (5.95) than all complete refinements (≥11.31). This demonstrates:

1. **Canonical schedule maximizes parallelism:**
   - Activities 0 and 3 run in parallel (overlap: [0,2) ∩ [0,5))
   - Activities 1 and 2 run in parallel after 0 (overlap: [2,6) ∩ [2,5))
   - Deterministic makespan: max{2, 6, 5, 5} = 6.0
   - Parallelism reduces completion time despite KO risk

2. **Complete refinements force sequential execution:**
   - All activities execute sequentially (no overlaps)
   - Deterministic makespan: 2+4+3+5 = 14.0
   - Eliminates KO risk but increases completion time significantly
   - The benefit of parallelism outweighs the KO risk

3. **Theorem Application:**
   - For the canonical refinement (empty), we use the canonical earliest-start schedule ✓
   - For each complete refinement, we use the canonical earliest-start schedule for that refinement ✓
   - We correctly minimize over all refinements using canonical schedules ✓

**Conclusion:** For this problem instance, **the canonical schedule (empty refinement) is optimal**. No additional constraints should be added - parallelism provides the best expected makespan.
