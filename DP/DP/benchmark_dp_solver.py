import os
import re
import json
import time
from DP import parse_cnf_file, run_dp_with_timeout

def extract_number(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else float('inf')

def benchmark_solver(folder_path, timeout=60):
    results = {"SATISFIABLE": 0, "UNSATISFIABLE": 0, "TIMEOUT": 0}
    times = []
    result_log = []

    print(f"Benchmarking folder: {folder_path}")
    total_start = time.time()

    for filename in sorted(os.listdir(folder_path), key=extract_number):
        if filename.endswith(".cnf"):
            path = os.path.join(folder_path, filename)
            clauses = parse_cnf_file(path)

            print(f"Solving: {filename}")
            start = time.time()
            result = run_dp_with_timeout(clauses, timeout=timeout)
            elapsed = round(time.time() - start, 2)

            if result is None:
                status = "TIMEOUT"
            elif result:
                status = "SATISFIABLE"
            else:
                status = "UNSATISFIABLE"

            results[status] += 1
            times.append(elapsed)
            result_log.append({
                "filename": filename,
                "status": status,
                "time": elapsed
            })

            print(f"{filename}: {status} in {elapsed}s")

    total_elapsed = round(time.time() - total_start, 2)

    summary = {
        "results": result_log,
        "summary": {
            "SATISFIABLE": results["SATISFIABLE"],
            "UNSATISFIABLE": results["UNSATISFIABLE"],
            "TIMEOUT": results["TIMEOUT"],
            "total_files": len(result_log),
            "average_time": round(sum(times) / len(times), 2) if times else 0.0,
            "total_time": total_elapsed
        }
    }

    json_path = os.path.join(folder_path, "benchmark_dp_results.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=4)

    print("\nBenchmark complete")
    print(f"Total files: {summary['summary']['total_files']}")
    print(f"SATISFIABLE: {results['SATISFIABLE']}")
    print(f"UNSATISFIABLE: {results['UNSATISFIABLE']}")
    print(f"TIMEOUT: {results['TIMEOUT']}")
    print(f"Total time: {total_elapsed}s")
    print(f"Average time per file: {summary['summary']['average_time']}s")
    print(f"Results saved to: {json_path}")

if __name__ == "__main__":
    benchmark_solver("C:\\Users\\rober\\Desktop\\Facultate\\MPI SAT\\SAT-SOLVING\\real testing-10 variables" , timeout=60)
