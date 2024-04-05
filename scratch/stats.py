import csv
import statistics
import numpy as np
from tqdm import tqdm
import argparse
import re

def ip_key(ip):
    parts = re.split(r'\.', ip)
    return tuple(int(part) for part in parts)

def box_whiskers_plot(data, box_weight=1.5):
    q1, median, q3 = np.percentile(data, [25, 50, 75])
    iqr = q3 - q1
    whisker_low, whisker_high = q1 - box_weight * iqr, q3 + box_weight * iqr
    
    min_val, max_val = min(data), max(data)
    whisker_low, whisker_high = max(min_val, whisker_low), min(max_val, whisker_high)

    plot_width = 100
    plot_min, plot_max = min_val, max_val
    plot_range = plot_max - plot_min
    scale_factor = (plot_width - 2) / plot_range
    
    median_pos = int((median - plot_min) * scale_factor) + 1
    q1_pos = int((q1 - plot_min) * scale_factor) + 1
    q3_pos = int((q3 - plot_min) * scale_factor) + 1
    whisker_low_pos = int((whisker_low - plot_min) * scale_factor) + 1
    whisker_high_pos = int((whisker_high - plot_min) * scale_factor) + 1

    plot = ['-'] * plot_width
    plot[whisker_low_pos] = '<' if whisker_low > min_val else '|'
    plot[whisker_high_pos] = '>' if whisker_high < max_val else '|'
    plot[q1_pos:q3_pos+1] = '=' * (q3_pos - q1_pos + 1)
    plot[median_pos] = '0'

    return ''.join(plot)

def calculate_stats(csv_file):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)

        # Validate header
        expected_header = [
            'test_name', 'title', 'client_ip', 'server_ip', 'role', 'device', 'local_lid',
            'local_gid', 'remote_lid', 'remote_gid', 'num_bytes', 'num_iterations',
            'bw_peak_mbps', 'bw_average_mbps', 'msg_rate_mpps'
        ]
        if reader.fieldnames != expected_header:
            raise ValueError("CSV header does not match the expected format.")

        data = list(reader)

    # Calculate overall statistical measures
    bw_average_mbps_all = [float(row['bw_average_mbps']) for row in data]
    msg_rate_mpps_all = [float(row['msg_rate_mpps']) for row in data]

    overall_stats = {
        'mean_bandwidth': statistics.mean(bw_average_mbps_all),
        'median_bandwidth': statistics.median(bw_average_mbps_all),
        'iqr_bandwidth': np.percentile(bw_average_mbps_all, 75) - np.percentile(bw_average_mbps_all, 25),
        'std_bandwidth': statistics.stdev(bw_average_mbps_all),
        'percentile_5_bandwidth': np.percentile(bw_average_mbps_all, 5),
        'percentile_95_bandwidth': np.percentile(bw_average_mbps_all, 95),
        'mean_msg_rate': statistics.mean(msg_rate_mpps_all),
        'median_msg_rate': statistics.median(msg_rate_mpps_all),
        'iqr_msg_rate': np.percentile(msg_rate_mpps_all, 75) - np.percentile(msg_rate_mpps_all, 25),
        'std_msg_rate': statistics.stdev(msg_rate_mpps_all),
        'percentile_5_msg_rate': np.percentile(msg_rate_mpps_all, 5),
        'percentile_95_msg_rate': np.percentile(msg_rate_mpps_all, 95)
    }

    # Group data by client_ip
    grouped_data = {}
    for row in data:
        client_ip = row['client_ip']
        if client_ip not in grouped_data:
            grouped_data[client_ip] = []
        grouped_data[client_ip].append(row)

    # Calculate statistical measures for each client IP
    results = []
    for client_ip, group_data in tqdm(grouped_data.items(), desc="Calculating statistics", unit="client"):
        bw_average_mbps = [float(row['bw_average_mbps']) for row in group_data]
        msg_rate_mpps = [float(row['msg_rate_mpps']) for row in group_data]

        median_bw = statistics.median(bw_average_mbps)
        iqr_bw = np.percentile(bw_average_mbps, 75) - np.percentile(bw_average_mbps, 25)
        median_msg_rate = statistics.median(msg_rate_mpps)
        iqr_msg_rate = np.percentile(msg_rate_mpps, 75) - np.percentile(msg_rate_mpps, 25)

        bw_color = "\033[92m" if abs(median_bw - overall_stats['median_bandwidth']) <= overall_stats['iqr_bandwidth'] else "\033[91m"
        msg_rate_color = "\033[92m" if abs(median_msg_rate - overall_stats['median_msg_rate']) <= overall_stats['iqr_msg_rate'] else "\033[91m"

        bw_plot = box_whiskers_plot(bw_average_mbps)
        msg_rate_plot = box_whiskers_plot(msg_rate_mpps)

        result = {
            'client_ip': client_ip,
            'median_bandwidth': f"{bw_color}{median_bw:.2f}\033[0m",
            'iqr_bandwidth': f"{bw_color}{iqr_bw:.2f}\033[0m",
            'median_msg_rate': f"{msg_rate_color}{median_msg_rate:.2f}\033[0m",
            'iqr_msg_rate': f"{msg_rate_color}{iqr_msg_rate:.2f}\033[0m",
            'bw_plot': bw_plot,
            'msg_rate_plot': msg_rate_plot
        }
        results.append(result)

    # Sort the results by ascending order of client IP
    results.sort(key=lambda x: ip_key(x['client_ip']))

    return overall_stats, results

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Calculate statistical measures for network performance data.')
parser.add_argument('csv_file', type=str, help='Path to the CSV file')
args = parser.parse_args()

# Usage example
csv_file_path = args.csv_file
overall_stats, client_stats = calculate_stats(csv_file_path)

# Print the overall statistics
print("\033[1mOverall Statistics:\033[0m")
print("{:<40} \033[96m{:.2f} Mbps\033[0m".format("Median Bandwidth:", overall_stats['median_bandwidth']))
print("{:<40} \033[96m{:.2f} Mbps\033[0m".format("Interquartile Range of Bandwidth:", overall_stats['iqr_bandwidth']))
print("{:<40} \033[96m{:.2f} Mbps\033[0m".format("Mean Bandwidth:", overall_stats['mean_bandwidth']))
print("{:<40} \033[96m{:.2f} Mbps\033[0m".format("Standard Deviation of Bandwidth:", overall_stats['std_bandwidth']))
print("{:<40} \033[96m{:.2f} Mbps\033[0m".format("5th Percentile of Bandwidth:", overall_stats['percentile_5_bandwidth']))
print("{:<40} \033[96m{:.2f} Mbps\033[0m".format("95th Percentile of Bandwidth:", overall_stats['percentile_95_bandwidth']))
print("{:<40} \033[96m{:.2f} Mpps\033[0m".format("Median Message Rate:", overall_stats['median_msg_rate']))
print("{:<40} \033[96m{:.2f} Mpps\033[0m".format("Interquartile Range of Message Rate:", overall_stats['iqr_msg_rate']))
print("{:<40} \033[96m{:.2f} Mpps\033[0m".format("Mean Message Rate:", overall_stats['mean_msg_rate']))
print("{:<40} \033[96m{:.2f} Mpps\033[0m".format("Standard Deviation of Message Rate:", overall_stats['std_msg_rate']))
print("{:<40} \033[96m{:.2f} Mpps\033[0m".format("5th Percentile of Message Rate:", overall_stats['percentile_5_msg_rate']))
print("{:<40} \033[96m{:.2f} Mpps\033[0m".format("95th Percentile of Message Rate:", overall_stats['percentile_95_msg_rate']))
print("---")

# Print the statistics for each client IP in one line, sorted by ascending order of client IP
print("\033[1mClient IP Statistics (Sorted by Client IP):\033[0m")
print("{:<18} {:<25} {:<25} {:<25} {:<25}".format("Client IP", "Median Bandwidth (Mbps)", "IQR Bandwidth (Mbps)", "Median Msg Rate (Mpps)", "IQR Msg Rate (Mpps)"))
for result in client_stats:
    print("{:<18} {:<25} {:<25} {:<25} {:<25}".format(result['client_ip'], result['median_bandwidth'], result['iqr_bandwidth'], result['median_msg_rate'], result['iqr_msg_rate']))

print("---")

# Print the box and whiskers plot for each client IP
print("\033[1mBox and Whiskers Plot:\033[0m")
print("{:<18} {:<102} {:<102}".format("Client IP", "Bandwidth Plot", "Msg Rate Plot"))
for result in client_stats:
    print("{:<18} {:<102} {:<102}".format(result['client_ip'], result['bw_plot'], result['msg_rate_plot']))
