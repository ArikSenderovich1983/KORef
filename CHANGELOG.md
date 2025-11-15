# Changelog

## Version 0.2 (2024-11-15)

### Optimality Verification and Documentation

**New Features:**
- ✅ Manual verification script (`verify_optimality.py`) for exhaustive enumeration
- ✅ Pen-and-paper Bellman equation proof (`PEN_AND_PAPER_VERIFICATION.md`)
- ✅ Verification summary comparing manual vs DIDP results (`VERIFICATION_SUMMARY.md`)

**Bug Fixes:**
- ✅ Fixed `check_acyclic()`: Now properly detects bidirectional cycles (a→b and b→a)
  - Previously only checked for self-loops
  - Now correctly identifies all cyclic refinements

**Verification Results:**
- Verified optimality for `mixed_4` problem instance
- Optimal expected makespan: 11.31
- All 8 valid refinements evaluated and compared
- Bellman equation optimality condition confirmed

**Files Added:**
- `verify_optimality.py` - Exhaustive enumeration and verification script
- `PEN_AND_PAPER_VERIFICATION.md` - Detailed mathematical proof
- `VERIFICATION_SUMMARY.md` - Summary and comparison document

## Version 0.1 (2024-11-15)

### Initial Release

**Core Implementation:**
- ✅ Complete DIDP model for KORef (KO-plan Refinement) problem
- ✅ Exact expected makespan computation using bucket-based algorithm
- ✅ Optimal exhaustive search that guarantees optimality
- ✅ Support for multiple DIDP solvers (Optimal, FR, CABS, LNBS, etc.)

**Key Features:**
- State representation: Tracks unresolved pairs and added precedence constraints
- Transitions: Add precedence constraints while preserving acyclicity
- Terminal cost computation: Exact expected makespan calculation for each refinement
- Solution extraction: Reconstructs optimal precedence relation

**Problem Instances:**
- ✅ YAML format for problem instances (human-readable, structured)
- ✅ 14 problem instances across 3 difficulty levels:
  - Small: 6 instances (3-5 activities)
  - Medium: 5 instances (6-10 activities)
  - Large: 3 instances (12-20 activities)
- ✅ Various structures: chains, parallel, mixed, DAGs
- ✅ Different complexity scenarios: low/high risk, varied durations

**Utilities:**
- `koref_utils.py`: Core algorithms (schedule computation, expected makespan)
- `read_koref.py`: Instance reader (supports YAML and legacy text format)
- `koref_domain.py`: DIDP model and solver integration

**Documentation:**
- README.md with usage instructions
- INSTANCE_GUIDE.md with problem descriptions
- IMPLEMENTATION_NOTES.md with technical details

**Files:**
- `koref_domain.py` - Main DIDP model and solver
- `koref_utils.py` - Core algorithms
- `read_koref.py` - Instance reader
- `problems/` - Problem instance repository
- `README.md` - User documentation
- `IMPLEMENTATION_NOTES.md` - Technical documentation

### Algorithm Details

**Expected Makespan Computation:**
1. Compute canonical earliest-start schedule from precedence relation
2. Compute abort times for each activity (max finish time of overlapping activities)
3. Group activities by abort time into buckets
4. Compute survival probabilities: Q_j = ∏(1-p(a)) for a in bucket j
5. Compute cumulative probabilities: P_j = ∏Q_i for i=1..j
6. Apply formula: E[M] = Σ(t_j * P_{j-1} * (1-Q_j)) + T * P_k

**Optimal Search:**
- Exhaustive exploration of all terminal states
- Exact makespan computation for each refinement
- Guarantees optimality

### Usage

```bash
# Find optimal solution
python koref_domain.py problems/small/chain_3.yaml --config Optimal

# With time limit
python koref_domain.py problems/medium/parallel_6.yaml --config Optimal --time-out 300
```

### Dependencies

- Python 3.x
- didppy (DIDP Python package)
- PyYAML (for YAML support)
