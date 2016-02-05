#!/usr/bin/env python


import sys 
import xmlrpclib 
import roslib.names  
import roslib.network  
import rospkg
import roslaunch.core
import roslaunch.remote

import rospy
from std_msgs.msg import Float64, Float64MultiArray

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
nodosActivos={}

#hay que verificar que se recibieron mensajes de todos los nodos del tipo inactivo para recien apagar los motores,
# esto es debido a que si se recibe un mensaje de inactivo y se apaga pero hay otro de activo estaria haciendo on off a cada mensaje


 
#esto capaz deberia ser una especie de interfaz de modo de resolver los actuadores segun donde se embeba el producto esto es VREP 
def actuarMotoresVREP(data):
        leftMsg = Float64()
        rightMsg = Float64()
        publicar=False      
        global tope
        global cantMensajesStop
        global nodosActivos
        
        if data.data[1]==0 and data.data[2] ==0: 
                #se detiene por numero de mensajes          
                cantMensajesStop=cantMensajesStop +1
                print cantMensajesStop
                #si llegan mas de tope mensajes de apagado recien apago
                if cantMensajesStop>=tope:  
                        publicar=True  
                        print "DETENER MOTORES ",tope," ",cantMensajesStop
                        
                #se detiene porque todos los comportamientos se detuvieron
                nodosActivos[data.data[0]]=False  
                apagar=True                
                for a in  nodosActivos:
                        if nodosActivos[a]:
                                apagar=False                                                              
                                break                                
                #si no hay ningun nodo activo se puede apagar
                if apagar:  
                        publicar=True  
                        print "DETENER MOTORES "        
                        
        else:         
                nodosActivos[data.data[0]]=True             
                publicar=True       
                
        if publicar:
                cantMensajesStop=0
                leftMsg.data = data.data[1]
                rightMsg.data = data.data[2]
                leftVelocity.publish(leftMsg)
                rightVelocity.publish(rightMsg)
                
                
                
                
                      
        elif data.data[1]==0 and data.data[2] ==0:  
                nodosActivos[data.data[0]]=False  
                apagar=True
                
                for a in  nodosActivos:
                        if nodosActivos[a]:
                                apagar=False                                                              
                                break
                                
                                
                #si no hay ningun nodo activo se puede apagar
                if apagar:  
                        publicar=True  
                        print "DETENER MOTORES "
        else:   
                #se agrega el id al diccionario
                nodosActivos[data.data[0]]=True             
                publicar=True           
                
                
                
                
                
                
                
                
                
  
'''
#esto capaz deberia ser una especie de interfaz de modo de resolver los actuadores segun donde se embeba el producto esto es VREP 
def actuarMotoresVREP(data):
        leftMsg = Float64()
        rightMsg = Float64()
        publicar=False      
        global tope
        global cantMensajesStop
        
        if data.data[1]==0 and data.data[2] ==0:           
                cantMensajesStop=cantMensajesStop +1
                print cantMensajesStop
                #si llegan mas de tope mensajes de apagado recien apago
                if cantMensajesStop>=tope:  
                        publicar=True  
                        print "DETENER MOTORES ",tope," ",cantMensajesStop
        else:                
                publicar=True           
                
        if publicar:
                cantMensajesStop=0
                leftMsg.data = data.data[1]
                rightMsg.data = data.data[2]
                leftVelocity.publish(leftMsg)
                rightVelocity.publish(rightMsg)
'''   
  
  
  
  
  
  
  
  
  
'''            
#esto capaz deberia ser una especie de interfaz de modo de resolver los actuadores segun donde se embeba el producto esto es VREP 
def actuarMotoresVREP(data):  
        global nodosActivos
              
        leftMsg = Float64()
        rightMsg = Float64()
        publicar=False      
        
        if data.data[0]==-1:
                print "id menos uno"
        #mensaje de apagado
        elif data.data[1]==0 and data.data[2] ==0:  
                nodosActivos[data.data[0]]=False  
                apagar=True
                
                for a in  nodosActivos:
                        if nodosActivos[a]:
                                apagar=False                                                              
                                break
                                
                                
                #si no hay ningun nodo activo se puede apagar
                if apagar:  
                        publicar=True  
                        print "DETENER MOTORES "
        else:   
                #se agrega el id al diccionario
                nodosActivos[data.data[0]]=True             
                publicar=True   
                
        print " ACTIVOs ", nodosActivos              
                
        if publicar:
                leftMsg.data = data.data[1]
                rightMsg.data = data.data[2]
                leftVelocity.publish(leftMsg)
                rightVelocity.publish(rightMsg)  
              
'''

               
#al iniciar una nueva ejecucion se debe reiniciar la estructura                
          
                

if __name__ == '__main__':
        print "iniciando motores"  

        rospy.init_node('motores', anonymous=True)
        rospy.Subscriber("topicoActuarMotores", Float64MultiArray, actuarMotoresVREP)
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
