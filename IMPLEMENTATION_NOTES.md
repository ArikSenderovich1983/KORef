# KORef Implementation Notes

## Implementation Status

✅ **Completed:**
- Expected makespan computation algorithm (bucket-based)
- Canonical earliest-start schedule computation
- Instance reader for KO-plan format
- DIDP domain model with state representation
- Transitions for adding precedence constraints
- Solution extraction and validation
- Basic solver integration

## Architecture

### State Representation
- **State variable**: `unresolved` - Set of unresolved unordered pairs (represented by canonical pair indices)
- **Tables**: 
  - Initial precedence relation (for cycle checking)
  - Durations and probabilities
  - Pair-to-activity mappings

### Transitions
For each unresolved pair `{a, b}`, two transitions:
1. Add `a < b` (if it doesn't create an immediate cycle)
2. Add `b < a` (if it doesn't create an immediate cycle)

### Terminal States
When `unresolved` is empty, we have a complete refinement. Expected makespan is computed post-solution.

## Current Limitations

### 1. Cost Computation During Search
**Issue**: Transitions use zero cost, so DIDP cannot guide search toward optimal solutions.

**Impact**: 
- The solver finds *a* valid refinement, but not necessarily optimal
- For optimal search, all terminal states would need to be explored and evaluated

**Solution Approaches**:
1. **Incremental cost computation**: Track precedence relation in state and compute expected makespan incrementally (requires complex state representation)
2. **Heuristic costs**: Use approximation of expected makespan as transition cost
3. **Exhaustive search**: Use ForwardRecursion to explore all terminal states, then evaluate

### 2. Cycle Detection
**Issue**: Transitions only check cycles against initial precedence, not dynamically added constraints.

**Impact**: Some transitions may create cycles that are only detected post-solution.

**Current Mitigation**: 
- Check acyclicity when extracting solution
- Filter out invalid solutions

**Better Solution**: Track added constraints in state and check cycles dynamically (requires set variables or tables for constraint tracking)

### 3. Transitive Closure Updates
**Issue**: Cannot update precedence table with transitive closure during transitions.

**Current Approach**: Compute transitive closure only when extracting solution.

## Extending for Optimal Search

To enable optimal search with proper cost guidance:

1. **Enhanced State Representation**:
   - Add set variable or table tracking which precedence constraints have been added
   - Or use a more compact representation of the current partial order

2. **Incremental Cost Computation**:
   - Compute schedule incrementally as constraints are added
   - Update expected makespan approximation during search
   - Use this as transition cost

3. **Dynamic Cycle Checking**:
   - Maintain transitive closure in state (or compute on-the-fly)
   - Check cycles in transition preconditions

4. **Terminal Cost Expression**:
   - If DIDP supports custom cost functions, use them
   - Otherwise, precompute costs for terminal states or use approximation

## Testing

Basic functionality tested:
- ✅ Schedule computation
- ✅ Expected makespan calculation
- ✅ Instance reading
- ✅ Utility functions

**TODO**: 
- Test with DIDP solver (requires didppy installation)
- Test with instances containing precedence constraints
- Validate against known optimal solutions

## File Structure

```
/workspace/
├── koref_utils.py          # Core algorithms
├── read_koref.py           # Instance I/O
├── koref_domain.py         # DIDP model and solver
├── test_instance.koref     # Example instance
├── README.md               # User documentation
└── IMPLEMENTATION_NOTES.md # This file
```

## Next Steps

1. Install `didppy` and test with real DIDP solver
2. Create more test instances
3. Implement optimal search version (if needed)
4. Add performance optimizations
5. Integrate into didp-models repository structure
