from django.db import models


class SKU(models.Model):
    """
    One row per spare part. Mirrors spare_parts_inventory.csv directly,
    plus two fields the app itself owns:

    - risk / risk_score: computed once at seed time (see services/risk.py
      and migrations/0002_seed_inventory.py), not recalculated on every
      request.
    - action_status: the planner's decision, set via the accept/decline
      endpoints.
    """

    RISK_CRITICAL = "critical"
    RISK_WARNING = "warning"
    RISK_OK = "ok"
    RISK_CHOICES = [
        (RISK_CRITICAL, "Critical"),
        (RISK_WARNING, "Warning"),
        (RISK_OK, "Ok"),
    ]

    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_DECLINED = "declined"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_DECLINED, "Declined"),
    ]

    sku = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=64)

    on_hand = models.IntegerField()
    avg_daily_demand = models.FloatField()
    lead_time_days = models.IntegerField()
    safety_stock = models.IntegerField()
    unit_cost_eur = models.FloatField()
    last_delivery_date = models.DateField()

    risk = models.CharField(max_length=16, choices=RISK_CHOICES, default=RISK_OK)
    risk_score = models.FloatField(default=0.0)

    action_status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING
    )

    class Meta:
        ordering = ["risk_score"]

    def __str__(self):
        return f"{self.sku} ({self.risk})"
