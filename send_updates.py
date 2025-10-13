import httpx

async def send_device1_update(account_id: int, OID: float, message: dict, notify: bool = False):
    url = "https://updates.gritticon.com/api/update/send_update"
    params = {
        "account_id": account_id,
        "OID": OID,
        "notify": str(notify).lower()
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params, json=message)
        return response.json()

