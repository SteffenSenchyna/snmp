# SNMP Server
This Python script implements a Simple Network Management Protocol (SNMP) trap receiver that can handle SNMP traps sent by various network devices. The script uses pysnmp library to listen for SNMP traps on a specified IP address and port. It also integrates with Discord and MongoDB to send notifications and store the received SNMP traps. This server is part of a larger project, which includes several microservices and other components that collectively provide tools to manage on-premise networking devices. The view the cluster architecture and the CI/CD pipeline for deployment, refer to the [Cluster Manifest Repository](https://github.com/SteffenSenchyna/cluster-chart).

## Prerequisites
* Python 3.7 or later
* A MongoDB database
* A Discord channel 

## Getting Started
To run this application, follow these steps:

* Clone this repository
* Install the required packages using `pip install -r requirements.txt`
* Run the application using `python server.py`
* The application will listen on port 514 for syslog messages

## MongoDB Storage
Each incoming SNMP trap is stored in its own collection within the snmp database, the trap data is stored in the following format:
```
{
    "system_up_time_instance": <system_up_time_instance>,
    "source_address": <source_ip_address>,
    "module_id": <trap_oid>,
    "message": <trap_message>,
}
```

## Discord Alerting
When a trap message is received an alert will be sent to the Discord channel specified in the DISCORDURL environment variable. The alert will include the device IP address, OID, and the message.

## Environmental Variables
Create a .env file in the root directory of the project and set the following environment variables:
```
MONGOURL=<MongoDB URL>
DISCORDURL=https://discord.com/api/webhooks/<your_webhook_url>
```
