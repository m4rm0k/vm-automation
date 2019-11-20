# vm-automation
Python script that can be used to test software/scripts/etc on VMs (currently only VirtualBox is supported).

Both Windows and Linux are supported as host OS.

# Configuration
* vms_list - list of VMs to use. Example: ['w10_x64', 'w10_x86', 'w81_x64', 'w81_x86', 'w7_x64', 'w7_x86']
* snapshots_list - list of snapshots to use. Example: ['java8', 'java11', 'office2013', 'office2016', 'office2019']
* vm_gui - start VM with GUI (vm_gui = 'gui') or without GUI (vm_gui = 'headless')
* vboxmanage_path - path to 'vboxmanage' executable. On Windows you can leave it as-is and add VirtualBox'es folder in $PATH. Example: 'vboxmanage'
* vm_guest_username - login for guest OS. Example: 'user'
* vm_guest_password - password for guest OS. Example: 'P@ssw0rd'
* remote_folder - directory, where executable is uploaded (on guest host). Example: 'C:\\\\Users\\\\user\\\\Desktop\\\\'
* vm_network_state - option to enable (vm_network_state = 'on') or disable (vm_network_state = 'off') network on guest VM
* vm_guest_resolution - change screen resolution on guest. Example: vm_guest_resolution = '1024 768 32'
* preexec - application or script to run before main file. Example: preexec = 'notepad.exe'
* postexec - application or script to run after main file. Example: postexec = 'notepad.exe'
* timeout - global timeout for all vboxmanage commands (seconds). Example: 60
* calculate_hash - calculate sha256 hash of file. Example: calculate_hash = 1
* show_links - show links for VirusTotal and Google search. Example: show_links = 1

# Usage
python vm-automation.py binary.exe

# TODO:
* Control how many threads run simultaneously (currently equals to number of VMs)

# Changelog
Version 0.3.1:
* Optionally calculate sha256 hash of file and show links to VirusTotal and Google searches

Version 0.3:
* Added option to enable/disable network on guest
* Added option to start scripts before/after running main file
* Added option to change display resolution
* Code refactoring

Version 0.2:
* Added multithreading
* Code refactoring

Version 0.1:
* First public release

# Example videos
* Windows host (version 0.2):

<a href="http://www.youtube.com/watch?feature=player_embedded&v=nIj4cW_miuA" target="_blank"><img src="http://img.youtube.com/vi/nIj4cW_miuA/0.jpg" width="320" height="240" border="10" /></a>

