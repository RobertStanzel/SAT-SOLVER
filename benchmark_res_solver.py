import os
import time
import re
import json
from RES import parse_cnf_file, run_resolution_with_timeout  # 👈 adjust this!

def extract_number(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else float('inf')

def benchmark_solver(folder_path, timeout=60):
    results = {"SATISFIABLE": 0, "UNSATISFIABLE": 0, "TIMEOUT": 0}
    times = []
    results_list = []

    print(f"Running Resolution benchmark in: {folder_path}")
    total_start = time.time()

    for filename in sorted(os.listdir(folder_path), key=extract_number):
        if filename.endswith(".cnf"):
            path = os.path.join(folder_path, filename)
            clauses = parse_cnf_file(path)

            print(f"Solving: {filename}")
            start = time.time()
            result = run_resolution_with_timeout(clauses, timeout=timeout)
            elapsed = time.time() - start

            if result is None:
                status = "TIMEOUT"
            elif result:
                status = "SATISFIABLE"
            else:
                status = "UNSATISFIABLE"

            results[status] += 1
            times.append(elapsed)
            results_list.append({
                "filename": filename,
                "status": status,
                "time": round(elapsed, 2)
            })
            print(f"{filename}: {status} in {elapsed:.2f}s")

    total_elapsed = time.time() - total_start
    total_files = len(results_list)

    summary = {
        "results": results_list,
        "summary": {
            "SATISFIABLE": results["SATISFIABLE"],
            "UNSATISFIABLE": results["UNSATISFIABLE"],
            "TIMEOUT": results["TIMEOUT"],
            "total_files": total_files,
            "average_time": round(sum(times) / total_files, 2) if total_files > 0 else 0.0,
            "total_time": round(total_elapsed, 2)
        }
    }

    json_path = os.path.join(folder_path, "benchmark_resolution_results.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=4)

    print("\n--- Resolution Benchmark Summary ---")
    for k, v in results.items():
        print(f"{k}: {v}")
    print(f"Total files tested: {total_files}")
    print(f"Total benchmark time: {total_elapsed:.2f}s")
    if times:
        print(f"Average time per file: {sum(times)/total_files:.2f}s")

if __name__ == "__main__":
    benchmark_solver("C:\\Users\\rober\\Desktop\\Facultate\\MPI SAT\\SAT-SOLVING\\hard cnf testing-res ", timeout=60)
