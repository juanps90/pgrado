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
from std_msgs.msg import String, Int32MultiArray
from random import randint


postConditionDetect = None

identify=-1#modicar mediante mensajes al lanzar el nuevo nodo
idComportamiento = 2
reejecutar=True
ejecutando=False
permanent = {}
enablig = {}
ordering = {}
nivelActivacion=0
estado=1
motorLibre=False
caminos=[]



#se deben de mandar mensajes continuamente si se ejecuta tanto como si no a los motores
def actuar():
    global motores
    global motorLibre  
    msg = Int32MultiArray()
    if cumplePrecondiciones () and nivelActivacion>0 and motorLibre:
        # Aca iria la operacion de wander.  
        azar=randint(0,9)
        if identify == 3:
            msg.data = [identify,0,-azar]
        else:
            msg.data = [identify,0,azar]      
        
           
         	 
        motores.publish(msg)             
        rospy.loginfo(">>>ON avanzar id:"+str(identify))
        #rospy.loginfo( nivelActivacion) 
        ejecutando=True
        msg.data = [identify,identify] #por si necesito otro parametro        
        nodoEjecutando.publish(msg) 
        
    else: 
	rospy.loginfo(">>>OFF avanzar id:"+str(identify))
	ejecutando=False
	'''
	msg.data = [identify,0,0] 	 
        motores.publish(msg)
        '''
        
        
def atenderMotorLockeado(data): 
    global motorLibre       
    if data.data[1] == -1 or data.data[1]== identify:   #el valor 0 es para el id del motor
        motorLibre=True
    else :
        motorLibre=False
  
          
        
        

def verificarPoscondicionesSensores(data):
    activate=False
    if  data.data[0] == 2:
        print "se cumple postcondicion avanzar"
	activate=True
    elif cumplePrecondiciones():#cumple precondiciones y no cumple postcondicion
	#actuar()
	print "no se cumple postcondicion"
    return activate




def atenderSensores(data):
    #se verifican las condiciones en base a los sensores
    verificarPoscondicionesSensores(data)

    print "aprender avanzar"
    global postConditionDetect
    global preConditionDetect
    global estado
    global solicitarOLiberarMotores
    msg = Int32MultiArray()

    
    valorEncendido=0
    if verificarPoscondicionesSensores(data):
        print "se cumple postcondicion avanzar"
        valorEncendido=1            
    else:#redundante solo para ver que paso
	#rospy.loginfo("se apago postcondicion avanzar")
	valorEncendido=0       
    print "call avanzar"
    #rospy.loginfo(estado)
    if estado ==1 and identify==-1:#aprender el -1 es para que contesten nodos lanzados para aprender	
	msg.data = [idComportamiento,valorEncendido]#se envia el id del comportamiento cuando se aprende
	postConditionDetect.publish(msg)
    elif estado ==2:#ejecutar
        nodoEjecutable = evaluarPrecondicionesPorCaminos() and nivelActivacion>0
        
        rospy.loginfo("nodo ejecutable avanzar id:"+str(identify)+" "+str(nodoEjecutable))
        rospy.loginfo("post detec avanzar id:"+str(identify)+" "+str(valorEncendido and nodoEjecutable))
	msg.data = [identify,valorEncendido and nodoEjecutable]   #cuando se ejecuta se envia el id del nodo
	preConditionDetect.publish(msg)
	
	msg.data = [identify,nodoEjecutable,-1]  
	solicitarOLiberarMotores.publish(msg)
	
	
	
	actuar()
    



    
    
def setEstado(data):    
    global estado
    estado=data.data[0]
    if estado==3:
	#se detienen los motores estamos en estado come 
	msg = Int32MultiArray() 
	msg.data = [identify,0,0] 	 
        motores.publish(msg) 
    rospy.loginfo("estado"+str(estado))
    

#cuando un nodo ejecuta avisa que lo hace hasta que un nuevo comportamiento no ejecute no avisa
#supongamos que el comportamiento habilante se esta ejecutandode repente el comportamiento que es habilitado recibe de sensore
#la senal que esperaba pasa a estar activo avisa de este hecho...luego cuando se pregunte por el enlace de habilitacion se preguntara
#si esta ejecutando y no importaria ya si el habilitante esta o no activo  
def atenderNodoEjecutando(data):
    if  data.data[0] == identify:
        ejecutando=True
    else:    
        ejecutando=False



def cumplePrecondiciones():
    #salida = evaluation(permanent.values()) and (ejecutando or evaluation(enablig.values()) ) and evaluation(ordering.values()) #si esta ejecutando no se evalua enabling
    salida = evaluarPrecondicionesPorCaminos()
    print "cumplePrecondiciones ",salida
    return salida
    
    
 

 
def evaluarPrecondicionesPorCaminos():
    global caminos
    global permanent
    global enablig
    global ordering 
    salida=True
    #Se evalua para cada camino si se cumplen las precondiciones para cada nodo del camino
    for c in range (len(caminos)):
        salida=True
        #para un camino se cumplen todas las precondiciones de los nodos
        for n in caminos[c]:
            if permanent.has_key(n):
                if not permanent[n]:
                    salida= False
                    break 
            if enablig.has_key(n):
                if not enablig[n]:#ADEMAS VERIFICAR QUE NO SE ESTA EJECUTANDO
                    salida= False
                    break  
            if ordering.has_key(n):
                if not ordering[n]:
                    salida= False
                    break 
        if salida:
            break
    rospy.loginfo("entro en evaluarporcaminos "+str(identify)+" " +str(salida) + str(caminos))
    return salida 


def setting(data):
    print "entro en setting avanzar "
    
    # data.data[0] = fromCompID, data.data[1] = toCompID, data.data[2] = linkType. linkType puede ser permantente(0), de orden(1) o de habilitacion(2)
    if data.data[1] == identify:
        print "es mi id"
        if data.data[2] == 2:
            permanent[data.data[0]] = False
	    print "permanente "
            print len(permanent)
        elif data.data[2] == 1:
            print "habilitacion "
            enablig[data.data[0]] = False
        elif data.data[2] == 0:
            print "orden "
            ordering[data.data[0]] = False

'''
    global reejecutar
    if data.data[0] == identify and data.data[2] == 2:#soy origen de un enlace permamente
	reejecutar = True
    print "reejecutar ",reejecutar
'''

'''
def atenderCaminos(data):
    global pathPosibles
    #si es mi id agrego a la lista de un camino el nuevo nodo
    if data.data[0] == identify: 
        lista=list(data.data)
        indice=data.data[1]
        #se borran los primeros datos y queda la lista con el path
        del lista[0]
        del lista[0]
        pathPosibles[indice]=lista
        #print lista
'''   
    
    
def atenderCaminos(data):
    global caminos
    #si es mi id agrego la lista de caminos camino el nodo
    if data.data[0] == identify:
        #elimina de la lista el dato del id
        lista=list(data.data)        
        #print lista
        del lista[0]
        
        caminos= separarCaminos(lista)
        print caminos

def separarCaminos(caminos):
    salida = []
    inicio=0
    fin=0
    guardaSeparacion=-10
    while inicio< len (caminos):    
        fin=caminos.index(guardaSeparacion,inicio)
        #print fin
        tramo=caminos[inicio:fin]
        #print tramo
        salida.append(tramo) 
        inicio=fin+1    
    return salida  
    
    
    
    
    
    

def atenderNivel (data):
  #  rospy.loginfo("Entro en nivel")
    msg = Int32MultiArray()
    global nivelActivacion
    #inicializar el nivel 
    if data.data[1] == -1:#el segundo valor se usa solo reiniciar si es -1 sino es el id objetivo          
        nivelActivacion=0
        rospy.loginfo("me llego nivel a 0 avanzar  id:"+str(identify) )   
    elif data.data[1] == identify:
	nivelActivacion=nivelActivacion+1
        rospy.loginfo("me llego nivel avanzar  "+str(identify)+"<-"+str(data.data[0]))
        
        #se recorre la lista de predecesores solo se verifican para cada nodo final si alguno se cumple no se manda
        #para atras, si ninguno se cumple manda a todos esos nodos finales
        listaNodosAEnviarNivel=[]
        for c in caminos:
            ultimoNodo=c[len(c)-1] #ultimo nodo del camino previo
            #se verifica a cual de los link pertenece
            if permanent.has_key(ultimoNodo):
                #si no cumple precondicion se agrega a la lista a enviar
                if not permanent[ultimoNodo]: 
                    if not ultimoNodo in listaNodosAEnviarNivel:
                        listaNodosAEnviarNivel.append(ultimoNodo) 
                else:
                    #si cumple se limpia la lista porque este camino ya se cumple
                    listaNodosAEnviarNivel=[]
                    break                              
            elif enablig.has_key(ultimoNodo): 
                if not enablig[ultimoNodo]: 
                    if not ultimoNodo in listaNodosAEnviarNivel:
                        listaNodosAEnviarNivel.append(ultimoNodo) 
                else:
                    listaNodosAEnviarNivel=[]
                    break        
            elif ordering.has_key(ultimoNodo):
                if not ordering[ultimoNodo]: 
                    if not ultimoNodo in listaNodosAEnviarNivel:
                        listaNodosAEnviarNivel.append(ultimoNodo) 
                else:
                    listaNodosAEnviarNivel=[]
                    break      
                 
	for l in listaNodosAEnviarNivel:
	    msg.data = [identify, l]#manda para atras el nivel  
            nivel.publish(msg)





def evaluarPrecondicion(data):#invocado en etapa de ejecucion cuando llega una postcondicion
    print "entro en ejecutar avanzar"
    global permanent
    global enablig
    global ordering
    comportamiento=data.data[0] 
    postcondicion=data.data[1]

    if permanent.has_key(comportamiento):
        permanent[comportamiento] = postcondicion == 1
	if permanent[comportamiento]:
            print "es permanente"
	else:
	    print "salio de permanente"
    elif enablig.has_key(comportamiento):
        enablig[comportamiento] = postcondicion == 1
        if enablig[comportamiento] or ejecutando:#si se esta ejecutando no importa que se apague
 	    print "esta habilitado"	
	else:
	    print "se inhabilito"
    elif ordering.has_key(comportamiento):
        ordering[comportamiento] = ordering[comportamiento] or (postcondicion == 1)
        print "es de orden"
     

    #global nivelActivacion
    #nivelActivacion=0

  #  if not skip:
#	actuar()

 


if __name__ == '__main__':
    print "iniciando avanzar"  

    rospy.init_node('avanzar', anonymous=True)

    
    #global identify
    identify=int(rospy.myargv(argv=sys.argv)[1])
    rospy.loginfo("identificador avanzar "+str(identify))

    motores = rospy.Publisher('topicoActuarMotores', Int32MultiArray, queue_size=10)
    postConditionDetect = rospy.Publisher('postConditionDetect', Int32MultiArray, queue_size=10) #usado para aprender
    preConditionDetect = rospy.Publisher('preConditionDetect', Int32MultiArray, queue_size=10) #usado para ejecutar
    rospy.Subscriber("input", Int32MultiArray, atenderSensores)
    rospy.Subscriber("preConditionDetect", Int32MultiArray, evaluarPrecondicion)
    rospy.Subscriber("preConditionsSetting", Int32MultiArray, setting)	    
    rospy.Subscriber("topicoEstado", Int32MultiArray, setEstado)
    rospy.Subscriber("topicoNivel", Int32MultiArray, atenderNivel)
    rospy.Subscriber("topicoCaminos", Int32MultiArray, atenderCaminos)
    nivel = rospy.Publisher('topicoNivel', Int32MultiArray, queue_size=10)
    nodoEjecutando=rospy.Publisher('topicoNodoEjecutando', Int32MultiArray, queue_size=10)
    rospy.Subscriber("topicoNodoEjecutando", Int32MultiArray, atenderNodoEjecutando)
    rospy.Subscriber("topicoMotorLockeado", Int32MultiArray, atenderMotorLockeado)
    solicitarOLiberarMotores=rospy.Publisher('topicoSolicitarLockeo', Int32MultiArray, queue_size=10) 
    
    
    rospy.spin()
    