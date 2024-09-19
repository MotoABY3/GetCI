#!/usr/bin/env python
# coding: UTF-8

import json
import os
import difflib
import pexpect
import datetime
import re
import time
from datetime import datetime, timedelta
from collections import OrderedDict

LISTFILE = "/home/mochida/ci_expect/list.txt"

# JSONファイルの読み込み
def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


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

            # ホスト名を取得
            connect.sendline("hostnamectl")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            hostnamectl_info = connect.before.strip()
            match = re.search(r'Static hostname:\s+(.+)', hostnamectl_info)
            hostname = match.group(1).strip()
            #print(match)
            #print(hostname)

            # Linuxバージョンを取得
            match = re.search(r'Operating System:\s+(.+)', hostnamectl_info)
            linux_version = match.group(1)
            #print(match)
            #print(linux_version)

            # Linuxカーネルを取得
            match = re.search(r'Kernel:\s+(.+)', hostnamectl_info)
            linux_kernel = match.group(1)
            #print(match)
            #print(linux_kernel)

            # HWタイプ
            match = re.search(r'Chassis:\s+(.+)', hostnamectl_info)
            hw_type = match.group(1)
            #print(match)
            #print(hw_type)

            # ハードウェア情報
            connect.sendline("sudo dmidecode -s system-manufacturer")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            hardware_manufacturer = connect.before.strip().splitlines()[1]
            #print(hardware_manufacturer)

            connect.sendline("sudo dmidecode -s system-product-name")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            hardware_model = connect.before.strip().splitlines()[1]
            #print(hardware_model)

            # CPU情報
            connect.sendline("nproc")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            cpu_count = connect.before.strip().splitlines()[1]
            #print(cpu_count)

            connect.sendline("lscpu")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            lscpu_info = connect.before.strip()
            match = re.search(r'Vendor ID:\s+(.+)', lscpu_info)
            cpu_vendor = match.group(1).strip()
            #print(cpu_vendor)

            connect.sendline("lscpu | grep 'Model name'")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            match = re.search(r'Model name:\s+(.+)', lscpu_info)
            cpu_model = match.group(1).strip()
            #print(cpu_model)

            # メモリサイズ
            connect.sendline("free -h")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            memory_info = connect.before.strip()
            match = re.search(r'Mem:\s+(\S+)\s+.+', memory_info)
            mem_total = match.group(1).strip() 
            #print(mem_total)


            # ディスクサイズをパーティションごとに取得する関数
            connect.sendline("df -h")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            disk_info_raw = connect.before.strip()

            # パーティションごとに情報を辞書にまとめてリストに格納
            disk_info_list = []
            lines = disk_info_raw.splitlines()
            for line in lines[1:]:  # ヘッダー行をスキップ
                parts = line.split()
                if len(parts) >= 6:  # フィールド数が足りない行を無視
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


            # ネットワークインターフェース、IPアドレス、MACアドレスを取得
            connect.sendline("ip -o addr show")
            connect.expect(r"\[.*\]\$ ", timeout=10)
            network_info_raw = connect.before.strip()
            #print(network_info)

            # 対向機器のMACアドレスを取得 (ARPテーブルから)
            connect.sendline("ip neigh show")
            connect.expect(r"\[.*\]\$ ", timeout=10)
            arp_table = connect.before.strip()
            #print(arp_table)

            # ネットワークインターフェース、IPアドレス、MACアドレスをパースして対向機器のMACアドレスを取得
            network_data_list = []

            for line in network_info_raw.splitlines():

            # IPv4アドレスを抽出
                match = re.search(r'(\d+): (\w+)\s+inet\s+(\d+\.\d+\.\d+\.\d+)/\d+', line)
                if match:
                    interface = match.group(2)
                    ip_address = match.group(3)
                    print(interface)
                    print(ip_address)


                    # MACアドレスを取得するために `ip link show <interface>` を実行
                    connect.sendline("ip link show {}".format(interface))
                    connect.expect(r"\[.*\]\$ ", timeout=10)
                    link_info = connect.before.strip()
                    print(link_info)

                    # MACアドレスを抽出 (link/etherから)
                    mac_match = re.search(r'link/ether\s+([\da-fA-F:]+)', link_info)
                    mac_address = mac_match.group(1) if mac_match else "Unknown"

                    # 対向機器のMACアドレスをARPテーブルから取得
                    opposing_mac = "Not found"
                    arp_match = re.search(r'{}.*lladdr\s+([\da-fA-F:]+)'.format(ip_address), arp_table)
                    if arp_match:
                        opposing_mac = arp_match.group(1)

                    # ネットワーク情報をリストに追加
                    network_data_list.append(OrderedDict([
                        ("interface", interface),
                        ("ip_address", ip_address),
                        ("mac_address", mac_address),
                        ("opposing_mac", opposing_mac)
                    ]))
            network_data = network_data_list
            #

            # インストール済みソフトウェア (RHEL/CentOSの場合はrpm)
            connect.sendline("rpm -qa")
            connect.expect(r"\[.*\]\$ ",timeout=10)
            installed_software = connect.before.strip().splitlines()[1:]
            #print(installed_software)



            connect.sendline("exit")

            return OrderedDict([
                ("Server", OrderedDict([
                    ("hostname", hostname),
                    ("linux_version", linux_version),
                    ("linux_kernel", linux_kernel),
                    ("cpu_count", cpu_count),
                    ("memory_size", mem_total),  # メモリサイズを含む
                    ("disk_info", disk_info),  # パーティションごとのディスク情報
                    ("network_info", network_data),
                    ("installed_software", installed_software)  # ソフトウェアごとに格納
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


# 実行例
if __name__ == "__main__":
    input_file = "."        # 出力元ファイル
    input_directory = "."   # 出力元ディレクトリ
    output_file = "ci.json" # 出力先ファイル
    output_directory = "."  # 出力先ディレクトリ

    with open(LISTFILE, 'r') as f:
        current_time = datetime.now().strftime('%Y%m%d')
        system_info_all = OrderedDict()
 
        output_file = os.path.join(output_directory, "ci_{}.json".format(current_time))
        data = json.load(f)
        for entry in data:
            system_info = ci_get(no = entry["no"], ip = entry["ip"], user = entry["user"], password = entry["password"])
            system_info_all[entry["no"]] = system_info

            # JSONとして出力
            with open(output_file, 'w') as f:
                json.dump(system_info_all, f, indent=4)

            print("System information saved to {}".format(output_file))

