import os
import re
from multiprocessing import Process, Queue, freeze_support

def parse_cnf_file(path):
    clause_list = []
    print(f"Parsing file: {path}")
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(('c', 'p', '%', '0')):
                continue
            try:
                literals = list(map(int, line.split()))
                clause = set(literals[:-1])
                clause_list.append(clause)
            except ValueError as e:
                print(f"Skipping line due to error: {line} ({e})")
    print(f"Parsed clauses: {len(clause_list)}")
    return clause_list


def dpll(clauses, assignment=None):
    if assignment is None:
        assignment = {}

    def simplify(clauses, assignment):
        simplified = []
        for clause in clauses:
            if any(lit in assignment and assignment[lit] for lit in clause):
                continue
            new_clause = set()
            for lit in clause:
                if -lit in assignment and not assignment[-lit]:
                    continue
                new_clause.add(lit)
            simplified.append(new_clause)
        return simplified

    def unit_propagate(clauses, assignment):
        changed = True
        while changed:
            changed = False
            unit_clauses = [c for c in clauses if len(c) == 1]
            for uc in unit_clauses:
                lit = next(iter(uc))
                if -lit in assignment and assignment[-lit]:
                    return None, None  # Conflict
                assignment[lit] = True
                assignment[-lit] = False
                clauses = simplify(clauses, assignment)
                changed = True
                break
        return clauses, assignment

    clauses = simplify(clauses, assignment)
    clauses, assignment = unit_propagate(clauses, assignment) or (None, None)
    if clauses is None:
        return False
    if not clauses:
        return True

    var = next(iter(next(iter(clauses))))
    for val in [True, False]:
        new_assignment = assignment.copy()
        new_assignment[var] = val
        new_assignment[-var] = not val
        new_clauses = simplify(clauses, new_assignment)
        if dpll(new_clauses, new_assignment):
            return True
    return False

def dpll_worker(clauses, queue):
    try:
        result = dpll(clauses)
        queue.put(result)
    except Exception as e:
        print(f"[dpll_worker] Exception: {e}")
        queue.put(None)

def run_dpll_with_timeout(clauses, timeout=60):
    queue = Queue()
    p = Process(target=dpll_worker, args=(clauses, queue))
    p.start()
    p.join(timeout)

    if p.is_alive():
        print("Timeout! Killing process...")
        p.terminate()
        p.join()
        return None
    return queue.get()


def extract_number(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else float('inf')

def solve_cnf_folder(folder_path, timeout=60):
    print(f"\nScanning folder: {folder_path}")
    for filename in sorted(os.listdir(folder_path), key=extract_number):
        if filename.endswith(".cnf"):
            print(f"\nSolving: {filename}")
            path = os.path.join(folder_path, filename)
            clauses = parse_cnf_file(path)
            result = run_dpll_with_timeout(clauses, timeout=timeout)

            if result is None:
                print(f"Result for {filename}: TIMEOUT — RESULT INCONCLUSIVE")
            elif result:
                print(f"Result for {filename}: SATISFIABLE")
            else:
                print(f"Result for {filename}: UNSATISFIABLE")


if __name__ == "__main__":
    freeze_support()
    solve_cnf_folder("C:\\Users\\rober\\Desktop\\Facultate\\MPI SAT\\SAT-SOLVING\\real testing-10 variables", timeout=60)
