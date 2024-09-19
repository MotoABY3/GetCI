# GetCI
A Python script that retrieves system information such as OS version, hostname, CPU, memory, disk, and network details from multiple hosts, and saves it in a configuration-manageable JSON format.

# Server Information Retrieval Script

This project provides a Python script that retrieves system information from multiple Linux servers, including OS version, hostname, CPU information, memory size, disk details, network interfaces, and installed software. The script connects to the servers via SSH, gathers the data, and outputs it in a structured JSON format suitable for configuration management or audit purposes.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)
- [Configuration](#configuration)
- [Output Format](#output-format)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features

- Retrieve system information from multiple hosts, including:
  - OS version (Linux distribution and version)
  - Hostname
  - CPU information (vendor, model, and core count)
  - Memory size
  - Disk usage per partition
  - Network interface details, including IP addresses and MAC addresses
  - Installed software (on RPM-based systems)
- Output the collected information in JSON format for easy integration with configuration management tools (e.g., Ansible, Puppet) or audits.
- Supports retry mechanisms for SSH connections in case of temporary network issues.
- Compatible with Python 2.7.

## Requirements

- **SSH access** to the target servers with appropriate credentials (usernames and passwords).
- The following Python libraries are required:
  - `pexpect`: for handling SSH connections and command execution.

You can install the required Python library using `pip`:

```bash
pip install pexpect
```

## Installation
1. Clone this repository to your local machine:
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```
2. Install the required Python package (pexpect):
```bash
pip install pexpect
```


## Usage
To use the script, you need to modify the Python file to include your server details (IP addresses, usernames, and passwords). You can either edit the file directly or pass these values programmatically in your code.

Running the Script
```bash
python your_script.py
```
This will execute the script and retrieve system information from the specified servers, storing the results in a JSON file. Each execution will generate a new JSON file with a name like system_info_YYYYMMDD.json, where YYYYMMDD corresponds to the current date.

### Command-line Execution Example
Here’s how to run the script after defining your servers:
```python
servers = ["192.168.1.10", "192.168.1.11", "192.168.1.12"]
check_multiple_systems(servers, "your_user", "your_password", ".")
```
This will connect to the provided servers via SSH, collect the necessary system information, and save it in a JSON file.

## Configuration
### Modifying the Script for Customization
You can customize the script to meet specific needs, such as:

- Changing the output format: The script currently saves data in JSON format. If you need a different format (e.g., CSV, XML), you can modify the output section of the script.
- Adjusting the retry mechanism: The script includes a retry mechanism to handle SSH connection issues. You can modify the number of retries or the delay between retries in the get_system_info() function.
- Adding or removing information: If you want to collect additional information (e.g., running processes, open ports), you can add more commands to the script.
### Adding More Servers
To add more servers to the script, simply extend the servers list with the additional IP addresses:
```python
servers = ["192.168.1.10", "192.168.1.11", "192.168.1.12", "192.168.1.13"]
```
### Credentials
Make sure the SSH credentials you are using have sufficient privileges to run system-level commands on the target servers.

## Output Format
The output is saved as a JSON file. Here is an example of the structure:

```json
{
  "192.168.1.10": {
    "Server": {
      "linux_version": "Ubuntu 20.04.1 LTS",
      "hostname": "example-host",
      "memory_size": "7.8G",
      "disk_info": [
        {
          "filesystem": "/dev/sda1",
          "size": "50G",
          "used": "25G",
          "available": "23G",
          "used_percentage": "50%",
          "mount_point": "/"
        }
      ],
      "network_info": [
        {
          "interface": "eth0",
          "ip_address": "192.168.1.10",
          "mac_address": "00:0c:29:16:f9:b9",
          "opposing_mac": "00:0c:29:43:ad:ac"
        }
      ],
      "uuid": "52A936E5-F3ED-11DF-ADC1-AAABBCCDDEE0",
      "cpu_size": "4",
      "installed_software": [
        "bash-4.3.30-2.fc20.x86_64",
        "openssl-1.0.1e-42.el7.x86_64"
      ]
    },
    "Hardware": {
      "hardware_manufacturer": "Dell Inc.",
      "hardware_model": "PowerEdge R640",
      "disk_controller": "SATA controller: Intel Corporation C610/X99 series",
      "raid_info": "RAID 1",
      "cpu_vendor": "Intel",
      "cpu_model": "Intel(R) Xeon(R) CPU E5-2620 v4 @ 2.10GHz"
    }
  }
}
```
## Troubleshooting
### Common Issues and Fixes
SSH Connection Fails:
Ensure the credentials (username and password) are correct.
Verify that the server is accessible from your network.
Check if the target server allows SSH connections on the default port (22) or modify the script to use a custom port.
Permission Denied Errors:
Ensure the user has sufficient privileges to execute system commands on the server.
Incomplete Information:
Some commands might not return data if the necessary packages or permissions are missing on the target server. Ensure the required system utilities (e.g., dmidecode, lscpu) are installed.


