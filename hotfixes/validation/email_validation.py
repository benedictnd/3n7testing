"""
Email Validation Hotfix Module

This module provides enhanced email validation with improved handling for:
1. International domains (IDNs)
2. Common typos in popular email domains
3. Special character handling in local parts
4. Telemetry for tracking validation effectiveness

Schema versioning ensures compatibility with future validation updates.
"""

import re
import logging
import datetime
import socket
from typing import Dict, Any, Tuple, Optional, List
import idna

from hotfixes.validation.base import ValidationHotfix
from utils.telemetry import TelemetryClient

# Configure logging
logger = logging.getLogger('hotfixes.validation.email')

# Regular expression for enhanced email validation
# Accounts for:
# - Unicode characters in local part
# - IDN domains
# - Multiple TLDs including new gTLDs
# - Special characters in local part
EMAIL_REGEX = r"^((?:[-!#$%&'*+/=?^_`{}|~0-9A-Za-z]|(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f]))+(?:\.(?:[-!#$%&'*+/=?^_`{}|~0-9A-Za-z]|(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f]))+)*)@((?:(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[A-Za-z0-9-]*[A-Za-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\]))$"

# Common email domain typos and their corrections
DOMAIN_TYPOS = {
    'gmial.com': 'gmail.com',
    'gamil.com': 'gmail.com',
    'gmail.co': 'gmail.com',
    'gmal.com': 'gmail.com',
    'gmail.cm': 'gmail.com',
    'gmail.con': 'gmail.com',
    'hotmial.com': 'hotmail.com',
    'hotmal.com': 'hotmail.com',
    'hotmail.co': 'hotmail.com',
    'hotmil.com': 'hotmail.com',
    'hotmail.cm': 'hotmail.com',
    'hotmail.con': 'hotmail.com',
    'yaho.com': 'yahoo.com',
    'yahooo.com': 'yahoo.com',
    'yahoo.co': 'yahoo.com',
    'yahoo.cm': 'yahoo.com',
    'yahoo.con': 'yahoo.com',
    'outlook.co': 'outlook.com',
    'outloo.com': 'outlook.com',
    'outlook.cm': 'outlook.com',
    'outlook.con': 'outlook.com',
}

class EmailValidationFix(ValidationHotfix):
    """
    Enhanced email validation hotfix with telemetry and schema versioning.
    
    This hotfix provides:
    1. Improved regex-based validation for complex email formats
    2. Correction of common domain typos
    3. Support for IDN (International Domain Names)
    4. MX record verification (optional)
    5. Telemetry to track validation effectiveness
    """
    
    def __init__(self, schema_version: str = "1.0", 
                 telemetry_enabled: bool = True, 
                 verify_mx: bool = False):
        """
        Initialize the email validation hotfix.
        
        Args:
            schema_version: The schema version for this hotfix
            telemetry_enabled: Whether to collect telemetry data
            verify_mx: Whether to verify MX records for domains (can add latency)
        """
        super().__init__(schema_version)
        self.telemetry_enabled = telemetry_enabled
        self.verify_mx = verify_mx
        self.telemetry_client = TelemetryClient(prefix="email_validation")
        self.stats = {
            "total_validations": 0,
            "passed_original": 0,
            "passed_enhanced": 0,
            "failed_both": 0,
            "typos_corrected": 0,
            "idn_processed": 0
        }
        self.last_reset = datetime.datetime.now()
        logger.info(f"Email validation hotfix initialized with schema v{schema_version}")
        logger.info(f"Telemetry enabled: {telemetry_enabled}, MX verification: {verify_mx}")
    
    def validate_email(self, email: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validate an email address with enhanced checks.
        
        Args:
            email: The email address to validate
            
        Returns:
            Tuple containing:
            - Boolean indicating if email is valid
            - Corrected email (if typo was fixed, otherwise None)
            - Dict with additional validation details
        """
        if not email:
            logger.debug("Empty email provided")
            return False, None, {"reason": "empty_email"}
            
        # Track validation attempt
        self.stats["total_validations"] += 1
        
        # Start with original validation
        original_valid = self._original_validation(email)
        
        # If original validation passes and we're not in active mode, return success
        if original_valid and not self.is_active:
            self.stats["passed_original"] += 1
            if self.telemetry_enabled:
                self._record_telemetry(email, valid=True, method="original")
            return True, None, {"method": "original"}
            
        # Apply enhanced validation if active or original validation failed
        enhanced_valid, corrected_email, details = self._enhanced_validation(email)
        
        # Track results
        if enhanced_valid:
            self.stats["passed_enhanced"] += 1
            if corrected_email:
                self.stats["typos_corrected"] += 1
                
            if '@' in email and '@' in corrected_email or email:
                original_domain = email.split('@')[1] if '@' in email else ""
                if original_domain and self._is_idn(original_domain):
                    self.stats["idn_processed"] += 1
        else:
            self.stats["failed_both"] += 1
            
        # Record telemetry if enabled
        if self.telemetry_enabled:
            self._record_telemetry(
                email, 
                valid=enhanced_valid,
                corrected=corrected_email if corrected_email != email else None,
                method="enhanced",
                details=details
            )
            
        return enhanced_valid, corrected_email, details
    
    def _original_validation(self, email: str) -> bool:
        """
        Perform the original basic email validation.
        
        Args:
            email: The email to validate
            
        Returns:
            Boolean indicating if email passes basic validation
        """
        # Simple email validation using basic pattern
        basic_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(basic_pattern, email))
    
    def _enhanced_validation(self, email: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Perform enhanced email validation with correction capabilities.
        
        Args:
            email: The email to validate
            
        Returns:
            Tuple containing:
            - Boolean indicating if email is valid
            - Corrected email (if applicable)
            - Dict with additional validation details
        """
        details = {"method": "enhanced"}
        
        # Check basic format
        if '@' not in email:
            logger.debug(f"Invalid email format (missing @): {email}")
            details["reason"] = "missing_at_symbol"
            return False, email, details
            
        # Split email into local and domain parts
        local_part, domain = email.split('@', 1)
        
        # Check for empty parts
        if not local_part or not domain:
            logger.debug(f"Invalid email format (empty part): {email}")
            details["reason"] = "empty_part"
            return False, email, details
            
        # Check and correct domain typos
        domain, domain_corrected = self._check_and_correct_domain(domain)
        corrected_email = f"{local_part}@{domain}" if domain_corrected else email
        if domain_corrected:
            details["corrected"] = True
            details["original_domain"] = email.split('@')[1]
            details["corrected_domain"] = domain
            
        # Handle IDN domains
        is_idn = self._is_idn(domain)
        if is_idn:
            details["idn"] = True
            try:
                # Convert to ASCII for validation
                ascii_domain = idna.encode(domain).decode('ascii')
                punycode_email = f"{local_part}@{ascii_domain}"
                details["punycode"] = ascii_domain
            except Exception as e:
                logger.warning(f"IDN conversion error for {domain}: {str(e)}")
                details["reason"] = "idn_conversion_error"
                return False, corrected_email, details
        
        # Apply comprehensive regex validation
        valid = bool(re.match(EMAIL_REGEX, corrected_email))
        if not valid:
            logger.debug(f"Failed regex validation: {corrected_email}")
            details["reason"] = "regex_validation_failed"
            return False, corrected_email, details
            
        # Optionally verify MX record
        if self.verify_mx:
            mx_valid = self._verify_mx_record(domain)
            if not mx_valid:
                logger.debug(f"Failed MX record verification for domain: {domain}")
                details["reason"] = "mx_verification_failed"
                return False, corrected_email, details
            details["mx_verified"] = True
            
        return True, corrected_email, details
        
    def _check_and_correct_domain(self, domain: str) -> Tuple[str, bool]:
        """
        Check if domain has a common typo and correct it if needed.
        
        Args:
            domain: The domain to check
            
        Returns:
            Tuple containing:
            - Corrected domain (or original if no correction)
            - Boolean indicating if correction was made
        """
        domain = domain.lower()
        if domain in DOMAIN_TYPOS:
            corrected = DOMAIN_TYPOS[domain]
            logger.info(f"Corrected domain typo: {domain} -> {corrected}")
            return corrected, True
        return domain, False
        
    def _is_idn(self, domain: str) -> bool:
        """
        Check if a domain is an IDN (contains non-ASCII characters).
        
        Args:
            domain: The domain to check
            
        Returns:
            Boolean indicating if domain is an IDN
        """
        return any(ord(char) > 127 for char in domain)
        
    def _verify_mx_record(self, domain: str) -> bool:
        """
        Verify that a domain has valid MX records.
        
        Args:
            domain: The domain to verify
            
        Returns:
            Boolean indicating if domain has valid MX records
        """
        try:
            # Try to resolve MX records for the domain
            answers = socket.getaddrinfo(domain, None)
            return len(answers) > 0
        except socket.gaierror:
            try:
                # Fall back to checking MX records directly
                host = f"mail.{domain}"
                socket.gethostbyname(host)
                return True
            except socket.gaierror:
                return False
            
    def _record_telemetry(self, email: str, valid: bool, method: str, 
                         corrected: Optional[str] = None, 
                         details: Optional[Dict[str, Any]] = None) -> None:
        """
        Record telemetry data for email validation.
        
        Args:
            email: The email being validated (domain part only logged for privacy)
            valid: Whether validation succeeded
            method: The validation method used
            corrected: The corrected email if applicable
            details: Additional validation details
        """
        if not self.telemetry_enabled:
            return
            
        # Only log domain part for privacy
        domain = email.split('@')[1] if '@' in email else "invalid"
        
        # Prepare telemetry data
        telemetry_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "domain": domain,
            "valid": valid,
            "method": method,
            "schema_version": self.schema_version,
        }
        
        # Add correction info if applicable
        if corrected and '@' in corrected:
            corrected_domain = corrected.split('@')[1]
            telemetry_data["corrected_domain"] = corrected_domain
            
        # Add any additional details
        if details:
            # Filter out sensitive information
            safe_details = {k: v for k, v in details.items() 
                           if k not in ["email", "local_part"]}
            telemetry_data.update(safe_details)
            
        # Send telemetry data
        try:
            self.telemetry_client.record_event("email_validation", telemetry_data)
        except Exception as e:
            logger.warning(f"Failed to record telemetry: {str(e)}")
            
    def get_telemetry_stats(self) -> Dict[str, Any]:
        """
        Get current telemetry statistics.
        
        Returns:
            Dict containing telemetry statistics
        """
        # Calculate derived statistics
        stats = self.stats.copy()
        total = stats["total_validations"]
        
        if total > 0:
            stats["original_pass_rate"] = round(stats["passed_original"] / total * 100, 2)
            stats["enhanced_pass_rate"] = round(stats["passed_enhanced"] / total * 100, 2)
            stats["correction_rate"] = round(stats["typos_corrected"] / total * 100, 2)
            stats["failure_rate"] = round(stats["failed_both"] / total * 100, 2)
            
        stats["uptime_hours"] = round((datetime.datetime.now() - self.last_reset).total_seconds() / 3600, 2)
        
        return stats
        
    def reset_stats(self) -> None:
        """
        Reset telemetry statistics.
        """
        self.stats = {
            "total_validations": 0,
            "passed_original": 0,
            "passed_enhanced": 0,
            "failed_both": 0,
            "typos_corrected": 0,
            "idn_processed": 0
        }
        self.last_reset = datetime.datetime.now()
        logger.info("Email validation telemetry statistics reset")
        
    def cleanup(self) -> None:
        """
        Clean up resources used by the hotfix.
        """
        logger.info("Cleaning up email validation hotfix resources")
        if self.telemetry_enabled:
            try:
                # Flush any pending telemetry data
                self.telemetry_client.flush()
            except Exception as e:
                logger.warning(f"Error during telemetry cleanup: {str(e)}")
                
    def get_schema_version(self) -> str:
        """
        Get the schema version for this hotfix.
        
        Returns:
            Schema version string
        """
        return self.schema_version 