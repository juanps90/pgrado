#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package Locate
# @brief ----
# @details ----
# @authors Gustavo Irigoyen
# @authors Juan Pablo Sierra
# @authors Juan Eliel Ibarra
# @authors Gustavo Evovlockas
# @date Abril 2016
#

import sys 
import rospy
from std_msgs.msg import Int32MultiArray, Float64MultiArray
from random import randint
import Const
from AbstractBehavior import AbstractBehavior

class Locate(AbstractBehavior):
    rate=None
    postConditionDetect = None

 
    reejecutar=True
    ejecutando=False
    permanent = {}
    enablig = {}
    ordering = {}
    nivelActivacion=0
    estado=1
    motorLibre=False
    caminos=[]

    ACTION_FORWARD = 1
    ACTION_TURN_LEFT = 2
    ACTION_TURN_RIGHT = 3
    ACTION_BACK = 4

    speed = 2
    action = ACTION_BACK
    #seteado para iniciar
    dataSensorColor = [Const.SENSOR_COLOR_DETECT_WHITE, Const.SENSOR_COLOR_DETECT_WHITE,Const.SENSOR_COLOR_DETECT_WHITE]
    #colores que el comportamiento acepta para Locate lineas de piso
    colorValido=[Const.SENSOR_COLOR_DETECT_BLACK,Const.SENSOR_COLOR_DETECT_YELLOW,Const.SENSOR_COLOR_DETECT_ORANGE,Const.SENSOR_COLOR_DETECT_GREEN]


    recienEstuveEnColor=False
    delay = 0
    changeTime = None

  

    def __init__(self,datos): 
        super(Locate,self).__init__(datos) 
        self.idComportamiento="Locate"
        self.delay = 0
        self.changeTime = rospy.Time.now() + rospy.Duration(self.delay)
        self.rate = rospy.Rate(10)   
   

    def getAction(self,color):          
        if self.dataSensorColor[1] != color:
            if self.dataSensorColor[0] == color and self.dataSensorColor[2] == color:
                self.action = self.ACTION_BACK
            elif self.dataSensorColor[0] == color:
                self.action = self.ACTION_TURN_LEFT
                print "IZQUIERDA"  
            elif self.dataSensorColor[2] == color:
                self.action = self.ACTION_TURN_RIGHT
                print "DERECHA"
            elif self.recienEstuveEnColor:
                self.action = self.ACTION_BACK       
        elif self.dataSensorColor[0] == color or self.dataSensorColor[1] == color or self.dataSensorColor[2] == color  :
            self.recienEstuveEnColor=True
        else:    
            self.recienEstuveEnColor=False
		   
		   
    def publish(self,speedRight, speedLeft):
        msg = Float64MultiArray()
        msg.data = [self.identify, speedRight, speedLeft]
        self.motores.publish(msg)

    def wander(self,color): 
        self.getAction(color)      
 
        if self.action == self.ACTION_BACK:
            # voy hacia atras
            #azar=randint(0,2)
            self.publish(-self.speed, -self.speed + 2)
        elif self.action == self.ACTION_FORWARD:
            # sigo hacia adelante
            self.publish(self.speed, self.speed)
        elif self.action == self.ACTION_TURN_LEFT:
            # girar a la izquierda
            self.publish(-self.speed/2, self.speed/2)
        else:
            # girar a la derecha
            self.publish(self.speed/2, -self.speed/2)

        if not self.recienEstuveEnColor and self.changeTime < rospy.Time.now():
            if self.dataSensorColor[0] != color and self.dataSensorColor[1] != color and self.dataSensorColor[2] != color:
                if self.action == self.ACTION_FORWARD or self.action == self.ACTION_BACK:
                    if randint(0, 1) == 0:
                        self.action = self.ACTION_TURN_LEFT
                        print "IZQUIERDA"
                    else:
                        self.action = self.ACTION_TURN_RIGHT
                        print "DERECHA"
                else:
                    self.action = self.ACTION_FORWARD
                    print "ADELANTE"
            self.delay = randint(2, 9)
            self.changeTime = rospy.Time.now() + rospy.Duration(self.delay)
            self.rate.sleep() 

    #se deben de mandar mensajes continuamente si se ejecuta tanto como si no a los motores
    def actuar(self):
        if self.cumplePrecondiciones () and self.nivelActivacion>0 and self.motorLibre:
            # SE DEBE RECIBIR EL PARAMETRO DEL COLOR DE LA LINEA. POR AHORA ES SOLO NEGRO.
            self.wander(self.parametros[Const.SENSOR_COLOR_DETECT_LINE_ID][1])
            #rospy.loginfo(">>>ON Locate id:"+str(self.identify))
            ##rospy.loginfo( nivelActivacion)
            self.ejecutando=True
            msg2 = Int32MultiArray()  
            msg2.data = [self.identify,self.identify] #por si necesito otro parametro        
            self.nodoEjecutando.publish(msg2) 
        else: 
            #rospy.loginfo(">>>OFF Locate id:"+str(self.identify))
            self.ejecutando=False
		 




    def veriPosSenAprender(self, data):
        activate=False
        if not data.has_key(Const.SENSOR_COLOR_DETECT_LINE_ID):
            return False
        sensado=data[Const.SENSOR_COLOR_DETECT_LINE_ID]	
        self.processSensorLineDetectedColorData(sensado)		
        #se verifica el sensor del medio por eso es indice 1
        #si esta entre los colores validos deben ser distintos de los de avanzar
        if sensado[1]  in self.colorValido :
            rospy.loginfo("Se cumple postcondicion Locate para el color " + str(sensado[1]))
            activate=True
        return activate   
    


    def veriPosSenEjecutar(self,data):
        activate=False
	
        if not data.has_key(Const.SENSOR_COLOR_DETECT_LINE_ID):
            return False
	
        sensado=data[Const.SENSOR_COLOR_DETECT_LINE_ID]	
        self.processSensorLineDetectedColorData(sensado)		
        #los colores deben ser diferentes que los de avanzar     
        #es bastante cyancyo esto tuardar 3 valores y solo usar uno se 
        #deberian separar los sensores eso es lo mas correcto
        if sensado[1]==self.parametros[Const.SENSOR_COLOR_DETECT_LINE_ID][1] :
            print "se cumple postcondicion Locate"
            activate=True
            print "Active Locate",activate
        return activate


    def getParAprendidos(self,data):
        s=data[Const.SENSOR_COLOR_DETECT_LINE_ID]
        return str(Const.SENSOR_COLOR_DETECT_LINE_ID)+ "#" + str(s[0]) + "#" +str(s[1]) + "#" +str(s[2])  
    


if __name__ == '__main__':

    print "iniciando Locate"  

    rospy.init_node('Locate', anonymous=True) 
    #aca se recibe string se desenvuelve y se obtiene id y parametros       
    datos=str(rospy.myargv(argv=sys.argv)[1])
    rospy.loginfo("datos Locate "+str(datos)) 
    l = Locate(datos) 
    rospy.spin()
    l.endTopic() 
    rospy.signal_shutdown("Bye!")

