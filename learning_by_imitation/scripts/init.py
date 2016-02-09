#!/usr/bin/env python


import os 
import logging 
import socket 
import sys 
import xmlrpclib 
import roslib.names  
import roslib.network  
import rospkg
import roslaunch.core
import roslaunch.remote

import sys
import rospy
from std_msgs.msg import Int32MultiArray, Float64MultiArray
from random import randint


postConditionDetect = None

identify=-1#modicar mediante mensajes al lanzar el nuevo nodo
idComportamiento = 0
reejecutar=True
ejecutando=False
permanent = {}
enablig = {}
ordering = {}
nivelActivacion=0
estado=1
nodoEnEjecucion=-1
nodoEnEjecucionAnterior=-2
caminos=[]
dicPostCondicion={}#diccionario que se usa para evaluar un cambio de postcondicion de apagado a prendido y viceversa


    
def setEstado(data):    
    global estado
    estado=data.data[0]
    if estado==3:
	#se detienen los motores estamos en estado come 
	msg = Int32MultiArray() 
	msg.data = [identify,0,0] 	 
        motores.publish(msg) 
    elif estado==2:
        arranqueNivel()
    rospy.loginfo("estado"+str(estado))




#cuando un nodo ejecuta avisa que lo hace hasta que un nuevo comportamiento no ejecute no avisa
#supongamos que el comportamiento habilante se esta ejecutandode repente el comportamiento que es habilitado recibe de sensore
#la senal que esperaba pasa a estar activo avisa de este hecho...luego cuando se pregunte por el enlace de habilitacion se preguntara
#si esta ejecutando y no importaria ya si el habilitante esta o no activo  
def atenderNodoEjecutando(data):
    global nodoEnEjecucion
    nodoEnEjecucion=data.data[0]
    rospy.loginfo("atenderNodoEjecutando "+str(nodoEnEjecucion))    
    '''
    if  data.data[0] == identify:
        ejecutando=True
    else:    
        ejecutando=False
    '''  
        
        
#no lo uso
def cumplePrecondiciones():
    salida = evaluation(ordering.values()) 
    print "cumplePrecondiciones ",salida
    return salida

def evaluation(l):
    result = True
    for it in l:
        result = result and l[it]
        if not result:
            break
    return result

 



def setting(data):
    print "entro en setting localizar "
    
    # data.data[0] = fromCompID, data.data[1] = toCompID, data.data[2] = linkType. linkType puede ser permantente(0), de orden(1) o de habilitacion(2)
    if data.data[1] == identify and data.data[2] == 0:       
        ordering[data.data[0]] = False
        rospy.loginfo("init entro orden "+str(ordering)+str(data.data)) 

'''
    global reejecutar
    if data.data[0] == identify and data.data[2] == 2:#soy origen de un enlace permamente
	reejecutar = True
    print "reejecutar ",reejecutar
'''

    
def atenderCaminos(data):
    global caminos
    #si es mi id agrego la lista de caminos camino el nodo
    if data.data[0] == identify:
        #elimina de la lista el dato del id
        lista=list(data.data)        
        #print lista
        del lista[0]
        
        caminos= separarCaminos(lista)
        print caminos

def separarCaminos(caminos):
    salida = []
    inicio=0
    fin=0
    guardaSeparacion=-10
    while inicio< len (caminos):    
        fin=caminos.index(guardaSeparacion,inicio)
        #print fin
        tramo=caminos[inicio:fin]
        #print tramo
        salida.append(tramo) 
        inicio=fin+1    
    return salida  



def arranqueNivel():
  # print "nivel de activacion init"
    global nivel
    global nodoEnEjecucion
    global nodoEnEjecucionAnterior
    global ordering
    msg = Int32MultiArray()
        
    rospy.loginfo("nodo en ejecucion "+str(nodoEnEjecucion))    
    
    #se verifica que el comportamiento cambio
    
    finalizo = True
    rospy.loginfo("order init"+str(ordering))   
    for it in ordering:   
        finalizo = finalizo and ordering[it]
        if not finalizo:
            break
    '''
    if finalizo:
        msg = Int32MultiArray()   
        msg.data = [identify,identify]    
        nodoEjecutando.publish(msg) 
        nodoEjecutando
    '''
    


    '''
    rospy.loginfo("finalizo "+str(finalizo))   
    if nodoEnEjecucionAnterior == nodoEnEjecucion and not finalizo:
        return
    else:
        nodoEnEjecucionAnterior=nodoEnEjecucion 

    '''

     
     
            
    msg.data = [identify, -1]#manda para atras el nivel inicial
    nivel.publish(msg)        
    
    
    
    #CAMBIAR
    
    #se recorre la lista de predecesores solo se verifican para cada nodo final si alguno se cumple no se manda
    #para atras, si ninguno se cumple manda a todos esos nodos finales
    listaNodosAEnviarNivel=[]
    for c in caminos:
        ultimoNodo=c[len(c)-1] #ultimo nodo del camino previo
        #se verifica a cual de los link pertenece
        rospy.loginfo("ultimo nodo: "+str(ultimoNodo) + " "+ str(ordering))
        if ordering.has_key(ultimoNodo):
            rospy.loginfo("enabling init : "+str(ordering[ultimoNodo]))
            if not ordering[ultimoNodo]: 
                if not ultimoNodo in listaNodosAEnviarNivel:
                    listaNodosAEnviarNivel.append(ultimoNodo) 
            else:
                listaNodosAEnviarNivel=[]
                break         
        
    rospy.loginfo("largo listdenodos: "+ str (len(listaNodosAEnviarNivel)))     
    for l in listaNodosAEnviarNivel:
        msg.data = [identify, l]#manda para atras el nivel el segundo valor se usa solo para reiniciar lo hace init
        nivel.publish(msg)

    if len(listaNodosAEnviarNivel)==0:
        rospy.loginfo("termino el ciclo")
        


#invocado en etapa de ejecucion cuando llega una postcondicion de un nodo a ver si corresponde
#a una precondicion del nodo actual 
def evaluarPrecondicion(data):
    global ordering
    global dicPostCondicion
    skip = False
    nodo=data.data[0] 
    postcondicion=data.data[1]

    if ordering.has_key(nodo):
        ordering[nodo] = ordering[nodo] or (postcondicion == 1)  
       

    #se detecta cumplimiento de una postcondicion...entonces el init manda su nivel de activacion para
    #atras...si un nodo recibe y puede ejecutar ejecuta, si no puede manda
    #su nivel para atras y pone su nivel en 0 (no es tan asi VERIFICAR)
    #if postcondicion:
    

    #si hay un cambio en la postcondicion de algun nodo se lanza nivel
    activarNivel=False
    if not dicPostCondicion.has_key(nodo):
        dicPostCondicion[nodo]=postcondicion
        activarNivel=True

    if dicPostCondicion[nodo]!=postcondicion:
        dicPostCondicion[nodo]=postcondicion 
        activarNivel=True


    if activarNivel:
        arranqueNivel()

    rospy.loginfo("activarNivel "+str(activarNivel))


if __name__ == '__main__':
    print "iniciando localizar"  

    rospy.init_node('localizar', anonymous=True)

    
    #global identify
    identify=int(rospy.myargv(argv=sys.argv)[1])
    rospy.loginfo("identificador init "+str(identify))

    motores = rospy.Publisher('topicoActuarMotores', Float64MultiArray, queue_size=10)
    postConditionDetect = rospy.Publisher('postConditionDetect', Int32MultiArray, queue_size=10) #usado para aprender
    preConditionDetect = rospy.Publisher('preConditionDetect', Int32MultiArray, queue_size=10) #usado para ejecutar
    #rospy.Subscriber("input", Int32MultiArray, atenderSensores)
    rospy.Subscriber("preConditionDetect", Int32MultiArray, evaluarPrecondicion)
    rospy.Subscriber("preConditionsSetting", Int32MultiArray, setting)	    
    rospy.Subscriber("topicoEstado", Int32MultiArray, setEstado)
    #rospy.Subscriber("topicoNivel", Int32MultiArray, nivel)
    nivel = rospy.Publisher('topicoNivel', Int32MultiArray, queue_size=10)
    nodoEjecutando=rospy.Publisher('topicoNodoEjecutando', Int32MultiArray, queue_size=10)
    rospy.Subscriber("topicoNodoEjecutando", Int32MultiArray, atenderNodoEjecutando)
    rospy.Subscriber("topicoCaminos", Int32MultiArray, atenderCaminos)
   
    rospy.spin()
    
