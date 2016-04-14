#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @package Inputs
# @brief Modulo usado para capturar y procesar los datos enviados desde V-Rep.
# @details V-Rep publica los datos de los sensores en los topicos "/vrep/sensorLineDetectColorData", "/vrep/headSensor"
# y "/vrep/proximitySensorData". Los datos recibidos de los sensores son procesados y publicados en el topico "topicoSenores" como un String
# y en el formato DATOS_SENSOR_1|DATOS_SENSOR_2|DATOS_SENSOR_3|.... donde DATOS_SENSOR_N posee el subformato ID_SENSOR\#DATO_1\#DATO_2\#DATO_3\#...
# Como ejemplo supongamos que nuestro robot solo posee un sensor de distancia y uno de color. En esta situacion, en el topoico "topic_sensors"
# se debe publicar el String ID_SENSOR_DISTANCIA\#VALOR_DISTANCIA|ID_SENSOR_COLOR\#VALOR_COLOR. 
# Ademas V-Rep pulica datos de comandos ingresados por el usuario en el topico "/vrep/command" y luego estos datos se
# envian al sistema mediante el topico "topic_command".
# Esta clase debe ser reimplementada en caso de requerir un robot diferente o real manteniendo el 
# formato de los mensajes que se envien al sistema proveniente de los sensores.
# @authors Gustavo Irigoyen
# @authors Juan Pablo Sierra
# @authors Juan Eliel Ibarra
# @authors Gustavo Evovlockas
# @date Abril 2016
#

import rospy
from std_msgs.msg import String, Int32MultiArray
import time
import Const
import SaveXML
import LoadXML

delay=1.2
contador=0
topeContador=1


dataLineDetectColor=None
dataHeadVisionSensor=None
dataProximitySensor=None
detener=False
calibrarColor=-1
dicColores={} #diccionario de colores clave el color, dos array uno con lecturas de min y otra de max para RGB
estado=0
 



##
# Arma el String a partir del arrary data.
# @param data Array donde en la posicion 0 esta el ID del sensor y en el resto de las posiciones los datos que este proporciona.
# @return Retorna un String concatenando cada dato del array  con el caracter \#
#
def joinData(data):
    salida=""
    tamanio=len (data)
    if tamanio <2:
        return salida
        
    salida=salida+str(data[0])
    del data[0]
    for d in data:
        salida=salida+"#"
        salida=salida+str(d)
    return salida

##
# Procesa los datos originado por los tres sensores de vision usados para leer linea.
# La funcion retorna un array donde en la posicion 0 esta el id del conjunto de sensores, en la posicion 1 esta el id
# del color detectado por el sensor izquierdo, en la posicion 2 esta el id del color detectado por el sensor del medio y 
# en la posicion 3 esta el id del color detectado por el sensor derecho. Ver Const para saber los colores que pude detectar.
# @param data Datos originados por los tres sensores de vision.
# @return Retorna un array con el id del conjunto de sensores y los id de los colores sensados por cada sensor.
#
def processSensorLineDetectColorData(data):
    if data==None:
        return []
    global lineDetectColor
    ingreso = map(float, data.data.split('|'))  
    salida=[]
    sensorsData=[]
    for it in ingreso: 
        if it > 0.1 and it < 0.2:
             sensorsData.append(Const.SENSOR_COLOR_DETECT_BLACK) 
        if it > 0.2 and it < 0.3:
             sensorsData.append(Const.SENSOR_COLOR_DETECT_BLUE) 
        elif it > 0.3 and it < 0.35:
             sensorsData.append(Const.SENSOR_COLOR_DETECT_RED)
        elif it > 0.35 and it < 0.38:
             sensorsData.append(Const.SENSOR_COLOR_DETECT_ORANGE) 
        elif it > 0.38 and it < 0.4:
             sensorsData.append(Const.SENSOR_COLOR_DETECT_GREEN) 
        elif it > 0.4 and it < 0.5:
             sensorsData.append(Const.SENSOR_COLOR_DETECT_YELLOW) 
        elif it > 0.5 and it < 0.7:
             sensorsData.append(Const.SENSOR_COLOR_DETECT_WHITE) 
        else:
             sensorsData.append(Const.SENSOR_COLOR_DETECT_NONE)

    salida = [Const.SENSOR_COLOR_DETECT_LINE_ID,  sensorsData[0], sensorsData[1], sensorsData[2]]
    if Const.debugInputs == 1:
        print "color: ",sensorsData[1]
    return salida




##
# Procesa los datos originado por el sensor de vision ubicado en la cabeza.
# La funcion retorna un array donde en la posicion 0 esta el id del del senosr.
# En la posicion 1 hay un valor entre 0 y 1. 0 indica que el objeto esta lo mas a la izquierda
# posible de la imagen. 1 indica que el objeto esta lo mas a la derecha posible de la imagen.
# En la posicion 2 un valor entero que indica el color del objeto segun las constantes establecidas en Const.
# En la  posicion 3 el ancho de objeto.
# En la  posicion 4 el alto de objeto.
# @param data Datos originados por el sensor de vision de la cabeza del robot.
# @return Retorna un array con el id del sensor, un valor que indica si el objeto detectado esta hacia la izquierda o derecha.
#
def processHeadVisionSensor(data):
    global calibrarColor
    global dicColores 

    if data==None:
        return []
    #if Const.debugInputs == 1:
        # print "data vision:",data.data
    salida=[]
 
    # print "callback: ",data
    strData = str(data.data)
    
    separar= map(str, strData.split('|'))
    #print "separar", separar
    
    #llegan datos de varios objetos
    for s in  separar:
        if len(s)>1: 
            datos = map(float, s.split('#'))  
            colorCode = Const.SENSOR_COLOR_DETECT_NONE
            
            #en caso de quese este calibrando se ajustan minimos y maximos de cada color a calibrar
            if calibrarColor!=-1: 
                if dicColores.has_key(calibrarColor) :
                    for i in range(3):
                        if datos[i]<dicColores[calibrarColor][0][i]:
                            dicColores[calibrarColor][0][i]=datos[i]
                        if datos[i]>dicColores[calibrarColor][1][i]:
                            dicColores[calibrarColor][1][i]=datos[i]
                else:
                    dicColores[calibrarColor]=[ [datos[0],datos[1],datos[2]],[datos[0],datos[1],datos[2]] ]
                if Const.debugInputs == 1:
                    print "dicCol ",dicColores
            else:                
                #se compara con los datos ya calibrados si los hay sino se harcodea
                if len(dicColores) == 0:     
                    dicColores[Const.SENSOR_COLOR_DETECT_GREEN]= [[0.0, 0.65, 0.0], [0.17, 1.0, 0.23]]
                    dicColores[Const.SENSOR_COLOR_DETECT_RED]= [[0.60, 0.0, 0.0], [1.0, 0.12, 0.12]]
                    dicColores[Const.SENSOR_COLOR_DETECT_YELLOW]= [[0.69, 0.69, 0.0], [1.0, 1.0, 0.20]]
                    dicColores[Const.SENSOR_COLOR_DETECT_BLUE]= [[0.0, 0.0, 0.55], [0.25, 0.25, 1.0]] 
                    dicColores[Const.SENSOR_COLOR_DETECT_ORANGE]= [[0.65, 0.50, 0.20], [1.0, 1.0, 0.46]]
               
                match=False
                for c in dicColores:
                    
                    for i in range(3):
                        min=dicColores[c][0][i]
                        max=dicColores[c][1][i]
                        cond=min<=datos[i] and datos[i] <= max
                        if not cond:
                            break
                        elif i==2:
                            match=True
                            colorCode=c
                    if match:
                        break
                    
                #msgVisionSensorData.data = [Const.SENSOR_VISION_HEAD_ID,2, dataSensor[0], codeColor]
                if len (salida)==0:
                    salida=[Const.SENSOR_VISION_HEAD_ID]
                salida =salida+ [ datos[3], colorCode,datos[4],datos[5]]
    #if Const.debugInputs == 1:
        #print "cabeza ", salida
    return salida



##
# Procesa los datos originado por el sensor de distancia ubicado en la nariz del robot.
# La funcion retorna un array donde en la posicion 0 esta el id del del senosr y en la
# posicion 1 hay un valor entre que indica la distancia (en metros) del robot a un objeto del entorno.
# @param data Datos originados por el sensor de distancia de la nariz del robot.
# @return Retorna un array con el id del sensor y un valor que indica la distancia desde el robot a un objeto del entorno.
#
def processProximitySensorData(data):
    if data==None:
        return []
    return [Const.SENSOR_NOSE_ULTRASONIC_ID, float(data.data)]

##
# Copia datos provenientes de los tres senores de vision, usados para detectar lineas, hacia la variable  dataLineDetectColor.
# @param data Datos originados por los tres sensores de vision usados para detectar lineas.
#
def atenderSensorLineDetectColor(data):
    global dataLineDetectColor
    if len(data.data)>0: 
        dataLineDetectColor=data

##
# Copia datos provenientes del senor distancia hacia la variable  dataProximitySensor.
# @param data Datos originados por el sensor de distancia.
#
def atenderProximitySensor(data): 
    global dataProximitySensor 
    if len(data.data)>0:    
        dataProximitySensor=data

##
# Copia datos provenientes del senor de vision, ubicado en la cabeza del robot, hacia la variable  dataHeadVisionSensor.
# @param data Datos originados por el sensor de vision ubicado en la cabeza del robot.
#
def atenderHeadVisionSensor(data):
    global dataHeadVisionSensor
    if len(data.data)>0:
        dataHeadVisionSensor=data 
##
# Cada cierto intervalo de tiempo envia datos de los sensores con el formato que se indico al inicio.
# Solamente son enviados los datos si la variable de estado es distinta a cero.
#
def envioSensados(): 
    while (not rospy.is_shutdown()):
        global dataLineDetectColor 
        global dataHeadVisionSensor 
        global dataProximitySensor 
        global delayClearSensor
        global detener
        
        msg=String()
        
 
        head=processHeadVisionSensor(dataHeadVisionSensor)
        line=processSensorLineDetectColorData(dataLineDetectColor)
        proximity=processProximitySensorData(dataProximitySensor)
        
        mensaje=""
        l=joinData(line) 
        p=joinData(proximity)
        h=joinData(head)
        
        if len (l) > 0:
            mensaje=mensaje+l
        if len (p) > 0:  
            if len (mensaje) > 0:
                mensaje=mensaje+'|' 
            mensaje=mensaje+p    
        if len (h) > 0:  
            if len (mensaje) > 0:
                mensaje=mensaje+'|'  
            mensaje=mensaje+h           
         
        msg.data = mensaje
    
        if not detener and len(mensaje)>0:
            sensores.publish(msg) 
            if Const.debugInputs == 1:
                print "envio sensores",msg.data
            
        dataLineDetectColor=None
        dataHeadVisionSensor=None
        dataProximitySensor=None
        time.sleep(delay)
    
    
    
##
# Publica en el topico "topic_command" un String que indica el comando a ser ejecutado en el sistema.
#   - INIT_LEARNING: Comando que indica el comienzo de una demostracion.
#   - END_LEARNING: Comando que indica el fin de una demostracion. A este comando se le concatenar un "|" y un string que indica
#                   el nombre con el cual se persiste lo enseñado. Ejemplo: END_LEARNING|myDemo.xml.
#   - PLAY: Comando que indica el inicio de una reporduccion. A este comando se le concatena un "|" y un string que indica
#           la tarea a ser reporduciada.
#   - STOP: Comando que indica el fin de una reproduccion en curso.
#   - BAD: Comando que indica que la parte que se esta reproduciendo esta mal y por tanto debe ser eliminada.
#          Este comando me premite eliminar un nodo de la red de comportamientos.
#   - COME: Durante el aprendizaje el robot puede perder pasos relevantes. Este comando permite entrar en modo de aprendizaje
#         durante la reproduccion e indicar asi los pasos faltantes. Esto nos permite agregar una subred a la red actual.
#   - GO: Este comando perite retomar la reproduccion luego de haber entrado en modo aprendizaje con el comando COME
#   - HERE: ------------------------
#   - EXIT: Salir del sistema.
# Ademas de estos comandos tenemos otros comandos dedicados a calibrar colores.
#   - DEL_CALIBRATE: Elimina una calibracion existente.
#   - RED_CALIBRATE: Permite calibra el color rojo.
#   - GREEN_CALIBRATE: Permite calibra el color verde.
#   - BLUE_CALIBRATE: Permite calibra el color azul.
#   - ORANGE_CALIBRATE: Permite calibra el color naranja. 
#   - YELLOW_CALIBRATE: Permite calibra el color amarillo.
#   - END_CALIBRATE: Indica el fin de una calibracion.
# @param data Datos de los comandos originados desde V-Rep.
#
def processCommand(data):
    global calibrarColor
    global estado
    comando = data.data.split('|')
    msg = String()
    if comando[0] == "INIT_LEARNING":
        msg.data = str(Const.COMMAND_INIT_LEARNING)
    elif comando[0] == "END_LEARNING":
        msg.data = '{0}|{1}'.format(str(Const.COMMAND_END_LEARNING),comando[1]) 
    elif comando[0] == "PLAY":
        msg.data = '{0}|{1}'.format(str(Const.COMMAND_PLAY),comando[1])
    elif comando[0] == "STOP":
        msg.data = str(Const.COMMAND_STOP)
    elif comando[0] == "BAD":
        msg.data = str(Const.COMMAND_BAD)
    elif comando[0] == "GO":
        msg.data = str(Const.COMMAND_GO)
    elif comando[0] == "COME":
        msg.data = str(Const.COMMAND_COME)
    elif comando[0] == "HERE":
        msg.data = str(Const.COMMAND_HERE)
    elif comando[0] == "EXIT":
        msg.data = str(Const.COMMAND_EXIT)
        
    #solo se podria calibrar si no se esta ahciendo nada
    if estado ==0:   
        if comando[0] == "DEL_CALIBRATE":
           if calibrarColor!=-1:
               dicColores[calibrarColor]= [[10,10,10], [-1,-1,-1]]  
        if comando[0] == "RED_CALIBRATE":
           calibrarColor= Const.SENSOR_COLOR_DETECT_RED
        elif comando[0] == "GREEN_CALIBRATE":
            calibrarColor=Const.SENSOR_COLOR_DETECT_GREEN
        elif comando[0] == "BLUE_CALIBRATE":
            calibrarColor=Const.SENSOR_COLOR_DETECT_BLUE
        elif comando[0] == "ORANGE_CALIBRATE":
            calibrarColor=Const.SENSOR_COLOR_DETECT_ORANGE
        elif comando[0] == "YELLOW_CALIBRATE":
            calibrarColor=Const.SENSOR_COLOR_DETECT_YELLOW
        elif comando[0] == "END_CALIBRATE": 
            SaveXML.persistirConfiguracion(Const.CONFIG_XML_NAME, dicColores)
            calibrarColor=-1
            print "fin calibrar"
    command.publish(msg)

##
# Setea el estado actual. Permite detener el envio de los datos sensados si el estado es cero.
# @param data Datos publicados en el topico "topic_state".
#             
def setEstado(data):   
       global detener
       global estado
       estado=data.data[0]
       detener = estado == 0            
       print "Llego estado detener> " , detener 


##
# Carga una configuracion de calibracion de colores. Esta configuracion indica el maximio y minimo de R, G y B para cada color
# posible de ser detectado.
#     
def inicializarParametros():
    global dicColores 
    salida = LoadXML.obtenerConfiguracion(Const.CONFIG_XML_NAME)
    if salida[0] == 0:
        # Encontro el archivo y esta bien
        print 'Cargando configuracion existente de "{0}/{1}/{2}.xml"'.format(Const.PGRADO_HOME, Const.CONFIG_FOLDER_NAME, Const.CONFIG_XML_NAME)
        dicColores = salida[1]
    else:
        # No encontro archivo => Cargo default
        print 'No existe configuracion... usando default'
        # dicColores[Const.SENSOR_COLOR_DETECT_BLACK]= [[0.0, 0.65, 0.0], [0.17, 1.0, 0.23]]
        # dicColores[Const.SENSOR_COLOR_DETECT_WHITE]= [[0.60, 0.0, 0.0], [1.0, 0.12, 0.12]]
        dicColores[Const.SENSOR_COLOR_DETECT_GREEN]= [[0.0, 0.65, 0.0], [0.17, 1.0, 0.23]]
        dicColores[Const.SENSOR_COLOR_DETECT_RED]= [[0.60, 0.0, 0.0], [1.0, 0.12, 0.12]]
        dicColores[Const.SENSOR_COLOR_DETECT_YELLOW]= [[0.69, 0.69, 0.0], [1.0, 1.0, 0.20]]
        dicColores[Const.SENSOR_COLOR_DETECT_BLUE]= [[0.0, 0.0, 0.55], [0.25, 0.25, 1.0]] 
        dicColores[Const.SENSOR_COLOR_DETECT_ORANGE]= [[0.65, 0.50, 0.20], [1.0, 1.0, 0.46]]
        SaveXML.persistirConfiguracion(Const.CONFIG_XML_NAME, dicColores)

##
# Funcion que se ejecuta al recibir una señal signal_shutdown.
#   
def shutdown():
    print "Bye!"

##
# La funcion emite una señal signal_shutdown para finalizar este nodo.
# @param data Datos publicados en el tópico. No es usado.
#   
def finalize(data):
    rospy.signal_shutdown("Bye!")

if __name__ == '__main__':
    print "sensado"
    # Antes de iniciar cualquier cosa, configuro o cargo la configuracion existente.
    inicializarParametros()
    rospy.init_node('Inputs', anonymous=True)
    
    rospy.on_shutdown(shutdown)
    
    sensores = rospy.Publisher('topic_sensors', String, queue_size=1)
    command = rospy.Publisher('topic_command', String, queue_size=10)    
    
    rospy.Subscriber("topic_state", Int32MultiArray, setEstado)  
    rospy.Subscriber("/vrep/command", String, processCommand) # interprete de comandos
    rospy.Subscriber("/vrep/sensorLineDetectColorData", String, atenderSensorLineDetectColor) # Color en el piso (sensores de piso)
    rospy.Subscriber("/vrep/headSensor", String,atenderHeadVisionSensor) # vision color y angulo ("casquito")
    rospy.Subscriber("/vrep/proximitySensorData", String, atenderProximitySensor ) # distancia
    rospy.Subscriber("topic_finalize", String, finalize)
    
    envioSensados()	
    rospy.spin()
    finalize(None)
       
 
