import sys
import logging


def error_message_detail(error: Exception, error_detail: sys) -> str:
    """
    Extracts detailed error information, including file name, line number, and error message.

    :param error: The exception that occurred.
    :param error_detail: The sys module to access traceback details.
    :return: A formatted error message string.
    """
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno

    error_message = f"Error occurred in {file_name} at line {line_number}: {str(error)}"
    logging.error(error_message)  # Log the error for better tracking
    return error_message


class MyException(Exception):
    """
    Custom exception class for handling errors related to the US visa application.
    """
    def __init__(self, error_message: str, error_detail: sys):
        """
        Initializes the custom exception with a detailed error message.
        
        :param error_message: A description of the error.
        :param error_detail: The sys module to access traceback details.
        """
        super().__init__(error_message)  # Call the base class constructor
        self.error_message = error_message_detail(error_message, error_detail)

    def __str__(self) -> str:
        """
        Returns the string representation of the error message.
        """
        return self.error_message
