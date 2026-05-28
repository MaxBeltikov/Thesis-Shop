from django.urls import path

from .views import (
    DocumentsCsvExportView,
    DocumentsExcelExportView,
    OrdersCsvExportView,
    OrdersExcelExportView,
)

urlpatterns = [
    path("orders/export/", OrdersExcelExportView.as_view(), name="orders-excel-export"),
    path("orders/export.csv", OrdersCsvExportView.as_view(), name="orders-csv-export"),
    path("documents/export/", DocumentsExcelExportView.as_view(), name="documents-excel-export"),
    path("documents/export.csv", DocumentsCsvExportView.as_view(), name="documents-csv-export"),
]
