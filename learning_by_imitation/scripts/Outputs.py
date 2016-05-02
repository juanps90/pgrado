#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package Outputs
# @brief Modulo usado para enviar comandos a los actuadores en V-Rep.
# @details Al publicar en los tópicos "/vrep/leftMotorVelocity", "/vrep/rightMotorVelocity" y "/vrep/actuatorLed1Topic"
# podemos controlar el motor iquierdo, el motor derecho y la luz respectivamente. Para manejar la velocidad de los motores
# basta con publicar un valor de tipo Float64 en los tópicos mencionados. En el caso de la luz se publica 
# el entero 0 para apagarla y 1 para encenderla.
# @authors Gustavo Irigoyen
# @authors Juan Pablo Sierra
# @authors Juan Eliel Ibarra
# @authors Gustavo Evovlockas
# @date Abril 2016
#

import rospy
from std_msgs.msg import Int32MultiArray, Float64, Float64MultiArray, Int32, String
import Const

identify=0
NodoActivo = -1

##
# La funcion atiende los mensajes publicados en el topico "topic_engineAccess". En 
# este tópico se pulica un array de tipo Int32MultiArray , donde la posición 0 contiene el id del nodo,
# la posición 1 contiene el nodo ejecutable y la posición 2 el id del motor.
# Por este medio los nodos mandan solicitudes de para poder usar los motores.
# @param data Datos publicados en el tópico "topic_engineAccess".
# 
def atendersolicitarOLiberarMotores(data):
    
    global NodoActivo    
    nodo=data.data[0] 
    nodoEjecutable=data.data[1]
    
    # liberan los motores y se apagan
    #el nodo no es ejecutable (no cumple precondiciones o nivel 0)
    if NodoActivo== nodo and nodoEjecutable == 0:
	NodoActivo = -1 
	leftVelocity.publish(0)
	rightVelocity.publish(0)
    elif NodoActivo == -1 and nodoEjecutable == 1:
        NodoActivo = nodo #se asigna al nodo 	
        
    if Const.debugMotores == 1:
        print "Outputs node activo: ", str(NodoActivo),str(data.data)     
        
    msg = Int32MultiArray()   
    msg.data = [identify,NodoActivo] #por si necesito los id del par motor     
    motoresLockeado.publish(msg) 
   
 
##
# La funcion atiende los mensajers publicados en el topico "topic_operateEngine". En 
# este tópico se pulica un array de tipo Float64MultiArray , donde la posición 0 contiene el id del nodo,
# la posición 1 contiene la velocidad a aplicar al motor izquierdo y la posicion 2 contiene la velocidad
# a aplicar al motor derecho. Solo es atendido un nodo activo y una acción especial si el id del nodo es -2.
# Para que un nodo sea activo debe previaiente haber enviado una solicitudo usando el tópico "topic_engineAccess".
# @param data Datos publicados en el tópico "topic_operateEngine".
#
def actuarMotoresVREP(data):
    leftMsg = Float64()
    rightMsg = Float64()
    global NodoActivo 
    
    
    nodo=int(data.data[0])
    leftMsg.data = data.data[1]
    rightMsg.data = data.data[2]
        
    
    #solo se atiende a un nodo activo o a una accion especial si el nodo es -2
    if NodoActivo == nodo or nodo== -2:   
		leftVelocity.publish(leftMsg)
		rightVelocity.publish(rightMsg)
                

##
# La funcion atiende los mensajers publicados en el tópico "topic_led". En 
# este tópico se pulica un array de tipo Int32MultiArray, donde la posición 0 contiene el id del nodo y 
# la posición 1 contiene un 1 si se desea prender el led y 0 si se desea apagarlo. Solo es atendido el nodo activo.
# Para que un nodo sea activo debe previamente haber enviado una solicitudo usando el tópico "topic_engineAccess".
# @param data Datos publicados en el tópico "topic_led".
#            
def actuatorLed1TopicProccessing(data):
    #VERIFICAR ESTO DEBE MANEJASRSE parecido a motor   
    if NodoActivo == data.data[0]: 
        light.publish(data.data[1])
               
##
# La funcion atiende los mensajers publicados en el tópico "topic_led". En 
# este tópico se pulica un array de tipo Int32MultiArray, donde la posición 0 contiene el estado actual y 
# la posición 1 contiene el id del AbstractBehavior aunque aquí no sea usado. Se setea el NodoActivo a -1 y la velocidad de 
# ambos motores a 0. Además si el estado es 1, 2 o 3 se envia un mensaje para apagar el led. 
# @param data Datos publicados en el tópico "topic_state".
#
def setEstado(data):  
    #al iniciar una nueva ejecucion se debe reiniciar la estructura                
    sta=data.data[0]
    if sta==1 or sta==2 or sta==3:
        light.publish(0)    
    
    if Const.debugMotores == 1:
        print "Llego estado" , data.data[0]
    global NodoActivo
    NodoActivo = -1   
    leftVelocity.publish(0)
    rightVelocity.publish(0)


    if Const.debugMotores == 1:
        print "Outputs nodo activo: ", str(NodoActivo),str(data.data)         

##
# Funcion que se ejecuta al recibir una señal signal_shutdown.
#  
def shutdown():
    print "Bye!"

##
# La funcion emite una señal signal_shutdown para finalizar este nodo.
# @param data Datos publicados en el tópico. No es usado.
#   
def finalize(data):
    rospy.signal_shutdown("Bye!")



if __name__ == '__main__':
    print "Outputs inicializado"  

    rospy.init_node('Outputs', anonymous=True)
    
    rospy.on_shutdown(shutdown)
    
    motoresLockeado = rospy.Publisher('topic_engineLocked', Int32MultiArray, queue_size=1)
    rospy.Subscriber("topic_operateEngine", Float64MultiArray, actuarMotoresVREP)
    leftVelocity=rospy.Publisher('/vrep/leftMotorVelocity', Float64, queue_size = 1)
    rightVelocity=rospy.Publisher('/vrep/rightMotorVelocity', Float64, queue_size = 1)
    
    #Publico el entero 1 para prender luz y 0 para apagarla.
    light=rospy.Publisher('/vrep/actuatorLed1Topic', Int32, queue_size = 1)
    
    #Me suscribo para recibir los mensajes de encendido o apagado de luz
    rospy.Subscriber("topic_led", Int32MultiArray, actuatorLed1TopicProccessing)
    
    rospy.Subscriber("topic_engineAccess", Int32MultiArray, atendersolicitarOLiberarMotores)
    rospy.Subscriber("topic_state", Int32MultiArray, setEstado)  
    rospy.Subscriber("topic_finalize", String, finalize)
   
   
    rospy.spin()
        
