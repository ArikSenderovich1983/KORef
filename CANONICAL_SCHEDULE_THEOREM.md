# Canonical Schedule Optimality Theorem

## Theorem Statement

**For any refinement ≺' (partial order extending the original precedence ≺), the canonical earliest-start schedule is optimal among all schedules consistent with ≺'.**

That is, if we fix a refinement ≺', then:
- The canonical earliest-start schedule minimizes expected makespan
- Any schedule that delays activities beyond their canonical start times can only increase expected makespan

## Why This Holds

1. **Earliest-start maximizes parallelism:** Starting activities as early as possible (subject to precedence) maximizes concurrent execution
2. **No benefit from delays:** Delaying an activity beyond its earliest start time:
   - Cannot reduce deterministic makespan
   - Cannot reduce KO risk (activities still overlap if they would have overlapped)
   - Can only increase makespan
3. **Monotonicity:** Expected makespan is monotonic in start times - later starts → later finishes → potentially higher makespan

## Implementation Verification

### Our Implementation Always Uses Canonical Schedules

**In `koref_utils.py`:**
```python
def compute_earliest_start_schedule(activities, precedence, durations):
    """
    Compute the canonical earliest-start schedule for a given partial order.
    """
    # Uses topological sort and assigns earliest possible start time
    # s(a) = max{f(pred) | pred precedes a}
    # This is the canonical earliest-start schedule
```

**In `koref_domain.py`:**
```python
def compute_terminal_cost(refined_precedence, n, durations, probabilities):
    """
    Compute the exact expected makespan for a terminal state.
    """
    # Always uses canonical earliest-start schedule
    schedule = compute_earliest_start_schedule(
        activities, refined_precedence, durations
    )
    # Then computes expected makespan from canonical schedule
    expected_makespan = compute_expected_makespan(...)
```

### Verification for mixed_4

For each refinement, we compute:
1. **Canonical earliest-start schedule** from the refined precedence
2. **Expected makespan** of that canonical schedule

**Example - Refinement {0→3, 1→2, 1→3, 2→3}:**
- Precedence: {0→1, 0→2, 0→3, 1→2, 1→3, 2→3}
- Canonical schedule:
  - s(0) = 0.0 (earliest - no predecessors)
  - s(1) = f(0) = 2.0 (earliest - after 0)
  - s(2) = max{f(0), f(1)} = max{2.0, 6.0} = 6.0 (earliest - after 0 and 1)
  - s(3) = max{f(0), f(1), f(2)} = max{2.0, 6.0, 9.0} = 9.0 (earliest - after 0, 1, 2)
- Expected makespan: 11.31

This is the **canonical** schedule - we don't consider non-canonical schedules.

## Conclusion

✅ **Yes, we take this into account:**
- We always compute the canonical earliest-start schedule for each refinement
- We never consider non-canonical schedules
- The theorem guarantees this is optimal for each fixed refinement
- Our DP correctly minimizes over refinements, and for each refinement uses the canonical schedule

## Implication

The optimization problem reduces to:
```
min_{refinement ≺'} ExpectedMakespan(CanonicalSchedule(≺'))
```

Where `CanonicalSchedule(≺')` is the unique earliest-start schedule consistent with ≺'.

This is exactly what our implementation does.
