# Constraint Propagation Analysis for KORef

## The Question
Can we identify constraints that are **forced** to be in the optimal solution, before exhaustive search?

## Types of Forced Constraints

### 1. Transitivity (Already Handled)
- If `a < b` and `b < c`, then `a < c` is implied
- Current implementation computes transitive closure

### 2. Cycle Prevention (Partially Handled)
- If `a < b` is added, then `b < a` is forbidden
- Current implementation checks initial precedence, but not dynamic constraints

### 3. Dominance-Based Forcing (NOT Implemented)

#### Definition: Activity Dominance
Activity `i` **dominates** activity `j` if:
1. `duration_i <= duration_j` AND
2. `p_i >= p_j`

#### Claim: Dominated Ordering is Never Optimal
If activity `i` dominates activity `j`, then **any schedule where `j < i` can be improved** by swapping to `i < j`.

#### Proof Sketch:
Consider two schedules:
- Schedule A: `j` before `i` (other activities unchanged)
- Schedule B: `i` before `j` (other activities unchanged)

**Case 1: Neither `i` nor `j` knocks out**
- Both schedules have same makespan contribution from `i` and `j`

**Case 2: `j` knocks out** (prob = `p_j`)
- Schedule A: Pays for duration `d_j`, then knockout
- Schedule B: Pays for duration `d_i` (if knockout, saves `d_j` entirely; if not, pays `d_j` later)
- Since `d_i <= d_j` and `p_i >= p_j`, Schedule B has lower expected cost

**Case 3: `i` knocks out** (prob = `p_i`)
- Schedule A: Pays `d_j`, then `d_i`, then knockout
- Schedule B: Pays `d_i`, then knockout (saves `d_j`)
- Since `p_i >= p_j`, the probability of saving `d_j` is higher in Schedule B

**Therefore**: Dominance implies `i < j` should always be added.

### 4. Risk-Duration Ratio Ordering (Heuristic)

#### Observation
In empty precedence problems with high risk, optimal solutions tend to order activities by **decreasing risk-to-duration ratio** (`p/d`).

**Intuition**: Activities with high `p/d` have:
- High probability of knockout (saving future work)
- Low cost if they knock out (short duration wasted)

#### Heuristic Rule
For activities `i` and `j`:
- If `p_i/d_i >> p_j/d_j`, consider adding `i < j`
- Threshold: `(p_i/d_i) / (p_j/d_j) > 2.0` (heuristic)

**Not a guarantee**, but strong indicator for empty/low-precedence problems.

## Cascading Constraints

### Your Scenario
> "We could have a chain of no-decision for 10 pairs, and only when I consider the 11th pair, I need to add all 11 as constraints"

**Example**:
- Activities: `a₀, a₁, ..., a₁₀`
- Optimal: Full chain `a₀ < a₁ < ... < a₁₀`
- But: No single pair's constraint is "forced" in isolation

**This happens when**:
1. There's a **global ordering** based on risk/duration ratios
2. Individual pairs don't have dominance relationships
3. The full chain is only optimal when **all** constraints are present

### Detection Strategy

**Global Analysis** (before search):
1. Compute risk-duration ratios: `r_i = p_i / d_i`
2. Sort activities by decreasing `r_i`
3. Check for "strong" ordering:
   - If `r_i >> r_{i+1}` for all `i`, likely a chain is optimal
   - Add all chain constraints as initial precedence

**Problem**: This is a **heuristic**, not a guarantee!

## Implementation Options

### Option A: Dominance Preprocessing (Conservative)
```python
def add_dominance_constraints(n, durations, probabilities, precedence):
    """Add constraints for dominated activities."""
    for i in range(n):
        for j in range(n):
            if i != j:
                # Check dominance: i dominates j
                if durations[i] <= durations[j] and probabilities[i] >= probabilities[j]:
                    # Check not already determined
                    if (i, j) not in precedence and (j, i) not in precedence:
                        precedence[(i, j)] = True  # Force i < j
    return precedence
```

**Pros**: Provably correct (never adds wrong constraints)
**Cons**: Only catches strict dominance (rare in practice)

### Option B: Risk-Ratio Heuristic (Aggressive)
```python
def add_ratio_heuristic_constraints(n, durations, probabilities, precedence, threshold=2.0):
    """Add constraints based on risk-duration ratio differences."""
    ratios = [probabilities[i] / durations[i] if durations[i] > 0 else 0 for i in range(n)]
    
    for i in range(n):
        for j in range(n):
            if i != j and ratios[i] > 0 and ratios[j] > 0:
                # If i has much higher ratio than j
                if ratios[i] / ratios[j] > threshold:
                    if (i, j) not in precedence and (j, i) not in precedence:
                        precedence[(i, j)] = True  # Force i < j
    return precedence
```

**Pros**: Catches more patterns, especially for high-risk problems
**Cons**: Heuristic - might add sub-optimal constraints in corner cases

### Option C: Hybrid Approach
1. **Always** apply dominance preprocessing (safe)
2. **Optionally** apply ratio heuristic for "ultra_risky" problems (flag-controlled)
3. **Log** which constraints were added automatically

## Recommendation

For the current KORef implementation:

1. **Implement dominance preprocessing** (Option A) - always safe
2. **Add flag** for ratio heuristic (Option B) - for high-risk problems
3. **Keep exhaustive search** as fallback - guarantees optimality even if heuristics fail

This would:
- ✅ Reduce search space for problems with clear dominance
- ✅ Maintain optimality guarantees
- ✅ Provide insight into problem structure (how many constraints are "obvious")
- ✅ Speed up search for ultra-large high-risk problems

## Open Question

**Is there a polynomial-time algorithm to detect ALL forced constraints?**

Likely **NO** - this would require solving a related optimization problem, which is itself NP-hard.

But **dominance** gives us a subset of forced constraints efficiently!

