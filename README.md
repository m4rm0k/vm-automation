# vm-automation
Python script that can be used to test software/scripts/etc on VMs (currently only VirtualBox is supported).

Both Windows and Linux are supported as host OS.

# Configuration:
* vms_list - list of VMs to use. Example: ['w10_x64', 'w10_x86', 'w81_x64', 'w81_x86', 'w7_x64', 'w7_x86']
* snapshots_list - list of snapshots to use. Example: ['java8', 'java11', 'office2013', 'office2016', 'office2019']

Note. If snapshot does not exist on specific VM it will be skipped.

* vm_gui - start VM with GUI (vm_gui=1) or without GUI (vm_gui=0)
* vboxmanage_path - path to 'vboxmanage' executable. On Windows you can leave it as-is and add VirtualBox'es folder in $PATH. Example: 'vboxmanage'
* vm_guest_username - login for guest OS. Example: 'user'
* vm_guest_password - password for guest OS. Example: 'P@ssw0rd'
* remote_folder - directory, where executable is uploaded (on guest host). Example: 'C:\\\\Users\\\\user\\\\Desktop\\\\'
* timeout - global timeout for all vboxmanage commands (seconds). Example: 60

# Usage:
python vm-automation.py binary.exe

# TODO:
* Control how many threads run simultaneously (currently equals to number of VMs)
* Optionally disable network for guest
* Optional commands to run before/after analysis

# Example video:
* Windows host (version 0.2):

<a href="http://www.youtube.com/watch?feature=player_embedded&v=nIj4cW_miuA" target="_blank"><img src="http://img.youtube.com/vi/nIj4cW_miuA/0.jpg" width="320" height="240" border="10" /></a>

