#!/usr/bin/env python
import sys 
import rospy
from std_msgs.msg import Int32MultiArray, Float64MultiArray, String
from random import randint
import Const
from comportamiento import comportamiento


class irA(comportamiento):
    rate=None
 
    ACTION_FORWARD = 1
    ACTION_TURN_LEFT = 2
    ACTION_TURN_RIGHT = 3
    ACTION_BACK = 4

    DELTA_DISTANCE = 0.08
    DELTA_ANGLE = 0.2
    
 
    PARAM_COLOR = Const.SENSOR_COLOR_DETECT_RED
    PARAM_DISTANCE = 0.5
    PARAM_ANGLE = 0.5    
 
    
    action = ACTION_TURN_RIGHT
    delay = 0
    changeTime = None
    
    colorValido=[Const.SENSOR_COLOR_DETECT_RED,Const.SENSOR_COLOR_DETECT_RED,
    Const.SENSOR_COLOR_DETECT_GREEN,Const.SENSOR_COLOR_DETECT_BLUE,
    Const.SENSOR_COLOR_DETECT_YELLOW,Const.SENSOR_COLOR_DETECT_ORANGE]

    def __init__(self,datos): 
        super(irA,self).__init__(datos) 
        self.idComportamiento="irA"
        self.delay = 0
        self.changeTime = rospy.Time.now() + rospy.Duration(self.delay)
        self.rate = rospy.Rate(10)  

    def getAction(self, color, distance, angle):
        see = False        
        sensoVision = self.dataSensor.has_key(Const.SENSOR_VISION_HEAD_ID) 
        #colorVisto=""       
        if sensoVision :  
            rospy.loginfo("visto")   
            see = True  
            #colorVisto=str(self.dataSensor[Const.SENSOR_VISION_HEAD_ID][1]) 
            if self.dataSensor[Const.SENSOR_VISION_HEAD_ID][1] == color: 
                   
                if self.dataSensor.has_key(Const.SENSOR_NOSE_ULTRASONIC_ID):                
                    if self.dataSensor[Const.SENSOR_NOSE_ULTRASONIC_ID][0] > distance + self.DELTA_DISTANCE:
                        self.action = self.ACTION_FORWARD
                    elif self.dataSensor[Const.SENSOR_NOSE_ULTRASONIC_ID][0] < distance - self.DELTA_DISTANCE:
                        self.action = self.ACTION_BACK
                    elif self.dataSensor[Const.SENSOR_VISION_HEAD_ID][0] < angle + self.DELTA_ANGLE:
                        self.action = self.ACTION_TURN_LEFT
                    elif self.dataSensor[Const.SENSOR_VISION_HEAD_ID][0] > angle - self.DELTA_ANGLE:
                        self.action = self.ACTION_TURN_RIGHT
                else:
                    self.action = self.ACTION_FORWARD
            #no es el color buscado 
            elif self.dataSensor.has_key(Const.SENSOR_NOSE_ULTRASONIC_ID):
                #rospy.loginfo("otro color"+str(self.dataSensor[Const.SENSOR_NOSE_ULTRASONIC_ID][0]))  
                # estoy muy cerca entonces retrocedo
                if self.dataSensor[Const.SENSOR_NOSE_ULTRASONIC_ID][0] < 0.1 :  
                    self.action = self.ACTION_BACK
                elif randint(0, 1) == 0:
                    self.action = self.ACTION_TURN_LEFT 

        #rospy.loginfo("action " + str( self.action )+ " "+colorVisto+" "+str(see))   
        return see
		   
		   
    def publish(self,speedRight, speedLeft):
        msg = Float64MultiArray()
        msg.data = [self.identify, speedRight, speedLeft]
        self.motores.publish(msg)

    def findObject(self, color, distance, angle):

        wander=not self.getAction(color, distance, angle)
  
        
 
 
        if wander and self.changeTime < rospy.Time.now(): 
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
            
 
        if self.action == self.ACTION_BACK:
            # voy hacia atras
            #azar=randint(0,2)
            self.publish(-self.speed, -self.speed)
        elif self.action == self.ACTION_FORWARD:
            # sigo hacia adelante
            self.publish(self.speed, self.speed)
        elif self.action == self.ACTION_TURN_LEFT:
            # girar a la izquierda
            self.publish(-self.speed/2, self.speed/2)
        else:
            # girar a la derecha
            self.publish(self.speed/2, -self.speed/2)   
         
         
        rospy.loginfo("action " + str( self.action )+ " color "+str(color)+str(wander)) 

  
 
  

    #se deben de mandar mensajes continuamente si se ejecuta tanto como si no a los motores
    def actuar(self):
        if self.cumplePrecondiciones () and self.nivelActivacion>0 and self.motorLibre:
            
            # SE DEBE RECIBIR EL PARAMETROS DEL COLOR DISTANCIA Y ANGULO.
            head=[-1,-1]
            if self.parametros.has_key(Const.SENSOR_VISION_HEAD_ID):
                head=self.parametros[Const.SENSOR_VISION_HEAD_ID]
            dist=[200]
            if self.parametros.has_key(Const.SENSOR_NOSE_ULTRASONIC_ID):    
                dist=self.parametros[Const.SENSOR_NOSE_ULTRASONIC_ID]
            self.findObject(head[1], dist[0], head[0])
#            rospy.loginfo(">>>ON irA id:"+str(self.identify))
            #rospy.loginfo( nivelActivacion)
            self.ejecutando=True
            msg2 = Int32MultiArray()  
            msg2.data = [self.identify,self.identify] #por si necesito otro parametro        
            self.nodoEjecutando.publish(msg2) 
        else: 
#           rospy.loginfo(">>>OFF irA id:"+str(self.identify))
            self.ejecutando=False

   
    def veriPosSenAprender(self, data):
       activate=False
       if (not data.has_key(Const.SENSOR_VISION_HEAD_ID)) or (not data.has_key(Const.SENSOR_NOSE_ULTRASONIC_ID)):
           return False
           
       headSensor = data[Const.SENSOR_VISION_HEAD_ID]
       noseSensor = data[Const.SENSOR_NOSE_ULTRASONIC_ID]
       
       # La condicion es que color sea igual al color dado.
       # La distancia este en el intervalo [PARAM_DISTANCE - DELTA_DISTANCE, PARAM_DISTANCE + self.DELTA_DISTANCE]
       # El angulo este en el intervalo [PARAM_ANGLE - DELTA_ANGLE, PARAM_ANGLE + self.DELTA_ANGLE]
        
       
       cond0=  headSensor[1] in self.colorValido 
       cond1=self.PARAM_DISTANCE - self.DELTA_DISTANCE <= noseSensor 
       cond2=noseSensor[0] <= self.PARAM_DISTANCE + self.DELTA_DISTANCE  
       cond3=self.PARAM_ANGLE - self.DELTA_ANGLE <= headSensor[0] 
       cond4=headSensor[0] <= self.PARAM_ANGLE + self.DELTA_ANGLE
       
       if cond0 and cond1 and cond2 and cond3 and cond4:       
       
           rospy.loginfo("SE CUMPLE POSTCONDICION IR A")
           activate=True
       rospy.loginfo("Active irA" + str(activate))
       rospy.loginfo("color = " + str(headSensor[1]) + " distancia  = " + str(noseSensor) + " angulo = " + str(headSensor[0]))
       return activate
       
       
       

    
    def veriPosSenEjecutar(self,data):
       activate=False
       if (not data.has_key(Const.SENSOR_VISION_HEAD_ID)) or (not data.has_key(Const.SENSOR_NOSE_ULTRASONIC_ID)):
           return False
           
       headSensor = data[Const.SENSOR_VISION_HEAD_ID]
       noseSensor = data[Const.SENSOR_NOSE_ULTRASONIC_ID]
       
       
       rospy.loginfo("parametros " + str(self.parametros))       
       
       
       # La condicion es que color sea igual al color dado.
       # La distancia este en el intervalo [PARAM_DISTANCE - DELTA_DISTANCE, PARAM_DISTANCE + self.DELTA_DISTANCE]
       # El angulo este en el intervalo [PARAM_ANGLE - DELTA_ANGLE, PARAM_ANGLE + self.DELTA_ANGLE]
       angulo=self.parametros[Const.SENSOR_VISION_HEAD_ID][0]
       distancia=self.parametros[Const.SENSOR_NOSE_ULTRASONIC_ID][0]
       
       cond0=self.parametros[Const.SENSOR_VISION_HEAD_ID][1]==headSensor[1]
       cond1= distancia - self.DELTA_DISTANCE <= noseSensor 
       cond2=noseSensor[0] <= distancia + self.DELTA_DISTANCE  
       cond3= angulo - self.DELTA_ANGLE <= headSensor[0] 
       cond4=headSensor[0] <= angulo + self.DELTA_ANGLE
       
       if cond0 and cond1 and cond2 and cond3 and cond4:       
       
           rospy.loginfo("SE CUMPLE POSTCONDICION IR A")
           activate=True
       rospy.loginfo("Active irA" + str(activate))
       rospy.loginfo("color = " + str(headSensor[1]) + " distancia  = " + str(noseSensor) + " angulo = " + str(headSensor[0]))
       return activate




    def getParAprendidos(self,data):
        rospy.loginfo("getparaprendidos ir a "+str(data))
        proxim=[]
        head=[]
        outHead=""
        outProxim=""
        if data.has_key(Const.SENSOR_VISION_HEAD_ID):
            head=data[Const.SENSOR_VISION_HEAD_ID]
            outHead=str (Const.SENSOR_VISION_HEAD_ID) + "#" +str(head[0]) + "#" +str(head[1]) 
        if data.has_key(Const.SENSOR_NOSE_ULTRASONIC_ID):   
            proxim=data[Const.SENSOR_NOSE_ULTRASONIC_ID]
            outProxim=str (Const.SENSOR_NOSE_ULTRASONIC_ID) + "#" +str(proxim[0]) 
        salida=""
        if len(outHead)>0:
            salida=salida+outHead 
        if len(outProxim)>0:
            if len(salida):
                salida=salida+ "|"
            salida=salida+outProxim 
        return salida



if __name__ == '__main__':

    print "iniciando irA"  
    rospy.init_node('irA', anonymous=True) 
    #aca se recibe string se desenvuelve y se obtiene id y parametros       
    datos=str(rospy.myargv(argv=sys.argv)[1])
    rospy.loginfo("datos irA "+str(datos)) 
    i = irA(datos)
    rospy.spin()
    i.endTopic()















