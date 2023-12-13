'''Autor: Borja'''
import json
import requests
import os
import csv
from datetime import datetime

# The purpose of this script is to change Okta usernames to contain @fluidra.com, using the fluidra.com username 
# attribute that is already stored in each Okta profile. It is applied to users in the selected group so that 
# the rebranding can be done gradually.

api_key = 'x'
okta_domain = 'https://x.okta.com'

# ID of the okta group from which users will be updated
org_group = ' '

headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
           'Authorization': 'SSWS ' + api_key}

# Global counters for the execution log summary
cont_total = 0
cont_correct = 0
cont_incorrect = 0
cont_ignored = 0
cont_deactivated = 0

# A given user is updated with their correspondant fluidra.com username. 
# For that, a HTTP post request is sent to the endpoint below
def update_user(id, fluidraUsername):
    global cont_correct
    global cont_incorrect

    okta_profile = {"profile": {
                                "login": fluidraUsername
                                }
                    }

    endpoint = '/api/v1/users/' + id
    endpoint_uri = okta_domain + endpoint

    # The HTTP post request is commented to avoid unintentional executions
    # response = requests.post(endpoint_uri, json=okta_profile, headers=headers)
    #
    #status = response.status_code
    #
    #if status == 200:
    #    cont_correct += 1
    #    logFile.write("User updated correctly" + "\n")
    #else:
    #    cont_incorrect += 1
    #    logFile.write("Unexpected error. Moving to the next user" + "\n")
    
    logFile.write("\n")

# A list of users is received and for each user, information about its profile is obtained. 
# Depending on the value of different attributes, the user will be updated or not.
def process_users(users):
    global cont_total
    global cont_ignored
    global cont_deactivated

    for user in users:
            id = user['id']
            username = user['profile']['login']
            status = user['status']

            logFile.write("User " + username + " being processed" + "\n")

            if (status != "DEPROVISIONED"):

                if not 'fluidraUsername' in user['profile']:
                    fluidraUsername = ""
                else:
                    fluidraUsername = user['profile']['fluidraUsername']

                cont_total += 1
                print(str(cont_total) + " users processed")

                if fluidraUsername == "":
                    cont_ignored += 1
                    logFile.write("User does not have a Fluidra username assigned. Moving to the next user" + "\n")
                    logFile.write("\n")
                else:
                    logFile.write("Login username should change to: " + fluidraUsername + "\n")
                    update_user(id, fluidraUsername)
            else:
                cont_deactivated += 1
                logFile.write("User is deactivated. Moving to the next user" + "\n")
                logFile.write("\n")

# A HTTP get request is done to the endpoint below to get all the users from the selected group. 
# Only 200 users are shown in the same page. It is necessary to loop through the "links" received 
# in the request response to see the following 200 users
def main():

    endpoint = '/api/v1/groups/' + org_group + '/users'
    endpoint_uri = okta_domain + endpoint

    response = requests.get(endpoint_uri, headers=headers)
    
    status = response.status_code
    users = response.json()
    links = response.links

    print(status)

    if status == 200:
        process_users(users)

    while 'next' in links and 'url' in links['next']:
        next_url = links['next']['url']

        response = requests.get(next_url, headers=headers)

        status = response.status_code
        users = response.json()
        links = response.links

        if status == 200:
            process_users(users)

# Execution and generation of log file
if __name__ == "__main__":
    print("Execution started")

    if not os.path.exists('Logs'):
        os.makedirs('Logs')
    dateTimeObj = datetime.now()
    dt_string = dateTimeObj.strftime("%d-%m-%Y_%H.%M.%S")
    fileName = "rebrandingUsername (2) _ " + str(dt_string) + '.txt'
    logFile = open("Logs/" + fileName,"w+") 

    logFile.write("STARTING ALL PROFILES UPDATE WITH FLUIDRA USERNAME AS LOGIN"+ "\n")
    logFile.write("-----------------------------------------------------------"+ "\n")
    logFile.write("\n")

    main()

    logFile.write("EXECUTION FINISHED" + "\n")
    logFile.write("Number of users processed: " + str(cont_total) + "\n")
    logFile.write("Number of users updated correctly: " + str(cont_correct) + "\n")
    logFile.write("Number of users skipped due to errors: " + str(cont_incorrect) + "\n")
    logFile.write("Number of users without valid fluidra username value: " + str(cont_ignored) + "\n")
    logFile.write("Number of deactivated users ignored: " + str(cont_deactivated) + "\n")
    print("Execution finished. Please check the log")
