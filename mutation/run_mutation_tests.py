# mutation/run_mutation_tests.py
"""
Run this as:

    python -m mutation.run_mutation_tests

from the project root (course_mgmt_project).
"""
import os
from .mutator import run_mutation_campaign, summarize_results


def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"Running mutation campaign in: {project_root}")
    results = run_mutation_campaign(project_root)
    summary = summarize_results(results)

    print("\n=== Mutation Testing Summary ===")
    print(f"Total mutants: {summary['total_mutants']}")
    print(f"Killed      : {summary['killed']}")
    print(f"Survived    : {summary['survived']}")
    print(f"Errored     : {summary['errored']}")
    print(f"Mutation score: {summary['mutation_score']:.2f}%")

    # Optional: list surviving mutants for analysis
    print("\n=== Surviving Mutants ===")
    for r in results:
        if not r.killed and not r.error:
            print(
                f"- {r.operator_name} in {r.file_path} occurrence #{r.index}"
            )


if __name__ == "__main__":
    main()
