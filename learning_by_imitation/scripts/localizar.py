#!/usr/bin/env python


import sys 
import rospy
from std_msgs.msg import String, Int32MultiArray, Float64MultiArray, Float64
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

pathPosibles=[]

speed = 8
crash = False
spin = 0
delay = 0
hasFollow = False
changeTime = rospy.Time.now() + rospy.Duration(delay)
rate = rospy.Rate(100)

def publish(speedRight, speedLeft):
    global identify
    global motores
    msg = Float64MultiArray()
    msg.data = [identify, speedRight, speedLeft]
    motores.publish(msg)


def wander():
    global speed
    global crash
    global spin
    global delay
    global hasFollow
    global changeTime
    global rate

    if crash:
        # voy hacia atras
        publish(-speed, -speed)
    elif hasFollow:
        # sigo hacia adelante
        publish(speed, speed)
    elif spin == 0:
        # girar a la izquierda
        publish(speed/8, speed/2)
    else:
        # girar a la derecha
        publish(speed/2, speed/8)
    
    if changeTime < rospy.Time.now():
        hasFollow = not hasFollow
        spin = randint(0, 1)
        delay = randint(2, 9)
        changeTime = rospy.Time.now() + rospy.Duration(delay)
        crash = False
        
    rate.sleep()

#se deben de mandar mensajes continuamente si se ejecuta tanto como si no a los motores
def actuar():
    global motores
    msg = Int32MultiArray()   
    if cumplePrecondiciones () and nivelActivacion>0:
        wander()
        
#        msg.data = [identify,5,5] 	 
#        motores.publish(msg)     
#        
#        rospy.loginfo("Ejecutando localizar...")
#        #rospy.loginfo( nivelActivacion)
        ejecutando=True
        msg.data = [identify,identify] #por si necesito otro parametro        
        nodoEjecutando.publish(msg) 
    else: 
	rospy.loginfo("Se detuvo localizar...")
	ejecutando=False
	msg.data = [identify,0,0] 	 
        motores.publish(msg)

def verificarPoscondicionesSensores(data):
    activate=False
    if data.data == Const.SENSOR_COLOR_DETECT_BLACK or data.data == Const.SENSOR_COLOR_DETECT_GREEN:#para que sea de permanencia hay que revisar
        print "se cumple postcondicion localizar"
	activate=True
    elif cumplePrecondiciones():#cumple precondiciones y no cumple postcondicion	
        print "no se cumple postcondicion",activate
    return activate


#posiblemente haya mas sensores, se debe realizar una lectura de todos los sensores y luego de esto verificar si el estado es de ejecucion
def processSensorLineDetectedColorData(data):
    #se verifican las condiciones en base a los sensores
    #verificarPoscondicionesSensores(data)

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
	msg.data = [identify,valorEncendido]   #cuando se ejecuta se envia el id del nodo
	actuar()
	#rospy.loginfo("localizar ",valorEncendido)
	preConditionDetect.publish(msg)
    
def setEstado(data):    
    global estado
    estado=data.data[0]
    if estado==3:
	#se detienen los motores estamos en estado come 
	msg = Float64MultiArray() 
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
    salida = evaluation(permanent.values()) and (ejecutando or evaluation(enablig.values()) ) and evaluation(ordering.values()) #si esta ejecutando no se evalua enabling
    print "cumplePrecondiciones ",salida
    return salida

def evaluation(l):
    result = True
    for it in l:
        result = result and it
        if not result:
            break
    return result

 



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
        rospy.loginfo("me llego nivel localizar")
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



def evaluarPrecondicion(data):#invocado en etapa de ejecucion cuando llega una postcondicion
    print "entro en evaluarPrecondicion localizar"
    skip = False
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
    else:
        skip = True

def processProximitySensorData(data):
    global crash
    crash = data.data < 0.25


if __name__ == '__main__':
    print "iniciando localizar"  

    rospy.init_node('localizar', anonymous=True)

    
    #global identify
    identify=int(rospy.myargv(argv=sys.argv)[1])
    rospy.loginfo("identificador localizar "+str(identify))

    motores = rospy.Publisher('topicoActuarMotores', Float64MultiArray, queue_size=10)
    postConditionDetect = rospy.Publisher('postConditionDetect', Int32MultiArray, queue_size=10) #usado para aprender
    preConditionDetect = rospy.Publisher('preConditionDetect', Int32MultiArray, queue_size=10) #usado para ejecutar
#    rospy.Subscriber("input", Int32MultiArray, atenderSensores)
    
    rospy.Subscriber("sensorLineDetectedColorData", String, processSensorLineDetectedColorData)
    
    rospy.Subscriber("preConditionDetect", Int32MultiArray, evaluarPrecondicion)
    rospy.Subscriber("preConditionsSetting", Int32MultiArray, setting)	    
    rospy.Subscriber("topicoEstado", Int32MultiArray, setEstado)
    rospy.Subscriber("topicoNivel", Int32MultiArray, nivel)
    rospy.Subscriber("topicoCaminos", Int32MultiArray, atenderCaminos)
    nivel = rospy.Publisher('topicoNivel', Int32MultiArray, queue_size=10)
    nodoEjecutando=rospy.Publisher('topicoNodoEjecutando', Int32MultiArray, queue_size=10)
    rospy.Subscriber("topicoNodoEjecutando", Int32MultiArray, atenderNodoEjecutando)

    rospy.Subscriber("proximitySensorData", Float64, processProximitySensorData)
   
    rospy.spin()
