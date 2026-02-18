"""
Utility functions for the Databricks DBT project
"""

import os
from typing import Dict, Any
import yaml
import json


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML or JSON file
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        if config_path.lower().endswith('.yaml') or config_path.lower().endswith('.yml'):
            return yaml.safe_load(f)
        else:
            return json.load(f)


def get_env_variable(var_name: str, default_value: str = None) -> str:
    """
    Get environment variable with optional default value
    
    Args:
        var_name: Name of the environment variable
        default_value: Default value if variable is not set
        
    Returns:
        Value of the environment variable or default value
    """
    value = os.getenv(var_name)
    if value is None:
        if default_value is not None:
            return default_value
        else:
            raise ValueError(f"Environment variable {var_name} not set and no default provided")
    
    return value


def validate_required_params(params: Dict[str, Any], required_keys: list) -> None:
    """
    Validate that all required keys are present in the parameters dictionary
    
    Args:
        params: Dictionary of parameters to validate
        required_keys: List of required keys
        
    Raises:
        ValueError: If any required key is missing
    """
    missing_keys = [key for key in required_keys if key not in params]
    if missing_keys:
        raise ValueError(f"Missing required parameters: {missing_keys}")


def format_sql_column_list(columns: list) -> str:
    """
    Format a list of column definitions into a SQL column list
    
    Args:
        columns: List of column dictionaries with 'name' and optionally 'alias' and 'expression'
        
    Returns:
        Formatted SQL column list string
    """
    formatted_columns = []
    for col in columns:
        if 'expression' in col:
            expr = col['expression']
        else:
            expr = col['name']
        
        alias = col.get('alias', col.get('name'))
        formatted_columns.append(f"  {expr} AS {alias}")
    
    return ',\n'.join(formatted_columns)


def build_filter_clause(filters: list) -> str:
    """
    Build a SQL WHERE clause from a list of filter conditions
    
    Args:
        filters: List of filter condition strings
        
    Returns:
        SQL WHERE clause string
    """
    if not filters:
        return ""
    
    return f"WHERE {' AND '.join(filters)}"


def pluralize(word: str, count: int) -> str:
    """
    Simple pluralization helper
    
    Args:
        word: Word to potentially pluralize
        count: Count to determine if plural form is needed
        
    Returns:
        Singular or plural form of the word
    """
    if count == 1:
        return word
    else:
        return f"{word}s"