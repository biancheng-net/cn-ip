import requests
import math
import os

def download_apnic_data():
    url = "https://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest"
    response = requests.get(url)
    return response.text

def process_apnic_data(data):
    china_ip_allocations_ipv4 = []
    china_ip_allocations_ipv6 = []

    for line in data.splitlines():
        if line.startswith("#") or not line.strip():
            continue

        fields = line.split("|")

        if len(fields) > 6 and fields[1].upper() == "CN":
            resource_type = fields[2].lower()

            if resource_type == "ipv4":
                ip_range = fields[3]
                count = int(fields[4])
                cidr_prefix = 32 - int(math.log2(count))
                china_ip_allocations_ipv4.append(f"{ip_range}/{cidr_prefix}")

            elif resource_type == "ipv6":
                ipv6_range = fields[3]
                prefix_length = fields[4]
                china_ip_allocations_ipv6.append(f"{ipv6_range}/{prefix_length}")

    return china_ip_allocations_ipv4, china_ip_allocations_ipv6

if __name__ == "__main__":
    print("Starting job...")
    apnic_data = download_apnic_data()
    ipv4_cidrs, ipv6_cidrs = process_apnic_data(apnic_data)
    print("Job completed.")