from pprint import pprint
import asyncio
import logging
import aiohttp
import requests
import ipaddress
import argparse

from rcsdb.connection import session as rcsdb_session
from rcsdb.models import VM, VMLoad, GPULoad

from vm_monitor_central_utils import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vm_monitor_central.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def check_vm_status(session, ip):
    try:
        # Validate IP address format
        ipaddress.ip_address(ip)
        async with session.get(f'http://{ip}:8000/check_up', timeout=5) as response:
            data = await response.json()
            return ip, data
    except Exception as e:
        return ip, f'Error: {e}'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def check_all_vms() -> list[tuple[str, dict]]:

    vm_ips = [vm.ip for vm in rcsdb_session.query(VM).all()]

    async with aiohttp.ClientSession() as session:
        tasks = [check_vm_status(session, ip) for ip in vm_ips]
        results = await asyncio.gather(*tasks)
        return results

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def get_vm_usage_data(session,
                            payload: dict) -> tuple[str, dict]:

    try:
        # Validate IP address format
        ipaddress.ip_address(payload[IP_ADDR])
        request_str = f'http://{payload[IP_ADDR]}:8000/get_usage_data?start={payload[START_DATE]}&end={payload[END_DATE]}'

        logger.info(f'Request URL: {request_str}')

        async with session.get(request_str, timeout=5) as response:
            data = await response.json()
            return payload[VM_ID], data

    except Exception as e:
        return payload[VM_ID], f'Error: {e}'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def get_all_vm_usage_data() -> list[tuple[str, dict]]:

    usage_payloads = [get_usage_payload(vm) for vm in rcsdb_session.query(VM).all()]

    async with aiohttp.ClientSession() as session:

        tasks = [get_vm_usage_data(session, payload) for payload in usage_payloads]
        results = await asyncio.gather(*tasks)

        return results

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_one_vm_usage_data(ip: str) -> tuple[str, dict]:
    pass
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def purge_old_data():
    # Placeholder for purge logic
    pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main(args):

    if args.gather_all:
        results = asyncio.run(get_all_vm_usage_data())
        add_load_data_to_database(results)
    elif args.gather_one:
        result = get_one_vm_usage_data(args.gather_one)
        pprint(result)
    elif args.purge_all:
        asyncio.run(purge_old_data())
    else:
        # Default behavior
        results = asyncio.run(check_all_vms())
        results.sort(key=lambda x: x[0])
        pprint(results)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='VM Monitor Central')
    parser.add_argument('--gather_one', type=str, metavar='IP', help='Gather usage data from a specific VM by IP address')
    parser.add_argument('--gather_all', action='store_true', help='Gather usage data from all VMs')
    parser.add_argument('--purge_one', type=str, metavar='IP', help='Purge old data for a specific VM by IP address')
    parser.add_argument('--purge_all', action='store_true', help='Purge old data')
    parser.add_argument('--checkup_one', type=str, metavar='IP', help='Check status of a specific VM by IP address')
    parser.add_argument('--checkup_all', action='store_true', help='Check status of all VMs')

    main(parser.parse_args())
