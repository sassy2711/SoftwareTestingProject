# mutation/operators.py
import ast
from typing import List, Tuple, Type


class MutationOperator(ast.NodeTransformer):
    """
    Base class for mutation operators.
    We use an index-based approach to create one mutant per occurrence.
    """

    def __init__(self, target_index: int) -> None:
        self.target_index = target_index
        self.current_index = 0
        self.mutated = False

    def _match(self) -> bool:
        if self.current_index == self.target_index:
            self.mutated = True
            self.current_index += 1
            return True
        self.current_index += 1
        return False

    @classmethod
    def count_applicable(cls, tree: ast.AST) -> int:
        counter = cls(target_index=-1)
        counter.visit(tree)
        return counter.current_index


# -------- Unit-level operators --------

class ArithmeticOperatorReplacement(MutationOperator):
    """
    Replace + with -, * with / and vice versa for BinOp nodes.
    """

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            if self._match():
                if isinstance(node.op, ast.Add):
                    node.op = ast.Sub()
                elif isinstance(node.op, ast.Sub):
                    node.op = ast.Add()
                elif isinstance(node.op, ast.Mult):
                    node.op = ast.Div()
                elif isinstance(node.op, ast.Div):
                    node.op = ast.Mult()
        return node


class RelationalOperatorReplacement(MutationOperator):
    """
    Replace relational operators: > < >= <= == != with another logically close variant.
    """

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        self.generic_visit(node)
        new_ops = []
        for op in node.ops:
            if isinstance(op, (ast.Gt, ast.GtE, ast.Lt, ast.LtE, ast.Eq, ast.NotEq)):
                if self._match():
                    if isinstance(op, ast.Gt):
                        new_ops.append(ast.GtE())
                    elif isinstance(op, ast.GtE):
                        new_ops.append(ast.Gt())
                    elif isinstance(op, ast.Lt):
                        new_ops.append(ast.LtE())
                    elif isinstance(op, ast.LtE):
                        new_ops.append(ast.Lt())
                    elif isinstance(op, ast.Eq):
                        new_ops.append(ast.NotEq())
                    elif isinstance(op, ast.NotEq):
                        new_ops.append(ast.Eq())
                else:
                    new_ops.append(op)
            else:
                new_ops.append(op)
        node.ops = new_ops
        return node


class LogicalConnectorReplacement(MutationOperator):
    """
    Replace 'and' with 'or' and vice versa in BoolOp nodes.
    """

    def visit_BoolOp(self, node: ast.BoolOp) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.op, (ast.And, ast.Or)):
            if self._match():
                if isinstance(node.op, ast.And):
                    node.op = ast.Or()
                else:
                    node.op = ast.And()
        return node


# -------- Integration-level operators --------

class ParameterSwapMutator(MutationOperator):
    """
    Swap first two arguments of selected cross-module function calls,
    e.g., compute_grade_with_bonus(score, bonus).
    """

    TARGET_FUNC_NAMES = {"compute_grade_with_bonus"}

    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name in self.TARGET_FUNC_NAMES and len(node.args) >= 2:
            if self._match():
                node.args[0], node.args[1] = node.args[1], node.args[0]
        return node


class CallDeletionMutator(MutationOperator):
    """
    Remove cross-module calls like record_score_for_enrollment or save-like operations.
    We implement it by replacing the Expr(Call(...)) with a Pass.
    """

    TARGET_FUNC_NAMES = {"record_score_for_enrollment"}

    def visit_Expr(self, node: ast.Expr) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.value, ast.Call):
            func = node.value.func
            func_name = None
            if isinstance(func, ast.Name):
                func_name = func.id
            elif isinstance(func, ast.Attribute):
                func_name = func.attr

            if func_name in self.TARGET_FUNC_NAMES:
                if self._match():
                    return ast.Pass()
        return node


class ReturnValueModificationMutator(MutationOperator):
    """
    Modify return values at integration boundaries.
    For report generation / grading, we can tweak a dict or string.
    """

    def visit_Return(self, node: ast.Return) -> ast.AST:
        self.generic_visit(node)
        # Apply only to functions returning a dict or simple variable
        if self._match():
            # Simple heuristic: wrap in a dummy expression or replace with None
            if node.value is not None:
                # Replace return X with return None (breaking the contract)
                node.value = ast.Constant(value=None)
        return node


# List of operator classes for convenience
UNIT_LEVEL_OPERATORS: List[Type[MutationOperator]] = [
    ArithmeticOperatorReplacement,
    RelationalOperatorReplacement,
    LogicalConnectorReplacement,
]

INTEGRATION_LEVEL_OPERATORS: List[Type[MutationOperator]] = [
    ParameterSwapMutator,
    CallDeletionMutator,
    ReturnValueModificationMutator,
]
