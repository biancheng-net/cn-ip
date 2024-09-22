import requests
import math
import os
from github import Github

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

def update_github_repo(ipv4_cidrs, ipv6_cidrs):
    github_token = os.environ["GITHUB_TOKEN"]
    repo_name = os.environ["GITHUB_REPOSITORY"]

    g = Github(github_token)
    repo = g.get_repo(repo_name)

    content = "\n".join(ipv6_cidrs + ipv4_cidrs)

    try:
        contents = repo.get_contents("cn-ip.txt")
        repo.update_file("cn-ip.txt", "Update China IP allocations", content, contents.sha)
        print("Successfully updated cn-ip.txt")
    except:
        repo.create_file("cn-ip.txt", "Initial commit for China IP allocations", content)
        print("Successfully created cn-ip.txt")

if __name__ == "__main__":
    print("Starting job...")
    apnic_data = download_apnic_data()
    ipv4_cidrs, ipv6_cidrs = process_apnic_data(apnic_data)
    update_github_repo(ipv4_cidrs, ipv6_cidrs)
    print("Job completed.")