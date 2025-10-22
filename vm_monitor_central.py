import openstack
from pprint import pprint
import requests

from rcsdb.connection import session as rcsdb_session
from rcsdb.models import VM
import asyncio
import aiohttp

# # Create connection to OpenStack cloud
# conn = openstack.connect(cloud='RCS')

# # Get list of all servers (VMs)
# servers = conn.compute.servers(all_projects=True)

# # Print server details
# for server in servers:
#     ip_addresses = []
#     for network_name, network_info in server.addresses.items():
#         print(f'Network name: {network_name}')
#         for address_info in network_info:
#             print(f"  IP address: {address_info['addr']}")
#             ip_addresses.append(address_info['addr'])
#     print(f"Server: {server.name}, IPs: {', '.join(ip_addresses)}")
#     print('-' * 40)
#     input()

# ip_address = '134.117.214.70'

# response = requests.get(f'http://{ip_address}:8000/check_up')

# pprint(response.json())


async def check_vm_status(session, ip):
    try:
        async with session.get(f'http://{ip}:8000/check_up', timeout=5) as response:
            data = await response.json()
            return ip, data
    except Exception as e:
        return ip, f'Error: {e}'

async def check_all_vms():
    vm_ips = [vm.ip for vm in rcsdb_session.query(VM).all()]

    async with aiohttp.ClientSession() as session:
        tasks = [check_vm_status(session, ip) for ip in vm_ips]
        results = await asyncio.gather(*tasks)
        return results

# Run the async function
results = asyncio.run(check_all_vms())

results.sort(key=lambda x: x[0])

pprint(results)
