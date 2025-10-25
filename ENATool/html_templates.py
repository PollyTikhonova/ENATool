"""
HTML Templates for ENA Sample Extractor

This module contains HTML templates for generating interactive data tables
using DataTables.js library.
"""

import pandas as pd


def generate_html_report(table: pd.DataFrame, title: str = "ENA Sample Information") -> str:
    """
    Generate an interactive HTML report from a pandas DataFrame.
    
    Uses DataTables.js for interactive features including:
    - Searching and filtering
    - Column sorting
    - Export to CSV/Excel
    - Advanced search builder
    
    Args:
        table: DataFrame to convert to HTML
        title: Title for the HTML page
        
    Returns:
        Complete HTML string
    """
    columns_config = [f'{{data:"{col}"}}' for col in table.columns.values]
    columns_string = '[' + ', '.join(columns_config) + ']'
    
    # Convert table to HTML and customize
    table_html = table.to_html(index=False).replace(
        '<table border="1" class="dataframe">',
        '<table id="filter_table" class="display nowrap" style="width:100%">'
    )
    
    return HTML_TEMPLATE_HEADER.format(
        title=title,
        columns=columns_string
    ) + table_html + HTML_TEMPLATE_FOOTER


# HTML template header with DataTables configuration
HTML_TEMPLATE_HEADER = '''<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=no">
    <title>{title}</title>
    
    <!-- DataTables CSS -->
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.22/css/jquery.dataTables.min.css">
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/buttons/1.6.4/css/buttons.dataTables.min.css">
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/select/1.3.1/css/select.dataTables.min.css">
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/searchbuilder/1.0.0/css/searchBuilder.dataTables.min.css">
    
    <style type="text/css">
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        h1 {{
            color: #333;
        }}
    </style>
    
    <!-- jQuery -->
    <script type="text/javascript" src="https://code.jquery.com/jquery-3.5.1.js"></script>
    
    <!-- DataTables JS -->
    <script type="text/javascript" src="https://cdn.datatables.net/1.10.22/js/jquery.dataTables.min.js"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/buttons/1.6.4/js/dataTables.buttons.min.js"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/buttons/1.6.4/js/buttons.flash.min.js"></script>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js"></script>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/pdfmake.min.js"></script>
    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/vfs_fonts.js"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/buttons/1.6.4/js/buttons.html5.min.js"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/buttons/1.6.4/js/buttons.print.min.js"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/select/1.3.1/js/dataTables.select.min.js"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/searchbuilder/1.0.0/js/dataTables.searchBuilder.min.js"></script>
    
    <script type="text/javascript">
        $(document).ready(function() {{
            $('#filter_table').DataTable({{
                scrollX: '80vw',
                scrollY: '60vh',
                scrollCollapse: true,
                paging: false,
                dom: 'BQfrtip',
                deferRender: true,
                columns: {columns},
                buttons: [
                    'copy',
                    'csv',
                    'excel'
                ],
                searchBuilder: {{
                    greyscale: true
                }}
            }});
        }});
    </script>
</head>
<body>
'''


# HTML template footer
HTML_TEMPLATE_FOOTER = '''
</body>
</html>
'''
