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
from std_msgs.msg import String, Int32MultiArray

postConditionDetect = None

identify=-1#modicar mediante mensajes al lanzar el nuevo nodo
idComportamiento = 1
reejecutar=True
ejecutando=False
permanent = {}
enablig = {}
ordering = {}
nivelActivacion=0
activate=False
estado=1

#se deben de mandar mensajes continuamente si se ejecuta tanto como si no a los motores
def actuar():
    global activate
    print "activo ",activate
    global motores
    msg = Int32MultiArray()
    if cumplePrecondiciones () and not activate and nivelActivacion>0:
        # Aca iria la operacion de wander.
        
        msg.data = [5,5] 	 
        motores.publish(msg)     
        
        rospy.loginfo("Ejecutando localizar...")
        #rospy.loginfo( nivelActivacion)
        ejecutando=True
    else: 
	#rospy.loginfo("Se detuvo localizar...")
	ejecutando=False
	msg.data = [0,0] 	 
        motores.publish(msg)

def verificarPoscondicionesSensores(data):
    global activate
    activate=False
    if data.data[0] == 0 or data.data[0] == 2:#para que sea de permanencia hay que revisar
        print "se cumple postcondicion localizar"
	activate=True
    elif cumplePrecondiciones():#cumple precondiciones y no cumple postcondicion	
	#actuar()
	print "no se cumple postcondicion",activate
    return activate

def atenderSensores(data):
    #se verifican las condiciones en base a los sensores
    verificarPoscondicionesSensores(data)

    print "aprender localizar"
    global postConditionDetect
    global preConditionDetect
    global estado
    msg = Int32MultiArray()

    
    valorEncendido=0
    if verificarPoscondicionesSensores(data):
        print "se cumple postcondicion localizar"
        valorEncendido=1            
    else:#redundante solo para ver que paso
	#rospy.loginfo("se apago postcondicion localizar")
	valorEncendido=0       
    print "call localizar"
    #rospy.loginfo(estado)
    if estado ==1:#aprender	
	msg.data = [idComportamiento,valorEncendido]#se envia el id del comportamiento cuando se aprende
	postConditionDetect.publish(msg)
    elif estado ==2:#ejecutar
	msg.data = [identify,valorEncendido]   #cuando se ejecuta se envia el id del nodo
	#actuar()
	#rospy.loginfo("localizar ",valorEncendido)
	preConditionDetect.publish(msg)
    
def setEstado(data):    
    global estado
    global activate
    estado=data.data[0]
    activate = False
    if estado==2:
	#actuar()
        print "estado ", estado
    rospy.loginfo("estado"+str(estado))

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


def nivel (data):
  #  rospy.loginfo("Entro en nivel")
    msg = Int32MultiArray()
    global nivelActivacion
    if data.data[1] == identify:
	nivelActivacion=nivelActivacion+1
        #rospy.loginfo("me llego nivel localizar")
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
       
        #si no cumple condiciones el nivel de activacion se hace 0 para estar listo cuando se 
        #reciba otra senal de activacion 
        if not cumplePrecondiciones: 
            nivelActivacion=0
        actuar()





def evaluarPrecondicion(data):#invocado en etapa de ejecucion cuando llega una postcondicion
    print "entro en ejecutar localizar"
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

    #global nivelActivacion
    #nivelActivacion=0

  #  if not skip:
#	actuar()

 


if __name__ == '__main__':
    print "iniciando localizar"  

    rospy.init_node('localizar', anonymous=True)

    
    #global identify
    identify=int(rospy.myargv(argv=sys.argv)[1])
    rospy.loginfo("identificador localizar "+str(identify))

    motores = rospy.Publisher('topicoActuarMotores', Int32MultiArray, queue_size=10)
    postConditionDetect = rospy.Publisher('postConditionDetect', Int32MultiArray, queue_size=10) #usado para aprender
    preConditionDetect = rospy.Publisher('preConditionDetect', Int32MultiArray, queue_size=10) #usado para ejecutar
    rospy.Subscriber("input", Int32MultiArray, atenderSensores)
    rospy.Subscriber("preConditionDetect", Int32MultiArray, evaluarPrecondicion)
    rospy.Subscriber("preConditionsSetting", Int32MultiArray, setting)	    
    rospy.Subscriber("topicoEstado", Int32MultiArray, setEstado)
    rospy.Subscriber("topicoNivel", Int32MultiArray, nivel)
    nivel = rospy.Publisher('topicoNivel', Int32MultiArray, queue_size=10)

    estado = 1
    rospy.spin()
