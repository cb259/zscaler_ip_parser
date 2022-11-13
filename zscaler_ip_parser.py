import urllib.request
import json
import os
import boto3

# Pseudo code
# X Download json IP list: https://api.config.zscaler.com/zscalertwo.net/cenr/json
# X Exclude locations/City: Moscow III, Beijing, Beijing III, Shanghai, Shanghai II, Tianjin
# X Scrape IP/range for remaining cities
# X Remove IPv6, if required
# X Pass cloud value
# X Pass URL or derrive URL from cloud value
# X Format output in Palo format
# X Save/export file
# - Global configs: File name, cloud, bucket name, excluded cities, 
# - Determine how to run (Function)
# - Determine run frequency: Interval based
# - Input validation
# - Extend to PAC

def zscaleIpParser (cloud):
     # URL to be targeted
    url = "https://api.config.zscaler.com/" + cloud + "/cenr/json"

    # Form the request including setting user-agent
    request = urllib.request.Request(url)
    request.add_header("User-Agent", "Mozilla/5.0")

    # Fetch the response from the URL
    response = urllib.request.urlopen(request)

    # Load the response as JSON
    data = json.loads(response.read())

    # List of excluded cities (Do not need to be an exact match for Zscaler cities)
    excluded_cities = ["city : Moscow III", "city : Beijing", "city : Beijing III", "city : Shanghai", "city : Shanghai II", "city : Tianjin"]

    # Build IP list
    z_ip_list = buildIpList(excluded_cities, data)

    # Create file and upload to S3
    uploadToS3(z_ip_list, "zscaler_ip_list.txt", "cb-test-buc")

    # Return the IP list
    return z_ip_list

def buildIpList (exclusions, json_data):
    # Create IP prefix list
    zscaler_ip_list = []

    # Grab continents
    zscaler_continents = []
    for continent in json_data["zscalertwo.net"]:
        zscaler_continents.append(continent)

    # Enumerate through Zscaler continents
    for i in zscaler_continents:
        for city in json_data["zscalertwo.net"][i]:
            # Confirm that city is not in the exclusion list
            if city not in exclusions:
                # Enumerate though cities in Zscaler data
                for dic_data in json_data["zscalertwo.net"][i][city]:
                    # Check to ensure the data does not have a colon (IPv6) before adding it
                    if ":" not in dic_data.get('range'):
                        # Add range (IP subnet) to output list
                        zscaler_ip_list.append(dic_data.get('range'))

    # Return the IP list
    return zscaler_ip_list

def uploadToS3(data, file_name, bucket_name):
     # Open the file
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

    # Remove local file
    if os.path.exists(file_name):
        os.remove(file_name)

# If application is being called directly
if __name__ == '__main__':
    data = zscaleIpParser("zscalertwo.net")

    #print(data)