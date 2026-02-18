"""
API Connector Module for Databricks DBT Project
Handles API connections and data retrieval for metadata-driven transformations
"""

import requests
from typing import Dict, Any, Optional
import logging


class APIConnector:
    """
    A class to handle API connections and data retrieval
    """
    
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None, 
                 auth: Optional[tuple] = None):
        """
        Initialize the API connector
        
        Args:
            base_url: Base URL for the API
            headers: Optional headers to include in requests
            auth: Optional authentication tuple
        """
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.auth = auth
        self.session = requests.Session()
        
        # Update session with provided headers and auth
        self.session.headers.update(self.headers)
        if self.auth:
            self.session.auth = self.auth
            
        # Set up logging
        self.logger = logging.getLogger(__name__)
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to the API
        
        Args:
            endpoint: API endpoint to call
            params: Optional query parameters
            
        Returns:
            Response JSON data
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            self.logger.info(f"Making GET request to {url}")
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making GET request to {url}: {str(e)}")
            raise
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a POST request to the API
        
        Args:
            endpoint: API endpoint to call
            data: Data to send in request body
            
        Returns:
            Response JSON data
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            self.logger.info(f"Making POST request to {url}")
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making POST request to {url}: {str(e)}")
            raise
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a PUT request to the API
        
        Args:
            endpoint: API endpoint to call
            data: Data to send in request body
            
        Returns:
            Response JSON data
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            self.logger.info(f"Making PUT request to {url}")
            response = self.session.put(url, json=data)
            response.raise_for_status()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making PUT request to {url}: {str(e)}")
            raise
    
    def delete(self, endpoint: str) -> bool:
        """
        Make a DELETE request to the API
        
        Args:
            endpoint: API endpoint to call
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            self.logger.info(f"Making DELETE request to {url}")
            response = self.session.delete(url)
            response.raise_for_status()
            
            return True
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making DELETE request to {url}: {str(e)}")
            return False


def create_api_connector(config: Dict[str, Any]) -> APIConnector:
    """
    Factory function to create an API connector from configuration
    
    Args:
        config: Configuration dictionary with connection details
        
    Returns:
        APIConnector instance
    """
    return APIConnector(
        base_url=config.get('base_url', ''),
        headers=config.get('headers'),
        auth=(config['auth']['username'], config['auth']['password'])
        if config.get('auth') else None
    )