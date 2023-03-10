from odoo import models
import xlsxwriter


class IgmXlsx(models.AbstractModel):
    _name = "report.exim.igm_report_template_excel"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, igm_data):
        column_names_0 = [
            {"name": "Shipment", "value": str(igm_data.shipment_no.shipment_no)},
            {"name": "Foreign Currency", "value": str(igm_data.foreign_currency.name)},
            {"name": "Home Currency", "value": str(igm_data.home_currency.name)},
            {"name": "Lot no.", "value": str(igm_data.lot_no)},
            {"name": "Grade.", "value": str(igm_data.grade)},
            {"name": "BOE No.", "value": igm_data.boe_no},
            {"name": "BOE Date", "value": str(igm_data.boe_date)},
            {"name": "IGM No.", "value": str(igm_data.igm_no)},
            {"name": "IGM Date", "value": str(igm_data.igm_date)},
            {"name": "Exchange Rate", "value": igm_data.ex_rate},
            {"name": "Inward Date", "value": str(igm_data.inward_date)},
            {"name": "Quality", "value": str(igm_data.quality)},
            {"name": "Incoterms", "value": str(igm_data.incoterms)},
        ]

        column_names_1 = [
            {"name": "CI Line Item", "value": "ci_product_line_item.product.name"},
            {"name": "Net Wt", "value": "qty"},
            {"name": "Qty Box", "value": "qty_box"},
            {"name": "Invoice Value", "value": "invoice_value"},
            {"name": "Invoice Value(INR)", "value": "invoice_value_inr"},
            {"name": "Insurance", "value": "insurance"},
            {"name": "Freight", "value": "freight"},
            {"name": "Freight INR", "value": "freight_inr"},
            {"name": "CIF", "value": "cif"},
        ]

        column_names_2 = [
            {"name": "CI Line Item", "value": "ci_product_line_item.product.name"},
            {"name": "BCD", "value": "duty_bcd"},
            {"name": "SWS", "value": "duty_sws"},
            {"name": "AIDC", "value": "duty_aidc"},
            {"name": "IGST", "value": "duty_gst"},
            {"name": "Shipping Line", "value": "shipping_line"},
            {"name": "Penalty", "value": "penalty"},
            {"name": "Others", "value": "others"},
            {"name": "CFS", "value": "cfs"},
            {"name": "FASSAI", "value": "fssai"},
            {"name": "PQ", "value": "pq"},
            {"name": "CHA", "value": "cha"},
            {"name": "Transportation Cost", "value": "transportation_cost"},
            {"name": "Total", "value": "total"},
        ]

        column_names_3 = [
            {"name": "Container No", "value": "container_no"},
            {"name": "Weight", "value": "container_weight"},
            {"name": "Port In", "value": "port_in_date"},
            {"name": "Port Out", "value": "port_out_date"},
            {"name": "Port time Diff(HR)", "value": "port_time_diff"},
            {"name": "CFS In", "value": "cfs_in_date"},
            {"name": "CFS Out", "value": "cfs_out_date"},
            {"name": "CFS time Diff(HR)", "value": "cfs_time_diff"},
            {"name": "Transporter Name", "value": "transporter_name"},
            {"name": "Vehicle No", "value": "vehicle_no"},
            {"name": "OOC", "value": "ooc"},
            {"name": "Release", "value": "release"},
        ]
        column_names_4 = [
            {"name": "Claim Amount", "value": igm_data.claim_amount},
            {"name": "Total Net Wt.", "value": igm_data.sum_net_wt},
            {
                "name": "Claim Settlement Amount",
                "value": igm_data.claim_settlement_amount,
            },
            {"name": "Actual Weight", "value": igm_data.actual_weight},
            {"name": "Claim Settled", "value": igm_data.claim_settled},
            {"name": "Sample Weight", "value": igm_data.sample_weight},
            {"name": "Unloading Weight", "value": igm_data.unloading_weight},
            {"name": "Warehouse", "value": igm_data.warehouse},
            {"name": "Weight Diff", "value": igm_data.weight_diff},
            {"name": "BR", "value": igm_data.br},
            {"name": "Final Noc", "value": igm_data.final_noc},
        ]
        sheet_0 = workbook.add_worksheet("Shipment"[:31])
        # sheet_1 = workbook.add_worksheet("CIF Line"[:31])
        # sheet_2 = workbook.add_worksheet("Duty Line"[:31])
        # sheet_3 = workbook.add_worksheet("Container"[:31])
        # sheet_4 = workbook.add_worksheet("Release"[:31])
        columns = [
            column_names_0,
            column_names_1,
            column_names_2,
            column_names_3,
            column_names_4,
        ]
        sheets = [sheet_0, sheet_0, sheet_0, sheet_0, sheet_0]
        header = workbook.add_format({"bold": True, "font_color": "black"})
        header.set_font_size(15)
        # header.set_bg_color('#8C8C8C')
        value_format = workbook.add_format({"bold": False, "font_color": "black"})
        value_format.set_font_size(13)
        cell_format = workbook.add_format({"bold": False, "font_color": "white"})
        cell_format.set_font_size(14)
        # cell_format.set_text_wrap()
        cell_format.set_bg_color("#050138")
        sheet_0.set_column(0, 16, 18)
        # sheet_0.set_row(0, 20)
        number_format = workbook.add_format({"num_format": "???#,0.00"})
        number_format.set_font_size(15)
        summary = workbook.add_format({"bold": True, "font_color": "black"})
        summary.set_font_size(16)
        sheet_0.write(2, 0, "General Details", header)
        sheet_0.write(6, 0, "CIF Line", header)
        sheet_0.write(16, 0, "Duty Line", header)
        sheet_0.write(24, 0, "Container", header)
        sheet_0.write(29, 0, "Release", header)
        sheet_0.write(36, 7, "CIF VALUE", summary)
        sheet_0.write(36, 8, igm_data.cif_value, number_format)
        sheet_0.write(37, 7, "Landing Cost", summary)
        sheet_0.write(37, 8, igm_data.landing_cost, number_format)
        sheet_0.write(38, 7, "Per KG Cost", summary)
        sheet_0.write(38, 8, igm_data.per_box_cost, number_format)
        sheet_0.write(39, 7, "Per Box Cost", summary)
        sheet_0.write(39, 8, igm_data.pb_cost, number_format)

        # sheet_0.write(0, col_num, column_name["name"])
        for i in range(5):
            for col_num, column_name in enumerate(columns[i]):
                if i == 0:
                    sheets[i].write(3, col_num, column_name["name"], cell_format)
                    sheets[i].write(4, col_num, column_name["value"], value_format)
                if i == 1:
                    row = 7
                    for lines in igm_data.cif_details:
                        row = row + 1
                        x = column_name["value"]
                        y = column_name["name"]
                        sheets[i].write(7, col_num, column_name["name"], cell_format)
                        if y == "CI Line Item":
                            sheets[i].write(
                                row,
                                col_num,
                                lines.ci_product_line_item.product.name,
                                value_format,
                            )
                        else:
                            sheets[i].write(
                                row, col_num, getattr(lines, x), value_format
                            )
                if i == 2:
                    row = 17
                    for lines in igm_data.duty_details:
                        row = row + 1
                        x = column_name["value"]
                        y = column_name["name"]
                        sheets[i].write(17, col_num, column_name["name"], cell_format)
                        if y == "CI Line Item":
                            sheets[i].write(
                                row,
                                col_num,
                                lines.ci_product_line_item.product.name,
                                value_format,
                            )
                        else:
                            sheets[i].write(
                                row, col_num, getattr(lines, x), value_format
                            )
                if i == 3:
                    row = 25
                    for lines in igm_data.container_details:
                        row = row + 1
                        x = column_name["value"]
                        y = column_name["name"]
                        sheets[i].write(25, col_num, column_name["name"], cell_format)
                        sheets[i].write(
                            row, col_num, str(getattr(lines, x)), value_format
                        )
                if i == 4:
                    sheets[i].write(30, col_num, column_name["name"], cell_format)
                    sheets[i].write(31, col_num, column_name["value"], value_format)
