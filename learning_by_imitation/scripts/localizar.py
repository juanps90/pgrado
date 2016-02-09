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
from std_msgs.msg import Int32MultiArray, Float64MultiArray, Float64
from random import randint
import Const


postConditionDetect = None

identify=-1#modicar mediante mensajes al lanzar el nuevo nodo
idComportamiento = 1
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

speed = 10
action = ACTION_BACK
dataSensorColor = [Const.SENSOR_COLOR_DETECT_WHITE, Const.SENSOR_COLOR_DETECT_WHITE, Const.SENSOR_COLOR_DETECT_WHITE]
# delay = 0
# changeTime = 0


def getAction(color):
    global action
    if dataSensorColor[0] == color and dataSensorColor[1] == Const.SENSOR_COLOR_DETECT_WHITE and dataSensorColor[2] == Const.SENSOR_COLOR_DETECT_WHITE:
        action = ACTION_TURN_LEFT
        print "IZQUIERDA"
    elif dataSensorColor[0] == Const.SENSOR_COLOR_DETECT_WHITE and dataSensorColor[1] == Const.SENSOR_COLOR_DETECT_WHITE and dataSensorColor[2] == color:
       action = ACTION_TURN_RIGHT
       print "DERECHA"
    elif dataSensorColor[0] == Const.SENSOR_COLOR_DETECT_WHITE and dataSensorColor[1] == color and dataSensorColor[2] == Const.SENSOR_COLOR_DETECT_WHITE:
       action = ACTION_FORWARD
       print "ADELANTE"
    elif dataSensorColor[0] == color and dataSensorColor[1] == color and dataSensorColor[2] == Const.SENSOR_COLOR_DETECT_WHITE:
       action = ACTION_TURN_LEFT
       print "IZQUIERDA"
    elif dataSensorColor[0] == Const.SENSOR_COLOR_DETECT_WHITE and dataSensorColor[1] == color and dataSensorColor[2] == color:
       action = ACTION_TURN_RIGHT
       print "DERECHA"
    elif dataSensorColor[0] == color and dataSensorColor[1] == color and dataSensorColor[2] == color:
       action = ACTION_TURN_RIGHT
       print "DERECHA"
       
def publish(speedRight, speedLeft):
    global identify
    global motores
    msg = Float64MultiArray()
    msg.data = [identify, speedRight, speedLeft]
    motores.publish(msg)

def wander(color):
    global speed
    global action
    global delay
    global changeTime
    global rate

    getAction(color)        
    
    if action == ACTION_BACK:
        # voy hacia atras
        publish(-speed, -speed)
    elif action == ACTION_FORWARD:
        # sigo hacia adelante
        publish(speed, speed)
    elif action == ACTION_TURN_LEFT:
        # girar a la izquierda
        publish(speed/8, speed/2)
    else:
        # girar a la derecha
        publish(speed/2, speed/8)
    
    if changeTime < rospy.Time.now():
        if dataSensorColor[0] == Const.SENSOR_COLOR_DETECT_WHITE and dataSensorColor[1] == Const.SENSOR_COLOR_DETECT_WHITE and dataSensorColor[2] == Const.SENSOR_COLOR_DETECT_WHITE:
            if action == ACTION_FORWARD or action == ACTION_BACK:
                if randint(0, 1) == 0:
                    action = ACTION_TURN_LEFT
                    print "IZQUIERDA"
                else:
                    action = ACTION_TURN_RIGHT
                    print "DERECHA"
            else:
                 action = ACTION_FORWARD
                 print "ADELANTE"
        delay = randint(2, 9)
        changeTime = rospy.Time.now() + rospy.Duration(delay)
    rate.sleep()

def processSensorLineDetectedColorData(data):
    global dataSensorColor
    dataSensorColor = [data.data[1], data.data[2], data.data[3]]


def processProximitySensorData(data):
    global action
    if data.data[1] < 0.25:
        action = ACTION_BACK
        print "ATRAS"
    #print data.data



#se deben de mandar mensajes continuamente si se ejecuta tanto como si no a los motores
def actuar():
    global motores
    global motorLibre
     
    if cumplePrecondiciones () and nivelActivacion>0 and motorLibre:
        '''
        # Aca iria la operacion de wander.
        msg = Float64MultiArray()  
        if identify == 2:
            msg.data = [identify,-5,-5] 
        else:
            msg.data = [identify,5,5] 
        	 
        motores.publish(msg)     
        '''
        # SE DEBE RECIBIR EL PARAMETRO DEL COLOR DE LA LINEA. POR AHORA ES SOLO NEGRO.
        wander(Const.SENSOR_COLOR_DETECT_BLACK)

        
        rospy.loginfo(">>>ON localizar id:"+str(identify))
        #rospy.loginfo( nivelActivacion)
        ejecutando=True
        msg2 = Int32MultiArray()  
        msg2.data = [identify,identify] #por si necesito otro parametro        
        nodoEjecutando.publish(msg2) 
    else: 
	rospy.loginfo(">>>OFF localizar id:"+str(identify))
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

    #se puede evaluar aca o bien suscribirse a varios topicos y solo llamar a atendersensores (VER CAUL ES MEJOR ESTRATEGIA)
    if data.data[0]==0:
        processSensorLineDetectedColorData(data)

    if data.data[0]==1:
        processProximitySensorData(data)


    
    #esto es para probar con un comportamiento loc con otro color se haria con un topico de parametros     
    if identify==2:
        if data.data[0] == 0 and data.data[2] == 3:
            print "se cumple postcondicion localizar"
	    activate=True
    else:
        if data.data[0] == 0 and (data.data[2] == 0 or data.data[2] == 2):#para que sea de permanencia, hay que revisar
            print "se cumple postcondicion localizar"
	    activate=True
    
    '''
    if data.data[0] == 0 or data.data[0] == 2:#para que sea de permanencia hay que revisar
        print "se cumple postcondicion localizar"
	activate=True	
    elif cumplePrecondiciones():#cumple precondiciones y no cumple postcondicion
	print "no se cumple postcondicion",activate
    '''
    
    
    return activate


#posiblemente haya mas sensores, se debe realizar una lectura de todos los sensores y luego de esto verificar si el estado es de ejecucion
def atenderSensores(data):
    #se verifican las condiciones en base a los sensores
    verificarPoscondicionesSensores(data)

    print "aprender localizar"
    global postConditionDetect
    global preConditionDetect
    global estado
    msg = Int32MultiArray()
    
    valorEncendido=0
    if verificarPoscondicionesSensores(data):
        print "se cumple postcondicion localizar"
        valorEncendido=1            
    else:#redundante solo para ver que paso
	#rospy.loginfo("se apago postcondicion localizar")
	valorEncendido=0       
    print "call localizar"
    #rospy.loginfo(estado)
    if estado ==1 and identify==-1:#aprender el -1 es para que contesten nodos lanzados para aprender	
	msg.data = [idComportamiento,valorEncendido]#se envia el id del comportamiento cuando se aprende
	postConditionDetect.publish(msg)
    elif estado ==2:#ejecutar
        cumplePrecondiciones=evaluarPrecondicionesPorCaminos()
        nodoEjecutable = cumplePrecondiciones and nivelActivacion>0
        rospy.loginfo("nodo ejecutable localizar id:"+str(identify)+" "+str(nodoEjecutable))
        rospy.loginfo("post detec localizar id:"+str(identify)+" "+str(valorEncendido and nodoEjecutable))
	msg.data = [identify,valorEncendido]   #cuando se ejecuta se envia el id del nodo
	preConditionDetect.publish(msg)
	
	msg.data = [identify,nodoEjecutable,-1]  
	solicitarOLiberarMotores.publish(msg)
	
	actuar()
	
	
	
	#rospy.loginfo("localizar ",valorEncendido)
	
    
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
#supongamos que el comportamiento habilante se esta ejecutandode de pronto el comportamiento que es habilitado recibe de sensore
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
    print "entro en setting localizar "
    
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


def atenderCaminos(data):
    global caminos
    #si es mi id agrego la lista de caminos camino el nodo
    if data.data[0] == identify:
        #elimina de la lista el dato del id
        lista=list(data.data)        
        #print lista
        del lista[0]
        
        caminos= separarCaminos(lista)
        rospy.loginfo( caminos)

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
    if data.data[1] == -1:#manda para atras el nivel el segundo valor se usa solo para reiniciar lo hace init           
        nivelActivacion=0
        rospy.loginfo("me llego nivel a 0 localizar  id:"+str(identify) )   
    elif data.data[1] == identify:
	nivelActivacion=nivelActivacion+1
        rospy.loginfo("me llego nivel localizar "+str(identify)+"<-"+str(data.data[0]))
        
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




'''
def nivel (data):
  #  rospy.loginfo("Entro en nivel")
    msg = Int32MultiArray()
    global nivelActivacion
    #inicializar el nivel 
    if data.data[1] == -1:
        nivelActivacion=0
        rospy.loginfo("me llego nivel localizar a 0")   
    elif data.data[1] == identify:
	nivelActivacion=nivelActivacion+1
        rospy.loginfo("me llego nivel localizar id:"+str(identify)+" desde: "+str(data.data[0]))
        msg = Int32MultiArray()
	for p in permanent:
	    if not permanent[p] :
	        msg.data = [identify, p]#manda para atras el nivel
                nivel.publish(msg)	
	for e in enablig:
	    if not enablig[e] and not ejecutando:
		msg.data = [identify, e]#manda para atras el nivel
                nivel.publish(msg)
	for o in ordering:
	    if not ordering[o]:
		msg.data = [identify, o]#manda para atras el nivel
                nivel.publish(msg)
'''


def evaluarPrecondicion(data):#invocado en etapa de ejecucion cuando llega una postcondicion
    print "entro en evaluarPrecondicion localizar"
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

    #if not skip:
    #	actuar()

 


if __name__ == '__main__':
    print "iniciando localizar"  

    rospy.init_node('localizar', anonymous=True)

    global delay
    global changeTime
    global rate
#    
    delay = 0
    changeTime = rospy.Time.now() + rospy.Duration(delay)
    rate = rospy.Rate(100)
    
    
    
    #global identify
    identify=int(rospy.myargv(argv=sys.argv)[1])
    rospy.loginfo("identificador localizar "+str(identify))

    motores = rospy.Publisher('topicoActuarMotores', Float64MultiArray, queue_size=10)
    postConditionDetect = rospy.Publisher('postConditionDetect', Int32MultiArray, queue_size=10) #usado para aprender
    preConditionDetect = rospy.Publisher('preConditionDetect', Int32MultiArray, queue_size=10) #usado para ejecutar
    rospy.Subscriber("topicoSensores", Float64MultiArray, atenderSensores)
    rospy.Subscriber("preConditionDetect", Int32MultiArray, evaluarPrecondicion)
    rospy.Subscriber("preConditionsSetting", Int32MultiArray, setting)	    
    rospy.Subscriber("topicoEstado", Int32MultiArray, setEstado)
    rospy.Subscriber("topicoNivel", Int32MultiArray, atenderNivel)
    rospy.Subscriber("topicoCaminos", Int32MultiArray, atenderCaminos)
    nivel = rospy.Publisher('topicoNivel', Int32MultiArray, queue_size=10)
    nodoEjecutando=rospy.Publisher('topicoNodoEjecutando', Int32MultiArray, queue_size=10)
    rospy.Subscriber("topicoNodoEjecutando", Int32MultiArray, atenderNodoEjecutando)
    rospy.Subscriber("topicoMotorLockeado", Int32MultiArray, atenderMotorLockeado)
    solicitarOLiberarMotores=rospy.Publisher('topicosolicitarOLiberarMotores', Int32MultiArray, queue_size=10) 
    
  #  rospy.Subscriber("sensorLineDetectedColorData", Float64MultiArray, processSensorLineDetectedColorData)
   # rospy.Subscriber("proximitySensorData", Float64, processProximitySensorData)
   
    rospy.spin()
    
