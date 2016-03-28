#!/usr/bin/env python

import sys 
import Const
import rospy
from std_msgs.msg import Int32MultiArray, Float64MultiArray
from random import randint
from comportamiento import comportamiento

class avanzar(comportamiento):
        
    colorValido=[Const.SENSOR_COLOR_DETECT_RED,Const.SENSOR_COLOR_DETECT_GREEN,Const.SENSOR_COLOR_DETECT_BLUE]

         
    def __init__(self,datos): 
		super(avanzar,self).__init__(datos) 
                self.idComportamiento="avanzar"
 


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
    
            #rospy.loginfo(">>>ON avanzar id:"+str(self.identify))
            ##rospy.loginfo( nivelActivacion) 
            self.ejecutando=True
            msg2 = Int32MultiArray()  
            msg2.data = [self.identify,self.identify] #por si necesito otro parametro        
            self.nodoEjecutando.publish(msg2)  
        else: 
            #rospy.loginfo(">>>OFF avanzar id:"+str(self.identify))
            self.ejecutando=False


    ##
    # Retorna True si se cumple las postcondiciones del avanzar al aprender. False en otro caso.
    # @param data Datos sensados.
    # @return Retorna True si se cumple las postcondiciones del avanzar al aprender. False en otro caso.
    #
    def veriPosSenAprender(self, data):
        activate=False
        if not data.has_key(Const.SENSOR_COLOR_DETECT_LINE_ID):
            return False
        sensado=data[Const.SENSOR_COLOR_DETECT_LINE_ID]	
        self.processSensorLineDetectedColorData(sensado)		
        #se verifica el sensor del medio por eso es indice 1
        #si esta entre los colores validos deben ser distintos de los de localizar
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
        #los colores deben ser diferentes que los de localizar     
        #es bastante cyancyo esto tuardar 3 valores y solo usar uno se 
        #deberian separar los sensores eso es lo mas correcto
        if sensado[1]==self.parametros[Const.SENSOR_COLOR_DETECT_LINE_ID][1] :
            print "se cumple postcondicion avanzar"
            activate=True
            print "Active avanzar",activate
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








