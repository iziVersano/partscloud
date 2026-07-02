from django.urls import path

from apps.inventory.api.v1 import views

urlpatterns = [
    path("skus", views.list_skus, name="list-skus"),
    path("skus/stats", views.sku_stats, name="sku-stats"),
    path("skus/actions", views.bulk_update_sku_action, name="bulk-update-sku-action"),
    path("skus/<str:sku_id>/action", views.update_sku_action, name="update-sku-action"),
]
