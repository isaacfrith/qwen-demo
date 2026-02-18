"""
Metadata Framework for Databricks DBT Project
Provides a metadata-driven approach to managing transformations
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json
import yaml
from pathlib import Path


@dataclass
class TransformationRule:
    """
    Represents a single transformation rule
    """
    name: str
    source_table: str
    target_table: str
    transformation_type: str  # 'silver' or 'gold'
    columns: List[Dict[str, Any]]
    filters: Optional[List[str]] = None
    joins: Optional[List[Dict[str, Any]]] = None
    aggregations: Optional[List[Dict[str, Any]]] = None
    schedule: Optional[str] = None  # Cron expression for scheduling


@dataclass
class MetadataConfig:
    """
    Configuration for the metadata framework
    """
    project_name: str
    version: str
    transformations: List[TransformationRule] = field(default_factory=list)
    sources: Dict[str, Any] = field(default_factory=dict)
    targets: Dict[str, Any] = field(default_factory=dict)
    

class MetadataFramework:
    """
    Main class for the metadata-driven framework
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the metadata framework with a configuration file
        
        Args:
            config_path: Path to the metadata configuration file
        """
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.transformations = self.config.transformations
    
    def load_config(self) -> MetadataConfig:
        """
        Load the metadata configuration from file
        
        Returns:
            MetadataConfig object
        """
        with open(self.config_path, 'r') as f:
            if self.config_path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        # Create transformation rules from the loaded data
        transformations = [
            TransformationRule(
                name=tr.get('name'),
                source_table=tr.get('source_table'),
                target_table=tr.get('target_table'),
                transformation_type=tr.get('transformation_type'),
                columns=tr.get('columns', []),
                filters=tr.get('filters'),
                joins=tr.get('joins'),
                aggregations=tr.get('aggregations'),
                schedule=tr.get('schedule')
            )
            for tr in data.get('transformations', [])
        ]
        
        return MetadataConfig(
            project_name=data.get('project_name', 'unnamed'),
            version=data.get('version', '1.0.0'),
            transformations=transformations,
            sources=data.get('sources', {}),
            targets=data.get('targets', {})
        )
    
    def get_transformation_by_name(self, name: str) -> Optional[TransformationRule]:
        """
        Get a specific transformation rule by name
        
        Args:
            name: Name of the transformation rule
            
        Returns:
            TransformationRule if found, None otherwise
        """
        for transformation in self.transformations:
            if transformation.name == name:
                return transformation
        return None
    
    def get_transformations_by_type(self, transformation_type: str) -> List[TransformationRule]:
        """
        Get all transformation rules of a specific type (silver or gold)
        
        Args:
            transformation_type: Type of transformation ('silver' or 'gold')
            
        Returns:
            List of matching TransformationRule objects
        """
        return [
            t for t in self.transformations 
            if t.transformation_type == transformation_type
        ]
    
    def generate_dbt_model(self, transformation: TransformationRule) -> str:
        """
        Generate DBT model SQL based on transformation rule
        
        Args:
            transformation: Transformation rule to generate model for
            
        Returns:
            Generated SQL string
        """
        # Build the SELECT clause
        select_parts = []
        for col in transformation.columns:
            alias = col.get('alias', col['name'])
            expr = col.get('expression', col['name'])
            select_parts.append(f"  {expr} AS {alias}")
        
        select_clause = ',\n'.join(select_parts)
        
        # Build the FROM clause
        from_clause = f"FROM {{{{ source('{transformation.source_table.split('.')[0]}', '{transformation.source_table.split('.')[1]}') }}}}"
        
        # Build the WHERE clause if filters exist
        where_clause = ""
        if transformation.filters:
            where_clause = f"WHERE {' AND '.join(transformation.filters)}"
        
        # Combine all parts
        sql = f"""SELECT\n{select_clause}\n{from_clause}\n{where_clause}"""
        
        return sql
    
    def generate_all_models(self, output_dir: str):
        """
        Generate all DBT models based on transformation rules
        
        Args:
            output_dir: Directory to save the generated models
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for transformation in self.transformations:
            sql_content = self.generate_dbt_model(transformation)
            
            # Determine the subdirectory based on transformation type
            subdir = output_path / transformation.transformation_type
            subdir.mkdir(exist_ok=True)
            
            # Write the model file
            model_file = subdir / f"{transformation.name}.sql"
            with open(model_file, 'w') as f:
                f.write(sql_content)
    
    def validate_config(self) -> List[str]:
        """
        Validate the metadata configuration
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check that all transformations have required fields
        for i, transformation in enumerate(self.transformations):
            if not transformation.name:
                errors.append(f"Transformation {i} missing name")
            if not transformation.source_table:
                errors.append(f"Transformation {i} missing source_table")
            if not transformation.target_table:
                errors.append(f"Transformation {i} missing target_table")
            if transformation.transformation_type not in ['silver', 'gold']:
                errors.append(f"Transformation {i} has invalid transformation_type: {transformation.transformation_type}")
            if not transformation.columns:
                errors.append(f"Transformation {i} missing columns")
        
        return errors


def load_metadata_framework(config_path: str) -> MetadataFramework:
    """
    Factory function to create a metadata framework from configuration
    
    Args:
        config_path: Path to the metadata configuration file
        
    Returns:
        MetadataFramework instance
    """
    return MetadataFramework(config_path)