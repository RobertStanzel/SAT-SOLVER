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

def simplify_clauses(clause_list, assignment):
    simplified = []
    for clause in clause_list:
        if any(lit in assignment and assignment[lit] for lit in clause):
            continue
        new_clause = {lit for lit in clause if -lit not in assignment or assignment[-lit]}
        simplified.append(new_clause)
    return simplified

def unit_propagate(clause_list, assignment):
    changed = True
    while changed:
        changed = False
        unit_clauses = [c for c in clause_list if len(c) == 1]
        if not unit_clauses:
            break
        for unit in unit_clauses:
            lit = next(iter(unit))
            if -lit in assignment and assignment[-lit]:
                return None, None
            assignment[lit] = True
            assignment[-lit] = False
            clause_list = simplify_clauses(clause_list, assignment)
            changed = True
            break
    return clause_list, assignment

def pure_literal_assign(clause_list, assignment):
    literals = {lit for clause in clause_list for lit in clause}
    pure_literals = {lit for lit in literals if -lit not in literals}
    for lit in pure_literals:
        assignment[lit] = True
        assignment[-lit] = False
    new_clauses = [c for c in clause_list if not any(l in c for l in pure_literals)]
    return new_clauses, assignment

def dp_solver(clause_list):
    def recursive_solve(clause_list, assignment):
        clause_list, assignment = unit_propagate(clause_list, assignment)
        if clause_list is None:
            return False
        if not clause_list:
            return True
        clause_list, assignment = pure_literal_assign(clause_list, assignment)
        if not clause_list:
            return True
        var = next(iter(next(iter(clause_list))))
        for value in [True, False]:
            new_assignment = assignment.copy()
            new_assignment[var] = value
            new_assignment[-var] = not value
            new_clause_list = simplify_clauses(clause_list, new_assignment)
            if recursive_solve(new_clause_list, new_assignment):
                return True
        return False
    return recursive_solve([set(c) for c in clause_list], {})

def dp_worker(clauses, queue):
    try:
        result = dp_solver(clauses)
        queue.put(result)
    except Exception as e:
        print(f"[dp_worker] Exception: {e}")
        queue.put(None)

def run_dp_with_timeout(clauses, timeout=60):
    queue = Queue()
    p = Process(target=dp_worker, args=(clauses, queue))
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
            clause_list = parse_cnf_file(path)
            result = run_dp_with_timeout([set(c) for c in clause_list], timeout=timeout)
            if result is None:
                print(f"Result for {filename}: TIMEOUT — RESULT INCONCLUSIVE")
            elif result:
                print(f"Result for {filename}: SATISFIABLE")
            else:
                print(f"Result for {filename}: UNSATISFIABLE")

if __name__ == "__main__":
    freeze_support()
    solve_cnf_folder("C:\\Users\\rober\\Desktop\\Facultate\\MPI SAT\\SAT-SOLVING\\real testing-10 variables", timeout=60)
