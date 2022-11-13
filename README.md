# Zscaler IP Parser

## Description
This utility can be used to pull the IP addresses associated with a Zscaler cloud, format it into a file and upload that file to an S3 bucket.

## Usage
The intent is that is script would be run a regular interval to keep the bucket file up to date. The bucket file can then be consumed by firewalls or other security devices/software to be part of a programatic process to determine to which destinations traffic should be allowed.

## Service Scope
[*] Currently this utility is scoped to Zscaler Internet Access (ZIA). Specifically the cloud enforcement nodes.