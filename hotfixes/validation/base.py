"""
Base Validation Hotfix Module

This module provides the base class for all validation hotfixes in the 3&7 Training
Platform API. It defines the common interface that all specific validation 
hotfixes must implement.
"""

import abc
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger('hotfixes.validation.base')

class ValidationHotfix(abc.ABC):
    """
    Abstract base class for all validation hotfixes.
    
    This class defines the interface that all validation hotfixes must implement.
    It provides a foundation for creating hotfixes that can be applied to fix
    validation issues in the API.
    """
    
    def __init__(self, schema_version: str = "1.0"):
        """
        Initialize the validation hotfix.
        
        Args:
            schema_version: The schema version for this hotfix
        """
        self.schema_version = schema_version
        self.is_active = False
        logger.debug(f"Initialized validation hotfix with schema v{schema_version}")
        
    def activate(self) -> bool:
        """
        Activate the hotfix.
        
        Returns:
            Boolean indicating successful activation
        """
        try:
            self.is_active = True
            logger.info(f"Activated validation hotfix with schema v{self.schema_version}")
            return True
        except Exception as e:
            logger.error(f"Failed to activate validation hotfix: {str(e)}")
            return False
            
    def deactivate(self) -> bool:
        """
        Deactivate the hotfix.
        
        Returns:
            Boolean indicating successful deactivation
        """
        try:
            self.is_active = False
            logger.info(f"Deactivated validation hotfix with schema v{self.schema_version}")
            return True
        except Exception as e:
            logger.error(f"Failed to deactivate validation hotfix: {str(e)}")
            return False
            
    @abc.abstractmethod
    def cleanup(self) -> None:
        """
        Clean up resources used by the hotfix.
        """
        pass
        
    @abc.abstractmethod
    def get_schema_version(self) -> str:
        """
        Get the schema version for this hotfix.
        
        Returns:
            Schema version string
        """
        pass
        
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the hotfix.
        
        Returns:
            Dict containing status information
        """
        return {
            "active": self.is_active,
            "schema_version": self.schema_version
        } 