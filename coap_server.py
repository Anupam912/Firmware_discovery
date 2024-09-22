# coap_server.py (Device-Side CoAP Server)

import aiocoap
import aiocoap.resource as resource
import asyncio

class StatusResource(resource.Resource):
    async def render_get(self, request):
        # Simulate some device status (e.g., uptime, version)
        status = {
            "firmware_version": "1.2.3",
            "uptime": "1500s",
            "status": "online"
        }
        return aiocoap.Message(payload=str(status).encode())

async def main():
    root = resource.Site()
    root.add_resource(['status'], StatusResource())
    await aiocoap.Context.create_server_context(root)
    await asyncio.get_event_loop().create_future()  # Keep the server running

if __name__ == "__main__":
    asyncio.run(main())
