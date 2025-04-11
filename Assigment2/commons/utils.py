from datetime import datetime
from fpdf import FPDF
import datetime


# convert datetime to string format dd-mm-yyyy
# if format datetime differrent, return original datetime string format
def convert_date(date_string):
    try:
        datetimes = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%f')
        return datetime.strftime(datetimes, '%d-%m-%Y')
    except Exception as e:
        return date_string
    

class StockPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Stock Report", ln=True, align="C")
        self.ln(5)

    def item_header(self, item_code, item_name, unit):
        self.set_font("Arial", "", 11)
        self.cell(0, 8, f"Items code : {item_code}", ln=True)
        self.cell(0, 8, f"Name : {item_name}", ln=True)
        self.cell(0, 8, f"Unit : {unit}", ln=True)
        self.ln(4)

    def add_table_header(self):
        self.set_font("Arial", "B", 9)
        self.set_fill_color(220, 220, 220)
        headers = [
            ("No", 10), ("Date", 20), ("Description", 40), ("Code", 15),
            ("In", 35), ("Out", 35), ("Stock", 35)
        ]
        for title, width in headers:
            self.cell(width, 8, title, border=1, align="C", fill=True)
        self.ln()

        # Sub-header row
        self.set_font("Arial", "", 8)
        self.cell(85, 8, "", border=1, align="C")  # skip first columns
        for _ in range(3):  # In, Out, Stock columns
            self.cell(7, 8, "qty", border=1, align="C")
            self.cell(14, 8, "price", border=1, align="C")
            self.cell(14, 8, "total", border=1, align="C")
        self.ln()

    def add_row(self, no, date, desc, code, in_qty, in_price, out_qty, out_price, stock_qty, stock_price):
        in_total = in_qty * in_price
        out_total = out_qty * out_price
        stock_total = stock_qty * stock_price

        self.set_font("Arial", "", 8)
        self.cell(10, 8, str(no), border=1, align="C")
        self.cell(20, 8, date.strftime("%d-%m-%Y"), border=1)
        self.cell(40, 8, desc, border=1)
        self.cell(15, 8, code, border=1)

        self.cell(7, 8, str(in_qty), border=1, align="L")
        self.cell(14, 8, str(in_price), border=1, align="L")
        self.cell(14, 8, str(in_total), border=1, align="L")

        self.cell(7, 8, str(out_qty), border=1, align="L")
        self.cell(14, 8, str(out_price), border=1, align="L")
        self.cell(14, 8, str(out_total), border=1, align="L")

        self.cell(7, 8, str(stock_qty), border=1, align="L")
        self.cell(14, 8, str(stock_price), border=1, align="L")
        self.cell(14, 8, str(stock_total), border=1, align="L")
        self.ln()

    def add_balance_row(self, stock_qty, stock_price):
        total = stock_qty * stock_price
        self.set_font("Arial", "B", 8)
        self.cell(155, 8, "Balance", border=1, align="L")
        self.cell(7, 8, str(stock_qty), border=1, align="L")
        # self.cell(10, 8, str(stock_price), border=1, align="R")
        self.cell(28, 8, str(total), border=1, align="L")
        self.ln()

    def add_summary(self, total_in, total_out, stock_qty, stock_price):
        self.set_font("Arial", "B", 8)
        self.cell(85, 8, "Summary", border=1, align="L")
        self.set_font("Arial", "", 8)
        self.cell(35, 8, str(total_in), border=1,align="L")
        self.cell(35, 8, str(total_out), border=1, align="L")
        self.cell(35, 8, str(stock_qty * stock_price), border=1, align="L")

