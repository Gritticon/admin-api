"""
External Update Service Integration
Sends updates to client devices via external update service.
"""
import httpx
from core.config import settings


async def send_device1_update(account_id: int, OID: float, message: dict, notify: bool = False):
    """
    Send update notification to client devices via external update service.
    
    Args:
        account_id: Client account ID
        OID: Operation ID
        message: Update data dictionary
        notify: Whether to send notification (default: False)
        
    Returns:
        Response from the update service
    """
    url = settings.UPDATE_SERVICE_URL
    params = {
        "account_id": account_id,
        "OID": OID,
        "notify": str(notify).lower()
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params, json=message)
        return response.json()

