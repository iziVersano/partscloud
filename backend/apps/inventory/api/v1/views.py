"""
Views stay thin on purpose: parse the request, call a service or
repository, serialize the response. No business logic lives here —
see services/risk.py and services/actions.py for that.

Error handling philosophy: catch specific, expected failure modes
(bad query param, unknown SKU, invalid action) and return a clear 4xx
with a message a frontend can show. Anything not caught here is a
genuine bug and should surface as a 500, not be silently mapped to a
misleading 404 — see update_sku_action below for why this matters.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.inventory.models import SKU
from apps.inventory.repositories import sku_repository
from apps.inventory.serializers import SKUSerializer
from apps.inventory.services import actions
from apps.inventory.services.actions import InvalidActionError

ALLOWED_ORDERING_FIELDS = {
    "sku", "name", "category", "on_hand", "avg_daily_demand",
    "lead_time_days", "safety_stock", "unit_cost_eur", "risk_score",
}
ALLOWED_RISK_VALUES = {choice[0] for choice in SKU.RISK_CHOICES}

PAGE_SIZE = 10


@api_view(["GET"])
def list_skus(request):
    """
    GET /api/v1/skus
    Optional query params:
      ?risk=critical            filter by risk level
      ?ordering=risk_score      sort (prefix with "-" for descending)
      ?page=1                   page number (1-based)
      ?page_size=10             results per page (max 100)
    """
    skus = sku_repository.get_all()

    risk = request.query_params.get("risk")
    if risk:
        if risk not in ALLOWED_RISK_VALUES:
            return Response(
                {"detail": f"'risk' must be one of {sorted(ALLOWED_RISK_VALUES)}"},
                status=400,
            )
        skus = skus.filter(risk=risk)

    ordering = request.query_params.get("ordering", "risk_score")
    ordering_field = ordering.lstrip("-")
    if ordering_field not in ALLOWED_ORDERING_FIELDS:
        return Response(
            {"detail": f"'ordering' must be one of {sorted(ALLOWED_ORDERING_FIELDS)}"},
            status=400,
        )
    skus = skus.order_by(ordering)

    total = skus.count()

    try:
        page = max(1, int(request.query_params.get("page", 1)))
        page_size = min(100, max(1, int(request.query_params.get("page_size", PAGE_SIZE))))
    except ValueError:
        return Response({"detail": "'page' and 'page_size' must be integers"}, status=400)

    offset = (page - 1) * page_size
    skus = skus[offset: offset + page_size]

    serializer = SKUSerializer(skus, many=True)
    return Response({
        "results": serializer.data,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),
    })


@api_view(["POST"])
def update_sku_action(request, sku_id):
    """
    POST /api/v1/skus/<sku_id>/action
    body: { "action": "accepted" | "declined" }
    """
    action = request.data.get("action")

    try:
        sku = actions.apply_action(sku_id, action)
    except InvalidActionError as exc:
        return Response({"detail": str(exc)}, status=400)
    except SKU.DoesNotExist:
        return Response({"detail": f"SKU '{sku_id}' not found"}, status=404)

    serializer = SKUSerializer(sku)
    return Response(serializer.data)


@api_view(["POST"])
def bulk_update_sku_action(request):
    """
    POST /api/v1/skus/actions
    body: { "skus": ["SP-1007", "SP-1008"], "action": "accepted" }
    """
    sku_ids = request.data.get("skus", [])
    action = request.data.get("action")

    if not isinstance(sku_ids, list) or not sku_ids:
        return Response({"detail": "'skus' must be a non-empty list"}, status=400)

    try:
        updated_count = actions.apply_bulk_action(sku_ids, action)
    except InvalidActionError as exc:
        return Response({"detail": str(exc)}, status=400)

    # Compare against the count of *distinct* SKUs requested, not the raw
    # list length — Django's .update() returns distinct rows matched, so
    # a duplicate SKU in the request (e.g. a double-click sending the same
    # id twice) would otherwise be misreported as "skipped".
    distinct_requested = len(set(sku_ids))
    response = {"updated": updated_count}
    if updated_count < distinct_requested:
        response["detail"] = (
            f"{distinct_requested - updated_count} of {distinct_requested} SKUs "
            "were not found and were skipped"
        )
    return Response(response)
