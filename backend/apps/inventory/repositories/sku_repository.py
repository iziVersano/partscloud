"""
All direct database access for SKU lives here. Services call these
functions instead of touching SKU.objects directly — if the data layer
ever changes (different ORM, different DB, an external service), only
this file needs to change.
"""
from django.db.models import Count, Sum, F, DecimalField
from django.db.models.functions import Coalesce

from apps.inventory.models import SKU


def get_all():
    return SKU.objects.all()


def get_risk_counts():
    """Return {risk_level: count} across all SKUs in one grouped query."""
    rows = SKU.objects.values("risk").annotate(n=Count("sku"))
    return {row["risk"]: row["n"] for row in rows}


def get_at_risk_value():
    """
    Total inventory value (on_hand x unit_cost) of SKUs at risk
    (critical or warning) — the capital exposed to stockout.
    """
    result = SKU.objects.filter(risk__in=["critical", "warning"]).aggregate(
        value=Coalesce(
            Sum(
                F("on_hand") * F("unit_cost_eur"),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            ),
            0,
            output_field=DecimalField(max_digits=14, decimal_places=2),
        )
    )
    return result["value"]


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
