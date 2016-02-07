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
from std_msgs.msg import String, Int32MultiArray,Int64MultiArray , Float32,Float64

postConditionDetect = None
identify=0

NodoActivo = -1

#esto anda bien

#los nodos mandan solicitudes si cumplen sus precondiciones y su nivel de activacion >0
def atendersolicitarOLiberarMotores(data):
    
    #indices => 0:idNodo, 1:nodoEjecutable, 2:idMotor (esto hay que verificar si se sueltan de a uno los motores
    global NodoActivo    
    nodo=data.data[0] 
    nodoEjecutable=data.data[1]
    idMotor=data.data[2]
    
    
       
    
    # liberan los motores y se apagan
    #el nodo no es ejecutable (no cumple precondiciones o nivel 0)
    if NodoActivo== nodo and nodoEjecutable == 0:
	NodoActivo = -1 
	leftVelocity.publish(0)
	rightVelocity.publish(0)
    elif NodoActivo == -1 and nodoEjecutable == 1:
        NodoActivo = nodo #se asigna al nodo 	
        
    rospy.loginfo("motores nodo activo: " + str(NodoActivo))    
        
    msg = Int32MultiArray()   
    msg.data = [identify,NodoActivo] #por si necesito los id del par motor     
    motoresLockeado.publish(msg) 
   
 
 
 
#esto capaz deberia ser una especie de interfaz de modo de resolver los actuadores segun donde se embeba el producto esto es VREP 
def actuarMotoresVREP(data):
        leftMsg = Float64()
        rightMsg = Float64()
        global NodoActivo 
        
        
        nodo=data.data[0]
        leftMsg.data = data.data[1]
        rightMsg.data = data.data[2]
        
        
	'''
	if NodoActivo == -1 :
        	NodoActivo = nodo #se asigna al nodo 
        '''
        
        
        #solo se atiende a un nodo activo
        if NodoActivo == nodo:   
		leftVelocity.publish(leftMsg)
		rightVelocity.publish(rightMsg)
                
 
               
#al iniciar una nueva ejecucion se debe reiniciar la estructura                
          
                

if __name__ == '__main__':
        print "iniciando motores"  

        rospy.init_node('motores', anonymous=True)
        motoresLockeado = rospy.Publisher('topicoMotorLockeado', Int32MultiArray, queue_size=10)
        rospy.Subscriber("topicoActuarMotores", Int32MultiArray, actuarMotoresVREP)
        leftVelocity=rospy.Publisher('/vrep/leftMotorVelocity', Float64, queue_size = 10)
        rightVelocity=rospy.Publisher('/vrep/rightMotorVelocity', Float64, queue_size = 10)
        rospy.Subscriber("topicosolicitarOLiberarMotores", Int32MultiArray, atendersolicitarOLiberarMotores)
   
        rospy.spin()
        
