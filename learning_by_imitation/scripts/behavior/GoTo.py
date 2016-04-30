#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package GoTo
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
from std_msgs.msg import Int32MultiArray, Float64MultiArray, Int32
from random import randint
import Const
from AbstractBehavior import AbstractBehavior
import os

from attributes import SensorFactory

def mlog(msg):
    with open("/tmp/log.txt", "a") as myfile:
        myfile.write(msg + "\n")

class GoTo(AbstractBehavior):
    rate=None
 
    ACTION_FORWARD = 1
    ACTION_TURN_LEFT = 2
    ACTION_TURN_RIGHT = 3
    ACTION_BACK = 4

    DELTA_DISTANCE = 0.08
    DELTA_ANGLE = 0.1
    
 
    PARAM_COLOR = Const.SENSOR_COLOR_DETECT_RED
    PARAM_DISTANCE = 0.5
    PARAM_ANGLE = 0.5
    light = None
    isCenter = False 
    
    action = ACTION_TURN_RIGHT
    delay = 0
    changeTime = None
    prevColor=None
    
    colorValido=[Const.SENSOR_COLOR_DETECT_ORANGE,Const.SENSOR_COLOR_DETECT_YELLOW, Const.SENSOR_COLOR_DETECT_GREEN,Const.SENSOR_COLOR_DETECT_RED,Const.SENSOR_COLOR_DETECT_BLUE]
    
    #son las distancias minimas en aprender, angulo para esa distancia
    minDist=200
    angMinDist=1
    avgA = 0
    lastSeenRight = False

    def __init__(self,datos): 
        super(GoTo,self).__init__(datos) 
        self.idComportamiento="GoTo"
        self.delay = 0
        self.changeTime = rospy.Time.now() + rospy.Duration(self.delay)
        self.rate = rospy.Rate(10)
        self.light = rospy.Publisher('topic_led', Int32MultiArray, queue_size = 1)

    ##
    # Busca en los elementos impares de la lista de datos del sensor de vision
    # el color deseado, retornando  True si lo encuentra y false en otro caso.
    # @param ls lista de datos del sensor de vision.
    # @param c Color buscado.
    # @return Retorna elindice donde esta el color si encuentra el color. False en otro caso.
    #
           
        
    def getIndObjetoColor(self, data, c):
        indObj=-1
        i = 0
        salida=-1
        while i+3 < len(data):
            indObj=indObj+1
            if data[i+1]==c:
                return indObj
            i = i + 4
        return salida   
        
        
    def getColors(self, data):
        indObj=-1
        i = 0
        salida=[]
        while i+3 < len(data):
            indObj=indObj+1
            salida.append ( data[i+1] )
            i = i + 4
        return salida  
        
    #recibe los datos de los sensores y verifica cual es el objeto mas cercano por el tamanio
    def getIndObjMoreNear(self,data): 
        indObj=-1
        i = 0
        highMax=-1
        salida=-1
        while i +3< len(data):
            indObj=indObj+1
            aux= data[i+2] * data[i+3] 
            if aux>highMax:
                salida=indObj
                highMax=aux 
            i = i + 4

        return salida
        
    ##
    # Retorna un True si veo algun objeto. En caso de ser visto setea en action la correspondiente 
    # accion a ejecutar. Esta accion puede ser girar a la derecha, girar a la izquierda, avanzar o retroceder.
    # @param color Color buscado.
    # @param distance Distancia a posicionarse respecto al objeto.
    # @param angle Angulo a posicionarse respecto al objeto.
    # @return Retorna un True si veo algun objeto. False en otro caso.
    #
    def getAction(self, color, distance, angle):
        #mlog( "------------------------ GET ACTION")
        see = False
        sensoVision = self.dataSensor.has_key(Const.SENSOR_VISION_HEAD_ID) 
        #mlog("VEO EL COSITO?")
        #mlog("Busco Color: " + str(color) + ", array: " + str(self.dataSensor))
        try:
            mlog( "Angulo=" + str(self.dataSensor[Const.SENSOR_VISION_HEAD_ID][0]) + "; tgt=" + str(angle))
            
        except:
            pass
        try:
            mlog("dist=" + str(self.dataSensor[Const.SENSOR_NOSE_ULTRASONIC_ID][0]))
        except:
            pass
        
        
        if sensoVision :  
            #mlog("VISTO")   
            see = True  
            
            #Aca se deberia recibir todos los pares anguo color y ver si entr los vistos
            #esta el color buscado, hay que tener cuidado de no avanzar si 
            #hay un objeto en frente qu eno es nuestro color            
            #rospy.loginfo("DATA IN HEAD SENSOR " + str(self.dataSensor[Const.SENSOR_VISION_HEAD_ID]))
                
            
            
            auxIndColor=self.getIndObjetoColor(self.dataSensor[Const.SENSOR_VISION_HEAD_ID], color)
            
            #rospy.loginfo("Largo datos " +str(len(self.dataSensor[Const.SENSOR_VISION_HEAD_ID]))+str (  self.getColors (self.dataSensor[Const.SENSOR_VISION_HEAD_ID])) +"indColor:"+ str(color)+ " "+ str(auxIndColor )+" indCercano " +str( self.getIndObjMoreNear(self.dataSensor[Const.SENSOR_VISION_HEAD_ID]) ) )

            
            #hallo el color
            if auxIndColor!=-1:
                
               # rospy.loginfo("Largo datos " +str(len(self.dataSensor[Const.SENSOR_VISION_HEAD_ID]))+ "indColor "+ str(auxIndColor )+" indCercano " +str( self.getIndObjMoreNear(self.dataSensor[Const.SENSOR_VISION_HEAD_ID]) ) )

                indAngle=0
                if len (self.dataSensor[Const.SENSOR_VISION_HEAD_ID]) > 4 * (auxIndColor):
                    indAngle = 4 * (auxIndColor)
                
                curAngle = self.dataSensor[Const.SENSOR_VISION_HEAD_ID][indAngle]
                if self.avgA == 0:
                    self.avgA = curAngle
                else:
                    self.avgA = (self.avgA * 2 + curAngle)/3
                    
                curAngle = self.avgA
                #mlog(  "color en vista")
                #se pregunta si el sensor de distancia esta activo pero ademas se debe verificar que la 
                #distancia medida sea la del objeto y no de otro para eso se usa la altura
                if self.dataSensor.has_key(Const.SENSOR_NOSE_ULTRASONIC_ID) and self.getIndObjMoreNear(self.dataSensor[Const.SENSOR_VISION_HEAD_ID])==auxIndColor:                
                    #mlog( "GoTo if1")
                    rospy.loginfo("en color")
                    if self.dataSensor[Const.SENSOR_NOSE_ULTRASONIC_ID][0] > distance + self.DELTA_DISTANCE:
                        self.action = self.ACTION_FORWARD
                    elif self.dataSensor[Const.SENSOR_NOSE_ULTRASONIC_ID][0] < distance - self.DELTA_DISTANCE:
                        self.action = self.ACTION_BACK
                    elif self.dataSensor[Const.SENSOR_VISION_HEAD_ID][0] < angle - self.DELTA_ANGLE:
                        self.action = self.ACTION_TURN_LEFT
                        self.lastSeenRight = False
                    elif self.dataSensor[Const.SENSOR_VISION_HEAD_ID][0] > angle + self.DELTA_ANGLE:
                        self.action = self.ACTION_TURN_RIGHT
                        self.lastSeenRight = True
                else:
                    #mlog( "GoTo if2 con angle=" + str(angle) + "; " + str(self.dataSensor[Const.SENSOR_VISION_HEAD_ID][0]) )
                    #ve el color pero no esta a una distancia adecuada centra y luego avanza
                    
                    if abs(curAngle - angle) < self.DELTA_ANGLE:
                        # Muy proximos al angulo buscado
                        mlog("En el angulo")
                        self.action = self.ACTION_FORWARD
                    elif (curAngle > 0.5 and angle > curAngle):
                        mlog("Avance por derecha")
                        self.action = self.ACTION_FORWARD
                    elif (curAngle < 0.5 and angle < curAngle):
                        mlog("Avance por izquierda")
                        self.action = self.ACTION_FORWARD
                    elif (1-curAngle) < self.DELTA_ANGLE * 1.5:
                        mlog("Recupero derecha")
                        self.action = self.ACTION_TURN_RIGHT
                    elif curAngle < self.DELTA_ANGLE * 1.5:
                        mlog("Recupero izquierda")
                        self.action = self.ACTION_TURN_LEFT
                        # sdas
                    elif (curAngle > 0.5 and angle < curAngle):
                        mlog("Acomodo derecha")
                        self.action = self.ACTION_TURN_RIGHT
                    elif (curAngle < 0.5 and angle > curAngle):
                        mlog("Acomodo izquierda")
                        self.action = self.ACTION_TURN_LEFT
                    
                    '''if  < angle - self.DELTA_ANGLE:
                        mlog("Recupero para un lado")
                        self.action = self.ACTION_TURN_LEFT
                        self.lastSeenRight = False
                    elif self.dataSensor[Const.SENSOR_VISION_HEAD_ID][0] > angle + self.DELTA_ANGLE:
                        mlog("Recupero para el otro lado")
                        self.action = self.ACTION_TURN_RIGHT
                        self.lastSeenRight = True
                    elif (1-self.dataSensor[Const.SENSOR_VISION_HEAD_ID][0]) < self.DELTA_ANGLE * 1.5:
                        mlog("Engancho para la izquierda")
                        self.action = self.ACTION_TURN_RIGHT
                    elif self.dataSensor[Const.SENSOR_VISION_HEAD_ID][0] < self.DELTA_ANGLE * 1.5:
                        mlog("Engancho para la derecha")
                        self.action = self.ACTION_TURN_LEFT
                    else:
                        self.action = self.ACTION_FORWARD'''
            #no es el color buscado 
            elif self.dataSensor.has_key(Const.SENSOR_NOSE_ULTRASONIC_ID):
                #mlog( "GoTo if3")
                # estoy muy cerca entonces retrocedo
                if self.dataSensor[Const.SENSOR_NOSE_ULTRASONIC_ID][0] < 0.1 :  
                    self.action = self.ACTION_BACK
                    rospy.loginfo("pa atras")

                else:
                    if self.lastSeenRight:
                        self.action = self.ACTION_TURN_LEFT
                        self.lastSeenRight = False
                        rospy.loginfo("pa izq")
                    else:
                        self.action = self.ACTION_TURN_RIGHT
                        #self.lastSeenLeft = False
                        rospy.loginfo("pa derecha")
            else: 
                mlog( "GoTo if4")
                #self.action = self.ACTION_TURN_LEFT   
        #else:
            #self.action = self.ACTION_FORWARD
            
        return see




		   
    ##
    # Publica en el topico "topic_operateEngine" la velocidad del motor derecho e izuierdo a ser usada.
    # @param speedRight Velocidad del motor derecho.
    # @param speedLeft Velocidad del motor izquierdo.
    #		   
    def publish(self,speedRight, speedLeft):
        msg = Float64MultiArray()
        msg.data = [self.identify, speedRight, speedLeft]
        self.motores.publish(msg)

    def findObject(self, color, distance, angle):
        #En caso de no ser visto hago wander.
        wander=not self.getAction(color, distance, angle)
 
        if wander and self.changeTime < rospy.Time.now(): 
            if self.action == self.ACTION_FORWARD or self.action == self.ACTION_BACK:
                if randint(0, 1) == 0:
                    self.action = self.ACTION_TURN_LEFT
                else:
                    self.action = self.ACTION_TURN_RIGHT
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
         
         
        #rospy.loginfo("action " + str( self.action )+ " color "+str(color)+str(wander)) 

  
 
  

    #se deben de mandar mensajes continuamente si se ejecuta tanto como si no a los motores
    def perform(self):
        if self.cumplePrecondiciones () and self.nivelActivacion>0 and self.motorLibre:
            
            # SE DEBE RECIBIR EL PARAMETROS DEL COLOR DISTANCIA Y ANGULO.
            head=[-1,-1]
            if self.parametros.has_key(Const.SENSOR_VISION_HEAD_ID):
                head=self.parametros[Const.SENSOR_VISION_HEAD_ID]
            dist=[200]
            if self.parametros.has_key(Const.SENSOR_NOSE_ULTRASONIC_ID):    
                dist=self.parametros[Const.SENSOR_NOSE_ULTRASONIC_ID]
            self.findObject(head[1], dist[0], head[0])
#            #rospy.loginfo(">>>ON GoTo id:"+str(self.identify))
            ##rospy.loginfo( nivelActivacion)
            self.ejecutando=True
            msg2 = Int32MultiArray()  
            msg2.data = [self.identify,self.identify] #por si necesito otro parametro        
            self.nodoEjecutando.publish(msg2) 
        else: 
#           #rospy.loginfo(">>>OFF GoTo id:"+str(self.identify))
            self.ejecutando=False






    def similarHeadSensor(self, headSens, l):
        aux =False 
        indObj=-1
        i = 1
        
        while ((not aux) and (i < len(l))):
            indObj=indObj+1
            aux = aux or headSens.similar([l[i - 1], l[i]])
            i = i + 4

        #rospy.loginfo("EN SIMILAR HEAD SENSOR LOS DATOS SON " + str(l) + " Y LA SALIDA ES " + str(aux))
        if aux:
            return indObj
        return -1
           
 
    def activateOnEjecution(self,data): 
       activate=False
       if (not data.has_key(Const.SENSOR_VISION_HEAD_ID)) or (not data.has_key(Const.SENSOR_NOSE_ULTRASONIC_ID)):
           return False    
       #rospy.loginfo("Estoy en veriPosSenEjecutar")
       headSens = SensorFactory.get(Const.SENSOR_VISION_HEAD_ID,     self.parametros[Const.SENSOR_VISION_HEAD_ID])
       ultrSens = SensorFactory.get(Const.SENSOR_NOSE_ULTRASONIC_ID, self.parametros[Const.SENSOR_NOSE_ULTRASONIC_ID])
       msgLight = Int32MultiArray()       
       
       
       esSimiliar=self.similarHeadSensor(headSens, data[Const.SENSOR_VISION_HEAD_ID])
       if esSimiliar==self.getIndObjMoreNear(data[Const.SENSOR_VISION_HEAD_ID])  and ultrSens.similar(data[Const.SENSOR_NOSE_ULTRASONIC_ID])   :       
           #rospy.loginfo("CUMPLE POSTCONDICION IR_A PARA " + str(self.identify) + " CON DISTANCIA " + str(self.parametros[Const.SENSOR_NOSE_ULTRASONIC_ID]) + ", COLOR Y ANGULO " + str(self.parametros[Const.SENSOR_VISION_HEAD_ID]))
           msgLight.data = [self.identify,1]
           self.light.publish(msgLight)
           activate=True
       else:
           #rospy.loginfo("NO CUMPLE POSTCONDICION IR_A PARA " + str(self.identify))
           msgLight.data = [self.identify,0]
           self.light.publish(msgLight)
       #rospy.loginfo("Active GoTo" + str(activate))       
       return activate

 
 
    def activateOnDemonstration(self, data): 
        activate=False
        if (not data.has_key(Const.SENSOR_VISION_HEAD_ID)) or (not data.has_key(Const.SENSOR_NOSE_ULTRASONIC_ID)):
            return False
  
            
        headSensor = data[Const.SENSOR_VISION_HEAD_ID]
        noseSensor = data[Const.SENSOR_NOSE_ULTRASONIC_ID]       
        ##rospy.loginfo("EL COLOR EN IR_A ES " + str(headSensor[1]))       
        #esta entre los colores es la unica condicion a verificar
        #ya que se verifico que hay lectura de distancua mas arriba
        aux=self.getIndObjMoreNear(headSensor)
        if self.prevColor==None or self.prevColor != headSensor[aux*4+1]:
            self.prevColor = headSensor[aux*4+1]
            self.minDist=200
            self.angMinDist=10
            return False
        
        
        cond0=  headSensor[aux*4+1] in self.colorValido  
        cond1= noseSensor[0] > self.safeDist 
        #rospy.loginfo("color a aprender "+str(headSensor[aux*4+1])+str(cond0))
        '''
        cond1=self.PARAM_DISTANCE - self.DELTA_DISTANCE <= noseSensor 
        cond2=noseSensor[0] <= self.PARAM_DISTANCE + self.DELTA_DISTANCE  
        cond3=self.PARAM_ANGLE - self.DELTA_ANGLE <= headSensor[0] 
        cond4=headSensor[0] <= self.PARAM_ANGLE + self.DELTA_ANGLE       
        if cond0 and cond1 and cond2 and cond3 and cond4:       
        '''
        if cond0 and cond1:           
           #rospy.loginfo("SE CUMPLE POSTCONDICION IR A")
           activate=True
           #rospy.loginfo("Active GoTo" + str(activate))
           #rospy.loginfo("color = " + str(headSensor[aux*4+1]) + " distancia  = " + str(noseSensor) + " angulo = " + str(headSensor[aux*4]))
        return activate


 
    def getBehaviorParameters(self,data): 
        #rospy.loginfo("getparaprendidos ir a "+str(data))
        proxim=[]
        head=[]
        outHead=""
        outProxim=""
        esDistMin=False  
        
        if data.has_key(Const.SENSOR_NOSE_ULTRASONIC_ID):   
            proxim=data[Const.SENSOR_NOSE_ULTRASONIC_ID] 
            #se queda con la minima distancia
            if proxim[0] <= self.minDist:
                esDistMin=True
                self.minDist=proxim[0]                
            outProxim=str (Const.SENSOR_NOSE_ULTRASONIC_ID) + "#" +str(self.minDist) 
        else:
            self.minDist=200
            self.angMinDist=10
        if data.has_key(Const.SENSOR_VISION_HEAD_ID):
            head=data[Const.SENSOR_VISION_HEAD_ID]
            idObj=self.getIndObjMoreNear(head)   
            #si es la minima distancia se guarda el angulo
            if esDistMin:
                self.angMinDist=head[4*idObj]
            outHead=str (Const.SENSOR_VISION_HEAD_ID) + "#" +str(self.angMinDist) + "#" +str(head[4*idObj+1]) 

        salida=""
        if len(outHead)>0:
            salida=salida+outHead 
        if len(outProxim)>0:
            if len(salida):
                salida=salida+ "|"
            salida=salida+outProxim 
        return salida



if __name__ == '__main__':

    print "iniciando GoTo"  
    rospy.init_node('GoTo', anonymous=True) 
    #aca se recibe string se desenvuelve y se obtiene id y parametros       
    datos=str(rospy.myargv(argv=sys.argv)[1])
    #rospy.loginfo("datos GoTo "+str(datos)) 
    i = GoTo(datos)
    rospy.spin()
    i.endTopic()
    rospy.signal_shutdown("Bye!")





#    def getAction(self, color, distance, angle):
#        see = False        
#        sensoVision = self.dataSensor.has_key(Const.SENSOR_VISION_HEAD_ID) 
#        if sensoVision :  
#            #rospy.loginfo("VISTO")   
#            see = True  
#            if self.dataSensor[Const.SENSOR_VISION_HEAD_ID][1] == color: 
#                if self.dataSensor.has_key(Const.SENSOR_NOSE_ULTRASONIC_ID):                
#                    if self.dataSensor[Const.SENSOR_NOSE_ULTRASONIC_ID][0] > distance + self.DELTA_DISTANCE:
#                        self.action = self.ACTION_FORWARD
#                    elif self.dataSensor[Const.SENSOR_NOSE_ULTRASONIC_ID][0] < distance - self.DELTA_DISTANCE:
#                        self.action = self.ACTION_BACK
#                    elif self.dataSensor[Const.SENSOR_VISION_HEAD_ID][0] < angle + self.DELTA_ANGLE:
#                        self.action = self.ACTION_TURN_LEFT
#                    elif self.dataSensor[Const.SENSOR_VISION_HEAD_ID][0] > angle - self.DELTA_ANGLE:
#                        self.action = self.ACTION_TURN_RIGHT
#                else:
#                    self.action = self.ACTION_FORWARD
#            #no es el color buscado 
#            elif self.dataSensor.has_key(Const.SENSOR_NOSE_ULTRASONIC_ID):
#                # estoy muy cerca entonces retrocedo
#                if self.dataSensor[Const.SENSOR_NOSE_ULTRASONIC_ID][0] < 0.1 :  
#                    self.action = self.ACTION_BACK
#                elif randint(0, 1) == 0:
#                    self.action = self.ACTION_TURN_LEFT 
#        return see









