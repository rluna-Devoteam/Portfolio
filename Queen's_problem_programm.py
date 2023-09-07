#7/12/2022 codigo creado por Ricard Luna
#Red neuronal que resuelve un problema basado en el juego de ajedrez donde x numero de reinas (x siendo un numero definido en el código o a gusto del usuario, hay código para ambas opciones mas adelante) deben situarse en un tablero de ajedrez tan grande como numero de reinas haya al cuadrado. 
#Estas piezas deberán estar colocadas de tal manera que no se amenazan unas a otras basado en su movimiento en doble cruz que poseen en el juego normal

import numpy as np
import random


def mostrar(agente):                                                             #funcion para imprimir el tablero de reinas como 0 y 1
  
    mapa = np.zeros((len(agente),len(agente)))                                   #primero creamos un mapa de 0
    contador = 0                                                                 #esto nos permite movernos horizontalmente en el mapa segun avanzemos en el agente
  
    for numero in agente:                                                        # recorremos el agente
      
        mapa[numero-1][contador] = 1                                             #y llenamos el mapa de 0 con un 1 segun la posicion que indique el agente en este punto del recorrido
        contador += 1                           
      
    print(mapa, end=" ")
    print(" ")


def iniciapobla(agentes, reinas):                                                #creamos una lista que contendra tantas otras listas como le marquemos en la variable agentes
  
    lista = []
  
    for a in range(agentes):                    
      
        lista.append(iniciagente(reinas))
      
    return lista


def iniciagente(reinas):                                                         #abra tantas reinas en los agentes como le marquemos a la variable reinas
  
    val = range(1,reinas+1)
  
    for a in range(reinas):           
      
        reina = random.sample(val, reinas)                                       #asignar valor aleatorio entre 1 hasta el maximo que le hayamos marcado con la variable reinas
      
    return reina                                                                 #haciendo esto nos estamos asegurando que las reinas no chocaran ni vertical ni horizontalmente
  

def follaragente(agente1, agente2):                                              #combinar dos agentes para crear otros dos nuevos
  
    hijo1 = agente1[0:int(len(agente1)/2)]                                       #usamos solo la mitad de un primer agente para crear un hijo
    hijo2 = agente2[0:int(len(agente2)/2)]
  
    for x in agente2:                                                            #y luego le añadimos la mitad restante del segundo agente para completar
      
        if x not in (hijo1):
          
            hijo1.append(x) 
          
    mutarhijos(hijo1)                                                            #una vez acabado el hijo se muta (en base una probabilidad escrita dentro de la funcion) 
  
    for x in agente1:
      
        if x not in (hijo2):
          
            hijo2.append(x)  
          
    mutarhijos(hijo2)   
  
    return (hijo1, hijo2)


def mutarhijos(hijo):                                                            #segun cierta probabilidad, cambiar la posicion de dos componentes de un agente entre ellos
  
    if random.randint(1,100) <= 50:
      
        pos1 = random.randint(0,len(hijo)-1)
        pos2 = random.randint(0,len(hijo)-1)
      
        while pos1 == pos2:
          
            pos2 = random.randint(0,len(hijo)-1)
          
        hijo[pos1],hijo[pos2]=hijo[pos2],hijo[pos1]   
      
    return hijo 


def ordenarpoblacion(poblacion):                                                 #crear una nueva poblacion con nuevos agentes mas los originales 
  
    nuevapoblacion = poblacion
    random.shuffle(poblacion)                                                    #desordenar poblacion para dar aletoriedad
  
    for agente in range(0,(len(poblacion)-2),2):  
      
        newgen1, newgen2 = follaragente(poblacion[agente],poblacion[agente+1])   #creamos los dos nuevos hijos con la funcion
        nuevapoblacion.append(newgen1)                                           #y los añadimos a la nueva poblacion extendida
        nuevapoblacion.append(newgen2)
      
    return nuevapoblacion


def fitnesspoblacion(poblacion):                                                 #recorrer poblacion para poder comprobar el fitness de cada agente
  
    fitness = []                                                                 #creamos una lista que contendra el fitness de cada agente
  
    for x in range(len(poblacion)):
      
        fitness.append(fitnessagente(poblacion[x]))                              #y se ira añadiendo el resultado de cada uno segun la funcion
      
    return fitness


def fitnessagente(agente):                                                       #recorrer agente para comprobar si hay otras reinas en sus diagonales 
  
    col = 0                                                                      #variable manual para movernos por las columnas                  
    lin = 0                                                                      #variable manual para movernos por las lineas
    contador = 0                                                                 #variable para guardar si se tocan en diagonal las reinas
  
    for q1 in agente:                                                   
      
        col = 0   
      
        for q2 in agente:
          
            if abs(q1 - q2) == abs(lin - col):                                   #con las variables manuales podemos comprobar si de forma "diagonal" nuestra reina tiene el mismo numero que otra reina
              
                contador += 1                                                    #sumamos si hay una reina en nuestra diagonal   
              
            col += 1                                                             #saltamos columna dentro del bucle
          
        lin += 1                                                                 #saltamos linea dentro del bucle
      
    #este bucle tiene el problema que las reinas se detectaran una a otra en caso de chocar, por ello al devolver el resultado se debera restar tanto como tantas reinas haya 
    return contador - len(agente)                                                #a mayor el contador, con mas reinas esta tocando en sus diagonales


def segregacion_racial(poblacion, fitness):                                      #ordenamos la poblacion segun su fitness (de menor/mejor a mayor/peor)
  
    nuevapob = []
  
    for x,agente in sorted(zip(fitness,poblacion)):
      
        nuevapob.append(agente)
      
    return nuevapob


def escoger(poblacion, reinas, agentes):                                         #recortamos la poblacion segun su fitness (porcentaje de buenas y de malas)
  
    nuevapob = [[0 for x in range(reinas)] for y in range(agentes)]
    bien = 0.8
    mal = 0.2                                                                    #segun pruebas, a pesar de la teoria, usar el 100% de buenas a dado siempre el mejor resultado
    gentedebien = agentes*bien
    gentedemal = agentes*mal
    nuevapob[0:int(gentedebien)] = poblacion[0:int(gentedebien)]
    nuevapob[int(gentedebien):int(gentedebien)+int(gentedemal)] = poblacion[len(poblacion)-int(gentedemal):len(poblacion)]
  
    return nuevapob

#programa
#random.seed(20)                                                                 #definir la aletoriedad para poder comprobar resultados

reinas = 100                                                                     #cantidad de reinas dentro del tablero(al mimso tiempo tamaño del tablero)
agentes = 100                                                                    #cantidad de agentes dentro de la poblacion (a mas agentes menos epoch requerira)
#//int(input("Define la cantidad de reinas (num): "))                            #posibilidad de hacer tan grande el problema como marque el input
#//int(input("Define la cantidad de agentes (num): "))                        

generacion = iniciapobla(agentes, reinas)                                       #creamos la primera poblacion

gen = 0                                                                         #variable para controlar la cantidad de epoch que hace el programa
print (fitnessagente(generacion[0]))                                            
while fitnessagente(generacion[0]) != 0:                                        #comprobamos su fitness e inicializamos el bucle del programa en base a ello
    generacionimprov = ordenarpoblacion(generacion)                             #añadimos mas agentes a la poblacion (mutacion de los hijos se incluye en el proceso)
    fitpobla = fitnesspoblacion(generacionimprov)                               #comprobamos el fitness de esta nueva poblacion
    generacionperf = segregacion_racial(generacionimprov, fitpobla)             #ordenamos la poblacion segun su fitness para facilitar el siguiente paso
    generacion = escoger(generacionperf, reinas, agentes)                       #recortamos la poblacion al tamaño original (variable agentes del principio del programa)
    print("generacion: ",gen)
    print("mejor fitness: ", fitnessagente(generacion[0]))
    if gen == 10000:                                                            #control de errores (es viable suprimirlo)
        print("Too much gen")
        break
    gen+=1
print("mejor agente: ")             
mostrar(generacion[0])                                                          #una vez acabado el programa imprimimos el agente que ha logrado el fitness 0 (dado la funcion segregacion_racial sera siempre el primero)
