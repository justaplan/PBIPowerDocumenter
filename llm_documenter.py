import os
from openai import OpenAI
# from dotenv import load_dotenv
from tmdl_parser import Table, Measure, Column
import pandas as pd
import streamlit as st

# Load environment variables
# load_dotenv()

# Initialize OpenAI client with Qwen configuration
# api_key = st.secrets["DASHSCOPE_API_KEY"]
api_key = st.secrets["NEBIUS_API_KEY"]
if not api_key:
    raise ValueError("NEBIUS_API_KEY not found in environment variables")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.studio.nebius.com/v1/"
    # base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
)

def analyze_measure(measure: Measure) -> str:
    """Use LLM to analyze and document a measure in a concise, business-friendly way."""
    prompt = f"""
    Provide a concise, business-friendly definition of this Power BI measure in no more than 50 words. The definition must start with: 'The measure represents'.
    
    Name: {measure.name}
    Expression: {measure.expression}
    Format String: {measure.format_string or 'Not specified'}
    
    Focus on:
    1. What business metric this measure represents
    2. How it's calculated in simple terms
    3. Any important business context
    """
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-fast",
            messages=[
                {"role": "system", "content": "You are a business analyst helping to document Power BI measures in clear, concise language. Always start the definition with: 'The measure represents'."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating definition: {str(e)}"

def analyze_column(column: Column) -> str:
    """Use LLM to analyze and document a column in a concise, business-friendly way."""
    prompt = f"""
    Provide a concise, business-friendly definition of this Power BI column in no more than 50 words. The definition must start with: 'The column represents'.
    
    Name: {column.name}
    Data Type: {column.data_type or 'Not specified'}
    Source Column: {column.source_column or 'Not specified'}
    Format String: {column.format_string or 'Not specified'}
    
    Focus on:
    1. What business data this column represents
    2. How it's used in the business context
    3. Any important business rules or constraints
    """
    
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-fast",
            messages=[
                {"role": "system", "content": "You are a business analyst helping to document Power BI columns in clear, concise language. Always start the definition with: 'The column represents'."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating definition: {str(e)}"

def generate_llm_documentation(item, item_type: str) -> str:
    """Generate documentation for a single measure or column using LLM analysis."""
    if item_type == 'measure':
        return analyze_measure(item)
    elif item_type == 'column':
        return analyze_column(item)
    else:
        raise ValueError(f"Unknown item type: {item_type}") 