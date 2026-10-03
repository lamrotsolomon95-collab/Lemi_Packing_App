"""
utils.py
----------------------------------------------------------------------
Shared utilities for Excel generation, CSV exports, and formatting.
----------------------------------------------------------------------
"""

from io import BytesIO
import pandas as pd


def to_excel_bytes(data: list, sheet_name: str = "Report") -> bytes:
    """
    Converts a list of dicts to a formatted Excel file buffer with bold headers
    and auto-fitted column widths.
    """
    from openpyxl.styles import Font

    df = pd.DataFrame(data)
    if df.empty:
        buffer = BytesIO()
        pd.DataFrame().to_excel(buffer, index=False)
        return buffer.getvalue()

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
        worksheet = writer.sheets[sheet_name[:31]]

        header_font = Font(bold=True)
        for cell in worksheet[1]:
            cell.font = header_font
        worksheet.freeze_panes = "A2"

        for i, col_name in enumerate(df.columns, start=1):
            col_letter = worksheet.cell(row=1, column=i).column_letter
            longest = max(
                [len(str(col_name))] + [len(str(v)) for v in df[col_name].astype(str).tolist()]
            )
            worksheet.column_dimensions[col_letter].width = min(max(longest + 3, 12), 45)

    return buffer.getvalue()
