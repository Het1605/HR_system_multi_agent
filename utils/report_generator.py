# utils/report_generator.py
# Generates a structured Daily Work Report PDF (HR format)

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle


def generate_daily_report_pdf(report_data):
    """
    Generate a structured Daily Work Report PDF.
    """

    # Ensure reports directory exists
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    employee_id = report_data["employee_id"]
    date = report_data["date"]

    file_name = f"daily_report_{employee_id}_{date}.pdf"
    file_path = os.path.join(reports_dir, file_name)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    y = height - 50

    # ================= HEADER =================
    c.setFillColor(colors.HexColor("#FFD36E"))
    c.rect(0, y - 60, width, 60, stroke=0, fill=1)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, y - 35, "DAILY REPORT")

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, y - 55, "EMPLOYEE REPORT")

    y -= 100

    # ================= EMPLOYEE INFO TABLE =================
    info_data = [
        ["EMPLOYEE NAME", report_data["name"]],
        ["EMPLOYEE ID", str(report_data["employee_id"])],
        ["REPORT NO.", f"RPT-{employee_id}-{date}"],
        ["DATE", report_data["date"]],
    ]

    info_table = Table(info_data, colWidths=[150, 300])
    info_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONT", (1, 0), (1, -1), "Helvetica"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    info_table.wrapOn(c, width, height)
    info_table.drawOn(c, 50, y - 100)

    y -= 160

    # ================= WORK SUMMARY TABLE =================
    work_data = [
        ["WORK", "DESCRIPTION", "APPROVED BY"],
        [
            "Daily Attendance",
            f"Worked from {report_data['start_time']} to {report_data['end_time']} "
            f"({report_data['working_hours']} hours)",
            "System"
        ]
    ]

    work_table = Table(work_data, colWidths=[150, 220, 80])
    work_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FFD36E")),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONT", (0, 1), (-1, -1), "Helvetica"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    work_table.wrapOn(c, width, height)
    work_table.drawOn(c, 50, y - 80)

    y -= 140

    # ================= ADDITIONAL NOTES =================
    c.setFillColor(colors.HexColor("#FFD36E"))
    c.rect(50, y - 30, width - 100, 30, stroke=0, fill=1)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, y - 22, "ADDITIONAL NOTES")

    y -= 50

    c.setFont("Helvetica", 10)
    c.drawString(
        60,
        y,
        "This report is system-generated based on employee attendance data."
    )

    y -= 40

    # ================= FOOTER =================
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(
        50,
        y,
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    c.drawRightString(
        width - 50,
        y,
        "HR Management System"
    )

    c.showPage()
    c.save()

    return file_path