import json
import os
import urllib.request

import boto3
from botocore.exceptions import ClientError

# To-Do
# X Download json IP list: https://api.config.zscaler.com/zscalertwo.net/cenr/json
# X Exclude locations/City: Moscow III, Beijing, Beijing III, Shanghai, Shanghai II, Tianjin
# X Scrape IP/range for remaining cities
# X Remove IPv6, if required
# X Pass cloud value
# X Pass URL or derrive URL from cloud value
# X Format output in Palo format
# X Save/export file
# X Global configs: File name, cloud, bucket name, excluded cities, 
# - Determine how to run (Function)
# - Determine run frequency: Interval based
# - Input validation
# - Extend to hubs (PSE), PAC
# - Deduplicate data list

def zscaleIpParser (cloud, file_name, excluded_cities, bucket_name):
    # URL to be targeted
    cen_url = "https://api.config.zscaler.com/" + cloud + "/cenr/json"

    # Form the request including setting user-agent
    request = urllib.request.Request(cen_url)
    request.add_header("User-Agent", "Mozilla/5.0")

    # Fetch the response from the URL
    response = urllib.request.urlopen(request)

    # Load the response as JSON
    data = json.loads(response.read())

    # Build IP list
    z_ip_list = buildCenIpList(cloud, excluded_cities, data)

    # Create file and upload to S3
    uploadToS3(z_ip_list, file_name, bucket_name)

    # Return the IP list
    return z_ip_list

def buildCenIpList (cloud, exclusions, json_data):
    # Create IP prefix list
    zscaler_ip_list = []

    # Grab continents
    zscaler_continents = []
    for continent in json_data[cloud]:
        zscaler_continents.append(continent)

    # Enumerate through Zscaler continents
    for i in zscaler_continents:
        for city in json_data[cloud][i]:
            # Confirm that city is not in the exclusion list
            if city not in exclusions:
                # Enumerate though cities in Zscaler data
                for dic_data in json_data[cloud][i][city]:
                    # Check to ensure the data does not have a colon (IPv6) before adding it
                    if ":" not in dic_data.get('range'):
                        # Add range (IP subnet) to output list
                        zscaler_ip_list.append(dic_data.get('range'))

    # Deduplicate list
    deduped_ip_list = list(dict.fromkeys(zscaler_ip_list))
    # Return the IP list
    return deduped_ip_list

def uploadToS3(data, file_name, bucket_name):
    # Open the file & write data
    with open(file_name, 'w') as f:
        # Iterate over each item in the data
        for line in data:
            # Write each item to a new line in the file
            f.write(f"{line}\n")
    
    # Close the file
    f.close()

    # Set object name to the file name
    object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket_name, object_name)
    except ClientError as e:
        #logging.error(e)
        return False
    return True

# If application is being called directly
if __name__ == '__main__':
    # List of excluded cities (Do not need to be an exact match for Zscaler cities)
    excluded_cities = ["city : Moscow III", "city : Beijing", "city : Beijing III", "city : Shanghai", "city : Shanghai II", "city : Tianjin"]

    data = zscaleIpParser("zscalertwo.net", "zscaler_ip_list.txt", excluded_cities, "cb-test-buc")

    #print(data)