import pandas as pd
from tmdl_parser import Table, Measure, Column

def generate_documentation(table: Table) -> dict:
    """Generate Excel documentation from parsed TMDL data."""
    
    # Create measures documentation
    measures_data = []
    for measure in table.measures:
        measures_data.append({
            'Name': measure.name,
            'Expression': measure.expression,
            'Format String': measure.format_string or '',
            'Lineage Tag': measure.lineage_tag or ''
        })
    measures_df = pd.DataFrame(measures_data)

    # Create columns documentation
    columns_data = []
    for column in table.columns:
        columns_data.append({
            'Name': column.name,
            'Data Type': column.data_type or '',
            'Format String': column.format_string or '',
            'Source Column': column.source_column or '',
            'Lineage Tag': column.lineage_tag or ''
        })
    columns_df = pd.DataFrame(columns_data)

    # Create table overview
    table_overview = pd.DataFrame([{
        'Table Name': table.name,
        'Lineage Tag': table.lineage_tag or '',
        'Number of Measures': len(table.measures),
        'Number of Columns': len(table.columns)
    }])

    return {
        'Table Overview': table_overview,
        'Measures': measures_df,
        'Columns': columns_df
    } 