import logging
from datetime import datetime

from rcsdb.connection import session as rcsdb_session
from rcsdb.models import VM, VMLoad, GPULoad

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

IP_ADDR = 'ip_address'
VM_ID = 'vm_id'
START_DATE = 'start_date'
END_DATE = 'end_date'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def latest_vm_load_update(vm_id: int) -> datetime:
    vm_load_rows = rcsdb_session.query(VMLoad).filter(VMLoad.vm_id == vm_id).all()

    latest_date = datetime(2024, 1, 1)

    for row in vm_load_rows:
        if row.timestamp > latest_date:
            latest_date = row.timestamp

    return latest_date.date()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def latest_gpu_load_update(vm_id: int) -> datetime:
    gpu_load_rows = rcsdb_session.query(GPULoad).filter(GPULoad.vm_id == vm_id).all()

    latest_date = datetime(2024, 1, 1)

    for row in gpu_load_rows:
        if row.timestamp > latest_date:
            latest_date = row.timestamp

    return latest_date.date()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def latest_load_update(vm: VM) -> datetime:


    last_vm_date = latest_vm_load_update(vm.id)
    last_gpu_date = latest_gpu_load_update(vm.id)

    if not vm.gpu:
        return last_vm_date
    else:
        return max(last_vm_date, last_gpu_date)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_usage_payload(vm: VM) -> dict:

    start_data = latest_load_update(vm)
    end_date = datetime.now().date()

    return {VM_ID: vm.id,
            IP_ADDR: vm.ip,
            START_DATE: start_data.isoformat(),
            END_DATE: end_date.isoformat()}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def calculate_avg_load(cpu_usage: list[dict]) -> float:

    total_usage = sum(cpu['usage_percent'] for cpu in cpu_usage)
    avg_usage = total_usage / len(cpu_usage)

    return avg_usage

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def add_vm_load_to_database(vm_id: int, load_data: dict):

    for datum in load_data.get('data', []):
        vm_load = VMLoad(   vm_id=vm_id,
                            timestamp=datetime.fromisoformat(datum['timestamp']),
                            load=calculate_avg_load(datum.get('cpus', [])),
                            memfree=datum.get('memory', {}).get('used_mb', 0),
                            diskfree=datum.get('disk', {}).get('used_mb', 0))
        rcsdb_session.add(vm_load)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# gpu_count":1,"gpus":[{"gpu_index":0,"memory_total_mb":46068.0,"memory_used_mb":3.0,"usage_percent":0.0}]
def add_gpu_load_to_database(vm_id: int, load_data: dict):

    for datum in load_data.get('data', []):
        for gpu in datum.get('gpus', []):
            gpu_load = GPULoad(   vm_id=vm_id,
                                  timestamp=datetime.fromisoformat(datum['timestamp']),
                                  core_use=gpu.get('usage_percent', 0.0),
                                  mem_used=int(gpu.get('memory_used_mb', 0)))
            rcsdb_session.add(gpu_load)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def add_load_data_to_database(results : list[tuple[str, dict]]):

    for vm_id, data in results:
        if 'Error' in data:
            continue

        vm = rcsdb_session.query(VM).filter(VM.id == vm_id).first()

        if not vm:
            continue

        add_vm_load_to_database(int(vm_id), data)

        for gpu_entry in data.get('gpu_load', []):
            gpu_load = GPULoad(
                vm_id=vm.id,
                timestamp=datetime.fromisoformat(gpu_entry['timestamp']),
                core_use=gpu_entry.get('core_use'),
                mem_activity=gpu_entry.get('mem_activity'),
                mem_use=gpu_entry.get('mem_use')
            )
            rcsdb_session.add(gpu_load)

    rcsdb_session.commit()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~