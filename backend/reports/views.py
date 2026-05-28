from io import BytesIO
import csv

from django.http import HttpResponse
from openpyxl import Workbook
from rest_framework.views import APIView

from orders.models import Order
from users.permissions import IsManagerOrAdmin


class OrdersCsvExportView(APIView):
    """Экспорт заказов в CSV (менеджер / админ)."""

    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="orders_report.csv"'
        # BOM помогает корректно открыть UTF-8 CSV в Excel.
        response.write("\ufeff")
        writer = csv.writer(response)

        writer.writerow(
            [
                "ID",
                "Номер",
                "Клиент",
                "Менеджер",
                "Статус",
                "Сумма",
                "Создан",
                "Завершён",
            ]
        )

        qs = Order.objects.select_related("client", "manager").order_by("-created_at")
        for order in qs:
            writer.writerow(
                [
                    order.id,
                    order.number,
                    order.client.email if order.client_id else "",
                    order.manager.email if order.manager_id else "",
                    order.status,
                    str(order.total_amount),
                    order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else "",
                    order.completed_at.strftime("%Y-%m-%d %H:%M") if order.completed_at else "",
                ]
            )

        return response


class DocumentsCsvExportView(APIView):
    """Экспорт документов в CSV (менеджер / админ)."""

    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        from documents.models import Document

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="documents_report.csv"'
        response.write("\ufeff")
        writer = csv.writer(response)

        writer.writerow(["ID", "Номер", "Тип", "Заказ", "Статус", "Контрагент", "Создан", "Подписан"])
        qs = Document.objects.select_related("order").order_by("-created_at")
        for doc in qs:
            writer.writerow(
                [
                    doc.id,
                    doc.number,
                    doc.get_doc_type_display(),
                    doc.order.number if doc.order_id else "",
                    doc.get_status_display(),
                    doc.counterparty_name,
                    doc.created_at.strftime("%Y-%m-%d %H:%M") if doc.created_at else "",
                    doc.signed_at.strftime("%Y-%m-%d %H:%M") if doc.signed_at else "",
                ]
            )

        return response


class OrdersExcelExportView(APIView):
    """Экспорт заказов в Excel (менеджер / админ)."""

    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        wb = Workbook()
        ws = wb.active
        ws.title = "Заказы"
        ws.append(
            [
                "ID",
                "Номер",
                "Клиент",
                "Менеджер",
                "Статус",
                "Сумма",
                "Создан",
                "Завершён",
            ]
        )
        qs = Order.objects.select_related("client", "manager").order_by("-created_at")
        for order in qs:
            ws.append(
                [
                    order.id,
                    order.number,
                    order.client.email if order.client_id else "",
                    order.manager.email if order.manager_id else "",
                    order.status,
                    float(order.total_amount),
                    order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else "",
                    order.completed_at.strftime("%Y-%m-%d %H:%M") if order.completed_at else "",
                ]
            )

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="orders_report.xlsx"'
        return response


class DocumentsExcelExportView(APIView):
    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        from documents.models import Document

        wb = Workbook()
        ws = wb.active
        ws.title = "Документы"
        ws.append(["ID", "Номер", "Тип", "Заказ", "Статус", "Контрагент", "Создан", "Подписан"])
        qs = Document.objects.select_related("order").order_by("-created_at")
        for doc in qs:
            ws.append(
                [
                    doc.id,
                    doc.number,
                    doc.get_doc_type_display(),
                    doc.order.number if doc.order_id else "",
                    doc.get_status_display(),
                    doc.counterparty_name,
                    doc.created_at.strftime("%Y-%m-%d %H:%M") if doc.created_at else "",
                    doc.signed_at.strftime("%Y-%m-%d %H:%M") if doc.signed_at else "",
                ]
            )
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="documents_report.xlsx"'
        return response
