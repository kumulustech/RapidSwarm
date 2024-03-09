# RapidSwarm

## Overview
RapidSwarm is a Python-based toolset for managing multi-endpoint network validation testing for HPC clusters. It automates the discovery, testing, and reporting of network nodes with various hardware interfaces, focusing on enhancing the reliability and performance of network-intensive applications.

## Features
- **Automated Discovery and Testing**: Automatically discovers nodes and tests their network interfaces and GPU communications.
- **Flexible Test Definitions**: Define tests with custom parameters and output parsing rules to meet diverse testing requirements.
- **Dynamic Output Parsing**: Extract meaningful metrics and insights from test outputs with customizable parsing rules.
- **Comprehensive Reporting**: Analyze and report test results, facilitating performance monitoring and issue identification.

## Installation

Ensure Poetry is installed on your system. Visit [Poetry's documentation](https://python-poetry.org/docs/) for installation instructions.

1. **Clone the Repository**
2. **Navigate to the cloned directory**: Use the command `cd RapidSwarm` to move into the project directory.
3. **Install dependencies**: Run `poetry install` to install the necessary dependencies for RapidSwarm.
4. **Run tests**: Execute `poetry run pytest` to run the tests and ensure everything is set up correctly.
## Usage

To use RapidSwarm for network testing, follow these steps:

1. **Define your network tests**: Create test definitions according to your network's requirements. Use the examples in `src/rapidswarm/tests/` as a guide for defining tests for network interfaces and types.

2. **Configure your environment**: Ensure all dependencies are installed and your environment is set up as described in the Installation section. Additionally, configure your `config.yaml` file to define the nodes and interfaces to be scanned. The format should follow the example provided in the `config.yaml` section below.

3. **Run RapidSwarm**: Execute the command `poetry run rapidswarm` to start the discovery and testing process. Use the `-h` option to explore additional command-line options.

4. **Review test results**: After the tests have completed, review the generated reports in the `reports/` directory to analyze the performance and reliability of your network interfaces.

For more detailed instructions and advanced usage, refer to the documentation in the `docs/` directory.

## Configuring `config.yaml`

The `config.yaml` file is crucial for defining the network nodes and interfaces that RapidSwarm will scan and test. The file should be structured as follows from this example:

```
scanners:
  - type: CSVScanner
    config:
      csv_data: |
        node_name,interface_name,mac_address,ip_address
        node1,eth0,00:11:22:33:44:55,192.168.0.1
        node1,eth1,00:11:22:33:44:56,192.168.0.2
        node2,eth0,11:22:33:44:55:66,192.168.1.1
        node3,ib0,00:02:c9:44:55:66,192.168.1.2
        node3,eth0,00:02:c9:44:55:67,192.168.1.3
probes:
  - type: NetworkPerformanceProbe
    config:
      test_type: "throughput"
      duration: "30s"
reporters:
  - type: HTMLReporter
    config:
      output_directory: "./reports/"
      template: "network_performance.html"
managers:
  - type: Sequential
    config:
      interval: "5m"
      retry_on_failure: true
      max_retries: 3
```

The config file has four main sections:
- scanners
- probes
- reporters
- managers

Each section of the `config.yaml` file plays a crucial role in configuring RapidSwarm for network scanning and testing. Here's a detailed explanation of each section:

### Scanners
The `scanners` section defines the sources from which network nodes and interfaces will be discovered. Each scanner type has its own configuration options. 

For example, the `CSVScanner` type reads network node and interface information from a CSV formatted string. The `csv_data` key within the `config` specifies the actual CSV data, where each row represents a network node and its interface details such as `node_name`, `interface_name`, `mac_address`, and `ip_address`. The `CSVScanner` type is useful for testing a small set of known nodes and interfaces.

Future work will include adding support for other scanners such as `NmapScanner` and `SlurmScanner` to discover nodes and interfaces from Nmap and Slurm respectively. Other types such as MaasScanner will query services such as Ubuntu Maas to discover nodes and interfaces.

### Probes
The `probes` section specifies the tests that will be run against the discovered network interfaces. Each probe type has its own configuration. 

For instance, the `NetworkPerformanceProbe` type is configured to test network throughput over a specified duration (`30s` in the example). This section allows users to define various performance metrics and tests to assess the network's reliability and performance. A `PingProbe` type is also available to test network latency.

### Reporters
The `reporters` section defines how the results of the network tests will be reported. Each reporter type has its own configuration options. 

The `HTMLReporter` type, for example, generates an HTML report of the test results. The `output_directory` specifies where the report will be saved, and the `template` key defines the HTML template to use for the report. This section enables users to customize the reporting format and location according to their needs.

### Managers
The `managers` section configures how the scanning and testing processes are managed. Each manager type has its own set of configuration options. 

The `Sequential` manager type, as shown in the example, runs the tests sequentially with a specified interval (`5m`) between each test. It also includes options for retrying failed tests (`retry_on_failure: true`) and the maximum number of retries (`max_retries: 3`). This section allows users to control the execution flow of the tests, including scheduling, retries, and handling failures.

Understanding and configuring each of these sections correctly is essential for tailoring RapidSwarm to meet specific network testing requirements.

Another example of a config.yaml file is as follows:

```
scanners:
  - type: NmapScanner
    config:
      target_range: "192.168.1.0/24"
      scan_options: "-sP"
  - type: NvidiaScanner
    config:
      query_mode: "all"

probes:
  - type: NvidiaGPUPerformanceProbe
    config:
      test_type: "interconnect_bandwidth"
      duration: "60s"
      gpu_pairs: [
        {"source": "GPU0", "target": "GPU1"},
        {"source": "GPU1", "target": "GPU2"}
      ]

reporters:
  - type: JSONReporter
    config:
      output_directory: "./gpu_reports/"
      template: "gpu_performance.json"

managers:
  - type: Parallel
    config:
      max_concurrent_tests: 5
      retry_on_failure: false
```
