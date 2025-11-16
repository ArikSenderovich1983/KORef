# DIDP Problem Formulation for KORef

## Problem Structure

The KORef problem is formulated as a DIDP (Dynamic Integer Decision Programming) problem where:

### State Representation
- **`unresolved`**: Set of unresolved unordered pairs of activities (represented by canonical pair indices)
- **`added_constraints`**: Set of precedence constraints that have been added (pair indices)

### Transitions
For each unresolved pair `{a, b}`, we can add either:
- `a < b` (activity a precedes b)
- `b < a` (activity b precedes a)

Each transition:
- Removes the pair from `unresolved`
- Adds the constraint to `added_constraints`
- Has cost = 0 (actual cost computed at terminal states)

### Terminal States
Two types of terminal states:
1. **Complete refinements**: `unresolved.is_empty()` - all pairs resolved
2. **Partial refinements**: `added_constraints.len() > 0` - at least one constraint added

### Cost Computation

**Challenge**: Expected makespan computation requires:
1. Full precedence relation (original + added constraints)
2. Canonical earliest-start schedule computation
3. Abort time computation (overlap detection)
4. Bucket-based expected makespan formula

This is too complex to express as a DIDP cost expression, so costs are computed **post-search** at terminal states.

## Solver Choice

### Current Approach: DFBB (Depth-First Branch & Bound)

We use **DFBB** instead of naive BreadthFirstSearch because:

1. **Depth-First Exploration**: More memory efficient than breadth-first
2. **Optimization-Oriented**: Designed for minimization problems
3. **Better State Ordering**: Explores states in a more efficient order

**Limitation**: Since costs are computed at terminal states (not during transitions), DFBB cannot prune branches during search. However, it still provides better exploration order than breadth-first search.

### Alternative Approaches

For true branch & bound with pruning, we would need:

1. **Heuristic Transition Costs**: Approximate expected makespan incrementally
   - Pros: Enables pruning
   - Cons: May not be accurate, could miss optimal solutions

2. **Terminal Cost Expressions**: Express expected makespan as DIDP expression
   - Pros: Enables pruning
   - Cons: Very complex, may not be feasible

3. **Current Approach**: Compute costs post-search, use DFBB for exploration order
   - Pros: Exact costs, optimal solutions
   - Cons: No pruning, explores all terminal states

## Formulation Correctness

The formulation is **correct**:
- ✅ States represent partial refinements correctly
- ✅ Transitions preserve acyclicity (checked against initial precedence)
- ✅ Terminal states represent valid refinements
- ✅ Costs computed correctly at terminal states
- ✅ Optimal search explores all refinements

The solver (DFBB) is appropriate for optimization, even if it can't prune due to post-search cost computation.

