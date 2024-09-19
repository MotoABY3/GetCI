#!/usr/bin/env python

import json
import os
import difflib
import pexpect
import datetime
import re
import time
from datetime import datetime, timedelta
from collections import OrderedDict

def ci_get(no, ip, user, password, retries=3):
    try_count = 0

    while try_count < retries:
        try:
            print("Attempting SSH connection to {}@{} (Try {}/{})".format(user, ip, try_count + 1, retries))
            connect = pexpect.spawn('/usr/bin/ssh '+user+'@'+ip)
            time.sleep (1)
            # SSH Permission Reauest 
            MESSAGE1 = "Are you sure you want to continue connecting"
            # Password Request
            MESSAGE2 = "assword:"
            r = connect.expect([MESSAGE1, MESSAGE2, pexpect.EOF, pexpect.TIMEOUT],timeout=60)
            if r == 0:
                connect.sendline("yes")
                connect.expect(MESSAGE2)
                connect.sendline(password)
            if r == 1:
                connect.sendline(password)
            connect.expect(r"\[.*\]\$ ",timeout=10)

            connect.sendline("export LANG=en_US")
            connect.expect(r"\[.*\]\$ ",timeout=10)

            # hostname
            connect.sendline("hostnamectl")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            hostnamectl_info = connect.before.strip()
            match = re.search(r'Static hostname:\s+(.+)', hostnamectl_info)
            hostname = match.group(1).strip()

            # Linux version
            match = re.search(r'Operating System:\s+(.+)\r', hostnamectl_info)
            linux_version = match.group(1)

            # Linux kernel
            match = re.search(r'Kernel:\s+(.+)\r', hostnamectl_info)
            linux_kernel = match.group(1)

            # HW type
            match = re.search(r'Chassis:\s+(.+)\r', hostnamectl_info)
            hw_type = match.group(1)

            # HW info
            connect.sendline("sudo dmidecode -s system-manufacturer")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            hardware_manufacturer = connect.before.strip().splitlines()[1]

            connect.sendline("sudo dmidecode -s system-product-name")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            hardware_model = connect.before.strip().splitlines()[1]

            # cpu
            connect.sendline("nproc")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            cpu_count = connect.before.strip().splitlines()[1]

            connect.sendline("lscpu")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            lscpu_info = connect.before.strip()
            match = re.search(r'Vendor ID:\s+(.+)', lscpu_info)
            cpu_vendor = match.group(1).strip()

            connect.sendline("lscpu | grep 'Model name'")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            match = re.search(r'Model name:\s+(.+)', lscpu_info)
            cpu_model = match.group(1).strip()

            # memory
            connect.sendline("free -h")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            memory_info = connect.before.strip()
            match = re.search(r'Mem:\s+(\S+)\s+.+', memory_info)
            mem_total = match.group(1).strip() 

            # disk
            connect.sendline("df -h")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            disk_info_raw = connect.before.strip()

            disk_info_list = []
            lines = disk_info_raw.splitlines()
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 6:
                    partition_info = OrderedDict([
                        ("filesystem", parts[0]),
                        ("size", parts[1]),
                        ("used", parts[2]),
                        ("available", parts[3]),
                        ("used_percentage", parts[4]),
                        ("mount_point", parts[5])
                    ])
                    disk_info_list.append(partition_info)
            disk_info = disk_info_list


            # network
            connect.sendline("ip -o addr show")
            connect.expect(r"\[.*\]\$ ", timeout=10)
            network_info_raw = connect.before.strip()

            # arp
            connect.sendline("ip neigh show")
            connect.expect(r"\[.*\]\$ ", timeout=10)
            arp_table = connect.before.strip()

            network_data_list = []

            for line in network_info_raw.splitlines():
                match = re.search(r'(\d+): (\w+)\s+inet\s+(\d+\.\d+\.\d+\.\d+)/\d+', line)
                if match:
                    interface = match.group(2)
                    ip_address = match.group(3)

                    connect.sendline("ip link show {}".format(interface))
                    connect.expect(r"\[.*\]\$ ", timeout=10)
                    link_info = connect.before.strip()

                    mac_match = re.search(r'link/ether\s+([\da-fA-F:]+)', link_info)
                    mac_address = mac_match.group(1) if mac_match else "Unknown"

                    network_data_list.append(OrderedDict([
                        ("interface", interface),
                        ("ip_address", ip_address),
                        ("mac_address", mac_address),
                    ]))
            network_data = network_data_list

            # software (RHEL/CentOS by rpm)
            connect.sendline("rpm -qa")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            installed_software = connect.before.strip().splitlines()[1:]

            # SSH end
            connect.sendline("exit")

            return OrderedDict([
                ("Server", OrderedDict([
                    ("hostname", hostname),
                    ("linux_version", linux_version),
                    ("linux_kernel", linux_kernel),
                    ("cpu_count", cpu_count),
                    ("memory_size", mem_total),
                    ("disk_info", disk_info),
                    ("network_info", network_data),
                    ("installed_software", installed_software)
                ])),
                ("Hardware", OrderedDict([
                    ("hw_type", hw_type),
                    ("hardware_manufacturer", hardware_manufacturer),
                    ("hardware_model", hardware_model),
                    ("cpu_vendor", cpu_vendor),
                    ("cpu_model", cpu_model)
                ]))
            ])


        except (pexpect.EOF, pexpect.TIMEOUT):
            try_count += 1
            print("SSH connection failed (Try {}/{}). Retrying...".format(try_count, retries))
            time.sleep(2)

    return {"error": "Failed to establish SSH connection after {} retries.".format(retries)}


# main
if __name__ == "__main__":
    input_directory = "list"
    output_directory = "log"

    LISTFILE = os.path.join(input_directory, "list.json")
    with open(LISTFILE, 'r') as f:
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')
        system_info_all = OrderedDict()
 
        output_file = os.path.join(output_directory, "ci_{}.json".format(current_time))
        data = json.load(f)
        for entry in data:
            system_info = ci_get(no = entry["no"], ip = entry["ip"], user = entry["user"], password = entry["password"])
            system_info_all[entry["no"]] = system_info

            # output json
            with open(output_file, 'w') as f:
                json.dump(system_info_all, f, indent=4)

            print("System information saved to {}".format(output_file))

