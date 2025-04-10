"""
Validation hotfixes package for the 3&7 Training Platform API.

This package contains validation hotfixes to address common validation issues,
particularly email validation and null handling, with integrated telemetry
to monitor the effectiveness of the fixes.
"""

from hotfixes.validation.email_validator import ValidationHotfix, EmailValidationFix, NullHandlingFix

__all__ = ["ValidationHotfix", "EmailValidationFix", "NullHandlingFix"] 