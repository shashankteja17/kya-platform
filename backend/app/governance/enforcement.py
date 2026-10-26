"""Execution-boundary helper for trusted local tools.

Only call this from a host-controlled tool dispatcher after policy evaluation. Never expose
arbitrary Python callbacks or code execution to HTTP clients.
"""
from typing import Callable, TypeVar
T = TypeVar("T")

class ActionBlocked(PermissionError):
    pass

def execute_only_if_allowed(decision: str, operation: Callable[[], T]) -> T:
    """Execute a pre-registered operation only after an explicit ALLOW verdict."""
    if decision != "ALLOW":
        raise ActionBlocked(f"Operation not executed: governance decision was {decision}.")
    return operation()
