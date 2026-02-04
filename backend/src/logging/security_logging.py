import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from fastapi import Request
from pydantic import BaseModel


class SecurityEventType(str, Enum):
    AUTH_LOGIN_SUCCESS = "auth_login_success"
    AUTH_LOGIN_FAILURE = "auth_login_failure"
    AUTH_SIGNUP_SUCCESS = "auth_signup_success"
    AUTH_SIGNUP_FAILURE = "auth_signup_failure"
    AUTH_TOKEN_ISSUED = "auth_token_issued"
    AUTH_TOKEN_EXPIRED = "auth_token_expired"
    AUTH_ACCESS_DENIED = "auth_access_denied"
    DATA_ACCESS_ATTEMPT = "data_access_attempt"
    DATA_ACCESS_SUCCESS = "data_access_success"
    DATA_ACCESS_FAILURE = "data_access_failure"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INPUT_VALIDATION_FAILED = "input_validation_failed"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class SecurityLogEntry(BaseModel):
    timestamp: str
    event_type: SecurityEventType
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    status: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    severity: str = "info"  # info, warning, error, critical


class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger("security")

        # Set up the logger if it hasn't been configured yet
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _create_log_entry(self, event_type: SecurityEventType, **kwargs) -> SecurityLogEntry:
        return SecurityLogEntry(
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            **kwargs
        )

    def _log_security_event(self, entry: SecurityLogEntry):
        """Log the security event in JSON format for structured logging."""
        log_message = f"SECURITY_EVENT: {entry.json()}"
        self.logger.info(log_message)

    def log_auth_login_success(self, request: Request, user_id: str):
        """Log successful authentication."""
        entry = self._create_log_entry(
            SecurityEventType.AUTH_LOGIN_SUCCESS,
            user_id=user_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            severity="info"
        )
        self._log_security_event(entry)

    def log_auth_login_failure(self, request: Request, email: str, reason: str = "invalid_credentials"):
        """Log failed authentication attempt."""
        entry = self._create_log_entry(
            SecurityEventType.AUTH_LOGIN_FAILURE,
            user_id=email,  # Use email as identifier for failed logins
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={"reason": reason},
            severity="warning"
        )
        self._log_security_event(entry)

    def log_auth_signup_success(self, request: Request, user_id: str):
        """Log successful user registration."""
        entry = self._create_log_entry(
            SecurityEventType.AUTH_SIGNUP_SUCCESS,
            user_id=user_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            severity="info"
        )
        self._log_security_event(entry)

    def log_auth_signup_failure(self, request: Request, email: str, reason: str):
        """Log failed user registration."""
        entry = self._create_log_entry(
            SecurityEventType.AUTH_SIGNUP_FAILURE,
            user_id=email,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            details={"reason": reason},
            severity="warning"
        )
        self._log_security_event(entry)

    def log_auth_access_denied(self, request: Request, user_id: Optional[str] = None):
        """Log unauthorized access attempt."""
        entry = self._create_log_entry(
            SecurityEventType.AUTH_ACCESS_DENIED,
            user_id=user_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            resource=request.url.path if request.url else None,
            action=request.method if request.method else None,
            severity="warning"
        )
        self._log_security_event(entry)

    def log_data_access_attempt(self, request: Request, user_id: str, resource: str, action: str):
        """Log data access attempt."""
        entry = self._create_log_entry(
            SecurityEventType.DATA_ACCESS_ATTEMPT,
            user_id=user_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            resource=resource,
            action=action,
            severity="info"
        )
        self._log_security_event(entry)

    def log_data_access_success(self, request: Request, user_id: str, resource: str, action: str):
        """Log successful data access."""
        entry = self._create_log_entry(
            SecurityEventType.DATA_ACCESS_SUCCESS,
            user_id=user_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            resource=resource,
            action=action,
            severity="info"
        )
        self._log_security_event(entry)

    def log_data_access_failure(self, request: Request, user_id: str, resource: str, action: str, reason: str):
        """Log failed data access attempt."""
        entry = self._create_log_entry(
            SecurityEventType.DATA_ACCESS_FAILURE,
            user_id=user_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            resource=resource,
            action=action,
            details={"reason": reason},
            severity="warning"
        )
        self._log_security_event(entry)

    def log_rate_limit_exceeded(self, request: Request, identifier: str, limit: str):
        """Log rate limit exceeded event."""
        entry = self._create_log_entry(
            SecurityEventType.RATE_LIMIT_EXCEEDED,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            resource=request.url.path if request.url else None,
            action=request.method if request.method else None,
            details={"identifier": identifier, "limit": limit},
            severity="warning"
        )
        self._log_security_event(entry)

    def log_suspicious_activity(self, request: Request, user_id: Optional[str], activity: str, details: Dict[str, Any]):
        """Log suspicious activity."""
        entry = self._create_log_entry(
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            user_id=user_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            resource=request.url.path if request.url else None,
            action=request.method if request.method else None,
            details=details,
            severity="critical"
        )
        self._log_security_event(entry)


# Global security logger instance
security_logger = SecurityLogger()