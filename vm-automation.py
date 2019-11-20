import hashlib
import logging
import os
import random
import re
import string
import subprocess
import sys
import threading
import time

# =================== Options ===================
# List of VMs and snapshots to use
vms_list = ['w10_1903_x64', 'w10_1903_x86']
snapshots_list = ['live']
# Path to 'vboxmanage' executable
vboxmanage_path = 'vboxmanage'
# 'gui' or 'headless'
vm_gui = 'gui'
# Login and password for guest OS
vm_guest_username = 'user'
vm_guest_password = 'P@ssw0rd'
# Where to put test file
remote_folder = 'C:\\Users\\user\\Desktop\\'
# 'on' to enable; 'off' to disable; anything else to keep original network state
vm_network_state = 'off'
# Guest screen resolution ('Width Height Depth')
vm_guest_resolution = '1024 768 32'
# Script/applications to run before and after main file execution
# Specify full name for applications ('calc.exe', not 'calc')
preexec = ''
# preexec = 'C:\\SysinternalsSuite\\Procmon.exe /AcceptEula /Minimized /Quiet /LoadConfig config'
postexec = ''
# postexec = 'C:\\SysinternalsSuite\\Procmon.exe /Terminate'
# Timeout both for commands and VM
timeout = 60
# Calculate hash of input file
calculate_hash = 1
# Show search links to VirusTotal and Google. This will enable 'calculate_hash' too, if not set
show_links = 1
# Logging options
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
# ===============================================

logger = logging.getLogger('vm-automation')

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


# Wrapper for vboxmanage command
def vboxmanage(cmd):
    cmd = f'{vboxmanage_path} {cmd}'.split()
    logging.debug(f'Executing command: {cmd}')
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout, text=True)
        return [result.returncode, result.stdout, result.stderr]
    except FileNotFoundError:
        logging.critical(f'Vboxmanage path is incorrect. Exiting.')
        exit()


# VirtualBox version
def vm_version():
    result = vboxmanage('--version')
    return result[1].rstrip()


# Start virtual machine
def vm_start(vm_name, snapshot_name):
    if vm_gui in ['gui', 'sdl', 'headless', 'separate']:
        vm_start_type = vm_gui
    else:
        vm_start_type = 'gui'
    logging.info(f'{vm_name}({snapshot_name}): Starting VM')
    result = vboxmanage(f'startvm {vm_name} --type {vm_start_type}')
    if result[0] == 0:
        logging.info(f'{vm_name}({snapshot_name}): VM started')
    else:
        logging.error(f'{vm_name}({snapshot_name}): Error while starting VM. Code: {result[0]}')
        logging.debug(f'{vm_name}({snapshot_name}): stderr: {result[2]}')
        exit()


# Stop virtual machine
def vm_stop(vm_name, snapshot_name):
    logging.info(f'{vm_name}({snapshot_name}): Stopping VM')
    result = vboxmanage(f'controlvm {vm_name} poweroff')
    if result[0] == 0:
        logging.debug(f'{vm_name}({snapshot_name}): VM stopped')
        time.sleep(3)
    elif result[0] == 1:
        logging.debug(f'{vm_name}({snapshot_name}): VM not running')
    else:
        logging.error(f'{vm_name}({snapshot_name}): Unknown error: {result[0]}')
        logging.debug(f'{vm_name}({snapshot_name}): stderr: {result[2]}')


# Restore snapshot for virtual machine
def vm_restore(vm_name, snapshot_name):
    logging.info(f'{vm_name}({snapshot_name}): Restoring snapshot')
    result = vboxmanage(f'snapshot {vm_name} restore {snapshot_name}')
    if result[0] == 0:
        logging.debug(f'{vm_name}({snapshot_name}): Snapshot restored')
        time.sleep(3)
    else:
        logging.error(f'{vm_name}({snapshot_name}): Error while restoring snapshot. Code: {result[0]}')
        logging.debug(f'{vm_name}({snapshot_name}): stderr: {result[2]}')


# Change network link state
def vm_network(vm_name, snapshot_name, link_state):
    if link_state not in ['on', 'off']:
        logging.error(f'{vm_name}({snapshot_name}): link_state should be "on" or "off"')
        exit()
    logging.info(f'{vm_name}({snapshot_name}): Setting network parameters to {link_state}')
    result = vboxmanage(f'controlvm {vm_name} setlinkstate1 off')
    if result[0] == 0:
        logging.debug(f'{vm_name}({snapshot_name}): NIC state changed')
    else:
        logging.error(f'{vm_name}({snapshot_name}): Unable to change NIC state. Code: {result[0]}')
        logging.debug(f'{vm_name}({snapshot_name}): stderr: {result[2]}')


# Control screen resolution
def vm_setres(vm_name, snapshot_name, screen_resolution):
    logging.info(f'{vm_name}({snapshot_name}): Changing screen resolution for VM')
    result = vboxmanage(f'controlvm {vm_name} setvideomodehint {screen_resolution}')
    if result[0] == 0:
        logging.debug(f'{vm_name}({snapshot_name}): Screen resolution changed')
    else:
        logging.error(f'{vm_name}({snapshot_name}): Unable to change screen resolution. Code: {result[0]}')
        logging.debug(f'{vm_name}({snapshot_name}): stderr: {result[2]}')


# Execute file/command on VM
def vm_exec(vm_name, snapshot_name, vm_guest_username, vm_guest_password, remote_file):
    logging.info(f'{vm_name}({snapshot_name}): Executing file {remote_file}')
    _ = 0
    while _ < timeout:
        result = vboxmanage(
            f'guestcontrol {vm_name} --username {vm_guest_username} --password {vm_guest_password} start {remote_file}')
        if result[0] == 0:
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
        result = vboxmanage(
            f'guestcontrol {vm_name} --username {vm_guest_username} --password {vm_guest_password} copyto {local_file} {remote_file}')
        if result[0] == 0:
            logging.debug(f'{vm_name}({snapshot_name}): File uploaded')
            break
        else:
            logging.error(f'{vm_name}({snapshot_name}): Error while uploading file. Code: {result[0]}')
            logging.debug(f'{vm_name}({snapshot_name}): stderr: {result[2]}')
    time.sleep(1)
    _ += 1
    if _ >= timeout:
        logging.error(f'{vm_name}({snapshot_name}): Timeout while waiting for VM')
        exit()


# Copy file from VM
def vm_copyfrom(vm_name, snapshot_name, vm_guest_username, vm_guest_password, local_file, remote_file):
    logging.info(f'{vm_name}({snapshot_name}): Downloading file {remote_file} from VM as {local_file}')
    result = vboxmanage(
        f'guestcontrol {vm_name} --username {vm_guest_username} --password {vm_guest_password} copyfrom {remote_file} {local_file}')
    if result[0] == 0:
        logging.debug(f'{vm_name}({snapshot_name}): File downloaded')
    else:
        logging.error(f'{vm_name}({snapshot_name}): Error while downloading file. Code: {result[0]}')
        logging.debug(f'{vm_name}({snapshot_name}): stderr: {result[2]}')


# Take screenshot
def vm_screenshot(vm_name, snapshot_name, image_id=1):
    screenshot_name = f'{vm_name}_{snapshot_name}_{image_id}.png'
    logging.info(f'{vm_name}({snapshot_name}): Taking screenshot {screenshot_name}')
    result = vboxmanage(f'controlvm {vm_name} screenshotpng {screenshot_name}')
    if result[0] == 0:
        logging.debug(f'{vm_name}({snapshot_name}): Screenshot created')
    else:
        logging.error(f'{vm_name}({snapshot_name}): Unable to take screenshot')
        logging.debug(f'{vm_name}({snapshot_name}): stderr: {result[2]}')
    image_id += 1
    return image_id


# Main routines
def main_routine(vm_name, snapshots_list):
    for snapshot_name in snapshots_list:
        logging.info(f'{vm_name}({snapshot_name}): Task started')

        # Stop VM, if already running, restore snapshot and start VM
        vm_stop(vm_name, snapshot_name)
        vm_restore(vm_name, snapshot_name)
        vm_start(vm_name, snapshot_name)
        time.sleep(3)  # Just to make sure VM is alive

        # Set guest resolution
        if vm_guest_resolution:
            vm_setres(vm_name, snapshot_name, vm_guest_resolution)
        else:
            logging.debug(f'{vm_name}({snapshot_name}): vm_guest_resolution not set')

        # Set guest network state
        if vm_network_state == 'on':
            logging.debug(f'{vm_name}({snapshot_name}): Enabling network for guest')
            result = vm_network(vm_name, snapshot_name, 'on')
        elif vm_network_state == 'off':
            logging.debug(f'{vm_name}({snapshot_name}): Disabling network for guest')
            result = vm_network(vm_name, snapshot_name, 'off')
        else:
            logging.debug(f'{vm_name}({snapshot_name}): Keeping original network state')

        # Generate random file name
        if local_file_extension:
            logging.debug(f'{vm_name}({snapshot_name}): Extension obtained from original file')
            file_extension = local_file_extension
        else:
            logging.debug(f'{vm_name}({snapshot_name}): Unable to obtain file extension. Assuming *.exe')
            file_extension = '.exe'
        random_name = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(4, 20)))
        remote_file = remote_folder + random_name + ''.join(file_extension)

        # Run preexec script
        if preexec:
            vm_exec(vm_name, snapshot_name, vm_guest_username, vm_guest_password, preexec)
        else:
            logging.debug(f'{vm_name}({snapshot_name}): preexec not set')

        # Upload file to VM; take screenshot; start file; take screenshot; sleep 5 seconds; take screenshot;
        # wait for {timeout - 10} seconds, take screenshot
        vm_copyto(vm_name, snapshot_name, vm_guest_username, vm_guest_password, local_file, remote_file)
        screenshot = vm_screenshot(vm_name, snapshot_name)
        vm_exec(vm_name, snapshot_name, vm_guest_username, vm_guest_password, remote_file)
        screenshot = vm_screenshot(vm_name, snapshot_name)
        time.sleep(5)
        screenshot = vm_screenshot(vm_name, snapshot_name, screenshot)
        time.sleep(5)
        screenshot = vm_screenshot(vm_name, snapshot_name, screenshot)
        time.sleep(timeout - 10)
        screenshot = vm_screenshot(vm_name, snapshot_name, screenshot)

        # Run postexec script
        if postexec:
            vm_exec(vm_name, snapshot_name, vm_guest_username, vm_guest_password, postexec)
        else:
            logging.debug(f'{vm_name}({snapshot_name}): postexec not set')

        # Stop VM, restore snapshot
        vm_stop(vm_name, snapshot_name)
        vm_restore(vm_name, snapshot_name)
        logging.info(f'{vm_name}({snapshot_name}): Task finished')


# Show general info
logging.info(f'VirtualBox version: {vm_version()}; Script version: 0.3.1\n')
logging.info(f'VMs: {vms_list}')
logging.info(f'Snapshots: {snapshots_list}\n')
logging.info(f'File: "{local_file}"')
if calculate_hash or show_links:
    file_hash = hashlib.sha256()
    block_size = 65536
    with open(local_file, 'rb') as f:
        fb = f.read(block_size)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(block_size)
    sha256sum = file_hash.hexdigest()
    logging.info(f'sha256: {sha256sum}')
    if show_links:
        logging.info(f'Search VT: https://www.virustotal.com/gui/file/{sha256sum}/detection')
        logging.info(f'Search Google: https://www.google.com/search?q={sha256sum}\n')
time.sleep(1)

# Start threads
for vm_name in vms_list:
    t = threading.Thread(target=main_routine, args=(vm_name, snapshots_list))
    t.start()
    time.sleep(3)  # Delay before starting next VM
