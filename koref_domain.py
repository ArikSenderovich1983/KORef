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
    
    # Tables for initial precedence relation (read-only, for cycle checking)
    precedence_table_data = []
    for a in range(n):
        for b in range(n):
            if initial_precedence_closure.get((a, b), False):
                precedence_table_data.append(1)
            else:
                precedence_table_data.append(0)
    
    precedence_table = model.add_int_table(precedence_table_data)
    
    # Table mapping pair index to activity indices
    pair_to_a = model.add_int_table([pair_to_info[i][0] for i in range(num_pairs)])
    pair_to_b = model.add_int_table([pair_to_info[i][1] for i in range(num_pairs)])
    
    # Base case: terminal state when no unresolved pairs
    model.add_base_case([unresolved.is_empty()])
    
    # Transitions: for each unresolved unordered pair {a,b}, we can add either a<b or b<a
    # When we add a constraint, we remove the canonical pair index from unresolved
    # (both directions are resolved by choosing one)
    
    for (a, b), (pidx_ab, pidx_ba) in unresolved_pair_map.items():
        idx_ab = a * n + b
        idx_ba = b * n + a
        
        # Transition: add a < b
        # Remove the canonical pair index (pidx_ab represents the unordered pair)
        add_a_prec_b = dp.Transition(
            name=f"add_precedence_{a}_before_{b}",
            cost=dp.FloatExpr.state_cost(),  # Zero cost during search
            effects=[
                (unresolved, unresolved.remove(pidx_ab)),
            ],
            preconditions=[
                unresolved.contains(pidx_ab),
                precedence_table[idx_ba] == 0,  # b does not precede a initially
            ],
        )
        model.add_transition(add_a_prec_b)
        
        # Transition: add b < a
        # Remove the same canonical pair index
        add_b_prec_a = dp.Transition(
            name=f"add_precedence_{b}_before_{a}",
            cost=dp.FloatExpr.state_cost(),
            effects=[
                (unresolved, unresolved.remove(pidx_ab)),
            ],
            preconditions=[
                unresolved.contains(pidx_ab),
                precedence_table[idx_ab] == 0,  # a does not precede b initially
            ],
        )
        model.add_transition(add_b_prec_a)
    
    # Note: Terminal cost is 0 (we compute actual cost post-solution)
    # This means DIDP will explore all refinements, and we'll evaluate
    # them after extraction. For optimal search, we'd need to compute
    # expected makespan during search, which requires a more complex
    # state representation or custom cost computation.
    
    return model, pair_to_info, precedence, unresolved_pair_map


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
    
    # Compute transitive closure
    closure = compute_transitive_closure(refined_precedence, n)
    return closure


def solve(
    model,
    pair_to_info,
    n,
    durations,
    probabilities,
    initial_precedence,
    unresolved_pair_map,
    solver_name,
    history,
    time_limit=None,
    seed=2023,
    initial_beam_size=1,
    threads=1,
    parallel_type=0,
):
    """Solve the KORef problem using DIDP."""
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
    elif solver_name == "FR":
        solver = dp.ForwardRecursion(model, time_limit=time_limit, quiet=False)
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
            print("Warning: Solution contains cycles, trying to find another solution")
            return None, None, None, False, False
        
        # Compute actual expected makespan
        activities = list(range(n))
        schedule = compute_earliest_start_schedule(
            activities, refined_precedence, durations
        )
        expected_makespan = compute_expected_makespan(
            activities, schedule, durations, probabilities
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
    parser.add_argument("--config", default="CABS", type=str)
    parser.add_argument("--seed", default=2023, type=int)
    parser.add_argument("--threads", default=1, type=int)
    parser.add_argument("--initial-beam-size", default=1, type=int)
    parser.add_argument("--parallel-type", default=0, type=int)
    args = parser.parse_args()

    name, n, durations, probabilities, precedence = read_koref.read(args.input)
    
    model, pair_to_info, initial_precedence, unresolved_pair_map = create_model(
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
