import os
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

# Step 0: Initialize
station = 'CAS1'  # Replace with actual station name
year = '2021'  # Replace with actual year
signal = 'S2W'  # Replace with actual signal name

# Set input and output folders
input_folder = r'F:\data\result\ver3\DTW_results'
output_folder = r'F:\data\result\ver3\DTW_detection_result'
consolidated_output_folder = r'F:\data\result\ver3\consolidated_results'
image_output_folder = r'F:\data\result\ver3\outlier_detection_plots'

# Create output folders if they don't exist
for folder in [output_folder, consolidated_output_folder, image_output_folder]:
    os.makedirs(folder, exist_ok=True)

# Initialize variables to store all dates and data
all_dates = set()
all_data = defaultdict(dict)


# Define date to DOY function
def date_to_doy(date):
    return date.timetuple().tm_yday


# Step 1: Process each satellite
for sat_num in range(1, 33):
    sat = f'G{sat_num:02d}'  # Generate satellite ID (G01, G02, ..., G32)

    # Construct file path
    file_path = os.path.join(input_folder, f'{station}_{year}_{signal}_{sat}_DTW.csv')

    # Check if the file exists before attempting to read it
    if os.path.isfile(file_path):
        # Read data, handling non-numeric elements as NaN
        data = pd.read_csv(file_path, parse_dates=[0])
        dates = data.iloc[:, 0]
        values = pd.to_numeric(data.iloc[:, 1], errors='coerce')

        # Method 1: IQR (Interquartile Range) method
        multiplier = 9  # Default is 1.5, can be manually adjusted

        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1

        # Adjust upper bound based on multiplier
        upper_bound = Q3 + multiplier * IQR

        # Mark outliers
        is_outlier = values > upper_bound

        # Record outlier dates and values
        outlier_dates = dates[is_outlier]
        outlier_values = values[is_outlier]

        # Plot and save figure
        plt.figure(figsize=(12, 6))
        plt.scatter(dates[~is_outlier], values[~is_outlier], c='b', label='Non-Outlier Data')
        plt.scatter(outlier_dates, outlier_values, c='r', label='Outliers')
        plt.axhline(y=upper_bound, color='r', linestyle='--', label=f'Upper Threshold: {upper_bound:.2f}')

        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.title(f'Time Series Data with Outliers - {station} {year} - {sat}')
        plt.legend()

        image_path = os.path.join(image_output_folder, f'{station}_{year}_{signal}_{sat}_OutlierDetection.png')
        plt.savefig(image_path)
        plt.close()

        # Calculate DOY
        doy = dates.apply(date_to_doy)

        # Output results as CSV file
        output_df = pd.DataFrame({'Date': dates, 'DOY': doy, 'IsOutlier': is_outlier.astype(int)})
        output_path = os.path.join(output_folder, f'{station}_{year}_{signal}_{sat}_OutlierDetectionResults.csv')
        output_df.to_csv(output_path, index=False)

        # Add dates to all_dates
        all_dates.update(dates)

        # Store satellite data
        all_data[sat_num] = dict(zip(dates.astype(str), is_outlier.astype(int)))
    else:
        print(f'File not found: {file_path}')

# Step 2: Consolidate data
all_dates = sorted(all_dates)
all_doy = [date_to_doy(date) for date in all_dates]

# Create output data DataFrame
output_data = pd.DataFrame({'Date': all_dates, 'DOY': all_doy})

# Fill data
for sat_num in range(1, 33):
    sat = f'G{sat_num:02d}'
    if sat_num in all_data:
        output_data[sat] = output_data['Date'].astype(str).map(all_data[sat_num])

# Write to CSV file
consolidated_output_path = os.path.join(consolidated_output_folder,
                                        f'{station}_{year}_{signal}_ConsolidatedResults.csv')
output_data.to_csv(consolidated_output_path, index=False)

print('Processing completed.')
print(f'Outlier detection results saved to: {output_folder}')
print(f'Outlier detection plots saved to: {image_output_folder}')
print(f'Consolidated file saved to: {consolidated_output_path}')