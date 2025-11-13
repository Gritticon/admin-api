import httpx
from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


async def send_device1_update(account_id: int, OID: float, message: dict, notify: bool = False):
    """
    Send real-time update to WebSocket server for Flutter clients.
    
    Args:
        account_id: Business account ID
        OID: Operation ID
        message: Update message payload
        notify: Whether to send notification
        
    Returns:
        dict: Response from WebSocket server
    """
    url = settings.WEBSOCKET_UPDATE_URL
    params = {
        "account_id": account_id,
        "OID": OID,
        "notify": str(notify).lower()
    }

    headers = {
        "Authorization": f"Bearer {settings.WEBSOCKET_UPDATE_TOKEN}"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params, json=message, headers=headers)
            response.raise_for_status()
            logger.info(f"Update sent successfully for account {account_id}, OID {OID}")
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Failed to send update: {str(e)}", exc_info=True)
        raise
