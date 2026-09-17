import json
from typing import Dict, Any
import requests

API_URL = "https://qceservices.quezoncity.gov.ph/index.php/SMS/Send_request/bulk"
DEFAULT_COOKIE = "ci_session=1jqh5c9gvi6pht5gvaffhotcflmduhj4"

def build_payload(message: str, receivers: str) -> Dict[str, str]:
    """
    Constructs the exact JSON payload expected by QCEServices bulk SMS endpoint.
    """
    return {
        "message": message,
        "receivers": receivers
    }

def send_sms_blast(
    message: str,
    receivers: str,
    dry_run: bool = False,
    cookie: str = DEFAULT_COOKIE,
    timeout: int = 60
) -> Dict[str, Any]:
    """
    Sends bulk SMS request to QCEServices endpoint.
    
    :param message: The SMS message text
    :param receivers: Comma-separated list of 11-digit phone numbers
    :param dry_run: If True, skips live HTTP request and returns mock success
    :param cookie: Session cookie header value
    :param timeout: HTTP request timeout in seconds
    :return: Response status dictionary
    """
    payload_dict = build_payload(message, receivers)
    payload_json = json.dumps(payload_dict)
    
    headers = {
        'Content-Type': 'application/json',
        'Cookie': cookie
    }

    if dry_run:
        return {
            "success": True,
            "status_code": 200,
            "response_text": '[DRY-RUN] Request built successfully. Live call bypassed.',
            "payload": payload_json,
            "headers": headers,
            "dry_run": True
        }

    try:
        response = requests.post(API_URL, headers=headers, data=payload_json, timeout=timeout)
        is_success = "Succesful" in response.text or response.status_code == 200
        
        return {
            "success": is_success,
            "status_code": response.status_code,
            "response_text": response.text,
            "payload": payload_json,
            "headers": headers,
            "dry_run": False
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "status_code": 504,
            "response_text": "504 Gateway time-out (Request timed out)",
            "payload": payload_json,
            "headers": headers,
            "dry_run": False
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": 500,
            "response_text": f"Error initiating request: {str(e)}",
            "payload": payload_json,
            "headers": headers,
            "dry_run": False
        }
