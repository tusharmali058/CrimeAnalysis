"""
Sensitive data masking utilities.
"""

from __future__ import annotations

import re


def mask_name(name: str, keep_first: int = 1) -> str:
    """Mask a person's name, keeping first N characters."""
    if len(name) <= keep_first:
        return name
    parts = name.split()
    if len(parts) == 1:
        return name[:keep_first] + "*" * (len(name) - keep_first)
    masked_parts = []
    for i, part in enumerate(parts):
        if i == 0:
            masked_parts.append(part[:keep_first] + "." * (len(part) - keep_first))
        else:
            masked_parts.append("[Redacted]")
    return " ".join(masked_parts)


def mask_phone(phone: str) -> str:
    """Mask phone number showing only last 4 digits."""
    if len(phone) < 4:
        return "****"
    return "X" * (len(phone) - 4) + phone[-4:]


def mask_account(account_id: str) -> str:
    """Mask financial account ID."""
    if len(account_id) <= 4:
        return "****"
    return account_id[:4] + "*" * (len(account_id) - 8) + account_id[-4:]


def mask_address(address: str) -> str:
    """Mask detailed address, keeping district/city."""
    parts = address.split(",")
    if len(parts) <= 1:
        return "[Address Redacted]"
    return "[Redacted], " + parts[-1].strip()


def apply_masking(data: dict, role: str, fields_to_mask: list[str] | None = None) -> dict:
    """Apply data masking based on user role."""
    # Administrators and supervisors see full data
    if role in ("administrator", "supervisor"):
        return data

    masked = data.copy()
    mask_functions = {
        "name": mask_name,
        "complainant_name": mask_name,
        "contact": mask_phone,
        "complainant_contact": mask_phone,
        "address": mask_address,
        "account_id": mask_account,
    }

    for field, mask_fn in mask_functions.items():
        if field in masked and masked[field]:
            masked[field] = mask_fn(str(masked[field]))

    return masked
