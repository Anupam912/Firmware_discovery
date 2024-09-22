# coap_discovery.py

import aiocoap
import asyncio

async def discover_coap_devices():
    """Send a multicast CoAP discovery request and gather responses."""
    protocol = await aiocoap.Context.create_client_context()

    request = aiocoap.Message(code=aiocoap.GET, uri='coap://224.0.1.187/.well-known/core')

    try:
        response = await protocol.request(request).response
        print(f"Discovery response: {response.payload.decode('utf-8')}")
        return response.payload.decode('utf-8')
    except Exception as e:
        print(f"Discovery failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(discover_coap_devices())
