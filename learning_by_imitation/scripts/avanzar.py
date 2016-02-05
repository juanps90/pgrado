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
import Const

import sys
import rospy
from std_msgs.msg import String, Int32MultiArray, Float64MultiArray
from random import randint


postConditionDetect = None

identify=-1#modicar mediante mensajes al lanzar el nuevo nodo
idComportamiento = 2
reejecutar=True
ejecutando=False
permanent = {}
enablig = {}
ordering = {}
nivelActivacion=0
estado=1

pathPosibles=[]

#se deben de mandar mensajes continuamente si se ejecuta tanto como si no a los motores
def actuar():
    global motores
    msg = Float64MultiArray()
    if cumplePrecondiciones () and nivelActivacion>0:
        # Aca iria la operacion de wander.  
        azar=randint(0,9)   
        msg.data = [identify,0,azar] 	 
        motores.publish(msg)             
        rospy.loginfo("Ejecutando avanzar...")
        #rospy.loginfo( nivelActivacion) 
        msg.data = [identify,identify] #por si necesito otro parametro        
        nodoEjecutando.publish(msg) 
    else: 
	rospy.loginfo("Se detuvo avanzar...") 
	msg.data = [identify,0,0] 	 
        motores.publish(msg)

def verificarPoscondicionesSensores(data):
    activate=False
    if  data.data == Const.SENSOR_COLOR_DETECT_BLACK:
        print "se cumple postcondicion avanzar"
	activate=True
    elif cumplePrecondiciones():#cumple precondiciones y no cumple postcondicion
	#actuar()C
	print "no se cumple postcondicion"
    return activate

def processSensorLineDetectedColorData(data):
    #se verifican las condiciones en base a los sensores
    #verificarPoscondicionesSensores(data)

    print "aprender avanzar"
    global postConditionDetect
    global preConditionDetect
    global estado
    msg = Int32MultiArray()

    
    valorEncendido=0
    if verificarPoscondicionesSensores(data):
        print "se cumple postcondicion avanzar"
        valorEncendido=1            
    else:#redundante solo para ver que paso
	#rospy.loginfo("se apago postcondicion avanzar")
	valorEncendido=0       
    print "call avanzar"
    #rospy.loginfo(estado)
    if estado ==1 and identify==-1:#aprender el -1 es para que contesten nodos lanzados para aprender	
	msg.data = [idComportamiento,valorEncendido]#se envia el id del comportamiento cuando se aprende
	postConditionDetect.publish(msg)
    elif estado ==2:#ejecutar
	msg.data = [identify,valorEncendido]   #cuando se ejecuta se envia el id del nodo
	actuar()
	#rospy.loginfo("avanzar ",valorEncendido)
	preConditionDetect.publish(msg)
    



    
    
def setEstado(data):    
    global estado
    estado=data.data[0]
    if estado==3:
	#se detienen los motores estamos en estado come 
	msg = Int32MultiArray() 
	msg.data = [identify,0,0] 	 
        motores.publish(msg) 
    rospy.loginfo("estado"+str(estado))
    

#cuando un nodo ejecuta avisa que lo hace hasta que un nuevo comportamiento no ejecute no avisa
#supongamos que el comportamiento habilante se esta ejecutandode repente el comportamiento que es habilitado recibe de sensore
#la senal que esperaba pasa a estar activo avisa de este hecho...luego cuando se pregunte por el enlace de habilitacion se preguntara
#si esta ejecutando y no importaria ya si el habilitante esta o no activo  
def atenderNodoEjecutando(data):
    if  data.data[0] == identify:
        ejecutando=True
    else:    
        ejecutando=False



def cumplePrecondiciones():
    #si esta ejecutando no se evalua enabling
    salida = evaluation(permanent.values()) and (ejecutando or evaluation(enablig.values()) ) and evaluation(ordering.values())
    print "cumplePrecondiciones ",salida
    return salida

def evaluation(l):
    result = True
    for it in l:
        result = result and it
        if not result:
            break
    return result

 



def setting(data):
    print "entro en setting avanzar "
    
    # data.data[0] = fromCompID, data.data[1] = toCompID, data.data[2] = linkType. linkType puede ser permantente(0), de orden(1) o de habilitacion(2)
    if data.data[1] == identify:
        print "es mi id"
        if data.data[2] == 2:
            permanent[data.data[0]] = False
	    print "permanente "
            print len(permanent)
        elif data.data[2] == 1:
            print "habilitacion "
            enablig[data.data[0]] = False
        elif data.data[2] == 0:
            print "orden "
            ordering[data.data[0]] = False

'''
    global reejecutar
    if data.data[0] == identify and data.data[2] == 2:#soy origen de un enlace permamente
	reejecutar = True
    print "reejecutar ",reejecutar
'''


def atenderCaminos(data):
    global pathPosibles
    #si es mi id agrego a la lista de un camino el nuevo nodo
    if data.data[0] == identify: 
        lista=list(data.data)
        indice=data.data[1]
        #se borran los primeros datos y queda la lista con el path
        del lista[0]
        del lista[0]
        pathPosibles[indice]=lista
        #print lista
    
    

def nivel (data):
  #  rospy.loginfo("Entro en nivel")
    msg = Int32MultiArray()
    global nivelActivacion
    #inicializar el nivel 
    if data.data[1] == -1:
        nivelActivacion=0
        rospy.loginfo("me llego nivel avanzar a 0")   
    elif data.data[1] == identify:
	nivelActivacion=nivelActivacion+1
        rospy.loginfo("me llego nivel avanzar")
        msg = Int32MultiArray()
	for p in permanent:
	    if not permanent[p] :
	        msg.data = [identify, p]#manda para atras el nivel
                nivel.publish(msg)	
	for e in enablig:
	    if not enablig[e] and not ejecutando:
		msg.data = [identify, e]#manda para atras el nivel
                nivel.publish(msg)
	for o in ordering:
	    if not ordering[o]:
		msg.data = [identify, o]#manda para atras el nivel
                nivel.publish(msg)





def evaluarPrecondicion(data):#invocado en etapa de ejecucion cuando llega una postcondicion
    print "entro en ejecutar avanzar"
    skip = False
    comportamiento=data.data[0] 
    postcondicion=data.data[1]

    if permanent.has_key(comportamiento):
        permanent[comportamiento] = postcondicion == 1
	if permanent[comportamiento]:
            print "es permanente"
	else:
	    print "salio de permanente"
    elif enablig.has_key(comportamiento):
        enablig[comportamiento] = postcondicion == 1
        if enablig[comportamiento] or ejecutando:#si se esta ejecutando no importa que se apague
 	    print "esta habilitado"	
	else:
	    print "se inhabilito"
    elif ordering.has_key(comportamiento):
        ordering[comportamiento] = ordering[comportamiento] or (postcondicion == 1)
        print "es de orden"
    else:
        skip = True

if __name__ == '__main__':
    print "iniciando avanzar"  

    rospy.init_node('avanzar', anonymous=True)

    
    #global identify
    identify=int(rospy.myargv(argv=sys.argv)[1])
    rospy.loginfo("identificador avanzar "+str(identify))

    motores = rospy.Publisher('topicoActuarMotores', Float64MultiArray, queue_size=10)
    postConditionDetect = rospy.Publisher('postConditionDetect', Int32MultiArray, queue_size=10) #usado para aprender
    preConditionDetect = rospy.Publisher('preConditionDetect', Int32MultiArray, queue_size=10) #usado para ejecutar
#    rospy.Subscriber("input", Int32MultiArray, atenderSensores)


    rospy.Subscriber("sensorLineDetectedColorData", String, processSensorLineDetectedColorData)
    
    
    rospy.Subscriber("preConditionDetect", Int32MultiArray, evaluarPrecondicion)
    rospy.Subscriber("preConditionsSetting", Int32MultiArray, setting)	    
    rospy.Subscriber("topicoEstado", Int32MultiArray, setEstado)
    rospy.Subscriber("topicoNivel", Int32MultiArray, nivel)
    rospy.Subscriber("topicoCaminos", Int32MultiArray, atenderCaminos)
    nivel = rospy.Publisher('topicoNivel', Int32MultiArray, queue_size=10)
    nodoEjecutando=rospy.Publisher('topicoNodoEjecutando', Int32MultiArray, queue_size=10)
    rospy.Subscriber("topicoNodoEjecutando", Int32MultiArray, atenderNodoEjecutando)
 
    rospy.spin()
