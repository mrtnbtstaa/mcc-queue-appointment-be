from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .selectors import ReportSelector


class ReportService:
    """Builds PDF reports. Only PDF output is supported."""

    @classmethod
    def summary_pdf(
        cls,
        *,
        date_from=None,
        date_to=None,
    ) -> bytes:

        data = ReportSelector.summary(
            date_from=date_from,
            date_to=date_to,
        )

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            title="MCC Summary Report",
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
        )

        styles = getSampleStyleSheet()

        story = [
            Paragraph("Summary Report", styles["Title"]),
            Paragraph(
                f"Generated: {data['generated_at']:%Y-%m-%d %H:%M}",
                styles["Normal"],
            ),
            Paragraph(
                f"Period: {cls._period_label(date_from, date_to)}",
                styles["Normal"],
            ),
            Spacer(1, 8 * mm),
            Paragraph(
                f"Appointments ({data['appointment_total']})",
                styles["Heading2"],
            ),
            cls._table(data["appointment_statuses"]),
            Spacer(1, 6 * mm),
            Paragraph(
                f"Transactions ({data['transaction_total']})",
                styles["Heading2"],
            ),
            cls._table(data["transaction_statuses"]),
        ]

        document.build(story)

        return buffer.getvalue()

    @staticmethod
    def _period_label(date_from, date_to) -> str:

        if date_from and date_to:
            return f"{date_from} to {date_to}"
        if date_from:
            return f"From {date_from}"
        if date_to:
            return f"Up to {date_to}"
        return "All records"

    @staticmethod
    def _table(rows) -> Table:

        table = Table(
            [("Status", "Count")] + [
                (row["status"], row["count"])
                for row in rows
            ],
            colWidths=[90 * mm, 40 * mm],
        )

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        return table
