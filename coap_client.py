# coap_client.py

import aiocoap
import asyncio

async def get_firmware_version_coap(ip):
    """Query the firmware version from a device using CoAP."""
    protocol = await aiocoap.Context.create_client_context()

    request = aiocoap.Message(code=aiocoap.GET, uri=f'coap://{ip}/firmware')

    try:
        response = await protocol.request(request).response
        return response.payload.decode('utf-8')
    except Exception as e:
        print(f"Failed to fetch firmware from {ip} using CoAP: {str(e)}")
        return None
    
async def get_device_status_coap(ip):
    """Query the status of a device using CoAP."""
    protocol = await aiocoap.Context.create_client_context()

    request = aiocoap.Message(code=aiocoap.GET, uri=f'coap://{ip}/status')

    try:
        response = await protocol.request(request).response
        return response.payload.decode('utf-8')
    except Exception as e:
        print(f"Failed to fetch status from {ip} using CoAP: {str(e)}")
        return None
