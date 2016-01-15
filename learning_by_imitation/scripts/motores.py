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

identify=-1#modicar mediante mensajes al lanzar el nuevo nodo
idComportamiento = 1
reejecutar=True
ejecutando=False
permanent = {}
enablig = {}
ordering = {}
nivelActivacion=0
tope=10
cantMensajesStop=0


#hay que verificar que se recibieron mensajes de todos los nodos del tipo inactivo para recien apagar los motores, esto es debido a que si se recibe
#un mensaje de inactivo y se apaga pero hay otro de activo estaria haciendo on off a cada mensaje



#esto capaz deberia ser una especie de interfaz de modo de resolver los actuadores segun donde se embeba el producto esto es VREP 
def actuarMotoresVREP(data):
        leftMsg = Float64()
        rightMsg = Float64()
        publicar=False      
        global tope
        global cantMensajesStop
        
        if data.data[0]==0 and data.data[1] ==0:           
                cantMensajesStop=cantMensajesStop +1
                #si llegan mas de tope mensajes de apagado recien apago
                if cantMensajesStop>=tope:
                        publicar=True  
        else:
                cantMensajesStop=0
                publicar=True           
                
        if publicar:
                leftMsg.data = data.data[0]
                rightMsg.data = data.data[1]
                leftVelocity.publish(leftMsg)
                rightVelocity.publish(rightMsg)
        if data.data[0]==-1:
                leftMsg.data = 0
                rightMsg.data = 0
                leftVelocity.publish(leftMsg)
                rightVelocity.publish(rightMsg)    
                
                
                

if __name__ == '__main__':
        tope=0
        cantMensajesStop=0
        print "iniciando motores"  

        rospy.init_node('motores', anonymous=True)
        rospy.Subscriber("topicoActuarMotores", Int32MultiArray, actuarMotoresVREP)
        leftVelocity=rospy.Publisher('/vrep/leftMotorVelocity', Float64, queue_size = 10)
        rightVelocity=rospy.Publisher('/vrep/rightMotorVelocity', Float64, queue_size = 10)
        '''
        ingreso=raw_input()
        while ingreso!= "salir":
                # Aca se debe leer sensores     
                actuarMotoresVREP(1,1)
                ingreso=raw_input()
        print "Fin del ingreso de datos"
        '''    
   
        rospy.spin()
