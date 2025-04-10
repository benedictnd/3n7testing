"""
Email validation hotfix module for 3&7 Training Platform API.

This module provides enhanced email validation with telemetry and logging
to address common validation failures in production. It implements both 
standard RFC 5322 validation and additional business rule validation.
"""

import re
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logger = logging.getLogger("validation.hotfix")

# Metrics for telemetry
VALIDATION_ATTEMPTS = Counter(
    'validation_attempts_total', 
    'Number of validation attempts',
    ['validator_type', 'schema_version']
)

VALIDATION_FAILURES = Counter(
    'validation_failures_total', 
    'Number of validation failures',
    ['validator_type', 'failure_type', 'schema_version']
)

VALIDATION_DURATION = Histogram(
    'validation_duration_seconds', 
    'Time spent on validation',
    ['validator_type', 'schema_version']
)

VALIDATION_FIXED = Counter(
    'validation_fixed_total', 
    'Number of values fixed by validation',
    ['validator_type', 'fix_type', 'schema_version']
)

HOTFIX_ACTIVE = Gauge(
    'hotfix_active', 
    'Indicates if a hotfix is currently active',
    ['hotfix_type', 'schema_version']
)

class ValidationHotfix(ABC):
    """Base class for all validation hotfixes."""
    
    def __init__(self, schema_version: str = "v1"):
        """
        Initialize the validation hotfix.
        
        Args:
            schema_version: The schema version for telemetry tracking
        """
        self.schema_version = schema_version
        self.validation_type = self.__class__.__name__
        self.hotfix_active = True
        HOTFIX_ACTIVE.labels(
            hotfix_type=self.validation_type,
            schema_version=self.schema_version
        ).set(1)
        
        logger.info(f"Initialized {self.validation_type} hotfix for schema {schema_version}")
    
    def __del__(self):
        """Cleanup when the hotfix is removed."""
        try:
            HOTFIX_ACTIVE.labels(
                hotfix_type=self.validation_type,
                schema_version=self.schema_version
            ).set(0)
            logger.info(f"Deactivated {self.validation_type} hotfix for schema {self.schema_version}")
        except Exception:
            # Ignore errors during shutdown
            pass
    
    @abstractmethod
    def validate(self, value: Any) -> Tuple[bool, Optional[Any], Dict[str, Any]]:
        """
        Validate a value and return validation status.
        
        Args:
            value: The value to validate
            
        Returns:
            Tuple containing:
              - Boolean indicating if validation passed
              - Optional fixed value (if automatic fixing is possible)
              - Metadata dictionary with validation details
        """
        pass
    
    def validate_with_telemetry(self, value: Any) -> Tuple[bool, Optional[Any], Dict[str, Any]]:
        """
        Validate with integrated telemetry tracking.
        
        Args:
            value: The value to validate
            
        Returns:
            Same as validate() but with telemetry tracking
        """
        VALIDATION_ATTEMPTS.labels(
            validator_type=self.validation_type,
            schema_version=self.schema_version
        ).inc()
        
        start_time = time.time()
        try:
            valid, fixed_value, metadata = self.validate(value)
            
            if not valid:
                failure_type = metadata.get('failure_type', 'unknown')
                VALIDATION_FAILURES.labels(
                    validator_type=self.validation_type,
                    failure_type=failure_type,
                    schema_version=self.schema_version
                ).inc()
                logger.warning(
                    f"Validation failed: {self.validation_type}, "
                    f"failure: {failure_type}, value: {value}"
                )
            
            if fixed_value is not None and fixed_value != value:
                fix_type = metadata.get('fix_type', 'unknown')
                VALIDATION_FIXED.labels(
                    validator_type=self.validation_type,
                    fix_type=fix_type,
                    schema_version=self.schema_version
                ).inc()
                logger.info(
                    f"Value fixed: {self.validation_type}, "
                    f"from: {value}, to: {fixed_value}, fix_type: {fix_type}"
                )
                
            return valid, fixed_value, metadata
            
        finally:
            duration = time.time() - start_time
            VALIDATION_DURATION.labels(
                validator_type=self.validation_type,
                schema_version=self.schema_version
            ).observe(duration)


class EmailValidationFix(ValidationHotfix):
    """Email validation hotfix with RFC 5322 compliance and business rules."""
    
    # RFC 5322 compliant email regex pattern
    EMAIL_PATTERN = re.compile(r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""", re.IGNORECASE)
    
    # Simplified pattern for basic structural validation
    BASIC_EMAIL_PATTERN = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
    
    # Common typos in email domains
    COMMON_DOMAIN_TYPOS = {
        "gmail.co": "gmail.com",
        "gmail.cmo": "gmail.com",
        "gamil.com": "gmail.com",
        "gnail.com": "gmail.com",
        "gmail.comm": "gmail.com",
        "gmail.con": "gmail.com",
        "hotmail.co": "hotmail.com",
        "hotmail.cmo": "hotmail.com",
        "yaho.com": "yahoo.com",
        "yahooo.com": "yahoo.com",
        "yahoo.co": "yahoo.com",
        "ymail.com": "yahoo.com",
        "outlook.co": "outlook.com",
    }
    
    # Invalid TLDs that should be rejected
    INVALID_TLDS = {
        "local", "invalid", "localhost", "example", "test", "intranet"
    }
    
    def __init__(self, schema_version: str = "v1", auto_fix: bool = True):
        """
        Initialize the email validation hotfix.
        
        Args:
            schema_version: The schema version this hotfix applies to
            auto_fix: Whether to automatically fix common issues
        """
        super().__init__(schema_version)
        self.auto_fix = auto_fix
        logger.info(f"Email validation hotfix initialized with auto_fix={auto_fix}")
    
    def validate(self, value: Any) -> Tuple[bool, Optional[Any], Dict[str, Any]]:
        """
        Validate an email address according to RFC 5322 and business rules.
        
        Args:
            value: The email value to validate
            
        Returns:
            Tuple containing:
              - Boolean indicating if email is valid
              - Fixed email if auto_fix is True and fixing is possible
              - Metadata with validation details
        """
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "validator": "EmailValidationFix",
            "schema_version": self.schema_version,
        }
        
        # Handle null values
        if value is None:
            metadata["failure_type"] = "null_value"
            return False, None, metadata
        
        # Handle non-string values
        if not isinstance(value, str):
            try:
                value = str(value)
                metadata["fix_type"] = "type_conversion"
            except Exception as e:
                metadata["failure_type"] = "type_error"
                metadata["error_details"] = str(e)
                return False, None, metadata
        
        # Handle empty strings
        if value.strip() == "":
            metadata["failure_type"] = "empty_value"
            return False, None, metadata
        
        # Perform basic cleanup
        fixed_email = value.strip().lower()
        if fixed_email != value:
            metadata["fix_type"] = "basic_cleanup"
        
        # Check for basic structure
        if not self.BASIC_EMAIL_PATTERN.match(fixed_email):
            metadata["failure_type"] = "invalid_format"
            return False, None if not self.auto_fix else fixed_email, metadata
        
        # Extract domain for additional checks
        try:
            domain = fixed_email.split('@')[1]
        except IndexError:
            metadata["failure_type"] = "missing_domain"
            return False, None, metadata
        
        # Check for invalid TLDs
        tld = domain.split('.')[-1].lower()
        if tld in self.INVALID_TLDS:
            metadata["failure_type"] = "invalid_tld"
            return False, None, metadata
        
        # Fix common domain typos
        for typo, correction in self.COMMON_DOMAIN_TYPOS.items():
            if domain == typo:
                username = fixed_email.split('@')[0]
                corrected_email = f"{username}@{correction}"
                metadata["fix_type"] = "domain_typo_correction"
                metadata["original_domain"] = domain
                metadata["corrected_domain"] = correction
                return True, corrected_email if self.auto_fix else fixed_email, metadata
        
        # Full RFC 5322 validation
        if not self.EMAIL_PATTERN.match(fixed_email):
            metadata["failure_type"] = "rfc5322_failure"
            return False, None if not self.auto_fix else fixed_email, metadata
        
        # Additional business rules can be added here
        
        # If we reach here, the email is valid
        return True, fixed_email if fixed_email != value else None, metadata


class NullHandlingFix(ValidationHotfix):
    """Hotfix for handling null values in validation contexts."""
    
    def __init__(self, schema_version: str = "v1", default_value: Any = None, 
                 allow_nulls: bool = False):
        """
        Initialize the null handling hotfix.
        
        Args:
            schema_version: The schema version this hotfix applies to
            default_value: Default value to use when fixing null values
            allow_nulls: Whether to consider nulls as valid values
        """
        super().__init__(schema_version)
        self.default_value = default_value
        self.allow_nulls = allow_nulls
        logger.info(
            f"Null handling hotfix initialized with allow_nulls={allow_nulls}, "
            f"default_value={default_value}"
        )
    
    def validate(self, value: Any) -> Tuple[bool, Optional[Any], Dict[str, Any]]:
        """
        Validate value handling nulls according to configuration.
        
        Args:
            value: The value to validate
            
        Returns:
            Tuple containing:
              - Boolean indicating if handling is valid
              - Fixed value if applicable
              - Metadata with validation details
        """
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "validator": "NullHandlingFix",
            "schema_version": self.schema_version,
        }
        
        is_null = value is None
        
        # Empty strings are often treated like nulls
        if isinstance(value, str) and value.strip() == "":
            is_null = True
            metadata["null_type"] = "empty_string"
        
        if is_null:
            if self.allow_nulls:
                return True, None, metadata
            else:
                metadata["failure_type"] = "null_not_allowed"
                if self.default_value is not None:
                    metadata["fix_type"] = "default_value_applied"
                    return True, self.default_value, metadata
                return False, None, metadata
        
        # Value is not null, so it's valid in this context
        return True, None, metadata 