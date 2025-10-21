import openstack
from pprint import pprint
import requests

from rcsdb.connection import session as rcsdb_session
from rcsdb.models import VM

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

for vm in rcsdb_session.query(VM).all():
    pprint(vm)
    input()

# vm_ips = [vm.ip for vm in rcsdb_session.query(VM).all()]

for ip in vm_ips:
    try:
        response = requests.get(f'http://{ip}:8000/check_up', timeout=5)
        pprint(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to VM at {ip}: {e}")