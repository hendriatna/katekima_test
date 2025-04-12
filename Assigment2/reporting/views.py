from io import BytesIO
from rest_framework.views import APIView
from django.http import FileResponse
from commons.utils import StockPDF, convert_date
import datetime
from commons.constants import ResultMessage as message
from commons.headerresponse import ResultResponse as response
from items.models import Items
from purchases.models import PurchasesDetail
from sells.models import SellsDetails
from django.db.models import Value, CharField
from itertools import chain
from operator import attrgetter

class StockReportPDFView(APIView):
    def get(self, request, item_code):
        start_date = request.GET.get("start_date", None)
        end_date = request.GET.get("end_date", None)

        try:
            #get data item, if not found, except item does not exist
            item_data = Items.objects.get(code=item_code, is_deleted=False)
            #get data purchase by item_code, created_at >= start_date, created_at <=end_date
            #is_deleted false, is_deleted header is false
            #and add new field source with value purchase
            purchase_data = (
                 PurchasesDetail
                 .objects
                 .annotate(source=Value('purchase', output_field=CharField()))
                 .filter(
                      item_code=item_data,
                      created_at__date__gte=start_date,
                      created_at__date__lte=end_date,
                      is_deleted=False,
                      header_code__is_deleted=False
                 )
            )
            #get data sells by item_code, created_at >= start_date, created_at <=end_date
            #is_deleted false, is_deleted header is false
            #and add new field source with value sell
            sells_data = (
                 SellsDetails
                 .objects
                 .annotate(source=Value('sell', output_field=CharField()))
                 .filter(
                      item_code=item_code,
                      created_at__date__gte=start_date,
                      created_at__date__lte=end_date,
                      is_deleted=False,
                      header_code__is_deleted=False
                 )
            )

            # Merge & sort data sell & purchase by created_at asc
            all_trx_data = sorted(
                chain(sells_data,purchase_data),
                key=attrgetter('created_at'),
            )
            #setting item header
            item = {
                "code": item_data.code,
                "name": item_data.name,
                "unit": item_data.unit,
            }
            # generate pdf using fpdf2
            pdf = StockPDF()
            pdf.add_page()
            pdf.item_header(item["code"], item["name"], item["unit"])
            pdf.add_table_header()

            stock_qty = 0
            total_in = 0
            total_out = 0
            balance_price = 0
            purchase_data_arr = []
            no_data = 1
            #loop data purchase & sell
            for trx_data in all_trx_data:
                #count total data purchase
                total_in += trx_data.quantity if trx_data.source == 'purchase' else 0
                #count total data sell
                total_out += trx_data.quantity if trx_data.source == 'sell' else 0
                #if trx from purchase
                if trx_data.source == 'purchase':
                     #count stock balance quantity row
                     stock_qty += trx_data.quantity
                     #count stock balance price row
                     balance_price += trx_data.quantity * trx_data.unit_price
                     #add data to row fpdf
                     pdf.add_row(
                        no = no_data,
                        date = convert_date(trx_data.created_at),
                        desc = trx_data.header_code.description,
                        code = trx_data.header_code.code,
                        in_qty = trx_data.quantity,
                        in_price = trx_data.unit_price,
                        out_qty = 0,
                        out_price = 0,
                        stock_qty = trx_data.quantity,
                        stock_price = trx_data.unit_price
                    )
                     #add data to row balance
                     pdf.add_balance_row(stock_qty, balance_price)
                     #add data purchase to variable tmp, for count data sell
                     purchase_data_arr.append(trx_data)
                else:
                    out_qty = trx_data.quantity
                    #if data trx is sell, loop purchase tmp for count the sell data
                    for purchase in purchase_data_arr:
                         #if quantity sell >= purchase quantity, balance price - purchase quantity * unit price purchase
                         #else balance price - sell quantity * unit price purchase
                         balance_price -= (purchase.quantity if out_qty >= purchase.quantity else out_qty) * purchase.unit_price
                         #if quantity sell >= purchase quantity, balance quantity - purchase quantity
                         #else balance quantity - sell quantity
                         stock_qty -= purchase.quantity if out_qty >= purchase.quantity else out_qty
                         #add data to row pdf
                         pdf.add_row(
                            no = no_data,
                            date = convert_date(trx_data.created_at),
                            desc = trx_data.header_code.description,
                            code = trx_data.header_code.code,
                            in_qty = 0,
                            in_price = 0,
                            out_qty = purchase.quantity if out_qty >= purchase.quantity else out_qty,
                            out_price = purchase.unit_price,
                            stock_qty = purchase.quantity if out_qty >= purchase.quantity else out_qty,
                            stock_price = purchase.unit_price
                        )
                         #add balance stock and price
                         pdf.add_balance_row(stock_qty, balance_price)
                         #if sell quantity - purchase quantity <= 0
                         #set purchase quantity - sell quantity, and break the loop
                         if (out_qty - purchase.quantity) <= 0:
                              purchase.quantity = purchase.quantity - out_qty
                              break
                         else:
                            #else, sell quantity - purchase quantity
                            #set purchase quantity = 0
                            out_qty = out_qty - purchase.quantity
                            purchase.quantity = 0
                         no_data += 1
                    #delete data purchase on variable tmp if quantity = 0
                    purchase_data_arr = [obj for obj in purchase_data_arr if obj.quantity != 0]

                no_data += 1
            #add summary row
            pdf.add_summary(total_in, total_out, stock_qty, balance_price)
            #setting to byte input outpur
            buffer = BytesIO()
            pdf.output(buffer)
            buffer.seek(0)
            # return as file pdf
            return FileResponse(buffer, as_attachment=True, filename='stock_report.pdf')
        except Items.DoesNotExist:
             return response.to_json(message.NOT_FOUND_ERROR)
        except Exception as e:
                #return error general for handling other error
                return response.to_json(message.GENERAL_ERROR_RESPONSE)
