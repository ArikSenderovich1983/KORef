# Issue Analysis: Canonical vs Refined Makespan

## Problem

For `mixed_4`:
- **Canonical schedule** (no refinement): Expected makespan = **5.95**
- **Best complete refinement** (all pairs resolved): Expected makespan = **11.31**

The canonical schedule is **better** than any complete refinement!

## Root Cause

The current DP formulation requires:
- **Terminal state:** `unresolved.is_empty()` (all pairs must be resolved)

This forces a **complete refinement**, even when the canonical schedule (incomplete refinement) is optimal.

## Problem Definition Check

According to the LaTeX specification:
> "find a refinement ≺' with ≺ ⊆ ≺' such that the expected makespan is minimized"

**Question:** Does "refinement" require ALL pairs to be resolved, or can it be partial?

**Interpretation 1:** Refinement must be complete (total order)
- Current DP implementation
- Forces makespan 11.31 (suboptimal)

**Interpretation 2:** Refinement can be partial (any extension of initial precedence)
- Canonical schedule is valid (empty refinement)
- Optimal makespan = 5.95

## Solution Options

### Option 1: Allow Canonical as Terminal State
Modify DP to allow canonical schedule (no refinement) as a valid solution:
- Add base case for initial state if it's already optimal
- Compare canonical vs complete refinements
- Return the best overall

### Option 2: Check Problem Definition
Verify if the problem actually requires complete refinement or allows partial refinement.

### Option 3: Fix Makespan Computation
Verify that makespan computation is correct for both canonical and refined schedules.

## Current Status

- ✅ Canonical makespan computation: Verified correct (5.95)
- ✅ Complete refinement makespan: Verified correct (11.31)
- ❓ Problem definition: Needs clarification
- ❓ DP formulation: May need update to allow canonical

## Next Steps

1. Clarify problem definition: Must refinement be complete?
2. If partial refinement allowed: Update DP to include canonical
3. If complete required: Document that refinement can increase makespan
