#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys 
import Const
import rospy
from std_msgs.msg import Int32MultiArray, Float64MultiArray
from random import randint
from AbstractBehavior import AbstractBehavior

class Forward(AbstractBehavior):
        
    colorValido=[Const.SENSOR_COLOR_DETECT_RED,Const.SENSOR_COLOR_DETECT_GREEN,Const.SENSOR_COLOR_DETECT_BLUE]

         
    def __init__(self,datos): 
		super(Forward,self).__init__(datos) 
                self.idComportamiento="Forward"
 


    ##
    # Realiza las actuaciones correpondientes. En este caso solo avanza enviando a los motores los mensajes correspondientes.
    # Se deben de mandar mensajes continuamente tanto como si se ejecuta como si no.
    #
    def actuar(self):
        msgMotores = Float64MultiArray()
        if self.cumplePrecondiciones () and self.nivelActivacion>0 and self.motorLibre:
            #azar=randint(0,2)
            #msgMotores.data = [self.identify, self.speed, azar]
            msgMotores.data = [self.identify, self.speed, self.speed]
            self.motores.publish(msgMotores)
    
            self.ejecutando=True
            msg2 = Int32MultiArray()  
            msg2.data = [self.identify,self.identify] #por si necesito otro parametro        
            self.nodoEjecutando.publish(msg2)  
        else: 
            self.ejecutando=False


    ##
    # Retorna True si se cumple las postcondiciones del avanzar al momento de aprender. False en otro caso.
    # @param data Datos sensados.
    # @return Retorna True si se cumple las postcondiciones del avanzar al momento de aprender. False en otro caso.
    #
    def veriPosSenAprender(self, data):
        activate=False
        if not data.has_key(Const.SENSOR_COLOR_DETECT_LINE_ID):
            return False
        sensado=data[Const.SENSOR_COLOR_DETECT_LINE_ID]	
        self.processSensorLineDetectedColorData(sensado)		
        #se verifica el sensor del medio por eso es indice 1
        #si esta entre los colores validos deben ser distintos de los de Locate
        if sensado[1]  in self.colorValido :
            rospy.loginfo("Se cumple postcondicion avanzar para el color " + str(sensado[1]))
            activate=True
        return activate   
    
    ##
    # Retorna True si se cumple las postcondiciones del avanzar al ejecutar. False en otro caso.
    # @param data Datos sensados.
    # @return Retorna True si se cumple las postcondiciones del avanzar al ejecutar. False en otro caso.
    #
    def veriPosSenEjecutar(self,data):
        activate=False
	
        if not data.has_key(Const.SENSOR_COLOR_DETECT_LINE_ID):
            return False
	
        sensado=data[Const.SENSOR_COLOR_DETECT_LINE_ID]	
        self.processSensorLineDetectedColorData(sensado)		
        #los colores deben ser diferentes que los de Locate     
        #es bastante cyancyo esto tuardar 3 valores y solo usar uno se 
        #deberian separar los sensores eso es lo mas correcto
        if sensado[1]==self.parametros[Const.SENSOR_COLOR_DETECT_LINE_ID][1] :
            print "se cumple postcondicion avanzar"
            activate=True
            print "Active Forward",activate
        return activate


    ##
    # Retorna String con el formato ID_SENSORES#DATO_SENSOR_IZQUIERDO#DATO_SENSOR_MEDIO#DATO_SENSOR_DERECHO
    # @param data Datos sensados.
    # @return Retorna String con el formato indicado.
    #
    def getParAprendidos(self,data):
        s=data[Const.SENSOR_COLOR_DETECT_LINE_ID]
        return str(Const.SENSOR_COLOR_DETECT_LINE_ID)+ "#" + str(s[0]) + "#" +str(s[1]) + "#" +str(s[2])  
    
    
    
if __name__ == '__main__':

        #basicamente es lo que cambia de cada comportamiento
        rospy.loginfo("initialize Forward" )
        rospy.init_node('Forward', anonymous=True) 
        #aca se recibe string se desenvuelve y se obtiene id y parametros       
        datos=str(rospy.myargv(argv=sys.argv)[1])
        rospy.loginfo("datos avanzar "+str(datos)) 
        a = Forward(datos)
        
        rospy.spin()
        a.endTopic() 








