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
from std_msgs.msg import Int32MultiArray, Float64MultiArray
from random import randint




class comportamiento(object):

    motores = None
    postConditionDetect = None
    preConditionDetect = None
    nivel = None
    nodoEjecutando = None
    solicitarOLiberarMotores = None
    identify=-1#modicar mediante mensajes al lanzar el nuevo nodo
    idComportamiento = -1
    reejecutar=True
    ejecutando=False
    permanent = {}
    enablig = {}
    ordering = {}
    nivelActivacion=0
    estado=1
    motorLibre=False
    caminos=[]
    speed = 1
    parametros=None

    def __init__(self):
        print "nada"


    #se deben de mandar mensajes continuamente si se ejecuta tanto como si no a los motores
    def actuar( self ):
        pass              

    def verificarPoscondicionesSensores(self,data):
        pass


    def processSensorLineDetectedColorData(self,data):
        self.dataSensorColor = [data.data[1], data.data[2], data.data[3]]


    def processProximitySensorData(self,data): 
        if data.data[1] < 0.25:
            self.action = self.ACTION_BACK
            print "ATRAS"
        #print data.data


    def atenderMotorLockeado(self,data):   
        if data.data[1] == -1 or data.data[1]== self.identify:   #el valor 0 es para el id del motor
            self.motorLibre=True
        else :
            self.motorLibre=False  




    def evaluarPrecondicionesPorCaminos(self): 
	        salida=True
	        #Se evalua para cada camino si se cumplen las precondiciones para cada nodo del camino
	        for c in range (len(self.caminos)):
	            salida=True
	            #para un camino se cumplen todas las precondiciones de los nodos
	            for n in self.caminos[c]:
	                if self.permanent.has_key(n):
	                    if not self.permanent[n]:
	                        salida= False #si una precondicion no se cumple todo el camino es no cumpido
	                        break 
	                if self.enablig.has_key(n):
	                    if not self.enablig[n] and not self.ejecutando:#ADEMAS VERIFICAR QUE NO SE ESTA EJECUTANDO
	                        salida= False
	                        break  
	                if self.ordering.has_key(n):
	                    if not self.ordering[n]:
	                        salida= False
	                        break 
	            #en caso de que en la recorrida un camino cumplio todas las precondiciones se termina el ciclo
	            if salida:
	                break
	        rospy.loginfo("entro en evaluarporcaminos "+str(self.identify)+" " +str(salida) + str(self.caminos))
	        return salida  










    #posiblemente haya mas sensores, se debe realizar una lectura de todos los sensores
    # y luego de esto verificar si el estado es de ejecucion
    def atenderSensores(self,data):
        #se verifican las condiciones en base a los sensores

        print "aprender id>",self.identify 
        msg = Int32MultiArray()

        valorEncendido=0
        if self.verificarPoscondicionesSensores(data):
            print "se cumple postcondicion id>",self.identify 
            valorEncendido=1            
        else:#redundante solo para ver que paso
            print "se apago postcondicion id>",self.identify 
         
        #rospy.loginfo(estado)
        if self.estado ==1 and self.identify==-1:#aprender el -1 es para que contesten nodos lanzados para aprender	
            msg.data = [self.idComportamiento,valorEncendido]#se envia el id del comportamiento cuando se aprende
            self.postConditionDetect.publish(msg)
        elif self.estado ==2:#ejecutar
            cumplePrecondiciones=self.evaluarPrecondicionesPorCaminos()
            nodoEjecutable = cumplePrecondiciones and self.nivelActivacion > 0
            rospy.loginfo("nodo ejecutable id:"+str(self.identify)+" "+str(nodoEjecutable))
            rospy.loginfo("post detec id:"+str(self.identify)+" "+str(valorEncendido and nodoEjecutable))
            msg.data = [self.identify,valorEncendido]   #cuando se ejecuta se envia el id del nodo
            self.preConditionDetect.publish(msg)	
            msg.data = [self.identify,nodoEjecutable,-1]  
            self.solicitarOLiberarMotores.publish(msg)	
            self.actuar()	
            #rospy.loginfo("localizar ",valorEncendido)

	
    def setEstado(self,data):  
        self.estado=data.data[0]
        if self.estado==3:
            #se detienen los motores estamos en estado come 
            msg = Int32MultiArray() 
            msg.data = [self.identify,0,0] 	 
            self.motores.publish(msg) 
        rospy.loginfo("estado"+str(self.estado))




        #cuando un nodo ejecuta avisa que lo hace hasta que un nuevo comportamiento no ejecute no avisa
        #supongamos que el comportamiento habilante se esta ejecutandode de pronto el comportamiento que es habilitado recibe de sensore
        #la senal que esperaba pasa a estar activo avisa de este hecho...luego cuando se pregunte por el enlace de habilitacion se preguntara
        #si esta ejecutando y no importaria ya si el habilitante esta o no activo  
    def atenderNodoEjecutando(self,data):
        if  data.data[0] == self.identify:
            self.ejecutando=True
        else:    
            self.ejecutando=False
	            
	            
	            

    def cumplePrecondiciones(self):
        #salida = evaluation(permanent.values()) and (ejecutando or evaluation(enablig.values()) )
        # and evaluation(ordering.values()) #si esta ejecutando no se evalua enabling
        salida = self.evaluarPrecondicionesPorCaminos()
        print "cumplePrecondiciones ",salida
        return salida
        

  


    def setting(self,data):
                rospy.loginfo("entro en setting id>"+ str(self.identify) )
	
	        # data.data[0] = fromCompID, data.data[1] = toCompID, data.data[2] = linkType. linkType puede ser permantente(0), de orden(1) o de habilitacion(2)
                if data.data[1] == self.identify:
                        print "es mi id"
                        if data.data[2] == 2:
                                self.permanent[data.data[0]] = False
                                print "permanente "
                                print len(self.permanent)
                        elif data.data[2] == 1:
                                print "habilitacion "
                                self.enablig[data.data[0]] = False
                        elif data.data[2] == 0:
                                print "orden "
                                self.ordering[data.data[0]] = False

 


    def atenderCaminos(self,data): 
        #si es mi id agrego la lista de caminos camino el nodo
        if data.data[0] == self.identify:
            #elimina de la lista el dato del id
            lista=list(data.data)        
            #print lista
            del lista[0]

            self.caminos= self.separarCaminos(lista)
            rospy.loginfo(self.caminos)

    def separarCaminos(self,caminitos):
        salida = []
        inicio=0
        fin=0
        guardaSeparacion=-10
        while inicio< len (caminitos):    
            fin=caminitos.index(guardaSeparacion,inicio)
            #print fin
            tramo=caminitos[inicio:fin]
            #print tramo
            salida.append(tramo) 
            inicio=fin+1    
        return salida

    def atenderNivel (self,data):
        #  rospy.loginfo("Entro en nivel")
        msg = Int32MultiArray() 

        if data.data[1] == self.identify:
            rospy.loginfo("me llego nivel id>"+str(data.data[2])+": "+str(self.identify)+"<<"+str(data.data[0]))
            #no se suman niveles solo se verifica si es uno o cero
            self.nivelActivacion=data.data[2]
            nivelAtras=0
            if data.data[2] !=0 and not self.evaluarPrecondicionesPorCaminos(): 
                nivelAtras=1         
	            
            #se verifica si hay un camino cumplido se les manda a los predecesores inmediaros mensajes a 0
            #sino se envia mensaje de nivel 1 

            for c in self.caminos:
                ultimoNodo=c[len(c)-1] #ultimo nodo del camino previo
                msg.data = [self.identify, ultimoNodo,nivelAtras]#manda para atras el nivel  
                self.nivel.publish(msg)




    def evaluarPrecondicion(self,data):#invocado en etapa de ejecucion cuando llega una postcondicion
        print "entro en evaluarPrecondicion id>",self.identify 
        comportamiento=data.data[0] 
        postcondicion=data.data[1]

        if self.permanent.has_key(comportamiento):
            self.permanent[comportamiento] = postcondicion == 1
            if self.permanent[comportamiento]:
                print "es permanente"
            else:
                print "salio de permanente"
        elif self.enablig.has_key(comportamiento):
            self.enablig[comportamiento] = postcondicion == 1
            if self.enablig[comportamiento] or self.ejecutando:#si se esta ejecutando no importa que se apague
                print "esta habilitado"	
            else:
                print "se inhabilito"
        elif self.ordering.has_key(comportamiento):
            self.ordering[comportamiento] = self.ordering[comportamiento] or (postcondicion == 1)
            print "es de orden"


    #se fijan los publicadores
    def setMotores(self,dato):    
        self.motores= dato
     
    def setPostConditionDetect(self,dato):  
        self.postConditionDetect=dato 
        
    def setPreConditionDetect(self,dato): 
        self.preConditionDetect=dato
    
    def setNivel(self,dato):  
        self.nivel=dato
        
    def setNodoEjecutando(self,dato): 
        self.nodoEjecutando=dato
    
    
    def SetSLMotores (self,dato): 
        self.solicitarOLiberarMotores=dato 
   
    def setIdComp(self,dato):
        self.idComportamiento=dato
    
    
    
    
    
    
