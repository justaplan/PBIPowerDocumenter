import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import os
import time
from tmdl_parser import parse_tmdl
from llm_documenter import generate_llm_documentation

st.set_page_config(
    page_title="PBI Power Documenter",
    page_icon="📊",
    layout="wide"
)

# Sticky footer CSS and HTML (moved to top)
st.markdown(
    """
    <style>
    .stApp {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
    }
    main {
        flex: 1 0 auto;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: white;
        padding: 10px 0 10px 0;
        text-align: center;
        font-size: 0.95em;
        border-top: 1px solid #eee;
        z-index: 9999;
    }
    </style>
    <div class='footer'>
        App developed by <b>Nicky</b> &nbsp;|&nbsp;
        <a href='https://www.nickytan.com' target='_blank'>www.nickytan.com</a>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("PBI Power Documenter")
st.write("Upload one or more Power BI TMDL files to generate detailed documentation")

# Initialize session state
if 'tmdl_data_list' not in st.session_state:
    st.session_state.tmdl_data_list = []
if 'doc_data_list' not in st.session_state:
    st.session_state.doc_data_list = []
if 'tmp_file_paths' not in st.session_state:
    st.session_state.tmp_file_paths = []
if 'generating' not in st.session_state:
    st.session_state.generating = False

def start_generation():
    st.session_state.generating = True

# File upload (multiple files)
uploaded_files = st.file_uploader(
    "Choose one or more TMDL files", type=['tmdl'], accept_multiple_files=True
)

summary_rows = []
successful_files = []

if uploaded_files:
    st.session_state.tmdl_data_list = []
    st.session_state.tmp_file_paths = []
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmdl') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
            st.session_state.tmp_file_paths.append(tmp_file_path)
        try:
            tmdl_data = parse_tmdl(tmp_file_path)
            st.session_state.tmdl_data_list.append((uploaded_file.name, tmdl_data))
            successful_files.append(uploaded_file.name)
            summary_rows.append({
                "File Name": uploaded_file.name,
                "Table Name": tmdl_data.name,
                "Number of Measures": len(tmdl_data.measures),
                "Number of Columns": len(tmdl_data.columns)
            })
        except Exception as e:
            st.error(f"Error parsing file '{uploaded_file.name}': {str(e)}")

    # Combined success message
    if successful_files:
        if len(successful_files) == 1:
            msg = f"File '{successful_files[0]}' uploaded and parsed successfully!"
        else:
            msg = ", ".join(f"{f}" for f in successful_files[:-1])
            msg += f" and {successful_files[-1]}"
            msg = f"File '{msg}' uploaded and parsed successfully!"
        st.success(msg)

    # Show summary table with totals
    if summary_rows:
        df_summary = pd.DataFrame(summary_rows)
        total_row = {
            "File Name": "Total",
            "Table Name": "-",
            "Number of Measures": df_summary["Number of Measures"].sum(),
            "Number of Columns": df_summary["Number of Columns"].sum()
        }
        df_summary = pd.concat([df_summary, pd.DataFrame([total_row])], ignore_index=True)
        st.write("### Uploaded TMDL Files Summary")
        st.dataframe(df_summary, use_container_width=True)

# Generate button
if st.session_state.tmdl_data_list:
    st.button(
        "Generate Documentation",
        type="primary",
        disabled=st.session_state.generating,
        on_click=start_generation
    )

    if st.session_state.generating:
        # Define excel_file outside try block so it's accessible in finally
        excel_file = "powerbi_documentation.xlsx"
        try:
            start_time = time.time()
            all_doc_data = {}
            
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner(''):
                total_items = sum(len(tmdl.measures) + len(tmdl.columns) for _, tmdl in st.session_state.tmdl_data_list)
                current_item = 0
                
                for filename, tmdl_data in st.session_state.tmdl_data_list:
                    doc_data = {}
                    measures_data = []
                    columns_data = []
                    
                    # Process measures
                    for measure in tmdl_data.measures:
                        status_text.text(f"Analyzing measure: {measure.name}")
                        definition = generate_llm_documentation(measure, 'measure')
                        measures_data.append({
                            'Table Name': tmdl_data.name.split('lineageTag')[0].strip(),
                            'Name': measure.name,
                            'Expression': measure.expression,
                            'Format String': measure.format_string or '',
                            'Lineage Tag': measure.lineage_tag or '',
                            'Definition': definition
                        })
                        current_item += 1
                        progress_bar.progress(current_item / total_items)
                    
                    # Process columns
                    for column in tmdl_data.columns:
                        status_text.text(f"Analyzing column: {column.name}")
                        definition = generate_llm_documentation(column, 'column')
                        columns_data.append({
                            'Table Name': tmdl_data.name.split('lineageTag')[0].strip(),
                            'Name': column.name,
                            'Data Type': column.data_type or '',
                            'Format String': column.format_string or '',
                            'Source Column': column.source_column or '',
                            'Lineage Tag': column.lineage_tag or '',
                            'Definition': definition
                        })
                        current_item += 1
                        progress_bar.progress(current_item / total_items)
                    
                    # Create DataFrames
                    doc_data['Measures'] = pd.DataFrame(measures_data)
                    doc_data['Columns'] = pd.DataFrame(columns_data)
                    doc_data['Table Overview'] = pd.DataFrame([{
                        'Table Name': tmdl_data.name,
                        'Number of Measures': len(tmdl_data.measures),
                        'Number of Columns': len(tmdl_data.columns),
                        'Lineage Tag': tmdl_data.lineage_tag or ''
                    }])
                    
                    # Clean table name (remove any lineageTag if present)
                    clean_table_name = tmdl_data.name.split('lineageTag')[0].strip()
                    
                    # Add table name to each DataFrame
                    for df in doc_data.values():
                        if 'Table Name' in df.columns:
                            df['Table Name'] = clean_table_name
                    
                    all_doc_data.update(doc_data)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # Show elapsed time
            st.success(f"Documentation generated in {elapsed:.2f} seconds.")
            
            # Initialize consolidated dataframes
            consolidated_overview = pd.DataFrame()
            consolidated_measures = pd.DataFrame()
            consolidated_columns = pd.DataFrame()
            
            # Use the already processed data
            for df_type, df in all_doc_data.items():
                if df_type == 'Table Overview':
                    consolidated_overview = pd.concat([consolidated_overview, df], ignore_index=True)
                elif df_type == 'Measures':
                    consolidated_measures = pd.concat([consolidated_measures, df], ignore_index=True)
                elif df_type == 'Columns':
                    consolidated_columns = pd.concat([consolidated_columns, df], ignore_index=True)
            
            # Add Table Name column if not present
            if not consolidated_measures.empty and 'Table Name' not in consolidated_measures.columns:
                consolidated_measures['Table Name'] = ''  # Will be filled later
            if not consolidated_columns.empty and 'Table Name' not in consolidated_columns.columns:
                consolidated_columns['Table Name'] = ''  # Will be filled later
            
            # Reorder columns to put Table Name first for measures and columns
            if not consolidated_measures.empty and 'Table Name' in consolidated_measures.columns:
                measure_cols = ['Table Name'] + [col for col in consolidated_measures.columns if col != 'Table Name']
                consolidated_measures = consolidated_measures[measure_cols]
            if not consolidated_columns.empty and 'Table Name' in consolidated_columns.columns:
                column_cols = ['Table Name'] + [col for col in consolidated_columns.columns if col != 'Table Name']
                consolidated_columns = consolidated_columns[column_cols]
            
            # Write to Excel
            with pd.ExcelWriter(excel_file) as writer:
                if not consolidated_overview.empty:
                    consolidated_overview.to_excel(writer, sheet_name='Table Overview', index=False)
                if not consolidated_measures.empty:
                    consolidated_measures.to_excel(writer, sheet_name='Measures', index=False)
                if not consolidated_columns.empty:
                    consolidated_columns.to_excel(writer, sheet_name='Columns', index=False)
            
            # Show preview of the documentation (first 5 rows only)
            if not consolidated_measures.empty:
                st.subheader("Documentation Preview (Measures)")
                st.dataframe(consolidated_measures.head(5), use_container_width=True)
            
            if not consolidated_columns.empty:
                st.subheader("Documentation Preview (Columns)")
                st.dataframe(consolidated_columns.head(5), use_container_width=True)
                
            # Add a note about preview limitation
            st.caption("Note: Preview shows first 5 rows only. Download the Excel file for complete documentation.")
            
            # Provide download button
            with open(excel_file, 'rb') as f:
                st.download_button(
                    label="Download Full Documentation",
                    data=f,
                    file_name=excel_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
        except Exception as e:
            st.error(f"Error generating documentation: {str(e)}")
        finally:
            st.session_state.generating = False
            # Clean up Excel file
            if os.path.exists(excel_file):
                os.unlink(excel_file)
            # Clean up temporary TMDL files
            for tmp_file_path in st.session_state.tmp_file_paths:
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
            st.session_state.tmp_file_paths = [] 