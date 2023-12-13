# The purpose of this script is to change Okta usernames to contain @x.com, using the x.com username 
# attribute that is already stored in each Okta profile. It is applied to users in the selected group so that 
# the rebranding can be done gradually.

import requests
import json
import time
import urllib.parse as urlparse
from urllib.parse import urlencode, quote_plus
import os
import asyncio
from okta.client import Client as OktaClient
import okta.models
from datetime import datetime

#rellenamos los atributos de la api de okta
api_key = "x"#os.getenv('API_KEY')
okta_domain = "https://x.okta.com"#os.getenv('OKTA_URL')
headers = {
    'Content-Type': 'application/json',
    'Accept':'application/json',
    'Authorization':'SSWS ' + str(api_key)#os.getenv('API_KEY'))
}

#conseguimos la lista de usuarios y la convertimos a un .json
users_endpoint_uri = okta_domain + '/api/v1/users/00ud9ff0pqDjgXbOs5d7'
usuarios_a_actualizar = requests.get(users_endpoint_uri, headers=headers)
users_list = usuarios_a_actualizar.json()

#creamos las variables para controlar cuantas veces recorremos el bucle y sus condiciones
contadortotal = 0
contadorcambios = 0
contadorerores = 0

# generacion del log file 
if not os.path.exists('Logs'):
   os.makedirs('Logs')
dateTimeObj = datetime.now()
dt_string = dateTimeObj.strftime("%d-%m-%Y_%H.%M.%S")
fileName = "change email domain _ " + str(dt_string) + '.txt'
logFile = open("Logs/" + fileName,"w+") 

print("Execution started")
logFile.write("Changing all users domain email in" + okta_domain + "to a @y domain" +"\n")
logFile.write("-----------------------------------------------------------"+ "\n")

#iniciamos el bucle, se rompera una vez no haya mas usuarios en el link dado
while True:
    for usuario in users_list:

        #filtramos usuarios que no tengan el dominio que deseamos y ademas nos aseguramos de no incluir excepciones (admins)
        if not "@y.com" in usuario['profile']['email'] and usuario['profile']['email'] != 'admin@admin.com':

            #actualizamos el dominio que llamara a la api segun el usuario con el que estemos tratando
            api_url = okta_domain + '/api/v1/users/' + usuario['id'] 

            #sustituimos el dominio del correo a @y.com manteniendo el username de este
            nuevo_email = usuario['profile']['email'].replace(usuario['profile']['email'].split("@")[1], "y.com")
            print (f"Changing {usuario['profile']['email']} too", nuevo_email)
            logFile.write(f"Changing {usuario['profile']['email']} too" + nuevo_email + "\n")

            #creamos un .json con el nuevo mail y actualizamos el usuario con una llamada post a la api
            payload = {
                "profile":{
                    "email": nuevo_email
                    }
            }
            response = requests.post(api_url, json=payload, headers=headers)

            #comprobamos la respuesta de la api y guardamos el resultado
            if response.status_code == 200:
                print(f"Done, email updated too: {nuevo_email}")
                logFile.write(f"Done, email updated too: {nuevo_email}"+ "\n")
                contadorcambios += 1
            else:
                print(f"Error to update user's email {usuario['profile']['firstName']}. Status code: {response.status_code}")
                logFile.write(f"Error to update user's email {usuario['profile']['firstName']}. Status code: {response.status_code}"+ "\n")

                print(response.text)
                contadorerores +=1
        contadortotal += 1

        #evitamos sobrecargar el trafico dando un tiempo entre llamadas
        time.sleep(0.5)

    #nos aseguramos de seguir llamando a la api mientras haya usuarios
    if "next" in usuarios_a_actualizar.links:
        users_endpoint_uri = usuarios_a_actualizar.links["next"]["url"]
        usuarios_a_actualizar = requests.get(users_endpoint_uri, headers=headers)
        group_list = usuarios_a_actualizar.json()
    else:
        break

#acabamos de reportar en el logfile
logFile.write("\n")
logFile.write("EXECUTION FINISHED" + "\n")
logFile.write("Number of groups in total: " + str(contadortotal) + "\n")
logFile.write("Number of groups eliminated due to match: " + str(contadorcambios) + "\n")
logFile.write("Number of groups non eliminated due to unknown error : " + str(contadorerores) + "\n")

print("Execution finished. Please check the log")