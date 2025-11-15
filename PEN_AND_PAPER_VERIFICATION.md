# Pen-and-Paper Optimality Verification using Bellman Equation

## Problem: mixed_4

**Activities:**
- Activity 0: duration=2.0, KO_prob=0.05
- Activity 1: duration=4.0, KO_prob=0.2
- Activity 2: duration=3.0, KO_prob=0.15
- Activity 3: duration=5.0, KO_prob=0.1

**Initial Precedence:**
- 0 → 1 (Start must precede Parallel_A)
- 0 → 2 (Start must precede Parallel_B)

**Unresolved Pairs:** (0,3), (1,2), (1,3), (2,3)

## Bellman Equation for KORef

The dynamic programming formulation uses the Bellman equation:

```
V(S) = min_{transition} [cost(transition) + V(S')]
```

Where:
- **S** = state = (precedence_relation, unresolved_pairs)
- **V(S)** = optimal expected makespan from state S
- **transition** = adding a precedence constraint (a,b) or (b,a) for unresolved pair
- **cost(transition)** = 0 (transitions have zero cost; cost computed at terminal states)

### Terminal States

For terminal states (all pairs resolved):
```
V(S_terminal) = ExpectedMakespan(S_terminal)
```

The expected makespan is computed using the bucket-based algorithm:
1. Compute canonical earliest-start schedule
2. Compute abort times (max finish time of overlapping activities)
3. Group by abort times into buckets
4. Compute survival probabilities Q_j = ∏(1-p(a)) for a in bucket j
5. Compute cumulative probabilities P_j = ∏Q_i for i=1..j
6. E[M] = Σ(t_j * P_{j-1} * (1-Q_j)) + T * P_k

### Non-Terminal States

For non-terminal states:
```
V(S) = min_{unresolved pair (a,b)} [V(S + a<b), V(S + b<a)]
```

This means: the optimal value from state S is the minimum over all possible ways to resolve the next unresolved pair.

## State Space Enumeration

Initial state S₀:
- Precedence: {0→1, 0→2}
- Unresolved: {(0,3), (1,2), (1,3), (2,3)}

### All Valid Refinements (9 total: 1 canonical + 8 complete)

We evaluate:
1. **Canonical schedule** (empty refinement - no constraints added)
2. **8 complete refinements** (all pairs resolved)

After filtering out cyclic refinements, we have 9 valid terminal states:

#### Refinement 0: Canonical Schedule (Empty Refinement)

**Precedence:** {0→1, 0→2} (no additional constraints)

**Schedule:**
- Activity 0: start=0.0, finish=2.0
- Activity 3: start=0.0, finish=5.0 (parallel with 0)
- Activity 1: start=2.0, finish=6.0 (after 0)
- Activity 2: start=2.0, finish=5.0 (after 0, parallel with 1)

**Overlap Analysis:**
- Activities 0 and 3 overlap: [0.0, 2.0) ∩ [0.0, 5.0)
- Activities 1 and 2 overlap: [2.0, 6.0) ∩ [2.0, 5.0)
- Activities 1 and 3 overlap: [2.0, 6.0) ∩ [0.0, 5.0)
- Activities 2 and 3 overlap: [2.0, 5.0) ∩ [0.0, 5.0)

**Abort Times:**
- τ(0) = max{f(0), f(3)} = max{2.0, 5.0} = 5.0
- τ(1) = max{f(1), f(2), f(3)} = max{6.0, 5.0, 5.0} = 6.0
- τ(2) = max{f(1), f(2), f(3)} = max{6.0, 5.0, 5.0} = 6.0
- τ(3) = max{f(0), f(1), f(2), f(3)} = max{2.0, 6.0, 5.0, 5.0} = 6.0

**Buckets:**
- Bucket 1 (t=5.0): {0}, Q₁ = 0.95, P₀=1.0, P₁=0.95
- Bucket 2 (t=6.0): {1, 2, 3}, Q₂ = 0.80×0.85×0.90 = 0.612, P₂=0.5814

**Expected Makespan:**
E[M] = 5.0×1.0×(1-0.95) + 6.0×0.95×(1-0.612) + 6.0×0.5814
     = 5.0×0.05 + 6.0×0.95×0.388 + 3.4884
     = 0.25 + 2.2116 + 3.4884
     = **5.95**

#### Refinement 1: {0→3, 1→2, 1→3, 2→3}
**Schedule:**
- Activity 0: start=0.0, finish=2.0
- Activity 1: start=2.0, finish=6.0
- Activity 2: start=6.0, finish=9.0
- Activity 3: start=9.0, finish=14.0

**Overlap Analysis:**
- No activities overlap (sequential execution)
- Abort times: τ(0)=2.0, τ(1)=6.0, τ(2)=9.0, τ(3)=14.0

**Buckets:**
- Bucket 1 (t=2.0): {0}, Q₁ = 0.95, P₀=1.0, P₁=0.95
- Bucket 2 (t=6.0): {1}, Q₂ = 0.8, P₂=0.76
- Bucket 3 (t=9.0): {2}, Q₃ = 0.85, P₃=0.646
- Bucket 4 (t=14.0): {3}, Q₄ = 0.9, P₄=0.5814

**Expected Makespan:**
E[M] = 2.0×1.0×(1-0.95) + 6.0×0.95×(1-0.8) + 9.0×0.76×(1-0.85) + 14.0×0.646×(1-0.9) + 14.0×0.5814
     = 2.0×0.05 + 6.0×0.19 + 9.0×0.114 + 14.0×0.0646 + 8.1396
     = 0.1 + 1.14 + 1.026 + 0.9044 + 8.1396
     = **11.31**

#### Refinement 2: {0→3, 2→1, 1→3, 2→3}
**Schedule:**
- Activity 0: start=0.0, finish=2.0
- Activity 2: start=2.0, finish=5.0
- Activity 1: start=5.0, finish=9.0
- Activity 3: start=9.0, finish=14.0

**Expected Makespan:** 11.31 (same as Refinement 1, different ordering)

#### Refinement 3: {0→3, 1→2, 1→3, 3→2}
**Schedule:**
- Activity 0: start=0.0, finish=2.0
- Activity 1: start=2.0, finish=6.0
- Activity 3: start=6.0, finish=11.0
- Activity 2: start=11.0, finish=14.0

**Expected Makespan:** 11.652

#### Refinement 4: {0→3, 2→1, 3→1, 2→3}
**Schedule:**
- Activity 0: start=0.0, finish=2.0
- Activity 2: start=2.0, finish=5.0
- Activity 3: start=5.0, finish=10.0
- Activity 1: start=10.0, finish=14.0

**Expected Makespan:** 11.7945

#### Refinement 5: {0→3, 1→2, 3→1, 3→2}
**Schedule:**
- Activity 0: start=0.0, finish=2.0
- Activity 3: start=2.0, finish=7.0
- Activity 1: start=7.0, finish=11.0
- Activity 2: start=11.0, finish=14.0

**Expected Makespan:** 12.222

#### Refinement 6: {0→3, 2→1, 3→1, 3→2}
**Schedule:**
- Activity 0: start=0.0, finish=2.0
- Activity 3: start=2.0, finish=7.0
- Activity 2: start=7.0, finish=10.0
- Activity 1: start=10.0, finish=14.0

**Expected Makespan:** 12.222

#### Refinement 7: {3→0, 2→1, 3→1, 3→2}
**Schedule:**
- Activity 3: start=0.0, finish=5.0
- Activity 0: start=5.0, finish=7.0
- Activity 2: start=7.0, finish=10.0
- Activity 1: start=10.0, finish=14.0

**Expected Makespan:** 12.272

#### Refinement 8: {3→0, 1→2, 3→1, 3→2}
**Schedule:**
- Activity 3: start=0.0, finish=5.0
- Activity 0: start=5.0, finish=7.0
- Activity 1: start=7.0, finish=11.0
- Activity 2: start=11.0, finish=14.0

**Expected Makespan:** 12.272

## Optimality Proof

### Bellman Optimality Condition

The optimal solution satisfies:
```
V(S₀) = min_{all terminal states S_terminal} [ExpectedMakespan(S_terminal)]
```

From our enumeration (including canonical):
- V(S₀) = min{5.95, 11.31, 11.31, 11.652, 11.7945, 12.222, 12.222, 12.272, 12.272}
- V(S₀) = **5.95**

### Verification

The optimal solution is:
- **Type:** Canonical schedule (empty refinement - no constraints added)
- **Precedence:** {0→1, 0→2} (original only)
- **Expected Makespan:** 5.95

All complete refinements have expected makespan ≥ 11.31, which is worse than canonical.

### Backward Induction Verification

We can verify using backward induction from terminal states:

1. **Terminal states:** V(S_terminal) = ExpectedMakespan(S_terminal) ✓
2. **Non-terminal states:** V(S) = min[V(S + constraint), V(S_canonical)] ✓
3. **Initial state:** V(S₀) = min over all paths = 5.95 (canonical) ✓

## Conclusion

The Bellman equation is satisfied:
- All terminal states have V(S) = ExpectedMakespan(S)
- All non-terminal states satisfy V(S) = min[V(S')] over transitions
- The optimal value V(S₀) = 5.95 is achieved by the canonical schedule (empty refinement)

**Key Insight:** For this problem instance, the canonical schedule (with parallelism) is optimal. Adding constraints to create complete refinements increases expected makespan because:
- Complete refinements force sequential execution (makespan 14.0)
- Canonical schedule allows parallelism (makespan 6.0)
- The benefit of parallelism outweighs the KO risk from overlaps

**The KORef DIDP solver should find this same optimal solution (canonical schedule).**
