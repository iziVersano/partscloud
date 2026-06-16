"""
Accept/decline logic for a planner's response to a flagged SKU.
Kept separate from views.py so it can be tested without going through
HTTP, and reused identically by both the single and bulk endpoints.
"""
from apps.inventory.models import SKU
from apps.inventory.repositories import sku_repository

VALID_ACTIONS = {SKU.STATUS_ACCEPTED, SKU.STATUS_DECLINED}


class InvalidActionError(ValueError):
    pass


def _validate_action(action):
    if action is None:
        raise InvalidActionError("'action' is required")
    if action not in VALID_ACTIONS:
        raise InvalidActionError(
            f"'{action}' is not a valid action — use 'accepted' or 'declined'"
        )


def apply_action(sku_id, action):
    _validate_action(action)
    return sku_repository.update_action_status(sku_id, action)


def apply_bulk_action(sku_ids, action):
    _validate_action(action)
    return sku_repository.bulk_update_action_status(sku_ids, action)
