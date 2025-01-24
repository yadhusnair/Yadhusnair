#!/bin/bash

# Define the remote user, hosts, paths, and local destination directory
REMOTE_USER="ati"
REMOTE_HOSTS=("IP" "IP" "IP" "IP" "IP")
REMOTE_PATH="/opt/ati/run/reports"
LOCAL_DEST="/home/(username)/health_reports"

# Get the current date in the format "%Y-%m-%d"
CURRENT_DATE=$(date +"%Y-%m-%d")

# Create the date-named directory inside the local destination directory
DEST_DIR="${LOCAL_DEST}/${CURRENT_DATE}"
mkdir -p ${DEST_DIR}

# Function to perform rsync
perform_rsync() {
    local remote_host=$1
    local remote_path=$2
    local local_dest=$3

    rsync -avz --progress ${REMOTE_USER}@${remote_host}:${remote_path} ${local_dest}

    # Check if rsync was successful
    if [ $? -eq 0 ]; then
        echo "Successfully synchronized ${remote_path} from ${remote_host} to ${local_dest}"
    else
        echo "Failed to synchronize ${remote_path} from ${remote_host} to ${local_dest}" >&2
    fi
}

# Loop through each remote host and perform rsync
for host in "${REMOTE_HOSTS[@]}"; do
    perform_rsync ${host} ${REMOTE_PATH} ${DEST_DIR}
done
				
