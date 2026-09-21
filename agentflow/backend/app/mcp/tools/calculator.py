"""
AgentFlow — MCP Calculator Tool
Safe mathematical expression evaluation using asteval.
NEVER uses eval() or exec().
"""
from __future__ import annotations

import re
from typing import Any, Dict


def _sanitize_expression(expression: str) -> str:
    """Strip whitespace and validate that expression only has safe characters."""
    cleaned = expression.strip()
    # Only allow digits, operators, parentheses, dots, spaces, and ** for power
    if not re.match(r'^[\d\s\+\-\*\/\%\(\)\.\^]+$', cleaned):
        raise ValueError(f"Unsafe characters in expression: {cleaned!r}")
    # Replace ^ with ** for power (common math notation)
    cleaned = cleaned.replace("^", "**")
    return cleaned


def calculator(expression: str) -> Dict[str, Any]:
    """
    Evaluate a mathematical expression safely.

    Args:
        expression: A mathematical expression string (e.g., "12345 * 678")

    Returns:
        dict with 'result' and 'expression' keys
    """
    try:
        from asteval import Interpreter
        safe_expr = _sanitize_expression(expression)
        aeval = Interpreter()
        result = aeval(safe_expr)
        if aeval.error:
            error_msgs = [str(e.get_error()) for e in aeval.error]
            raise ValueError(f"Evaluation error: {'; '.join(error_msgs)}")
        if result is None:
            raise ValueError("Expression returned no result.")
        return {
            "expression": expression,
            "result": result,
            "formatted": str(result),
        }
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Calculator error: {exc}") from exc


TOOL_DEFINITION = {
    "name": "calculator",
    "description": "Evaluate a mathematical expression safely. Supports +, -, *, /, %, ** (power), and parentheses.",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "A mathematical expression to evaluate, e.g. '12345 * 678' or '(10 + 5) * 2'",
            }
        },
        "required": ["expression"],
    },
}
