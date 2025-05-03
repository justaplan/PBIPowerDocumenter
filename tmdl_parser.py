import re
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Measure:
    name: str
    expression: str
    format_string: Optional[str] = None
    lineage_tag: Optional[str] = None
    display_folder: Optional[str] = None
    annotations: Dict[str, str] = None
    changed_properties: List[str] = None

@dataclass
class Column:
    name: str
    data_type: Optional[str] = None
    format_string: Optional[str] = None
    lineage_tag: Optional[str] = None
    source_column: Optional[str] = None
    annotations: Dict[str, str] = None
    expression: Optional[str] = None
    summarize_by: Optional[str] = None

@dataclass
class Table:
    name: str
    measures: List[Measure]
    columns: List[Column]
    lineage_tag: Optional[str] = None
    annotations: Dict[str, str] = None

def extract_annotations(content: str) -> Dict[str, str]:
    """Extract annotations from a content block."""
    annotations = {}
    annotation_pattern = r'annotation\s+(\w+)\s*=\s*([^\n]+)'
    for match in re.finditer(annotation_pattern, content):
        key = match.group(1)
        value = match.group(2).strip()
        annotations[key] = value
    return annotations

def extract_changed_properties(content: str) -> List[str]:
    """Extract changed properties from a content block."""
    changed_properties = []
    changed_property_pattern = r'changedProperty\s*=\s*(\w+)'
    for match in re.finditer(changed_property_pattern, content):
        changed_properties.append(match.group(1))
    return changed_properties

def extract_expression(content: str) -> str:
    """Extract expression from a content block."""
    # Handle both backtick and non-backtick expressions
    if '```' in content:
        expression_match = re.search(r'```\s*([^`]+)\s*```', content, re.DOTALL)
    else:
        expression_match = re.search(r'=\s*([^`]+?)(?=\s*(?:dataType|formatString|lineageTag|sourceColumn|summarizeBy|annotation|displayFolder|changedProperty|$))', content, re.DOTALL)
    
    if expression_match:
        return expression_match.group(1).strip()
    return ''

def parse_tmdl(file_path: str) -> Table:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Support quoted and unquoted table names
    table_match = re.search(r"table\s+(['\"]?)([\w\s-]+)\1", content)
    if not table_match:
        raise ValueError("No table definition found in TMDL file")
    table_name = table_match.group(2).strip().split('lineageTag')[0].strip()  # Remove any lineageTag that might have been included

    # Extract table lineage tag
    table_lineage_match = re.search(r'lineageTag:\s*([a-f0-9-]+)', content)
    table_lineage_tag = table_lineage_match.group(1) if table_lineage_match else None

    # Extract table annotations
    table_annotations = extract_annotations(content)

    # Extract measures
    measures = []
    # Split content into measure blocks
    measure_blocks = re.split(r'(?=measure\s+\')', content)
    for block in measure_blocks:
        if not block.strip().startswith('measure'):
            continue
            
        # Extract measure name
        name_match = re.search(r'measure\s+\'([^\']+)\'', block)
        if not name_match:
            continue
        name = name_match.group(1)

        # Extract expression
        expression = extract_expression(block)

        # Extract format string
        format_match = re.search(r'formatString:\s*([^\n]+)', block)
        format_string = format_match.group(1).strip() if format_match else None

        # Extract lineage tag
        lineage_match = re.search(r'lineageTag:\s*([a-f0-9-]+)', block)
        lineage_tag = lineage_match.group(1) if lineage_match else None

        # Extract display folder
        display_folder_match = re.search(r'displayFolder:\s*([^\n]+)', block)
        display_folder = display_folder_match.group(1).strip() if display_folder_match else None

        # Extract measure annotations
        measure_annotations = extract_annotations(block)

        # Extract changed properties
        changed_properties = extract_changed_properties(block)

        measures.append(Measure(
            name=name,
            expression=expression,
            format_string=format_string,
            lineage_tag=lineage_tag,
            display_folder=display_folder,
            annotations=measure_annotations,
            changed_properties=changed_properties
        ))

    # Extract columns
    columns = []
    # Split content into column blocks
    column_blocks = re.split(r'(?=column\s+)', content)
    for block in column_blocks:
        if not block.strip().startswith('column'):
            continue

        # Extract column name: support quoted and unquoted names
        name_match = re.search(r"column\s+(['\"])(.+?)\1|column\s+([\w\- ]+?)(?=\s|=|:)", block)
        if name_match:
            if name_match.group(2):
                name = name_match.group(2).strip()
            else:
                name = name_match.group(3).strip()
        else:
            continue

        # Extract data type
        data_type_match = re.search(r'dataType:\s*(\w+)', block)
        data_type = data_type_match.group(1) if data_type_match else None

        # Extract format string
        format_match = re.search(r'formatString:\s*([^\n]+)', block)
        format_string = format_match.group(1).strip() if format_match else None

        # Extract lineage tag
        lineage_match = re.search(r'lineageTag:\s*([a-f0-9-]+)', block)
        lineage_tag = lineage_match.group(1) if lineage_match else None

        # Extract source column
        source_match = re.search(r'sourceColumn:\s*([\w\- ]+)', block)
        source_column = source_match.group(1) if source_match else None

        # Extract summarize by
        summarize_match = re.search(r'summarizeBy:\s*(\w+)', block)
        summarize_by = summarize_match.group(1) if summarize_match else None

        # Extract column expression
        expression = extract_expression(block)

        # Extract column annotations
        column_annotations = extract_annotations(block)

        columns.append(Column(
            name=name,
            data_type=data_type,
            format_string=format_string,
            lineage_tag=lineage_tag,
            source_column=source_column,
            summarize_by=summarize_by,
            expression=expression,
            annotations=column_annotations
        ))

    return Table(
        name=table_name,
        measures=measures,
        columns=columns,
        lineage_tag=table_lineage_tag,
        annotations=table_annotations
    ) 