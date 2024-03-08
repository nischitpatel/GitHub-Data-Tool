# GitHub Repository Analyzer

## Overview

This GitHub Repository Analyzer is a Python-based tool designed for the retrieval and analysis of pull request and user data across multiple repositories. The analyzer features statistical analyses, interactive visualizations, and the option to save comprehensive insights in CSV format. It seamlessly integrates with the GitHub API, ensuring efficient data retrieval and processing.

## Key Features

- **Comprehensive Analysis:** Retrieve and analyze pull request and user data simultaneously across multiple repositories, providing detailed insights into repository activity and user contributions.

- **Statistical Analyses:** Utilize statistical analyses to gain a deeper understanding of GitHub repository metrics, including pull requests per day, open vs. closed pull requests, and user distribution.

- **Interactive Visualizations:** Incorporate data visualization techniques using Pandas and Matplotlib libraries to generate informative line plots, bar charts, box plots, and scatter plots for a clear overview of repository metrics.

- **Configurability:** Implement a flexible and configurable system allowing users to specify time windows, output file paths, and other parameters for tailored analyses, ensuring adaptability to diverse analytical needs.

- **GitHub API Integration:** Seamlessly interact with the GitHub API to fetch and process repository data, with built-in handling for pagination, ensuring a comprehensive analysis of large datasets.

- **Technology Stack:** Developed using Python, leveraging Object-Oriented Programming principles for modular and reusable class structures. Integrates with the GitHub API and utilizes Matplotlib for data visualization.

## Usage

1. **Installation:**
   - Ensure Python is installed on your machine.
   - Install the required libraries by running `pip install pandas matplotlib requests` in the terminal.

2. **Configuration:**
   - Modify the configuration parameters in the code, such as time windows and output file paths, to tailor the analysis according to your requirements.

3. **Execution:**
   - Run the script to initiate the GitHub repository analysis. The tool will fetch data from specified repositories, perform statistical analyses, generate visualizations, and save insights in CSV format.

4. **Results:**
   - View the generated visualizations in the specified output file paths.
   - CSV files containing detailed insights will be saved for further analysis or reporting.

## Technology and Concepts Used

- Python
- Object-Oriented Programming
- GitHub API
- Matplotlib
- Data Analysis
- Data Visualization
