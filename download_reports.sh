#!/bin/bash

# List of IP addresses
ips=("172.29.100.223" "172.29.100.222" "172.29.100.111" "172.29.100.130")

# Remote directory path
remote_dir="/opt/ati/run/reports"

# Get yesterday's date in the format YYYY-MM-DD
report_date=$(date -d "yesterday" '+%Y-%m-%d')

# Destination directory (local directory where you want to save the files)
dest_dir="./$report_date"

# Create the destination directory with yesterday's date if it doesn't exist
mkdir -p "$dest_dir"

# Loop through each IP address
for ip in "${ips[@]}"; do
    # Get the vehicle name by SSHing into the machine and running the hostname command
    vehicle_name=$(ssh -o ConnectTimeout=5 "ati@$ip" 'hostname' 2>/dev/null)

    # Check if SSH was successful
    if [ $? -eq 0 ]; then
        # Construct the filename
        report_file="health-${vehicle_name}-${report_date}.txt"
        
        # Use scp to download the file
        scp -r "ati@$ip:$remote_dir/$report_file" "$dest_dir/" 2>/dev/null
        
        # Check if scp was successful
        if [ $? -eq 0 ]; then
            echo "Downloaded $report_file from $ip successfully."
        else
            echo "Failed to download $report_file from $ip. Skipping this machine."
        fi
    else
        echo "Failed to SSH into $ip. Skipping this machine."
    fi
done

