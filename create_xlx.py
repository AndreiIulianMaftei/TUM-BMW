"""
Excel Generator Script with Professional Formatting
Creates beautiful Excel spreadsheets with styling, colors, and formatting.
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference
from datetime import datetime


def create_simple_excel(filename='simple_output.xlsx'):
    """
    Creates a simple Excel file with pandas.
    """
    # Sample data
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Age': [25, 30, 35, 28, 32],
        'Department': ['Sales', 'IT', 'HR', 'Sales', 'IT'],
        'Salary': [50000, 75000, 60000, 55000, 70000]
    }
    
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False, sheet_name='Employees')
    print(f"✓ Simple Excel file created: {filename}")


def create_styled_excel(filename='styled_output.xlsx'):
    """
    Creates a professionally styled Excel file with headers, colors, and borders.
    """
    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Employee Report"
    
    # Sample data
    headers = ['Employee ID', 'Name', 'Department', 'Salary', 'Performance Score']
    data = [
        [101, 'Alice Johnson', 'Sales', 50000, 4.5],
        [102, 'Bob Smith', 'IT', 75000, 4.8],
        [103, 'Charlie Brown', 'HR', 60000, 4.2],
        [104, 'David Wilson', 'Sales', 55000, 4.6],
        [105, 'Eve Martinez', 'IT', 70000, 4.9],
    ]
    
    # Add headers
    ws.append(headers)
    
    # Style headers
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
    
    # Add data rows
    for row in data:
        ws.append(row)
    
    # Create borders
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Apply borders and alignment to all cells
    for row in ws.iter_rows(min_row=1, max_row=len(data)+1, min_col=1, max_col=len(headers)):
        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center", vertical="center")
    
    # Alternate row colors for better readability
    light_fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, max_row=len(data)+1), start=2):
        if row_idx % 2 == 0:
            for cell in row:
                cell.fill = light_fill
    
    # Format salary column as currency
    for row in ws.iter_rows(min_row=2, max_row=len(data)+1, min_col=4, max_col=4):
        for cell in row:
            cell.number_format = '$#,##0'
    
    # Adjust column widths
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 18
    
    # Save workbook
    wb.save(filename)
    print(f"✓ Styled Excel file created: {filename}")


def create_excel_with_chart(filename='excel_with_chart.xlsx'):
    """
    Creates an Excel file with a chart visualization.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Report"
    
    # Add data
    headers = ['Month', 'Sales']
    data = [
        ['January', 45000],
        ['February', 52000],
        ['March', 48000],
        ['April', 61000],
        ['May', 58000],
        ['June', 67000],
    ]
    
    ws.append(headers)
    for row in data:
        ws.append(row)
    
    # Style headers
    header_fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    
    # Format sales column as currency
    for row in ws.iter_rows(min_row=2, max_row=len(data)+1, min_col=2, max_col=2):
        for cell in row:
            cell.number_format = '$#,##0'
    
    # Create a bar chart
    chart = BarChart()
    chart.title = "Monthly Sales Performance"
    chart.style = 10
    chart.x_axis.title = "Month"
    chart.y_axis.title = "Sales ($)"
    
    # Add data to chart
    data_ref = Reference(ws, min_col=2, min_row=1, max_row=len(data)+1)
    categories = Reference(ws, min_col=1, min_row=2, max_row=len(data)+1)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(categories)
    
    # Add chart to worksheet
    ws.add_chart(chart, "D2")
    
    # Adjust column widths
    ws.column_dimensions['A'].width = 15
    ws.column_dimensions['B'].width = 12
    
    wb.save(filename)
    print(f"✓ Excel file with chart created: {filename}")


def create_multi_sheet_excel(filename='multi_sheet_output.xlsx'):
    """
    Creates an Excel file with multiple sheets and different formatting.
    """
    wb = Workbook()
    
    # Remove default sheet
    wb.remove(wb.active)
    
    # Sheet 1: Summary
    ws1 = wb.create_sheet("Summary", 0)
    ws1['A1'] = "Company Report"
    ws1['A1'].font = Font(size=18, bold=True, color="1F4E78")
    ws1['A2'] = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ws1['A2'].font = Font(size=10, italic=True)
    
    ws1['A4'] = "Total Employees:"
    ws1['B4'] = 150
    ws1['A5'] = "Average Salary:"
    ws1['B5'] = 62000
    ws1['B5'].number_format = '$#,##0'
    
    # Make labels bold
    for row in ['A4', 'A5']:
        ws1[row].font = Font(bold=True)
    
    # Sheet 2: Detailed Data
    ws2 = wb.create_sheet("Employee Details", 1)
    
    headers = ['ID', 'Name', 'Department', 'Join Date', 'Salary']
    ws2.append(headers)
    
    # Style headers
    header_fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for cell in ws2[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    
    # Sample data
    employees = [
        [101, 'Alice Johnson', 'Sales', '2020-03-15', 50000],
        [102, 'Bob Smith', 'IT', '2019-07-22', 75000],
        [103, 'Charlie Brown', 'HR', '2021-01-10', 60000],
    ]
    
    for emp in employees:
        ws2.append(emp)
    
    # Adjust column widths
    for col_idx, width in enumerate([8, 20, 15, 15, 12], start=1):
        ws2.column_dimensions[get_column_letter(col_idx)].width = width
    
    wb.save(filename)
    print(f"✓ Multi-sheet Excel file created: {filename}")


def main():
    """
    Main function to generate all Excel examples.
    """
    print("\n" + "="*50)
    print("Excel Generator - Creating Beautiful Spreadsheets")
    print("="*50 + "\n")
    
    try:
        # Generate different types of Excel files
        create_simple_excel()
        create_styled_excel()
        create_excel_with_chart()
        create_multi_sheet_excel()
        
        print("\n" + "="*50)
        print("✓ All Excel files generated successfully!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("Make sure you have the required packages installed:")
        print("  pip install pandas openpyxl")


if __name__ == "__main__":
    main()
