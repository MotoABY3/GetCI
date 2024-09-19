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
