import csv
import numpy as np
from collections import Counter

# Function to calculate mean, median, and standard deviation
def calculate_stats(data):
    mean = np.mean(data)
    median = np.median(data)
    std_dev = np.std(data)
    return mean, median, std_dev

# Function to identify outliers
def identify_outliers(data, mean, std_dev):
    return [x for x in data if abs(x - mean) > 2 * std_dev]

# Function to count the frequency of IP addresses in the outliers
def count_ip_frequency(outliers):
    client_ip_counter = Counter()
    server_ip_counter = Counter()

    for outlier in outliers:
        client_ip_counter[outlier['client IP']] += 1
        server_ip_counter[outlier['server IP']] += 1

    return client_ip_counter, server_ip_counter

# Read the CSV file and process the data
with open('data.csv', 'r') as csvfile:
    csvreader = csv.DictReader(csvfile)

    # Extract the data into lists
    rows = list(csvreader)
    client_avg_mbps = [float(row['client_avg_mbps']) for row in rows]
    server_avg_mbps = [float(row['server_avg_mbps']) for row in rows]

# Identify first-order outliers
client_mean, client_median, client_std = calculate_stats(client_avg_mbps)
server_mean, server_median, server_std = calculate_stats(server_avg_mbps)

client_outliers = identify_outliers(client_avg_mbps, client_mean, client_std)
server_outliers = identify_outliers(server_avg_mbps, server_mean, server_std)

# Remove outliers from the dataset
client_data_filtered = [x for x in client_avg_mbps if x not in client_outliers]
server_data_filtered = [x for x in server_avg_mbps if x not in server_outliers]

# Calculate statistics without outliers
client_mean_filtered, client_median_filtered, client_std_filtered = calculate_stats(client_data_filtered)
server_mean_filtered, server_median_filtered, server_std_filtered = calculate_stats(server_data_filtered)

# Identify second-order outliers
client_second_order_outliers = identify_outliers(client_data_filtered, client_mean_filtered, client_std_filtered)
server_second_order_outliers = identify_outliers(server_data_filtered, server_mean_filtered, server_std_filtered)

# Write first-order outliers to a CSV file
with open('outliers_report.csv', 'w', newline='') as csvfile:
    fieldnames = ['client IP', 'server IP', 'client perf', 'client std dev', 'server perf', 'server std dev']
    csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

    csvwriter.writeheader()
    for row in rows:
        client_mbps = float(row['client_avg_mbps'])
        server_mbps = float(row['server_avg_mbps'])
        if client_mbps in client_outliers or server_mbps in server_outliers:
            csvwriter.writerow({
                'client IP': row['client'],
                'server IP': row['server'],
                'client perf': f"{client_mbps:.2f}",
                'client std dev': f"{(client_mbps - client_mean) / client_std:.2f}",
                'server perf': f"{server_mbps:.2f}",
                'server std dev': f"{(server_mbps - server_mean) / server_std:.2f}"
            })

# Write second-order outliers to a separate CSV file
with open('second_order_outliers_report.csv', 'w', newline='') as csvfile:
    csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

    csvwriter.writeheader()
    for row in rows:
        client_mbps = float(row['client_avg_mbps'])
        server_mbps = float(row['server_avg_mbps'])
        if client_mbps in client_second_order_outliers or server_mbps in server_second_order_outliers:
            csvwriter.writerow({
                'client IP': row['client'],
                'server IP': row['server'],
                'client perf': f"{client_mbps:.2f}",
                'client std dev': f"{(client_mbps - client_mean_filtered) / client_std_filtered:.2f}",
                'server perf': f"{server_mbps:.2f}",
                'server std dev': f"{(server_mbps - server_mean_filtered) / server_std_filtered:.2f}"
            })

# Read the outliers from the CSV into a list of dictionaries
def read_outliers_from_csv(filename):
    with open(filename, 'r') as csvfile:
        return list(csv.DictReader(csvfile))

# Identify frequent IPs in both reports
first_order_outliers = read_outliers_from_csv('outliers_report.csv')
second_order_outliers = read_outliers_from_csv('second_order_outliers_report.csv')

first_order_client_ips, first_order_server_ips = count_ip_frequency(first_order_outliers)
second_order_client_ips, second_order_server_ips = count_ip_frequency(second_order_outliers)

# Combine client and server IP counts
combined_first_order_ips = Counter(first_order_client_ips) + Counter(first_order_server_ips)
combined_second_order_ips = Counter(second_order_client_ips) + Counter(second_order_server_ips)

# Filter IPs that appear more than twice in either role
frequent_combined_first_order_ips = {ip for ip, count in combined_first_order_ips.items() if count > 2}
frequent_combined_second_order_ips = {ip for ip, count in combined_second_order_ips.items() if count > 2}

# Function to extract outlier data for a specific IP
def extract_outlier_data_for_ip(ip, outliers):
    headers = outliers[0].keys()
    relevant_data = [row for row in outliers if ip in (row['client IP'], row['server IP'])] 
    return headers, relevant_data

# Function to write a section for a specific IP
def write_ip_section(mdfile, ip, headers, data):
    mdfile.write(f"### Outlier Data for IP {ip}\n\n")
    mdfile.write("| " + " | ".join(headers) + " |\n")
    mdfile.write("| " + " | ".join(['---'] * len(headers)) + " |\n")
    for row in data:
        mdfile.write("| " + " | ".join(str(row[h]) for h in headers) + " |\n")
    mdfile.write("\n")

# Generate markdown report
with open('report.md', 'w') as mdfile:
    mdfile.write("# Outlier Analysis Report\n\n")

    mdfile.write("## First-Order Outlier Report\n\n")
    mdfile.write("Outliers have been written to 'outliers_report.csv'.\n\n")
    mdfile.write("### IPs Frequent in Outliers (More than twice either as Client or Server)\n\n")
    mdfile.write(f"{', '.join(frequent_combined_first_order_ips)}\n\n")

    mdfile.write("## Second-Order Outlier Report\n\n")
    mdfile.write("Second-order outliers have been written to 'second_order_outliers_report.csv'.\n\n")
    mdfile.write("### IPs Frequent in Outliers (More than twice either as Client or Server)\n\n")
    mdfile.write(f"{', '.join(frequent_combined_second_order_ips)}\n\n")

    mdfile.write("## Second-Order Dataset Statistics\n\n")
    mdfile.write("| Metric | Client Traffic | Server Traffic |\n")
    mdfile.write("| ------ | -------------- | -------------- |\n")
    mdfile.write(f"| Mean | {client_mean_filtered:.2f} Mbps | {server_mean_filtered:.2f} Mbps |\n")
    mdfile.write(f"| Median | {client_median_filtered:.2f} Mbps | {server_median_filtered:.2f} Mbps |\n")
    mdfile.write(f"| Standard Deviation | {client_std_filtered:.2f} | {server_std_filtered:.2f} |\n")

    mdfile.write("## Detailed Outlier Data for Frequent IPs\n\n")

    # First-order Outliers
    mdfile.write("### First-Order Outliers\n\n")
    for ip in frequent_combined_first_order_ips:
        headers, data = extract_outlier_data_for_ip(ip, first_order_outliers)
        write_ip_section(mdfile, ip, headers, data)

    # Second-order Outliers
    mdfile.write("### Second-Order Outliers\n\n")
    for ip in frequent_combined_second_order_ips:
        headers, data = extract_outlier_data_for_ip(ip, second_order_outliers)
        write_ip_section(mdfile, ip, headers, data)
