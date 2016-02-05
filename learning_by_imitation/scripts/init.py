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
from std_msgs.msg import String, Int32MultiArray, Float64MultiArray
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






    
def setEstado(data):    
    global estado
    estado=data.data[0]
    if estado==3:
	#se detienen los motores estamos en estado come 
	msg = Float64MultiArray() 
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
    if  data.data[0] == identify:
        ejecutando=True
    else:    
        ejecutando=False
        
        
        

def cumplePrecondiciones():
    salida = evaluation(permanent.values()) and (ejecutando or evaluation(enablig.values()) ) and evaluation(ordering.values()) #si esta ejecutando no se evalua enabling
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
    print "entro en setting localizar "
    
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


def arranqueNivel():
  # print "nivel de activacion init"
    global nivel
    msg = Int32MultiArray()
        
    fin=True
    #para todos los nodos envia el valor para que se inicie el nivel
    for o in ordering:
        msg.data = [identify, -1]#manda para atras el nivel inicial
        nivel.publish(msg)        
    
    for o in ordering:
        #en caso que la relacion de orden aun no se cumplio
        if not ordering[o]:
            msg.data = [identify, o]#manda para atras el nivel
            nivel.publish(msg)
            fin=False
    #if fin:
        #rospy.loginfo("termino el ciclo")




def evaluarPrecondicion(data):#invocado en etapa de ejecucion cuando llega una postcondicion    
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
       # print "es de orden"
    else:
        skip = True
        
    #print "nodo llego postcondicion de tipo orden", ordering

    #se detecta cumplimiento de una postcondicio...entonces el init manda su nivel de activacion para
    #atras...si un nodo recibe y puede ejecutar ejecuta, si no puede manda
    #su nivel para atras y pone su nivel en 0 
    if postcondicion:
        arranqueNivel()

 


if __name__ == '__main__':
    print "iniciando init"  

    rospy.init_node('ini', anonymous=True)

    
    #global identify
    identify=int(rospy.myargv(argv=sys.argv)[1])
    rospy.loginfo("identificador localizar "+str(identify))

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

   
    rospy.spin()


