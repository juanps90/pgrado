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
from std_msgs.msg import Int32MultiArray, Float64MultiArray,String
from random import randint
from comportamiento import comportamiento







class avanzar(comportamiento):
        
         
    def __init__(self,datos): 
		super(avanzar,self).__init__(datos) 
                self.idComportamiento="avanzar"
 
        #se deben de mandar mensajes continuamente si se ejecuta tanto como si no a los motores
    def actuar(self):
                msg = Int32MultiArray()
                msgMotores = Float64MultiArray()
                if self.cumplePrecondiciones () and self.nivelActivacion>0 and self.motorLibre:
                        # Aca iria la operacion de wander.
                        azar=randint(0,2)
                        msgMotores.data = [self.identify, self.speed, azar]
                        self.motores.publish(msgMotores)

                        #rospy.loginfo(">>>ON avanzar id:"+str(self.identify))
                        ##rospy.loginfo( nivelActivacion) 
                        self.ejecutando=True
                        msg2 = Int32MultiArray()  
                        msg2.data = [self.identify,self.identify] #por si necesito otro parametro        
                        self.nodoEjecutando.publish(msg2)  
                
                else: 
                        #rospy.loginfo(">>>OFF avanzar id:"+str(self.identify))
                        self.ejecutando=False


    def veriPosSenAprender(self, data):
        activate=False
	
	if not data.has_key(Const.SENSOR_COLOR_DETECT_LINE_ID):
	    return False
	
	sensado=data[Const.SENSOR_COLOR_DETECT_LINE_ID]	
	self.processSensorLineDetectedColorData(sensado)		
	#esto es para probar con un comportamiento loc con otro color se haria con un topico de parametros     
	if sensado[1] == 2:
	    print "se cumple postcondicion localizar"
	    activate=True
	print "Active localizar",activate
        return activate   
    

    def veriPosSenEjecutar(self,data):
        activate=False
	
	if not data.has_key(Const.SENSOR_COLOR_DETECT_LINE_ID):
	    return False
	
	sensado=data[Const.SENSOR_COLOR_DETECT_LINE_ID]	
	self.processSensorLineDetectedColorData(sensado)		
	#esto es para probar con un comportamiento loc con otro color se haria con un topico de parametros     
	if sensado[1] == 2:
	    print "se cumple postcondicion localizar"
	    activate=True
	print "Active localizar",activate
        return activate


    def getParAprendidos(self,data):
        s=data[Const.SENSOR_COLOR_DETECT_LINE_ID]
        return str(Const.SENSOR_COLOR_DETECT_LINE_ID)+ "#" + str(s[0]) + "#" +str(s[1]) + "#" +str(s[2])  
    
    
    
if __name__ == '__main__':

        #basicamente es lo que cambia de cada comportamiento
        rospy.loginfo("iniciando avanzar" )
        rospy.init_node('avanzar', anonymous=True) 
        #aca se recibe string se desenvuelve y se obtiene id y parametros       
        datos=str(rospy.myargv(argv=sys.argv)[1])
        rospy.loginfo("datos avanzar "+str(datos)) 
        a = avanzar(datos)
        
        '''
        #lo que sigue se podria ver de meter en comportamiento
        rospy.Subscriber("topicoSensores", String, l.atenderSensores)
        rospy.Subscriber("preConditionDetect", Int32MultiArray, l.evaluarPrecondicion)
        rospy.Subscriber("preConditionsSetting", Int32MultiArray, l.setting)	    
        rospy.Subscriber("topicoEstado", Int32MultiArray, l.setEstado)
        rospy.Subscriber("topicoNivel", Int32MultiArray, l.atenderNivel)
        rospy.Subscriber("topicoCaminos", Int32MultiArray, l.atenderCaminos)
        rospy.Subscriber("topicoNodoEjecutando", Int32MultiArray, l.atenderNodoEjecutando)
        rospy.Subscriber("topicoMotorLockeado", Int32MultiArray, l.atenderMotorLockeado)

        motores = rospy.Publisher('topicoActuarMotores', Float64MultiArray, queue_size=10)
        l.setMotores(motores)
        postConditionDetect = rospy.Publisher('postConditionDetect', Int32MultiArray, queue_size=10) #usado para aprender
        l.setPostConditionDetect(postConditionDetect)
        preConditionDetect = rospy.Publisher('preConditionDetect', Int32MultiArray, queue_size=10) #usado para ejecutar
        l.setPreConditionDetect(preConditionDetect)
        nivel = rospy.Publisher('topicoNivel', Int32MultiArray, queue_size=10)
        l.setNivel(nivel)
        nodoEjecutando=rospy.Publisher('topicoNodoEjecutando', Int32MultiArray, queue_size=10)
        l.setNodoEjecutando(nodoEjecutando)
        solicitarOLiberarMotores=rospy.Publisher('topicosolicitarOLiberarMotores', Int32MultiArray, queue_size=10) 
        l.SetSLMotores(solicitarOLiberarMotores)
        #  rospy.Subscriber("sensorLineDetectedColorData", Float64MultiArray, processSensorLineDetectedColorData)
        # rospy.Subscriber("proximitySensorData", Float64, processProximitySensorData)
  
        '''
        rospy.spin()
        a.endTopic() 







