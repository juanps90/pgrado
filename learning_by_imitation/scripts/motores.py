#!/usr/bin/env python

import rospy
from std_msgs.msg import Int32MultiArray, Float64, Float64MultiArray, Int32, String
import Const

identify=0

NodoActivo = -1

#esto anda bien

#los nodos mandan solicitudes si cumplen sus precondiciones y su nivel de activacion >0
def atendersolicitarOLiberarMotores(data):
    
    #indices => 0:idNodo, 1:nodoEjecutable, 2:idMotor (esto hay que verificar si se sueltan de a uno los motores
    global NodoActivo    
    nodo=data.data[0] 
    nodoEjecutable=data.data[1]
    # idMotor=data.data[2]
    
    # liberan los motores y se apagan
    #el nodo no es ejecutable (no cumple precondiciones o nivel 0)
    if NodoActivo== nodo and nodoEjecutable == 0:
	NodoActivo = -1 
	leftVelocity.publish(0)
	rightVelocity.publish(0)
    elif NodoActivo == -1 and nodoEjecutable == 1:
        NodoActivo = nodo #se asigna al nodo 	
        
    if Const.debugMotores == 1:
        print "motores node activo: ", str(NodoActivo),str(data.data)     
        
    msg = Int32MultiArray()   
    msg.data = [identify,NodoActivo] #por si necesito los id del par motor     
    motoresLockeado.publish(msg) 
   
 
 
 
#esto capaz deberia ser una especie de interfaz de modo de resolver los actuadores segun donde se embeba el producto esto es VREP 
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
                
#VERIFICAR ESTO DEBE MANEJASRSE parecido a motor                
def actuatorLed1TopicProccessing(data):
    if NodoActivo == data.data[0]: 
        light.publish(data.data[1])
               
#al iniciar una nueva ejecucion se debe reiniciar la estructura                
def setEstado(data):  
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
        print "motores nodo activo: ", str(NodoActivo),str(data.data)         


def shutdown():
    print "Bye!"

def finalize(data):
    rospy.signal_shutdown("Bye!")



if __name__ == '__main__':
    print "motores inicializados"  

    rospy.init_node('motores', anonymous=True)
    
    rospy.on_shutdown(shutdown)
    
    motoresLockeado = rospy.Publisher('topicoMotorLockeado', Int32MultiArray, queue_size=1)
    rospy.Subscriber("topicoActuarMotores", Float64MultiArray, actuarMotoresVREP)
    leftVelocity=rospy.Publisher('/vrep/leftMotorVelocity', Float64, queue_size = 1)
    rightVelocity=rospy.Publisher('/vrep/rightMotorVelocity', Float64, queue_size = 1)
    
    #Publico el entero 1 para prender luz y 0 para apagarla.
    light=rospy.Publisher('/vrep/actuatorLed1Topic', Int32, queue_size = 1)
    
    #Me suscribo para recibir los mensajes de encendido o apagado de luz
    rospy.Subscriber("topic_led", Int32MultiArray, actuatorLed1TopicProccessing)
    
    rospy.Subscriber("topicosolicitarOLiberarMotores", Int32MultiArray, atendersolicitarOLiberarMotores)
    rospy.Subscriber("topic_state", Int32MultiArray, setEstado)  
    rospy.Subscriber("topic_finalize", String, finalize)
   
   
    rospy.spin()
        
