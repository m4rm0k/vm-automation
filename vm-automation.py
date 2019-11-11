import logging
import os
import random
import re
import subprocess
import sys
import time

# Options
vms_list = ['w10_1903_x64', 'w10_1903_x86']
snapshots_list = ['live']
# threads = len(vms_list)  # Can be set to static (e.g 'threads = 2'). Not used yet.
vm_gui = 1  # 1 (gui) or 0 (headless)
vboxmanage_path = ['vboxmanage']
vm_guest_username = 'user'
vm_guest_password = 'P@ssw0rd'
remote_folder = 'C:\\Users\\user\\Desktop\\'
vm_delay = 30
vm_start_timeout = 20
vboxmanage_timeout = 60

# Logging options
logger = logging.getLogger('vm-automation')
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)


# Check for command line args and file
args = ''.join(sys.argv[1:])
if args in ['-h', '--help', '/?'] or not args:
    logger.info('Usage: {} path_to_file'.format(sys.argv[0]))
    exit()
elif os.path.isfile(args):
    logger.info('Using file {}'.format(args))
    local_file = args
    local_file_extension = re.findall('\\.\\w+$', local_file)
else:
    logger.error('File "{}" does not exist. Exiting.'.format(args))
    exit()


# Wrapper for vboxmanage command
def vboxmanage(args):
    try:
        cmd = subprocess.run(vboxmanage_path + args, capture_output=True, timeout=vboxmanage_timeout, text=True)
        return cmd.returncode, cmd.stdout, cmd.stderr
    except FileNotFoundError:
        logging.error('Unable to start vboxmanage. Exiting.')
        exit()


# VirtualBox version
def vm_version():
    version = vboxmanage(['--version'])
    if version[0] == 0:
        logging.info('VirtualBox version: {}'.format(version[1]))
    else:
        logging.error('Unknown derp. Code: {}. Exiting.'.format(version[0]))
        exit()


# Start virtual machine
def vm_start(vm_name):
    if vm_gui == 1:
        vm_start_type = 'gui'
    elif vm_gui == 0:
        vm_start_type = 'headless'
    else:
        vm_start_type = 'gui'
        logging.error('hide_window option should be 1 (headless) or 0 (gui). Using 0 (gui).')
    logging.info('Starting VM {}'.format(vm_name))
    a, b, c = vboxmanage(['startvm', vm_name, '--type', vm_start_type])
    if a == 0:
        logging.info('VM started')
    elif a == 1:
        logging.error('VM already running')
        exit()
    else:
        logging.error('Unknown error: ' + str(a))
        exit()


# Stop virtual machine
def vm_stop(vm_name):
    logging.info('Stopping VM {}'.format(vm_name))
    a, b, c = vboxmanage(['controlvm', vm_name, 'poweroff'])
    if a == 0:
        logging.info('VM stopped')
    elif a == 1:
        logging.info('VM not running')
    else:
        logging.error('Unknown error: ' + str(a))


# Restore snapshot for virtual machine
def vm_restore(vm_name, snapshot_name):
    logging.info('Restoring VM {} to snapshot {}'.format(vm_name, snapshot_name))
    a, b, c = vboxmanage(['snapshot', vm_name, 'restore', snapshot_name])
    if a == 0:
        logging.info('Snapshot restored')
    elif a == 1:
        logging.error('Snapshot does not exist')
    else:
        logging.error('Unknown error: ' + str(a))


# Execute file on VM
def vm_start_on_vm(vm_name, vm_login, vm_guest_password, remote_file):
    logging.info('Executing file {} on VM {}'.format(remote_file, vm_name))
    _ = 0
    while _ < vm_start_timeout:
        a, b, c = vboxmanage(
            ['guestcontrol', vm_name, '--username', vm_guest_username, '--password', vm_guest_password, 'start',
             remote_file])
        if a == 0:
            logging.info('File executed successfully')
            break
        else:
            # File not executed. Waiting for VM to start.
            time.sleep(1)
            _ += 1
        if _ == vm_start_timeout:
            logging.error('Timeout while waiting for VM {}'.format(vm_name))
            vm_stop(vm_name)
            break


# Copy file from VM
def vm_copyfrom(vm_name, vm_login, vm_guest_password, local_file, remote_file):
    logging.info('Downloading file {} from VM {} as {}'.format(remote_file, vm_name, local_file))
    a, b, c = vboxmanage(
        ['guestcontrol', vm_name, '--username', vm_guest_username, '--password', vm_guest_password, 'copyfrom',
         remote_file,
         local_file])
    if a == 0:
        logging.info('File downloaded')
    else:
        logging.error('Error while downloading file. Code: {}'.format(a))


# Copy file to VM
def vm_copyto(vm_name, vm_login, vm_guest_password, local_file, remote_file):
    _ = 0
    while _ < vm_start_timeout:
        logging.info('Uploading file {} as {} to VM {}'.format(local_file, remote_file, vm_name))
        a, b, c = vboxmanage(
            ['guestcontrol', vm_name, '--username', vm_guest_username, '--password', vm_guest_password, 'copyto',
             local_file, remote_file])
        if a == 0:
            logging.info('File uploaded')
            break
        else:
            logging.error('Error while uploading file. Code: {}'.format(a))
        time.sleep(1)
        _ += 1
        if _ == vm_start_timeout:
            logging.error('Timeout while waiting for VM {}'.format(vm_name))
            exit()


# Take screenshot
def vm_screenshot(vm_name, screenshot_name):
    logging.info('Taking screenshot on VM {} as {}'.format(vm_name, screenshot_name))
    vboxmanage(['controlvm', vm_name, 'screenshotpng', screenshot_name])


# Main routines
logging.info('VMs: {}; Snapshots: {}'.format(str(vms_list), str(snapshots_list)))
vm_version()
for vm_name in vms_list:
    for snapshot_name in snapshots_list:
        logging.info('Using VM {} with snapshot {}'.format(vm_name, snapshot_name))
        vm_stop(vm_name)
        vm_restore(vm_name, snapshot_name)
        vm_start(vm_name)
        remote_file = remote_folder + str(random.randrange(1000000000)) + ''.join(local_file_extension)
        vm_copyto(vm_name, vm_guest_username, vm_guest_password, local_file, remote_file)
        vm_screenshot(vm_name, '{}_{}_1.png'.format(vm_name, snapshot_name))
        vm_start_on_vm(vm_name, vm_guest_username, vm_guest_password, remote_file)
        time.sleep(5)
        vm_screenshot(vm_name, '{}_{}_2.png'.format(vm_name, snapshot_name))
        logging.info('Waiting for results. Timeout: {} seconds.'.format(vm_delay))
        time.sleep(vm_delay)
        vm_screenshot(vm_name, '{}_{}_3.png'.format(vm_name, snapshot_name))
        vm_stop(vm_name)
        vm_restore(vm_name, snapshot_name)
        logging.info('Done')
