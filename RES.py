import os
from itertools import combinations
import time
from multiprocessing import Process, Queue
import re


def resolution_worker(clauses, queue):
    result = resolution(clauses)
    queue.put(result)


def run_resolution_with_timeout(clauses, timeout=10):
    queue = Queue()
    p = Process(target=resolution_worker, args=(clauses, queue))
    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        return None
    else:
        return queue.get()

def parse_cnf_file(path):
    clauses = []
    print(f"Parsing file: {path}")
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(('c', 'p', '%', '0')):
                continue
            try:
                literals = list(map(int, line.split()))
                clause = set(literals[:-1])
                clauses.append(clause)
            except ValueError as e:
                print(f"Skipping line due to error: {line} ({e})")
    print(f"Parsed clauses: {len(clauses)}")
    return clauses


def resolve(ci, cj):
    resolvents = []
    for li in ci:
        if -li in cj:
            resolvent = (ci - {li}) | (cj - {-li})
            if not contains_complementary_literals(resolvent):
                resolvents.append(resolvent)
    return resolvents

def contains_complementary_literals(clause):
    return any(-l in clause for l in clause)

def resolution(clauses, time_limit=10):
    start_time = time.time()
    new = set()
    clauses = [frozenset(c) for c in clauses]
    processed = set(clauses)

    while True:

        if time.time() - start_time > time_limit:
            print("Resolution timed out.")
            return None

        pairs = list(combinations(processed, 2))
        for (ci, cj) in pairs:
            resolvents = resolve(ci, cj)
            for r in resolvents:
                if not r:
                    return False
                if r not in processed:
                    new.add(frozenset(r))
        if new.issubset(processed):
            return True
        processed.update(new)
        new.clear()


def extract_number(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else float('inf')


def solve_cnf_folder(folder_path):
    print(f"Scanning folder: {folder_path}")
    for filename in sorted(os.listdir(folder_path), key=extract_number):
        print(f"Found file: {filename}")
        if filename.endswith(".cnf"):
            print(f"Starting: {filename}")
            path = os.path.join(folder_path, filename)
            clauses = parse_cnf_file(path)
            result = run_resolution_with_timeout(clauses, timeout=60)

            if result is None:
                print(f"Result for {filename}: TIMEOUT: RESULT INCONCLUSIVE")
            elif result:
                print(f"Result for {filename}: SATISFIABLE")
            else:
                print(f"Result for {filename}: UNSATISFIABLE")


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()

    solve_cnf_folder("C:\\Users\\rober\\Desktop\\Facultate\\MPI SAT\\SAT-SOLVING\\hard cnf testing-res")


