"""Utility functions to handle HTTP requests with retry logic."""

import time
import requests

MAX_RETRIES = 3


def retry_request(function):
    """
    Decorator function that retries a given function on transient failures.

    Retries on RequestException except for 401 and 404 errors, which are treated
    as permanent failures. Implements exponential backoff between retries.

    Args:
        function: The function to be retried.

    Returns:
        The result of the function if successful.

    Raises:
        TimeoutError: If the maximum number of retries is reached without success.
        RequestException: If a 401 or 404 error occurs (permanent failures).
    """
    def wrapper(*args, **kwargs):
        # Retry loop - attempts up to MAX_RETRIES times
        for attempt in range(MAX_RETRIES):
            try:
                result = function(*args, **kwargs)
                return result
            except requests.exceptions.RequestException as e:
                error_message = str(e.args[0]) if e.args else str(e)
                
                # Permanent errors - do not retry
                if error_message.startswith("401 Client Error"):
                    print("401 Client Error: Unauthorized. Please check your credentials.")
                    raise e
                if error_message.startswith("404 Client Error"):
                    raise e
                
                # Last attempt failed - give up
                if attempt == MAX_RETRIES - 1:
                    print(f"Reached max number of retries ({MAX_RETRIES}). Aborting...")
                    raise e
                
                # Exponential backoff: 2^0=1s, 2^1=2s, 2^2=4s
                wait_time = 2 ** attempt
                time.sleep(wait_time)
        
        raise TimeoutError("Max request retries reached")

    return wrapper