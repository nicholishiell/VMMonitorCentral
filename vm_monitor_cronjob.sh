#!/bin/bash
source /home/sysadmin/VMMonitorCentral/.venv/bin/activate
python /home/sysadmin/VMMonitorCentral/vm_monitor_central.py --gather_all
python /home/sysadmin/VMMonitorCentral/vm_monitor_central.py --purge_all 30