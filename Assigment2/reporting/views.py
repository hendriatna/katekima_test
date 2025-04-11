from io import BytesIO
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse
from commons.utils import StockPDF
import datetime


class StockReportPDFView(APIView):
    def get(self, request):
        # example mock data, replace with DB queries
        item = {
            "code": "I-001",
            "name": "History Book",
            "unit": "Pcs",
        }

        entries = [
            {"date": datetime.date(2025, 1, 1), "desc": "Buy history books", "code": "P-001", "in_qty": 10, "in_price": 60000, "out_qty": 0, "out_price": 0},
            {"date": datetime.date(2025, 2, 1), "desc": "Restock history books", "code": "P-002", "in_qty": 10, "in_price": 50000, "out_qty": 0, "out_price": 0},
            {"date": datetime.date(2025, 3, 1), "desc": "Sell history books to library", "code": "S-001", "in_qty": 0, "in_price": 0, "out_qty": 10, "out_price": 60000},
            {"date": datetime.date(2025, 3, 1), "desc": "Sell history books to library", "code": "S-001", "in_qty": 0, "in_price": 0, "out_qty": 5, "out_price": 50000},
        ]

        # generate pdf
        pdf = StockPDF()
        pdf.add_page()
        pdf.item_header(item["code"], item["name"], item["unit"])
        pdf.add_table_header()

        stock_qty = 0
        stock_price = 0
        total_in = 0
        total_out = 0

        for idx, entry in enumerate(entries, start=1):
            stock_qty += entry["in_qty"] - entry["out_qty"]
            stock_price = entry["in_price"] or stock_price  # update if in
            total_in += entry["in_qty"]
            total_out += entry["out_qty"]

            pdf.add_row(
                no=idx,
                date=entry["date"],
                desc=entry["desc"],
                code=entry["code"],
                in_qty=entry["in_qty"],
                in_price=entry["in_price"],
                out_qty=entry["out_qty"],
                out_price=entry["out_price"],
                stock_qty=stock_qty,
                stock_price=stock_price
            )
            pdf.add_balance_row(stock_qty, stock_price)

        pdf.add_summary(total_in, total_out, stock_qty, stock_price)

        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True, filename='stock_report.pdf')
