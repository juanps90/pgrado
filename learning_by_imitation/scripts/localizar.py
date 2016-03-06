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


import rospy
from std_msgs.msg import Int32MultiArray, Float64MultiArray, Float64,String
from random import randint
import Const
from comportamiento import comportamiento





class localizar(comportamiento):
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
    dataSensorColor = [Const.SENSOR_COLOR_DETECT_WHITE, Const.SENSOR_COLOR_DETECT_WHITE,Const.SENSOR_COLOR_DETECT_WHITE]

    recienEstuveEnColor=False
    delay = 0
    changeTime = None

    def __init__(self,identify): 
        super(localizar,self).__init__()
        self.identify=identify
        self.idComportamiento=1
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
            elif self.dataSensorColor[1] == color:
                action = self.ACTION_TURN_RIGHT
                print "DERECHA"  
            elif self.recienEstuveEnColor:
                self.action = self.ACTION_BACK       
        if self.dataSensorColor[0] == color or self.dataSensorColor[1] == color or self.dataSensorColor[2] == color  :
            self.recienEstuveEnColor=True
        else:    
            self.recienEstuveEnColor=False
		   
		   
    def publish(self,speedRight, speedLeft):
        msg = Float64MultiArray()
        msg.data = [self.identify, speedRight, speedLeft]
        self.motores.publish(msg)

    def wander(self,color): 
        publish=self.publish
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
            self.wander(Const.SENSOR_COLOR_DETECT_BLACK)
            rospy.loginfo(">>>ON localizar id:"+str(self.identify))
            #rospy.loginfo( nivelActivacion)
            self.ejecutando=True
            msg2 = Int32MultiArray()  
            msg2.data = [self.identify,self.identify] #por si necesito otro parametro        
            self.nodoEjecutando.publish(msg2) 
        else: 
            rospy.loginfo(">>>OFF localizar id:"+str(self.identify))
            self.ejecutando=False
		 


    '''
    def verificarPoscondicionesSensores(self,data):
        activate=False
        #se puede evaluar aca o bien suscribirse a varios topicos y solo llamar a atendersensores (VER CAUL ES MEJOR ESTRATEGIA)
        if data.data[0]==0:
	    self.processSensorLineDetectedColorData(data)

	if data.data[0]==1:
	    self.processProximitySensorData(data)		
	#esto es para probar con un comportamiento loc con otro color se haria con un topico de parametros     
	if data.data[0] == 0 and (data.data[2] == 0 or data.data[2] == 2):#para que sea de permanencia, hay que revisar
	    print "se cumple postcondicion localizar"
	    activate=True
	print "Active localizar",activate
        return activate
    '''

    def verificarPoscondicionesSensores(self,data):
        activate=False
	
	if not data.has_key(Const.SENSOR_COLOR_DETECT_LINE_ID):
	    return False
	
	sensado=data[Const.SENSOR_COLOR_DETECT_LINE_ID]	
	self.processSensorLineDetectedColorData(sensado)	
	#esto es para probar con un comportamiento loc con otro color se haria con un topico de parametros     
	if sensado[1] == 0 or sensado[1] == 2:#para que sea de permanencia, hay que revisar
	    print "se cumple postcondicion localizar"
	    activate=True
	print "Active localizar",activate
        return activate















    def setIdentify(self, dato):
        self.identify=dato




if __name__ == '__main__':


        print "iniciando localizar"  

        rospy.init_node('localizar', anonymous=True) 
        identify=int(rospy.myargv(argv=sys.argv)[1])  
        rospy.loginfo("identificador localizar "+str(identify)) 
        l = localizar(identify)
        l.setIdComp(1)
    
    
    
        '''
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

        

      #  self.postConditionDetect = rospy.Publisher('postConditionDetect', Int32MultiArray, queue_size=10) #usado para aprender 
    





	rospy.spin()












