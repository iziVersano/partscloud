"""
Views stay thin on purpose: parse the request, call a service or
repository, serialize the response. No business logic lives here —
see services/risk.py and services/actions.py for that.
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.inventory.repositories import sku_repository
from apps.inventory.serializers import SKUSerializer
from apps.inventory.services import actions
from apps.inventory.services.actions import InvalidActionError


@api_view(["GET"])
def list_skus(request):
    """
    GET /api/v1/skus
    Optional query params:
      ?risk=critical            filter by risk level
      ?ordering=risk_score       sort (any model field, prefix with
                                  "-" for descending)
    """
    skus = sku_repository.get_all()

    risk = request.query_params.get("risk")
    if risk:
        skus = skus.filter(risk=risk)

    ordering = request.query_params.get("ordering", "risk_score")
    skus = skus.order_by(ordering)

    serializer = SKUSerializer(skus, many=True)
    return Response(serializer.data)


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
    except Exception:
        return Response({"detail": "SKU not found"}, status=404)

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

    if not sku_ids:
        return Response({"detail": "'skus' must be a non-empty list"}, status=400)

    try:
        updated_count = actions.apply_bulk_action(sku_ids, action)
    except InvalidActionError as exc:
        return Response({"detail": str(exc)}, status=400)

    return Response({"updated": updated_count})
