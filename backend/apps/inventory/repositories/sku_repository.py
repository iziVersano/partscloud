"""
All direct database access for SKU lives here. Services call these
functions instead of touching SKU.objects directly — if the data layer
ever changes (different ORM, different DB, an external service), only
this file needs to change.
"""
from apps.inventory.models import SKU


def get_all(risk=None, ordering=None):
    queryset = SKU.objects.all()
    if risk:
        queryset = queryset.filter(risk=risk)
    if ordering:
        queryset = queryset.order_by(ordering)
    return queryset


def get_by_sku(sku_id):
    return SKU.objects.get(sku=sku_id)


def get_by_skus(sku_ids):
    return SKU.objects.filter(sku__in=sku_ids)


def update_action_status(sku_id, status):
    sku = get_by_sku(sku_id)
    sku.action_status = status
    sku.save(update_fields=["action_status"])
    return sku


def bulk_update_action_status(sku_ids, status):
    updated = SKU.objects.filter(sku__in=sku_ids).update(action_status=status)
    return updated
