# mutation/mutator.py
import ast
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from typing import List, Type, Dict

import astor  # <-- NEW

from .operators import (
    MutationOperator,
    UNIT_LEVEL_OPERATORS,
    INTEGRATION_LEVEL_OPERATORS,
)


@dataclass
class MutantResult:
    operator_name: str
    file_path: str
    index: int
    killed: bool
    error: bool
    message: str


def read_source(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_source(path: str, source: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(source)


def generate_mutants_for_file(
    operator_cls: Type[MutationOperator],
    source: str,
) -> List[ast.AST]:
    """
    Return list of mutated ASTs (one per occurrence).
    """
    tree = ast.parse(source)
    total = operator_cls.count_applicable(tree)
    mutants = []
    for i in range(total):
        tree_copy = ast.parse(source)
        mutator = operator_cls(target_index=i)
        mutated_tree = mutator.visit(tree_copy)
        if mutator.mutated:
            ast.fix_missing_locations(mutated_tree)
            mutants.append(mutated_tree)
    return mutants


def run_tests_in_temp_dir(temp_dir: str) -> subprocess.CompletedProcess:
    """
    Run pytest in the given temp directory.
    """
    return subprocess.run(
        ["pytest", "-q"],
        cwd=temp_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def apply_mutation_and_run_tests(
    project_root: str,
    relative_file: str,
    operator_cls: Type[MutationOperator],
    level_label: str,
) -> List[MutantResult]:
    """
    For a given file and mutation operator, generate mutants,
    run tests, and determine which mutants are killed.
    """
    abs_file = os.path.join(project_root, relative_file)
    original_source = read_source(abs_file)
    mutants = generate_mutants_for_file(operator_cls, original_source)

    results: List[MutantResult] = []

    for index, mutant_tree in enumerate(mutants):
        with tempfile.TemporaryDirectory() as temp_dir:
            # copy entire project into temp_dir
            for item in os.listdir(project_root):
                s = os.path.join(project_root, item)
                d = os.path.join(temp_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

            # overwrite the target file with mutated version
            mutated_source = astor.to_source(mutant_tree)  # <-- CHANGED
            mutated_file_path = os.path.join(temp_dir, relative_file)
            write_source(mutated_file_path, mutated_source)

            proc = run_tests_in_temp_dir(temp_dir)
            killed = proc.returncode != 0
            error = False
            msg = ""
            if proc.returncode not in (0, 1):
                # abnormal error (e.g., syntax), mark separately
                error = True
                msg = proc.stderr

            results.append(
                MutantResult(
                    operator_name=f"{level_label}:{operator_cls.__name__}",
                    file_path=relative_file,
                    index=index,
                    killed=killed,
                    error=error,
                    message=msg if error else proc.stdout,
                )
            )

    return results


def run_mutation_campaign(project_root: str) -> List[MutantResult]:
    """
    Run a full mutation campaign across selected files and operators.
    """

    # Files mainly used for unit-level mutation:
    unit_files = [
        os.path.join("app", "grading.py"),
        os.path.join("app", "models.py"),
    ]

    # Files mainly used for integration-level mutation:
    integration_files = [
        os.path.join("app", "enrollment.py"),
        os.path.join("app", "reporting.py"),
    ]

    all_results: List[MutantResult] = []

    for f in unit_files:
        for op in UNIT_LEVEL_OPERATORS:
            all_results.extend(
                apply_mutation_and_run_tests(
                    project_root=project_root,
                    relative_file=f,
                    operator_cls=op,
                    level_label="UNIT",
                )
            )

    for f in integration_files:
        for op in INTEGRATION_LEVEL_OPERATORS:
            all_results.extend(
                apply_mutation_and_run_tests(
                    project_root=project_root,
                    relative_file=f,
                    operator_cls=op,
                    level_label="INT",
                )
            )

    return all_results


def summarize_results(results: List[MutantResult]) -> Dict[str, float]:
    total = len(results)
    killed = sum(1 for r in results if r.killed)
    survived = sum(1 for r in results if not r.killed and not r.error)
    errored = sum(1 for r in results if r.error)

    mutation_score = (killed / total) * 100 if total else 0.0

    return {
        "total_mutants": total,
        "killed": killed,
        "survived": survived,
        "errored": errored,
        "mutation_score": mutation_score,
    }
