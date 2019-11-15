import logging
import os
import random
import re
import string
import subprocess
import sys
import threading
import time

# Options
vms_list = ['w10_1903_x64', 'w10_1903_x86']
snapshots_list = ['live']
threads = len(vms_list)  # Ignored
vm_gui = 1  # 1 (gui) or 0 (headless)
vboxmanage_path = 'vboxmanage'
vm_guest_username = 'user'
vm_guest_password = 'P@ssw0rd'
remote_folder = 'C:\\Users\\user\\Desktop\\'
timeout = 60

# Logging options
logger = logging.getLogger('vm-automation')
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)

# Check for command line args and file
args = ''.join(sys.argv[1:])
if args in ['-h', '--help', '/?'] or not args:
    print(f'Usage: {args} path_to_file')
    exit()
elif os.path.isfile(args):
    local_file = args
    local_file_extension = re.findall('\\.\\w+$', local_file)
else:
    print(f'File "{args}" does not exist. Exiting.')
    exit()


# Start virtual machine
def vm_start(vm_name, snapshot_name):
    if vm_gui == 1:
        vm_start_type = 'gui'
    elif vm_gui == 0:
        vm_start_type = 'headless'
    else:
        vm_start_type = 'gui'
    logging.info(f'{vm_name}({snapshot_name}): Starting VM')
    cmd = subprocess.run([vboxmanage_path, 'startvm', vm_name, '--type', vm_start_type], capture_output=True,
                         timeout=timeout, text=True)
    if cmd.returncode == 0:
        logging.info(f'{vm_name}({snapshot_name}): VM started')
    else:
        logging.error(f'{vm_name}({snapshot_name}): Error while starting VM. Code: {cmd.returncode}')
        exit()


# Stop virtual machine
def vm_stop(vm_name, snapshot_name):
    logging.info(f'{vm_name}({snapshot_name}): Stopping VM')
    cmd = subprocess.run([vboxmanage_path, 'controlvm', vm_name, 'poweroff'], capture_output=True, timeout=timeout,
                         text=True)
    if cmd.returncode == 0:
        logging.debug(f'{vm_name}({snapshot_name}): VM stopped')
        time.sleep(3)
    elif cmd.returncode == 1:
        logging.debug(f'{vm_name}({snapshot_name}): VM not running')
    else:
        logging.error(f'{vm_name}({snapshot_name}): Unknown error: {cmd.returncode}')


# Restore snapshot for virtual machine
def vm_restore(vm_name, snapshot_name):
    logging.info(f'{vm_name}({snapshot_name}): Restoring snapshot')
    cmd = subprocess.run([vboxmanage_path, 'snapshot', vm_name, 'restore', snapshot_name], capture_output=True,
                         timeout=timeout, text=True)
    if cmd.returncode == 0:
        logging.debug(f'{vm_name}({snapshot_name}): Snapshot restored')
        time.sleep(3)
    else:
        logging.error(f'{vm_name}({snapshot_name}): Error while restoring snapshot. Code: {cmd.returncode}')


# Execute file on VM
def vm_start_on_vm(vm_name, snapshot_name, vm_guest_username, vm_guest_password, remote_file):
    logging.info(f'{vm_name}({snapshot_name}): Executing file {remote_file}')
    _ = 0
    while _ < timeout:
        cmd = subprocess.run([vboxmanage_path,
                              'guestcontrol', vm_name, '--username', vm_guest_username, '--password',
                              vm_guest_password, 'start',
                              remote_file], capture_output=True, timeout=timeout, text=True)
        if cmd.returncode == 0:
            logging.debug(f'{vm_name}({snapshot_name}): File executed successfully')
            break
        else:
            # Waiting for VM to start
            time.sleep(1)
            _ += 1
    if _ >= timeout:
        logging.error(f'{vm_name}({snapshot_name}): Timeout while executing file on VM')
        exit()


# Copy file to VM
def vm_copyto(vm_name, snapshot_name, vm_guest_username, vm_guest_password, local_file, remote_file):
    _ = 0
    while _ < timeout:
        logging.info(f'{vm_name}({snapshot_name}): Uploading file {local_file} as {remote_file} to VM')
        cmd = subprocess.run([vboxmanage_path,
                              'guestcontrol', vm_name, '--username', vm_guest_username, '--password',
                              vm_guest_password, 'copyto',
                              local_file, remote_file], capture_output=True, timeout=timeout, text=True)
        if cmd.returncode == 0:
            logging.debug(f'{vm_name}({snapshot_name}): File uploaded')
            break
        else:
            logging.error(f'{vm_name}({snapshot_name}): Error while uploading file. Code: {cmd.returncode}')
    time.sleep(1)
    _ += 1
    if _ >= timeout:
        logging.error(f'{vm_name}({snapshot_name}): Timeout while waiting for VM')
        exit()


# Copy file from VM
def vm_copyfrom(vm_name, snapshot_name, vm_guest_username, vm_guest_password, local_file, remote_file):
    logging.info(f'{vm_name}({snapshot_name}): Downloading file {remote_file} from VM as {local_file}')
    cmd = subprocess.run([vboxmanage_path,
                          'guestcontrol', vm_name, '--username', vm_guest_username, '--password',
                          vm_guest_password, 'copyfrom',
                          remote_file, local_file], capture_output=True, timeout=timeout, text=True)
    if cmd.returncode == 0:
        logging.debug(f'{vm_name}({snapshot_name}): File downloaded')
    else:
        logging.error(f'{vm_name}({snapshot_name}): Error while downloading file. Code: {cmd.returncode}')


# Take screenshot
def vm_screenshot(vm_name, snapshot_name, image_id=1):
    screenshot_name = f'{vm_name}_{snapshot_name}_{image_id}.png'
    logging.info(f'{vm_name}({snapshot_name}): Taking screenshot {screenshot_name}')
    subprocess.run([vboxmanage_path, 'controlvm', vm_name, 'screenshotpng', screenshot_name], capture_output=True,
                   timeout=timeout, text=True)
    image_id += 1
    return image_id


# Main routines
def main_routine(vm_name, snapshots_list):
    for snapshot_name in snapshots_list:
        logging.info(f'{vm_name}({snapshot_name}): Task started')
        vm_stop(vm_name, snapshot_name)
        vm_restore(vm_name, snapshot_name)

        vm_start(vm_name, snapshot_name)

        if 'local_file_extension' not in locals():
            # Assuming '.exe' if no extension extracted from name
            local_file_extension = '.exe'
        random_name = ''.join(random.choice(string.ascii_letters) for x in range(random.randint(4, 20)))
        remote_file = remote_folder + random_name + ''.join(local_file_extension)
        vm_copyto(vm_name, snapshot_name, vm_guest_username, vm_guest_password, local_file, remote_file)
        screenshot = vm_screenshot(vm_name, snapshot_name)
        vm_start_on_vm(vm_name, snapshot_name, vm_guest_username, vm_guest_password, remote_file)
        time.sleep(5)
        screenshot = vm_screenshot(vm_name, snapshot_name, screenshot)
        time.sleep(timeout)
        screenshot = vm_screenshot(vm_name, snapshot_name, screenshot)

        vm_stop(vm_name, snapshot_name)
        vm_restore(vm_name, snapshot_name)
        logging.info(f'{vm_name}({snapshot_name}): Task finished')


max_threads = 2
# Show general info
logging.info(f'Using VMs: {vms_list} with snapshots: {snapshots_list}')
logging.info(f'Max threads: {threads}')
logging.info(f'Using file: "{local_file}"\n')
time.sleep(1)

# Start threads
for vm_name in vms_list:
    t = threading.Thread(target=main_routine, args=(vm_name, snapshots_list))
    t.start()
    time.sleep(3)
