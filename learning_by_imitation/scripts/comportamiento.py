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
from std_msgs.msg import Int32MultiArray, Float64MultiArray,String
from random import randint
import Const



class comportamiento(object):
 
    
    motores = rospy.Publisher('topicoActuarMotores', Float64MultiArray, queue_size=10) 
    postCondDet   = rospy.Publisher('topicoPostCondDet',String , queue_size=10) #usado para aprender 
    preCondDet = rospy.Publisher('preConditionDetect',Int32MultiArray , queue_size=10) #usado para ejecutar 
    nivel = rospy.Publisher('topicoNivel', Int32MultiArray, queue_size=10) 
    nodoEjecutando=rospy.Publisher('topicoNodoEjecutando', Int32MultiArray, queue_size=10) 
    solicitarOLiberarMotores=rospy.Publisher('topicosolicitarOLiberarMotores', Int32MultiArray, queue_size=10)


    topicoSen=None
    topicoPre=None
    topicoSet=None
    topicoEst=None
    topicoNiv=None
    topicoCam=None
    topicoEje=None
    topicoAct=None
    topicoOrd=None

    borrando=False


    '''
    motores = None
    postCondDet = None
    preCondDet = None
    nivel = None
    nodoEjecutando = None
    solicitarOLiberarMotores = None
    '''

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
    dataSensor={}

    def __init__(self,data):
        bloques=self.separarBloques(data) 
        self.identify=int(bloques[0])
 
        rospy.loginfo("comportamiento datos bloques"+str(bloques))
        del bloques[0]
        self.parametros=self.separarSensados(bloques)
        self.initTopicos()
        rospy.on_shutdown(self.endTopic)


    #se deben de mandar mensajes continuamente si se ejecuta tanto como si no a los motores
    def actuar( self ):
        pass              

    def veriPosSenEjecutar(self,data):
        pass
        
    def getParAprendidos(self):
        pass

    def veriPosSenAprender(self, data):
        pass


#############################
#procesado de sensores
###########################

    def processSensorLineDetectedColorData(self,data):
        self.dataSensorColor = [data[0], data[1], data[2]]


    def processProximitySensorData(self,data): 
        if data.data[1] < 0.25:
            self.action = self.ACTION_BACK
            print "ATRAS"
        #print data.data

 

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
	        #rospy.loginfo("entro en evaluarporcaminos "+str(self.identify)+" " +str(salida) + str(self.caminos))
	        return salida  

    
    def separarBloques(self,data):
        #rospy.loginfo("comportamiento datos recibidos"+str(data))
        return map(str, data.split('|'))
        
    #devuelve un diccionario con clave id del sensor 
    #values una lista de datos sensados
    def separarSensados(self,separar):
        sensados={}
        for s in  separar:
            if len(s)>1:
            	#rospy.loginfo(str(len(s))+"separar "+s)
            	datos = map(float, s.split('#'))
            	print s,datos
            	idSensor=int (datos[0])
            	del datos[0]
            	sensados[idSensor]=datos        
        return sensados


    #posiblemente haya mas sensores, se debe realizar una lectura de todos los sensores
    # y luego de esto verificar si el estado es de ejecucion
    def atenderSensores(self,data):
        #se verifican las condiciones en base a los sensores

        print "aprender id>",self.identify 
        

        valorEncendido=0
        bloques=self.separarBloques(data.data)
        self.dataSensor=self.separarSensados(bloques)        
        rospy.loginfo(str(self.dataSensor))
        
        
        if self.estado ==2:
            if self.veriPosSenEjecutar(self.dataSensor):
                print "se cumple postcondicion id>",self.identify, self.dataSensor
                valorEncendido=1  
        elif self.estado ==1 or self.estado ==3:  
            if self.veriPosSenAprender(self.dataSensor):
                print "se cumple postcondicion id>",self.identify, self.dataSensor
                valorEncendido=1            
            
         
        ##rospy.loginfo(estado)
        if self.estado ==1 and self.identify==-1:#aprender el -1 es para que contesten nodos lanzados para aprender	
            #msg.data = [self.idComportamiento,valorEncendido]#se envia el id del comportamiento cuando se aprende
            msgString=String()
            msgString.data = str(self.idComportamiento) + "#" + str(valorEncendido) 
            if valorEncendido==1:
                param= str(self.getParAprendidos(self.dataSensor))
                if len (param):
                    msgString.data = msgString.data + "|" + param            
                 #"|0#1#1#1"
            
            self.postCondDet.publish(msgString)
            rospy.loginfo("encendido "+str(valorEncendido)+"idCOmp :"+str(self.idComportamiento))
        elif self.estado ==2:#ejecutar
            msg = Int32MultiArray()
            cumplePrecondiciones=self.evaluarPrecondicionesPorCaminos()
            nodoEjecutable = cumplePrecondiciones and self.nivelActivacion > 0
            #rospy.loginfo("nodo ejecutable id:"+str(self.identify)+" "+str(nodoEjecutable))
            #rospy.loginfo("post detec id:"+str(self.identify)+" "+str(valorEncendido and nodoEjecutable))
            
            #se deben cumplir postcondiciones pero ademas precondiciones para enviar un dato true
            #esto para evitar que un nodo envie de orden cuando aun no deberia
            preCD=0
            if valorEncendido and cumplePrecondiciones:
                preCD=1
            msg.data = [self.identify,preCD]   #cuando se ejecuta se envia el id del nodo
            self.preCondDet.publish(msg)	
            msg.data = [self.identify,nodoEjecutable,-1]  
            self.solicitarOLiberarMotores.publish(msg)	
            self.actuar()	
            ##rospy.loginfo("localizar ",valorEncendido)


    def realizarBad(self,borrar):
        global borrando
        borrando=True
        msg = Int32MultiArray()

        #se borran de permanencia y de habilitacion y se agregan de orden y se da cumplidos
        if self.permanent.has_key(borrar):
            del self.permanent[borrar]
            self.ordering[borrar]=True
        if  self.enablig.has_key(borrar): 
            del self.enablig[borrar]
            self.ordering[borrar]=True
            
        #se agrega de orden si no esta  en vez del borrado  
        if self.ordering.has_key(borrar):
            self.ordering[borrar]=True
            

        #if self.identify== data:#por las dudas hago que todos liberen los actuadores
        borrando=False
        msg.data = [self.identify,0,-1]  
        self.solicitarOLiberarMotores.publish(msg)	


        #fata matar al nodo bad

    def atenderOrdenes(self,data):
        if data.data[0]==0:
            self.realizarBad(data.data[1])     

	
    def setEstado(self,data):  
        self.estado=data.data[0]
        if self.estado==3:
            #se detienen los motores estamos en estado come 
            msg = Float64MultiArray() 
            msg.data = [self.identify,0,0] 	 
            self.motores.publish(msg) 
        #rospy.loginfo("estado"+str(self.estado))
        elif self.estado==4:
            nodoABorrar=data.data[1]
            self.realizarBad(nodoABorrar)
 




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
        #rospy.loginfo("entro en setting id>"+ str(self.identify) )
	
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
            #rospy.loginfo(self.caminos)

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
        try:
            #  #rospy.loginfo("Entro en nivel")
            msg = Int32MultiArray() 
    
            if data.data[1] == self.identify:
                #rospy.loginfo("me llego nivel id>"+str(data.data[2])+": "+str(self.identify)+"<<"+str(data.data[0]))
                #no se suman niveles solo se verifica si es uno o cero
                self.nivelActivacion=data.data[2]
                nivelAtras=0
                if data.data[2] !=0 and not self.evaluarPrecondicionesPorCaminos(): 
                    nivelAtras=1         
    	            
                #se verifica si hay un camino cumplido se les manda a los predecesores inmediaros mensajes a 0
                #sino se envia mensaje de nivel 1 
    
                for c in self.caminos:
                    rospy.loginfo("lacan "+ str(len(c)))
                    ultimoNodo=c[len(c)-1] #ultimo nodo del camino previo
                    msg.data = [self.identify, ultimoNodo,nivelAtras]#manda para atras el nivel  
                    self.nivel.publish(msg)

        except: # catch *all* exceptions
            e = sys.exc_info()[0]
            rospy.loginfo("error "+ str(e)) 

    def evaluarPrecondicion(self,data):#invocado en etapa de ejecucion cuando llega una postcondicion
        print "entro en evaluarPrecondicion id>",self.identify 
        comportamiento=data.data[0] 
        postcondicion=data.data[1]
        try:
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
        except: # catch *all* exceptions
            e = sys.exc_info()[0]
            rospy.loginfo("error "+ str(e)) 

    def atenderMotorLockeado(self,data):   
        if data.data[1] == -1 or data.data[1]== self.identify:   #el valor 0 es para el id del motor
            self.motorLibre=True
        else :
            self.motorLibre=False  




    #se fijan los publicadores
    def setMotores(self,dato):    
        self.motores= dato
     
    #def setPostConditionDetect(self,dato):  
    #    self.postCondDet=dato 
        
    def setPreConditionDetect(self,dato): 
        self.preCondDet=dato
    
    def setNivel(self,dato):  
        self.nivel=dato
        
    def setNodoEjecutando(self,dato): 
        self.nodoEjecutando=dato
    
    
    def SetSLMotores (self,dato): 
        self.solicitarOLiberarMotores=dato 
   
    def setIdComp(self,dato):
        self.idComportamiento=dato
    
    
    def endTopic(self):    
        self.topicoSen.unregister() 
        self.topicoPre.unregister()
        self.topicoSet.unregister() 
        self.topicoEst.unregister() 
        self.topicoNiv.unregister() 
        self.topicoCam.unregister() 
        self.topicoEje.unregister() 
        self.topicoAct.unregister()    
        self.topicoOrd.unregister()    
        return 0
    
    def initTopicos(self):
                 
        self.topicoOrd=rospy.Subscriber("topicoOrdenes", Int32MultiArray, self.atenderOrdenes)         
        self.topicoSen=rospy.Subscriber("topicoSensores", String, self.atenderSensores)
        self.topicoPre=rospy.Subscriber("preConditionDetect", Int32MultiArray, self.evaluarPrecondicion)
        self.topicoSet=rospy.Subscriber("preConditionsSetting", Int32MultiArray, self.setting)	    
        self.topicoEst=rospy.Subscriber("topicoEstado", Int32MultiArray, self.setEstado)
        self.topicoNiv=rospy.Subscriber("topicoNivel", Int32MultiArray, self.atenderNivel)
        self.topicoCam=rospy.Subscriber("topicoCaminos", Int32MultiArray, self.atenderCaminos)
        self.topicoEje=rospy.Subscriber("topicoNodoEjecutando", Int32MultiArray, self.atenderNodoEjecutando)
        self.topicoAct=rospy.Subscriber("topicoMotorLockeado", Int32MultiArray, self.atenderMotorLockeado)
        rospy.Subscriber("finalize", String, self.finalize)


    def finalize(self, data):
        rospy.signal_shutdown("Bye!")

    
