"""
AgentFlow — MCP Current Time Tool
Returns current time in a given timezone.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict

import pytz


def current_time(timezone: str = "UTC") -> Dict[str, Any]:
    """
    Return the current time in a given timezone.

    Args:
        timezone: IANA timezone string (e.g. "Asia/Kolkata", "America/New_York", "UTC")

    Returns:
        dict with time information
    """
    # Validate timezone name — only allow IANA-format strings
    if not re.match(r'^[A-Za-z_/]+$', timezone):
        raise ValueError(f"Invalid timezone format: {timezone!r}")

    if timezone not in pytz.all_timezones_set:
        raise ValueError(f"Unknown timezone: {timezone!r}. Use IANA format (e.g. 'Asia/Kolkata').")

    tz = pytz.timezone(timezone)
    now = datetime.now(tz)

    return {
        "timezone": timezone,
        "datetime": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "utc_offset": now.strftime("%z"),
        "day_of_week": now.strftime("%A"),
    }


TOOL_DEFINITION = {
    "name": "current_time",
    "description": "Get the current date and time in a specific timezone. Use IANA timezone format.",
    "input_schema": {
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "IANA timezone string, e.g. 'UTC', 'Asia/Kolkata', 'America/New_York'",
                "default": "UTC",
            }
        },
        "required": [],
    },
}
