#!/bin/bash

# Specify the directory path
directory_path="~/apms_data_processing/logs/"

# Check if the directory exists
if [ ! -d "$directory_path" ]; then
    # If it doesn't exist, create it
    mkdir -p "$directory_path"
    echo "logs directory created: $directory_path"
else
    echo "logs directory found"
fi


echo "Processing Stony Point..."
/usr/bin/python3 ~/apms_data_processing/process_data.py stony_point   >> ~/apms_data_processing/logs/process_data_stony_log.txt 2>&1 || touch ~/apms_data_processing/logs/process_data_stony_log.txt

echo "Processing Bird Island..."
/usr/bin/python3 ~/apms_data_processing/process_data.py bird_island   >> ~/apms_data_processing/logs/process_data_bird_log.txt 2>&1 || touch ~/apms_data_processing/logs/process_data_bird_log.txt

echo "Processing Dyer Island..."
/usr/bin/python3 ~/apms_data_processing/process_data.py dyer_island   >> ~/apms_data_processing/logs/process_data_dyer_log.txt 2>&1 || touch ~/apms_data_processing/logs/process_data_dyer_log.txt

echo "Processing Robben Island..."
/usr/bin/python3 ~/apms_data_processing/process_data.py robben_island >> ~/apms_data_processing/logs/process_data_robben_log.txt 2>&1 || touch ~/apms_data_processing/logs/process_data_robben_log.txt

echo "Updating dashboard..."
/usr/bin/python3 ~/apms_data_processing/dashboard.py >> ~/apms_data_processing/logs/dashboard_log.txt 2>&1 || touch ~/apms_data_processing/logs/dashboard_log.txt

# echo "Generating graphs for website..."
# /usr/bin/python3 ~/apms_data_processing/website_upload.py >> ~/apms_data_processing/logs/website_log.txt 2>&1 || touch ~/apms_data_processing/logs/website_log.txt
echo "-DONE-"
