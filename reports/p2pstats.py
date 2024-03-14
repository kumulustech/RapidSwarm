import csv
import numpy as np

# Function to calculate mean, median, and standard deviation
def calculate_stats(data):
    mean = np.mean(data)
    median = np.median(data)
    std_dev = np.std(data)
    return mean, median, std_dev

# Read the CSV file and process the data
with open('data.csv', 'r') as csvfile:
    csvreader = csv.DictReader(csvfile)
    
    # Extract the data into lists
    rows = list(csvreader)
    client_avg_mbps = [float(row['client_avg_mbps']) for row in rows]
    server_avg_mbps = [float(row['server_avg_mbps']) for row in rows]

# Calculate statistics for client and server
client_mean, client_median, client_std = calculate_stats(client_avg_mbps)
server_mean, server_median, server_std = calculate_stats(server_avg_mbps)

# Print the statistics to the screen
print(f"Client Traffic: Mean = {client_mean:.2f}, Median = {client_median:.2f}, Standard Deviation = {client_std:.2f}")
print(f"Server Traffic: Mean = {server_mean:.2f}, Median = {server_median:.2f}, Standard Deviation = {server_std:.2f}")

# Find and print outliers, and write them to a new CSV file
outliers = []
with open('outliers_report.csv', 'w', newline='') as csvfile:
    fieldnames = ['client IP', 'server IP', 'client perf', 'client std dev', 'server perf', 'server std dev']
    csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    csvwriter.writeheader()
    for row in rows:
        client_mbps = float(row['client_avg_mbps'])
        server_mbps = float(row['server_avg_mbps'])
        client_deviation = abs(client_mbps - client_mean) / client_std
        server_deviation = abs(server_mbps - server_mean) / server_std
        if client_deviation > 2 or server_deviation > 2:
            outlier = {
                'client IP': row['client'],
                'server IP': row['server'],
                'client perf': f"{client_mbps:.2f}",
                'client std dev': f"{client_deviation:.2f}",
                'server perf': f"{server_mbps:.2f}",
                'server std dev': f"{server_deviation:.2f}"
            }
            outliers.append(outlier)
            csvwriter.writerow(outlier)

# Print the outliers to the screen
print("\nOutliers:")
for outlier in outliers:
    print(outlier)

print("\nOutliers have been written to 'outliers_report.csv'")
