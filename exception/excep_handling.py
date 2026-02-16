"""Custom exception classes for AI Trip Planner."""

import sys
import traceback


class TripPlannerException(Exception):
    """Base exception for the AI Trip Planner application."""

    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self):
        if self.original_error:
            return f"{self.message} | Caused by: {type(self.original_error).__name__}: {self.original_error}"
        return self.message


class ModelLoadError(TripPlannerException):
    """Raised when a model fails to load."""
    pass


class ToolExecutionError(TripPlannerException):
    """Raised when a tool encounters an error during execution."""
    pass


class APIConnectionError(TripPlannerException):
    """Raised when an external API call fails."""
    pass


class ConfigurationError(TripPlannerException):
    """Raised when configuration/environment variables are missing or invalid."""
    pass


def format_error_message(error: Exception) -> str:
    """Format an exception with traceback details for logging."""
    _, _, exc_tb = sys.exc_info()
    if exc_tb:
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno
        return f"Error in [{file_name}] at line {line_number}: {type(error).__name__}: {error}"
    return f"{type(error).__name__}: {error}"
