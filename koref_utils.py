#!/usr/bin/env python3
"""
Utility functions for KORef: schedule computation and expected makespan calculation.
"""


def compute_earliest_start_schedule(activities, precedence, durations):
    """
    Compute the canonical earliest-start schedule for a given partial order.
    
    Args:
        activities: List of activity indices [0, 1, ..., n-1]
        precedence: Dict mapping (a, b) -> True if a must precede b
        durations: List of durations for each activity
    
    Returns:
        schedule: Dict mapping activity -> start_time
    """
    n = len(activities)
    schedule = {}
    
    # Topological sort to determine order
    # Compute in-degrees
    in_degree = [0] * n
    for a in range(n):
        for b in range(n):
            if a != b and precedence.get((a, b), False):
                in_degree[b] += 1
    
    # Find activities with no predecessors
    queue = [a for a in range(n) if in_degree[a] == 0]
    
    while queue:
        a = queue.pop(0)
        # Compute start time: max of completion times of predecessors
        start_time = 0.0
        for pred in range(n):
            if pred != a and precedence.get((pred, a), False):
                pred_start = schedule.get(pred, 0.0)
                pred_finish = pred_start + durations[pred]
                start_time = max(start_time, pred_finish)
        
        schedule[a] = start_time
        
        # Update in-degrees and add new ready activities
        for b in range(n):
            if precedence.get((a, b), False):
                in_degree[b] -= 1
                if in_degree[b] == 0:
                    queue.append(b)
    
    return schedule


def compute_transitive_closure(precedence, n):
    """
    Compute the transitive closure of a precedence relation.
    
    Args:
        precedence: Dict mapping (a, b) -> True if a precedes b
        n: Number of activities
    
    Returns:
        closure: Dict mapping (a, b) -> True if a precedes b (transitively)
    """
    closure = {}
    
    # Initialize with direct edges
    for a in range(n):
        for b in range(n):
            if a != b:
                closure[(a, b)] = precedence.get((a, b), False)
    
    # Floyd-Warshall for transitive closure
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if i != j:
                    closure[(i, j)] = closure.get((i, j), False) or (
                        closure.get((i, k), False) and closure.get((k, j), False)
                    )
    
    return closure


def check_acyclic(precedence, n):
    """
    Check if a precedence relation is acyclic.
    
    Args:
        precedence: Dict mapping (a, b) -> True if a precedes b
        n: Number of activities
    
    Returns:
        True if acyclic, False otherwise
    """
    closure = compute_transitive_closure(precedence, n)
    
    # Check for self-loops (cycles)
    for a in range(n):
        if closure.get((a, a), False):
            return False
    
    # Check for bidirectional edges (a -> b and b -> a indicates a cycle)
    for a in range(n):
        for b in range(n):
            if a != b:
                if closure.get((a, b), False) and closure.get((b, a), False):
                    return False
    
    return True


def compute_expected_makespan(activities, schedule, durations, probabilities):
    """
    Compute the expected makespan of a schedule using the bucket-based algorithm.
    
    Args:
        activities: List of activity indices
        schedule: Dict mapping activity -> start_time
        durations: List of durations for each activity
        probabilities: List of KO probabilities for each activity
    
    Returns:
        Expected makespan (float)
    """
    n = len(activities)
    
    # Step 1: Compute completion times
    finish_times = {}
    for a in activities:
        start = schedule.get(a, 0.0)
        finish_times[a] = start + durations[a]
    
    T = max(finish_times.values()) if finish_times else 0.0
    
    # Step 2: Compute abort times (overlap detection)
    abort_times = {}
    for a in activities:
        abort_time = finish_times[a]
        # Find all activities that overlap with a
        for b in activities:
            if a != b:
                start_a = schedule.get(a, 0.0)
                finish_a = finish_times[a]
                start_b = schedule.get(b, 0.0)
                finish_b = finish_times[b]
                
                # Check overlap: [start_a, finish_a) ∩ [start_b, finish_b) ≠ ∅
                if not (finish_a <= start_b or finish_b <= start_a):
                    abort_time = max(abort_time, finish_b)
        
        abort_times[a] = abort_time
    
    # Step 3: Group by abort times into buckets
    abort_time_values = sorted(set(abort_times.values()))
    buckets = {}
    for i, t in enumerate(abort_time_values):
        buckets[i] = [a for a in activities if abort_times[a] == t]
    
    k = len(abort_time_values)
    
    # Step 4: Compute bucket survival probabilities
    Q = {}
    for j in range(k):
        # Q_j = product of (1 - p(a)) for all a in bucket j
        q_j = 1.0
        for a in buckets[j]:
            q_j *= (1.0 - probabilities[a])
        Q[j] = q_j
    
    # Step 5: Compute cumulative probabilities P_j
    P = {}
    P[0] = 1.0
    for j in range(1, k + 1):
        P[j] = P[j - 1] * Q[j - 1]
    
    # Step 6: Compute expected makespan
    expected_makespan = 0.0
    for j in range(k):
        t_j = abort_time_values[j]
        expected_makespan += t_j * P[j] * (1.0 - Q[j])
    
    expected_makespan += T * P[k]
    
    return expected_makespan
