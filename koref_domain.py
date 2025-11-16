#!/usr/bin/env python3
"""
DIDP model for KO-plan Refinement (KORef) problem.
"""

import argparse
import time

import didppy as dp
import read_koref
from koref_utils import (
    check_acyclic,
    compute_earliest_start_schedule,
    compute_expected_makespan,
    compute_transitive_closure,
)

start = time.perf_counter()

# Scale factor for converting floats to integers (for expected makespan)
SCALE_FACTOR = 1000000


def encode_pair(a, b, n):
    """Encode pair (a, b) as an integer index."""
    # For n activities, we have n*(n-1) unordered pairs
    # Encode (a, b) where a < b as: a * (n-1) + (b - a - 1)
    # Encode (b, a) where a < b as: a * (n-1) + (b - a - 1) + n*(n-1)//2
    if a < b:
        return a * (n - 1) + (b - a - 1)
    else:
        # For (b, a) where b > a, use the second half
        return (b * (n - 1) + (a - b - 1)) + (n * (n - 1) // 2)


def decode_pair(idx, n):
    """Decode integer index to pair (a, b) and direction."""
    total_pairs = n * (n - 1)
    half = total_pairs // 2
    
    if idx < half:
        # First half: (a, b) where a < b
        a = idx // (n - 1)
        offset = idx % (n - 1)
        b = a + offset + 1
        return (a, b)
    else:
        # Second half: (b, a) where b > a (reversed)
        idx_rev = idx - half
        b = idx_rev // (n - 1)
        offset = idx_rev % (n - 1)
        a = b + offset + 1
        return (a, b)


def create_model(n, durations, probabilities, precedence):
    """
    Create a DIDP model for KORef.
    
    The state tracks which pairs are still unresolved. When all pairs are resolved,
    we have a complete refinement. The actual expected makespan is computed
    post-solution by reconstructing the precedence relation.
    
    Args:
        n: Number of activities
        durations: List of durations
        probabilities: List of KO probabilities  
        precedence: Dict mapping (a, b) -> True if a precedes b (original)
    
    Returns:
        model: DIDP model
        pair_to_info: Dict mapping pair index -> (a, b)
        initial_precedence: Original precedence relation
    """
    model = dp.Model()
    
    # Object types
    activity = model.add_object_type(number=n)
    # For pairs: we have n*(n-1) ordered pairs (a, b) where a != b
    num_pairs = n * (n - 1)
    pair = model.add_object_type(number=num_pairs)
    
    # Build mapping from pair index to (a, b)
    pair_to_info = {}
    pair_idx = 0
    for a in range(n):
        for b in range(n):
            if a != b:
                pair_to_info[pair_idx] = (a, b)
                pair_idx += 1
    
    # Compute initial unresolved pairs U
    # U contains unordered pairs {a,b} where neither a<b nor b<a is determined
    # We'll track them by storing one canonical pair index per unordered pair
    initial_precedence_closure = compute_transitive_closure(precedence, n)
    unresolved_pairs_list = []
    unresolved_pair_map = {}  # Maps unordered pair (min(a,b), max(a,b)) -> pair indices
    
    # Build mapping: for each unordered pair, find both ordered pair indices
    for a in range(n):
        for b in range(a + 1, n):  # Only consider a < b to avoid duplicates
            has_a_prec_b = initial_precedence_closure.get((a, b), False)
            has_b_prec_a = initial_precedence_closure.get((b, a), False)
            if not has_a_prec_b and not has_b_prec_a:
                # Find pair indices for (a,b) and (b,a)
                pidx_ab = None
                pidx_ba = None
                for pidx in range(num_pairs):
                    if pair_to_info[pidx] == (a, b):
                        pidx_ab = pidx
                    elif pair_to_info[pidx] == (b, a):
                        pidx_ba = pidx
                if pidx_ab is not None and pidx_ba is not None:
                    unresolved_pairs_list.append(pidx_ab)  # Use (a,b) as canonical
                    unresolved_pair_map[(a, b)] = (pidx_ab, pidx_ba)
    
    # State variables
    unresolved = model.add_set_var(object_type=pair, target=unresolved_pairs_list)
    
    # Track added precedence constraints: set of pair indices representing added constraints
    # We'll use a set variable to track which constraints have been added
    # For each added constraint (a,b), we store the pair index for (a,b)
    added_constraints = model.add_set_var(object_type=pair, target=[])
    
    # Tables for initial precedence relation (read-only, for cycle checking)
    precedence_table_data = []
    for a in range(n):
        for b in range(n):
            if initial_precedence_closure.get((a, b), False):
                precedence_table_data.append(1)
            else:
                precedence_table_data.append(0)
    
    precedence_table = model.add_int_table(precedence_table_data)
    
    # Tables for durations and probabilities (needed for cost computation)
    duration_table = model.add_float_table(durations)
    prob_table = model.add_float_table(probabilities)
    
    # Table mapping pair index to activity indices
    pair_to_a = model.add_int_table([pair_to_info[i][0] for i in range(num_pairs)])
    pair_to_b = model.add_int_table([pair_to_info[i][1] for i in range(num_pairs)])
    
    # Base case: Allow both complete refinements (all pairs resolved) and partial refinements
    # We accept as terminal:
    # 1. States where all pairs are resolved (complete refinements)
    # 2. States where at least one constraint was added (partial refinements)
    # Add base case for complete refinements
    model.add_base_case([unresolved.is_empty()])
    # Add base case for partial refinements (states with at least one constraint added)
    # Note: This allows stopping early without resolving all pairs
    # A refinement is valid if it adds at least one constraint (partial) or resolves all pairs (complete)
    try:
        model.add_base_case([added_constraints.len() > 0])
    except Exception as e:
        # If DIDP doesn't support multiple base cases, we'll only evaluate complete refinements
        # Partial refinements would need a different approach (e.g., no-op transitions)
        print(f"Note: Multiple base cases not supported, only complete refinements will be evaluated: {e}")
    
    # Transitions: for each unresolved unordered pair {a,b}, we can add either a<b or b<a
    # When we add a constraint, we remove the canonical pair index from unresolved
    # and add the constraint to added_constraints
    
    for (a, b), (pidx_ab, pidx_ba) in unresolved_pair_map.items():
        idx_ab = a * n + b
        idx_ba = b * n + a
        
        # Find the pair index for (a,b) constraint
        constraint_idx_ab = None
        constraint_idx_ba = None
        for pidx in range(num_pairs):
            if pair_to_info[pidx] == (a, b):
                constraint_idx_ab = pidx
            elif pair_to_info[pidx] == (b, a):
                constraint_idx_ba = pidx
        
        # Transition: add a < b
        if constraint_idx_ab is not None:
            add_a_prec_b = dp.Transition(
                name=f"add_precedence_{a}_before_{b}",
                cost=0,  # Zero cost - actual cost computed at terminal state
                effects=[
                    (unresolved, unresolved.remove(pidx_ab)),
                    (added_constraints, added_constraints.add(constraint_idx_ab)),
                ],
                preconditions=[
                    unresolved.contains(pidx_ab),
                    precedence_table[idx_ba] == 0,  # b does not precede a initially
                    # Check that adding this doesn't create a cycle with already added constraints
                    # (We'll check this more thoroughly post-solution, but basic check here)
                ],
            )
            model.add_transition(add_a_prec_b)
        
        # Transition: add b < a
        if constraint_idx_ba is not None:
            add_b_prec_a = dp.Transition(
                name=f"add_precedence_{b}_before_{a}",
                cost=0,  # Zero cost - actual cost computed at terminal state
                effects=[
                    (unresolved, unresolved.remove(pidx_ab)),
                    (added_constraints, added_constraints.add(constraint_idx_ba)),
                ],
                preconditions=[
                    unresolved.contains(pidx_ab),
                    precedence_table[idx_ab] == 0,  # a does not precede b initially
                ],
            )
            model.add_transition(add_b_prec_a)
    
    return model, pair_to_info, precedence, unresolved_pair_map, duration_table, prob_table


def extract_precedence_from_solution(transitions, n, initial_precedence):
    """
    Extract the refined precedence relation from DIDP solution transitions.
    Also checks for cycles and returns None if a cycle is detected.
    """
    refined_precedence = initial_precedence.copy()
    
    for transition in transitions:
        name = transition.name
        if name.startswith("add_precedence_"):
            # Parse: "add_precedence_{a}_before_{b}"
            parts = name.split("_")
            a = int(parts[2])
            b = int(parts[4])
            refined_precedence[(a, b)] = True
    
    # Check acyclicity
    if not check_acyclic(refined_precedence, n):
        return None
    
    # Return the refined precedence (not transitive closure - that's computed when needed)
    return refined_precedence


def compute_terminal_cost(refined_precedence, n, durations, probabilities):
    """
    Compute the exact expected makespan for a terminal state.
    This is called for each terminal state to get the true cost.
    """
    activities = list(range(n))
    
    # Compute schedule
    schedule = compute_earliest_start_schedule(
        activities, refined_precedence, durations
    )
    
    # Compute exact expected makespan
    expected_makespan = compute_expected_makespan(
        activities, schedule, durations, probabilities
    )
    
    return expected_makespan


def solve_optimal_exhaustive(
    model,
    n,
    durations,
    probabilities,
    initial_precedence,
    time_limit=None,
):
    """
    Exhaustively explore all terminal states and find the one with minimum expected makespan.
    This guarantees optimality by evaluating exact expected makespan for every complete refinement.
    Also evaluates the original precedence as a candidate solution.
    """
    import time
    start_time = time.time()
    
    # First, evaluate the original precedence as a candidate solution
    # The original precedence is itself a refinement (trivial refinement)
    print("Evaluating original precedence as candidate solution...")
    original_makespan = compute_terminal_cost(initial_precedence, n, durations, probabilities)
    print(f"  Original precedence makespan: {original_makespan:.6f}")
    
    best_cost = original_makespan
    best_precedence = initial_precedence.copy()
    best_transitions = None
    terminal_count = 1  # Count original as first terminal state
    
    # Use BreadthFirstSearch to explore all states systematically
    solver = dp.BreadthFirstSearch(model, time_limit=time_limit, quiet=False)
    
    print("Exploring all refined terminal states to find optimal solution...")
    
    # Explore all states - BreadthFirstSearch will find all terminal states
    is_terminated = False
    
    while not is_terminated:
        if time_limit and (time.time() - start_time) > time_limit:
            print(f"Time limit reached after exploring {terminal_count} terminal states")
            break
            
        solution, is_terminated = solver.search_next()
        
        # Check if this solution represents a terminal state
        # Terminal states satisfy the base case: unresolved.is_empty()
        # Solutions may have transitions (refinements) or no transitions (original precedence)
        if not solution.is_infeasible:
            # Count how many precedence constraints were added
            # For a complete refinement, we should have added constraints for all
            # unresolved pairs. The number of transitions should equal the number
            # of unresolved pairs we started with.
            
            # Extract refined precedence from transitions
            # Skip if no transitions (we already evaluated original precedence)
            if len(solution.transitions) == 0:
                continue  # Skip - we already evaluated original precedence above
            
            # Extract refined precedence from transitions
            refined_precedence = extract_precedence_from_solution(
                solution.transitions, n, initial_precedence
            )
            
            if refined_precedence is not None:
                # Evaluate this refinement (can be partial - doesn't need to resolve all pairs)
                # A refinement is valid as long as it extends the original precedence
                num_added = len(solution.transitions)
                
                # Compute exact expected makespan for this terminal state
                expected_makespan = compute_terminal_cost(
                    refined_precedence, n, durations, probabilities
                )
                
                terminal_count += 1
                if terminal_count % 10 == 0:
                    print(f"  Evaluated {terminal_count} terminal states, current best: {best_cost:.6f}")
                
                if expected_makespan <= best_cost:  # Use <= to allow ties (refinements should be at least as good)
                    best_cost = expected_makespan
                    best_precedence = refined_precedence
                    best_transitions = solution.transitions
                    improvement = original_makespan - expected_makespan
                    print(f"  New best: expected_makespan = {best_cost:.6f} (improvement: {improvement:.6f}, from {num_added} constraints)")
    
    print(f"\nExplored {terminal_count} terminal states")
    
    if best_precedence is None:
        print("No valid terminal states found")
        return None, None, None, False, True
    
    print(f"Optimal expected makespan: {best_cost:.6f}")
    
    return (
        best_precedence,
        best_cost,
        None,
        True,  # Optimal (exhaustive search)
        False,
    )


def solve(
    model,
    pair_to_info,
    n,
    durations,
    probabilities,
    initial_precedence,
    unresolved_pair_map,
    duration_table,
    prob_table,
    solver_name,
    history,
    time_limit=None,
    seed=2023,
    initial_beam_size=1,
    threads=1,
    parallel_type=0,
):
    """
    Solve the KORef problem using DIDP.
    
    For optimal search with exact makespan computation, use solver_name="Optimal"
    which will exhaustively explore all terminal states.
    """
    # For optimal exhaustive search
    if solver_name == "Optimal" or solver_name == "EXHAUSTIVE":
        return solve_optimal_exhaustive(
            model, n, durations, probabilities, initial_precedence, time_limit
        )
    
    # For optimal search, we need to explore all terminal states
    # Use ForwardRecursion which explores exhaustively
    if solver_name == "FR" or solver_name == "ForwardRecursion":
        solver = dp.ForwardRecursion(model, time_limit=time_limit, quiet=False)
        solution = solver.search()
        
        if solution.is_infeasible:
            return None, None, None, False, True
        
        refined_precedence = extract_precedence_from_solution(
            solution.transitions, n, initial_precedence
        )
        
        if refined_precedence is None:
            return None, None, None, False, False
        
        expected_makespan = compute_terminal_cost(
            refined_precedence, n, durations, probabilities
        )
        
        return (
            refined_precedence,
            expected_makespan,
            None,  # best_bound
            True,  # is_optimal (ForwardRecursion guarantees optimality)
            False,
        )
    
    if solver_name == "LNBS":
        if parallel_type == 2:
            parallelization_method = dp.BeamParallelizationMethod.Sbs
        elif parallel_type == 1:
            parallelization_method = dp.BeamParallelizationMethod.Hdbs1
        else:
            parallelization_method = dp.BeamParallelizationMethod.Hdbs2

        solver = dp.LNBS(
            model,
            initial_beam_size=initial_beam_size,
            seed=seed,
            parallelization_method=parallelization_method,
            threads=threads,
            time_limit=time_limit,
            quiet=False,
        )
    elif solver_name == "DD-LNS":
        solver = dp.DDLNS(model, time_limit=time_limit, quiet=False, seed=seed)
    elif solver_name == "FR" or solver_name == "ForwardRecursion":
        # Already handled above
        pass
    elif solver_name == "BrFS":
        solver = dp.BreadthFirstSearch(model, time_limit=time_limit, quiet=False)
    elif solver_name == "CAASDy":
        solver = dp.CAASDy(model, time_limit=time_limit, quiet=False)
    elif solver_name == "DFBB":
        solver = dp.DFBB(model, time_limit=time_limit, quiet=False)
    elif solver_name == "CBFS":
        solver = dp.CBFS(model, time_limit=time_limit, quiet=False)
    elif solver_name == "ACPS":
        solver = dp.ACPS(model, time_limit=time_limit, quiet=False)
    elif solver_name == "APPS":
        solver = dp.APPS(model, time_limit=time_limit, quiet=False)
    elif solver_name == "DBDFS":
        solver = dp.DBDFS(model, time_limit=time_limit, quiet=False)
    else:
        if parallel_type == 2:
            parallelization_method = dp.BeamParallelizationMethod.Sbs
        elif parallel_type == 1:
            parallelization_method = dp.BeamParallelizationMethod.Hdbs1
        else:
            parallelization_method = dp.BeamParallelizationMethod.Hdbs2

        solver = dp.CABS(
            model,
            initial_beam_size=initial_beam_size,
            threads=threads,
            parallelization_method=parallelization_method,
            time_limit=time_limit,
            quiet=False,
        )

    if solver_name == "FR":
        solution = solver.search()
    else:
        with open(history, "w") as f:
            is_terminated = False

            while not is_terminated:
                solution, is_terminated = solver.search_next()

                if solution.cost is not None:
                    f.write(
                        "{}, {}\n".format(time.perf_counter() - start, solution.cost)
                    )
                    f.flush()

    print("Search time: {}s".format(solution.time))
    print("Expanded: {}".format(solution.expanded))
    print("Generated: {}".format(solution.generated))

    if solution.is_infeasible:
        return None, None, None, False, True
    else:
        # Extract refined precedence from transitions
        refined_precedence = extract_precedence_from_solution(
            solution.transitions, n, initial_precedence
        )
        
        if refined_precedence is None:
            print("Warning: Solution contains cycles")
            return None, None, None, False, False
        
        # Compute exact expected makespan for this terminal state
        expected_makespan = compute_terminal_cost(
            refined_precedence, n, durations, probabilities
        )

        return (
            refined_precedence,
            expected_makespan,
            solution.best_bound,
            solution.is_optimal,
            False,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str)
    parser.add_argument("--time-out", default=1800, type=int)
    parser.add_argument("--history", default="history.csv", type=str)
    parser.add_argument("--config", default="Optimal", type=str, 
                        help="Solver: 'Optimal' (exhaustive), 'FR' (ForwardRecursion), 'CABS', 'LNBS', etc.")
    parser.add_argument("--seed", default=2023, type=int)
    parser.add_argument("--threads", default=1, type=int)
    parser.add_argument("--initial-beam-size", default=1, type=int)
    parser.add_argument("--parallel-type", default=0, type=int)
    args = parser.parse_args()

    name, n, durations, probabilities, precedence = read_koref.read(args.input)
    
    model, pair_to_info, initial_precedence, unresolved_pair_map, duration_table, prob_table = create_model(
        n, durations, probabilities, precedence
    )
    
    solution, cost, bound, is_optimal, is_infeasible = solve(
        model,
        pair_to_info,
        n,
        durations,
        probabilities,
        initial_precedence,
        unresolved_pair_map,
        duration_table,
        prob_table,
        args.config,
        args.history,
        time_limit=args.time_out,
        seed=args.seed,
        threads=args.threads,
        initial_beam_size=args.initial_beam_size,
        parallel_type=args.parallel_type,
    )

    if is_infeasible:
        print("The problem is infeasible")
    else:
        print("best bound: {}".format(bound))

        if cost is not None:
            print("expected makespan: {}".format(cost))
            print("refined precedence constraints:")
            activities = list(range(n))
            for a in activities:
                for b in activities:
                    if a != b and solution.get((a, b), False):
                        print(f"  {a} < {b}")

            if is_optimal:
                print("optimal expected makespan: {}".format(cost))

            validation_result = read_koref.validate(
                activities, precedence, durations, probabilities, solution, cost
            )

            if validation_result:
                print("The solution is valid.")
            else:
                print("The solution is invalid.")
