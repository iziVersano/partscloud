from rest_framework import serializers

from apps.inventory.models import SKU


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = [
            "sku",
            "name",
            "category",
            "on_hand",
            "avg_daily_demand",
            "lead_time_days",
            "safety_stock",
            "unit_cost_eur",
            "last_delivery_date",
            "risk",
            "risk_score",
            "action_status",
        ]
