# vm-automation
Python script that can be used to test software/scripts/etc. on VMs (currently only VirtualBox is supported).

Both Windows and Linux are supported as host OS.

# Configuration:
* vms_list - list of VMs to use. Example: ['w10_x64', 'w10_x86', 'w81_x64', 'w81_x86', 'w7_x64', 'w7_x86']
* snapshots_list - list of snapshots to use. Example: ['java8', 'java11', 'office2013', 'office2016', 'office2019']

Note. If snapshot does not exist on specific VM it will be skipped.

* vm_gui - start VM with (1) or without (0) GUI
* vboxmanage_path - path to 'vboxmanage' executable. On Windows you can leave it as-is and add VirtualBox'es folder in $PATH. Example: ['vboxmanage']
* vm_guest_username - login for guest OS. Example: 'user'
* vm_guest_password - password for guest OS. Example: 'P@ssw0rd'
* remote_folder - directory, where executable is uploaded (on guest host). Example: 'C:\\\\Users\\\\user\\\\Desktop\\\\'
* vm_delay - Execution timeout in seconds. Example: 30
* vm_start_timeout - VM start timeout in seconds. Example: 20
* vboxmanage_timeout - global timeout for all vboxmanage commands. Example: 60

# Usage:
vm-automation.py binary.exe

# TODO:
* Run multiple VMs in parallel
* Optionally disable network for guest
* Optional commands to run before/after analysis

# Example video:
* Version 0.1 on Windows host:

<a href="http://www.youtube.com/watch?feature=player_embedded&v=IMrZaJPqVlA" target="_blank"><img src="http://img.youtube.com/vi/IMrZaJPqVlA/0.jpg" width="240" height="180" border="10" /></a>

# Example output:
```
PS C:\tmp> python .\vm-automation.py .\putty.exe
2019-11-11 17:48:37,942 [INFO] Using file .\putty.exe
2019-11-11 17:48:37,943 [INFO] VMs: ['w10_1903_x64', 'w10_1903_x86']; Snapshots: ['live']
2019-11-11 17:48:37,985 [INFO] VirtualBox version: 6.0.14r133895

2019-11-11 17:48:37,985 [INFO] Using VM w10_1903_x64 with snapshot live
2019-11-11 17:48:37,986 [INFO] Stopping VM w10_1903_x64
2019-11-11 17:48:38,036 [INFO] VM not running
2019-11-11 17:48:38,036 [INFO] Restoring VM w10_1903_x64 to snapshot live
2019-11-11 17:48:38,121 [INFO] Snapshot restored
2019-11-11 17:48:38,121 [INFO] Starting VM w10_1903_x64
2019-11-11 17:48:50,439 [INFO] VM started
2019-11-11 17:48:50,439 [INFO] Uploading file .\putty.exe as C:\Users\user\Desktop\635887651.exe to VM w10_1903_x64
2019-11-11 17:48:52,500 [INFO] File uploaded
2019-11-11 17:48:52,501 [INFO] Taking screenshot on VM w10_1903_x64 as w10_1903_x64_live_1.png
2019-11-11 17:48:52,620 [INFO] Executing file C:\Users\user\Desktop\635887651.exe on VM w10_1903_x64
2019-11-11 17:48:57,321 [INFO] File executed successfully
2019-11-11 17:49:02,322 [INFO] Taking screenshot on VM w10_1903_x64 as w10_1903_x64_live_2.png
2019-11-11 17:49:02,409 [INFO] Waiting for results. Timeout: 30 seconds.
2019-11-11 17:49:32,410 [INFO] Taking screenshot on VM w10_1903_x64 as w10_1903_x64_live_3.png
2019-11-11 17:49:32,504 [INFO] Stopping VM w10_1903_x64
2019-11-11 17:49:33,200 [INFO] VM stopped
2019-11-11 17:49:33,200 [INFO] Restoring VM w10_1903_x64 to snapshot live
2019-11-11 17:49:33,280 [INFO] Snapshot restored
2019-11-11 17:49:33,281 [INFO] Done
2019-11-11 17:49:33,282 [INFO] Using VM w10_1903_x86 with snapshot live
2019-11-11 17:49:33,282 [INFO] Stopping VM w10_1903_x86
2019-11-11 17:49:33,360 [INFO] VM not running
2019-11-11 17:49:33,360 [INFO] Restoring VM w10_1903_x86 to snapshot live
2019-11-11 17:49:33,456 [INFO] Snapshot restored
2019-11-11 17:49:33,456 [INFO] Starting VM w10_1903_x86
2019-11-11 17:49:45,791 [INFO] VM started
2019-11-11 17:49:45,791 [INFO] Uploading file .\putty.exe as C:\Users\user\Desktop\670555300.exe to VM w10_1903_x86
2019-11-11 17:49:47,292 [INFO] File uploaded
2019-11-11 17:49:47,292 [INFO] Taking screenshot on VM w10_1903_x86 as w10_1903_x86_live_1.png
2019-11-11 17:49:47,435 [INFO] Executing file C:\Users\user\Desktop\670555300.exe on VM w10_1903_x86
2019-11-11 17:49:51,855 [INFO] File executed successfully
2019-11-11 17:49:56,856 [INFO] Taking screenshot on VM w10_1903_x86 as w10_1903_x86_live_2.png
2019-11-11 17:49:56,946 [INFO] Waiting for results. Timeout: 30 seconds.
2019-11-11 17:50:26,946 [INFO] Taking screenshot on VM w10_1903_x86 as w10_1903_x86_live_3.png
2019-11-11 17:50:27,058 [INFO] Stopping VM w10_1903_x86
2019-11-11 17:50:27,705 [INFO] VM stopped
2019-11-11 17:50:27,706 [INFO] Restoring VM w10_1903_x86 to snapshot live
2019-11-11 17:50:27,796 [INFO] Snapshot restored
2019-11-11 17:50:27,796 [INFO] Done
PS C:\tmp>
```

