# KORef Problem Explanation

## Important: Knockout Semantics

**Key Understanding**: When an activity is "knocked out":
- ✅ The activity **executes fully** (completes its duration)
- ✅ The knockout event occurs **after** the activity finishes
- ✅ Other activities that started and are still running **finish their execution**
- ✅ The process stops only **after all concurrently running activities complete**
- ✅ The makespan is the latest finish time among all activities that were running concurrently

This semantics is implemented correctly in the code and affects how abort times and expected makespan are computed.

---

## 1. The KORef Problem

### Problem Definition

The **KO-plan Refinement (KORef)** problem is an optimization problem that deals with scheduling activities under uncertainty. Given a KO-plan `K = (A, ≺, d, p)` where:

- **`A`**: Set of activities `{0, 1, 2, ..., n-1}`
- **`≺`**: Partial order (precedence constraints) - a relation specifying which activities must complete before others can start
- **`d`**: Duration function assigning a positive duration to each activity
- **`p`**: Knockout (KO) probability function assigning a probability `p(a) ∈ [0,1]` to each activity

The goal is to find a **refinement** `≺'` of `≺` (i.e., `≺ ⊆ ≺'`) that minimizes the **expected makespan** of the canonical earliest-start schedule, where the makespan accounts for stochastic knockout events.

### Key Concepts

1. **Precedence Constraints**: A partial order `a ≺ b` means activity `a` must complete before activity `b` can start. The original precedence `≺` is partial, meaning some pairs of activities have no ordering constraint.

2. **Refinement**: A refinement `≺'` extends the original precedence by adding new constraints. It must preserve all original constraints (transitively) and remain acyclic.

3. **Knockout Events**: Each activity has a probability `p(a)` of being "knocked out". When an activity is knocked out:
   - The activity **does execute** fully (completes its duration)
   - After the activity finishes, the knockout event occurs
   - The process stops, but only after all other activities that started and are still running finish their execution
   - The makespan is determined by the latest finish time among all activities that were running concurrently

4. **Expected Makespan**: The expected value of the project completion time, accounting for all possible knockout scenarios.

### Problem Motivation

In real-world project planning:
- Activities have dependencies (precedence constraints)
- Activities may fail with some probability
- We want to optimize the schedule by strategically adding precedence constraints
- Adding constraints can reduce expected makespan by controlling when activities execute relative to each other

### Example

Consider 3 activities:
- Activity 0: duration 5.0, KO probability 0.3
- Activity 1: duration 3.0, KO probability 0.4
- Activity 2: duration 4.0, KO probability 0.2

**Original precedence**: Empty (all activities can run in parallel)

**Possible refinements**:
- Keep empty: All activities start at time 0
- Add `0 ≺ 1`: Activity 1 starts after Activity 0 completes
- Add `1 ≺ 2`: Activity 2 starts after Activity 1 completes
- Add `0 ≺ 1` and `1 ≺ 2`: Chain structure

Each refinement leads to different schedules and different expected makespans. The problem is to find the refinement that minimizes expected makespan.

---

## 2. Computing the Expected Makespan

The expected makespan computation is a multi-step process that accounts for knockout probabilities and activity overlaps.

### Step 1: Compute the Earliest-Start Schedule

Given a precedence relation `≺'`, we compute the canonical earliest-start schedule:

1. **Compute transitive closure**: Expand the precedence relation to include all transitive dependencies
   - If `a ≺ b` and `b ≺ c`, then `a ≺ c` (transitively)

2. **Topological sort**: Order activities respecting precedence constraints

3. **Schedule computation**: For each activity `a`:
   ```
   start_time[a] = max{finish_time[pred] : pred ≺ a}
   finish_time[a] = start_time[a] + duration[a]
   ```
   where `finish_time[pred] = start_time[pred] + duration[pred]`

This ensures each activity starts as early as possible while respecting all precedence constraints.

### Step 2: Compute Abort Times

An activity's **abort time** is the time at which the process stops if that activity is knocked out. This accounts for the fact that:
- The activity executes fully (finishes at `finish_time[a]`)
- Other activities that overlap with it also finish their execution
- The process stops only after all overlapping activities complete

For activity `a`:
```
abort_time[a] = max{finish_time[b] : activities a and b overlap}
```

This ensures that if activity `a` is knocked out, the process continues until all activities that were running concurrently with `a` finish.

Two activities overlap if their execution intervals intersect:
```
overlap(a, b) = [start_a, finish_a) ∩ [start_b, finish_b) ≠ ∅
```

**Example**: If Activity 0 runs from time 0-5 and Activity 1 runs from time 2-7 (overlapping):
- If Activity 0 is knocked out, it finishes at time 5
- Activity 1 is still running and finishes at time 7
- The process stops at time 7 (after Activity 1 finishes)
- Therefore, `abort_time[0] = max(5, 7) = 7`

### Step 3: Group Activities into Buckets

Activities are grouped into **buckets** based on their abort times:
- Bucket `j` contains all activities with abort time `t_j`
- Activities in the same bucket have the same abort time

### Step 4: Compute Survival Probabilities

For each bucket `j`:
```
Q_j = ∏(1 - p(a)) for all a in bucket j
```

This is the probability that **all** activities in bucket `j` survive (are not knocked out).

### Step 5: Compute Cumulative Probabilities

```
P_0 = 1.0
P_j = P_{j-1} × Q_{j-1}  for j = 1, 2, ..., k
```

`P_j` represents the probability that all activities in buckets 0 through j-1 survive.

### Step 6: Compute Expected Makespan

The expected makespan formula:
```
E[makespan] = Σ_{j=0}^{k-1} t_j × P_j × (1 - Q_j) + T × P_k
```

Where:
- `t_j`: Abort time for bucket `j`
- `P_j`: Cumulative survival probability up to bucket `j`
- `Q_j`: Survival probability of bucket `j`
- `T`: Maximum finish time (makespan if no knockouts occur)
- `P_k`: Probability that all activities survive

**Intuition**:
- The first term sums over buckets: if activities in bucket `j` are knocked out, the process stops at time `t_j` (after all overlapping activities finish)
- The probability of this happening is `P_j × (1 - Q_j)` (all previous buckets survive, but at least one activity in bucket `j` is knocked out)
- The second term accounts for the case where all activities survive: makespan is `T` with probability `P_k`

**Key Point**: When an activity is knocked out, it still executes fully. The knockout causes the process to stop after the activity finishes AND after all concurrently running activities finish. The abort time captures this "wait for concurrent activities" behavior.

### Example Calculation

Consider a schedule with:
- Activity 0: start=0, finish=5, KO prob=0.3
- Activity 1: start=5, finish=8, KO prob=0.4
- Activity 2: start=0, finish=4, KO prob=0.2

**Abort times**:
- Activity 0: abort_time = max(5, 4) = 5 (overlaps with Activity 2)
- Activity 1: abort_time = 8 (no overlap)
- Activity 2: abort_time = max(5, 4) = 5 (overlaps with Activity 0)

**Buckets**:
- Bucket 0 (t=5): Activities {0, 2}
- Bucket 1 (t=8): Activity {1}

**Survival probabilities**:
- Q_0 = (1-0.3) × (1-0.2) = 0.7 × 0.8 = 0.56
- Q_1 = (1-0.4) = 0.6

**Cumulative probabilities**:
- P_0 = 1.0
- P_1 = 1.0 × 0.56 = 0.56
- P_2 = 0.56 × 0.6 = 0.336

**Expected makespan**:
```
E[makespan] = 5 × 1.0 × (1 - 0.56) + 8 × 0.56 × (1 - 0.6) + 8 × 0.336
            = 5 × 0.44 + 8 × 0.224 + 2.688
            = 2.2 + 1.792 + 2.688
            = 6.68
```

---

## 3. DIDP Formulation

The KORef problem is formulated as a **Dynamic Integer Decision Programming (DIDP)** problem using the `didppy` framework.

### State Representation

The DIDP state tracks:

1. **`unresolved`**: Set variable containing unresolved unordered pairs `{a, b}` of activities
   - Each pair is represented by a canonical pair index
   - Initially contains all pairs `{a, b}` where neither `a ≺ b` nor `b ≺ a` is determined

2. **`added_constraints`**: Set variable containing precedence constraints that have been added
   - Each constraint is represented by a pair index `(a, b)` meaning `a ≺ b`

### Transitions

For each unresolved unordered pair `{a, b}`, we can choose to add either:
- **`a ≺ b`**: Activity `a` precedes `b`
- **`b ≺ a`**: Activity `b` precedes `a`

Each transition:
- Removes the pair from `unresolved`
- Adds the chosen constraint to `added_constraints`
- Has **cost = 0** (actual cost computed at terminal states)

**Preconditions**:
- The pair must be in `unresolved`
- Adding the constraint must not create a cycle (checked against initial precedence)

### Terminal States

Two types of terminal states are accepted:

1. **Complete refinements**: `unresolved.is_empty()` - all pairs are resolved
2. **Partial refinements**: `added_constraints.len() > 0` - at least one constraint added

The original precedence (no constraints added) is also evaluated as a candidate solution.

### Cost Computation

**Challenge**: Expected makespan computation is too complex to express as a DIDP cost expression because it requires:
1. Full precedence relation (original + added constraints)
2. Canonical earliest-start schedule computation (topological sort)
3. Abort time computation (overlap detection)
4. Bucket-based expected makespan formula

**Solution**: Costs are computed **post-search** at terminal states:
- When a terminal state is reached, extract the refined precedence relation
- Compute the schedule and expected makespan using the algorithm described in Section 2
- Compare with the best solution found so far

### Solver: DFBB (Depth-First Branch & Bound)

We use **DFBB** (Depth-First Branch & Bound) for optimal search:

**Advantages**:
- **Memory efficient**: Depth-first exploration uses less memory than breadth-first
- **Optimization-oriented**: Designed for minimization problems
- **Better state ordering**: Explores states in a more efficient order

**Limitation**: Since costs are computed at terminal states (not during transitions), DFBB cannot prune branches during search. However, it still provides better exploration order than naive breadth-first search.

**Search Process**:
1. Start with original precedence as baseline solution
2. Use DFBB to explore all terminal states
3. For each terminal state:
   - Extract refined precedence
   - Compute exact expected makespan
   - Update best solution if better
4. Return the best solution found

### Formulation Correctness

The formulation is **correct**:
- ✅ States represent partial refinements correctly
- ✅ Transitions preserve acyclicity (checked against initial precedence)
- ✅ Terminal states represent valid refinements
- ✅ Costs computed correctly at terminal states
- ✅ Optimal search explores all refinements

---

## 4. Benchmarking and Testing

### Benchmarking Approach

The benchmarking process evaluates solver performance across a diverse set of problem instances.

#### Problem Categories

Problems are organized by:

1. **Constraint Type**:
   - **Empty**: No initial precedence constraints (`precedence: []`)
   - **Non-empty**: Partial precedence constraints exist

2. **Size**:
   - **Small**: 3-5 activities
   - **Medium**: 6-10 activities
   - **Large**: 11-15 activities

3. **Structure** (for non-empty problems):
   - **Chain**: Linear sequence (0→1→2→...)
   - **Parallel**: Minimal constraints (mostly parallel execution)
   - **Mixed**: Combination of chains and parallel branches
   - **DAG**: Directed acyclic graph with branching

4. **Risk Level**:
   - **High**: KO probabilities 0.7-0.9
   - **Very High**: KO probabilities 0.75-0.95
   - **Medium**: KO probabilities 0.3-0.5
   - **Low**: KO probabilities 0.1-0.3

#### Benchmark Process

For each problem instance:

1. **Load Problem**: Read YAML file containing activities, durations, KO probabilities, and precedence constraints

2. **Compute Original Makespan**: 
   - Compute schedule for original precedence
   - Calculate expected makespan using the bucket-based algorithm
   - This serves as the baseline

3. **Solve Refinement Problem**:
   - Create DIDP model
   - Run optimal solver (DFBB) with time limit (default: 30 seconds)
   - Extract refined precedence and compute refined makespan

4. **Record Results**:
   - Original makespan
   - Refined makespan
   - Improvement: `original - refined`
   - Improvement percentage: `(improvement / original) × 100%`
   - Runtime
   - Solution status (Optimal, Heuristic, Timeout, Fail)

#### Output Format

Results are saved in two formats:

1. **CSV File**: Machine-readable table with all metrics
2. **Markdown File**: Human-readable table with summary statistics

**Summary Statistics**:
- Total problems tested
- Successfully solved (optimal + heuristic)
- Optimal solutions found
- Problems with improvement
- Average improvement percentage

### Testing Individual Instances

For quick testing of a single instance:

```bash
python koref_domain.py problems/non_empty/small/chain/chain_3.yaml --config Optimal
```

This will:
1. Load the problem
2. Display original makespan
3. Solve the refinement problem
4. Display refined makespan and improvement
5. Show the refined precedence constraints

### Benchmarking All Problems

To benchmark all problems:

```bash
# Default: 30 seconds per problem
python benchmark_unified.py

# Custom timeout
python benchmark_unified.py --time-limit 60 --output benchmark_results
```

This will:
1. Find all problem files (empty and non-empty)
2. Process each problem sequentially
3. Generate unified results table
4. Save results to CSV and Markdown files

### Evaluation Metrics

**Success Metrics**:
- **Optimal**: Found optimal solution (exhaustive search completed)
- **Heuristic**: Found solution but may not be optimal (timeout or incomplete search)
- **Timeout**: Search exceeded time limit
- **Fail**: No solution found

**Quality Metrics**:
- **Improvement**: Absolute reduction in expected makespan
- **Improvement %**: Relative improvement percentage
- **Runtime**: Time taken to solve

### Problem Generation

Problems can be generated using the unified generator:

```bash
# Generate all problem types
python generate_problems.py

# Generate specific types
python generate_problems.py --constraint-types empty non_empty \
                            --structures chain dag mixed parallel \
                            --risk-levels high medium \
                            --instances 5
```

This allows systematic testing across different problem characteristics.

---

## Summary

The KORef problem combines:
- **Scheduling**: Finding optimal activity ordering
- **Stochastic Optimization**: Accounting for knockout probabilities
- **Constraint Satisfaction**: Ensuring precedence constraints are valid

The DIDP formulation enables:
- **Systematic Exploration**: All valid refinements are explored
- **Optimal Solutions**: Exhaustive search guarantees optimality (within time limits)
- **Scalability**: DFBB provides efficient exploration order

The benchmarking framework enables:
- **Comprehensive Evaluation**: Tests across diverse problem types
- **Performance Analysis**: Measures solution quality and runtime
- **Reproducibility**: Systematic problem generation and testing

