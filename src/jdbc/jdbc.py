"""
JDBC Connector Module for Databricks DBT Project
Handles JDBC connections to Databricks and other databases for metadata-driven transformations
"""

from typing import Dict, Any, Optional, List
import logging
try:
    import pyodbc
except ImportError:
    pyodbc = None
try:
    import jaydebeapi
except ImportError:
    jaydebeapi = None


class JDBCConnector:
    """
    A class to handle JDBC connections to Databricks and other databases
    """
    
    def __init__(self, connection_string: str, driver: Optional[str] = None, 
                 username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the JDBC connector
        
        Args:
            connection_string: Full connection string for the database
            driver: JDBC driver class name
            username: Database username
            password: Database password
        """
        self.connection_string = connection_string
        self.driver = driver
        self.username = username
        self.password = password
        self.connection = None
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """
        Establish a connection to the database
        """
        if pyodbc:
            try:
                if self.username and self.password:
                    self.connection = pyodbc.connect(
                        self.connection_string,
                        uid=self.username,
                        pwd=self.password
                    )
                else:
                    self.connection = pyodbc.connect(self.connection_string)
                
                self.logger.info("Successfully connected to database via pyodbc")
            except Exception as e:
                self.logger.error(f"Error connecting to database with pyodbc: {str(e)}")
                raise
        elif jaydebeapi:
            try:
                # Using jaydebeapi as alternative
                if self.username and self.password:
                    self.connection = jaydebeapi.connect(
                        self.driver,
                        self.connection_string,
                        {'user': self.username, 'password': self.password}
                    )
                else:
                    self.connection = jaydebeapi.connect(
                        self.driver,
                        self.connection_string
                    )
                
                self.logger.info("Successfully connected to database via jaydebeapi")
            except Exception as e:
                self.logger.error(f"Error connecting to database with jaydebeapi: {str(e)}")
                raise
        else:
            raise ImportError("Either pyodbc or jaydebeapi must be installed to use JDBCConnector")
    
    def disconnect(self):
        """
        Close the database connection
        """
        if self.connection:
            try:
                self.connection.close()
                self.logger.info("Database connection closed")
            except Exception as e:
                self.logger.error(f"Error closing database connection: {str(e)}")
            finally:
                self.connection = None
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results
        
        Args:
            query: SQL query to execute
            
        Returns:
            List of dictionaries representing rows
        """
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [column[0] for column in cursor.description]
            
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            cursor.close()
            
            self.logger.info(f"Query executed successfully, returned {len(result)} rows")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing query: {str(e)}")
            raise
    
    def execute_non_query(self, query: str) -> int:
        """
        Execute a non-SELECT query (INSERT, UPDATE, DELETE)
        
        Args:
            query: SQL query to execute
            
        Returns:
            Number of affected rows
        """
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            affected_rows = cursor.rowcount
            self.connection.commit()
            cursor.close()
            
            self.logger.info(f"Non-query executed successfully, affected {affected_rows} rows")
            return affected_rows
            
        except Exception as e:
            self.logger.error(f"Error executing non-query: {str(e)}")
            self.connection.rollback()
            raise
    
    def fetch_metadata(self, table_name: str, schema_name: str = 'default') -> List[Dict[str, Any]]:
        """
        Fetch metadata for a specific table
        
        Args:
            table_name: Name of the table
            schema_name: Schema name (default is 'default')
            
        Returns:
            List of dictionaries with column metadata
        """
        query = f"""
        DESCRIBE TABLE {schema_name}.{table_name}
        """
        
        return self.execute_query(query)


def create_jdbc_connector(config: Dict[str, Any]) -> JDBCConnector:
    """
    Factory function to create a JDBC connector from configuration
    
    Args:
        config: Configuration dictionary with connection details
        
    Returns:
        JDBCConnector instance
    """
    return JDBCConnector(
        connection_string=config['connection_string'],
        driver=config.get('driver'),
        username=config.get('username'),
        password=config.get('password')
    )