#!/usr/bin/env python
import sys
import rospy
from std_msgs.msg import String, Float64, Float64MultiArray,Int32MultiArray
import Const
import time

delay=1.2
contador=0
topeContador=1


dataLineDetectColor=None
dataHeadVisionSensor=None
dataProximitySensor=None
detener=False
calibrarColor=-1
dicColores={}#diccionario de colores clave el color, dos array uno con lecturas de min y otra de max para RGB
estado=0
 

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


def processSensorLineDetectColorData(data):
    if data==None:
        return []
    global lineDetectColor
    ingreso = map(float, data.data.split('|'))  
    salida=[]
    sensorsData=[]
    for it in ingreso:
        #negro
        if it > 0.2 and it < 0.3:
             sensorsData.append(Const.SENSOR_COLOR_DETECT_BLACK)
        #blanco
        elif it > 0.6 and it < 0.8:
             sensorsData.append(Const.SENSOR_COLOR_DETECT_WHITE)
        #verde
        elif it > 0.4 and it < 0.5:
             sensorsData.append(Const.SENSOR_COLOR_DETECT_GREEN)
        else:
             sensorsData.append(Const.SENSOR_COLOR_DETECT_NONE)

    #id del sensor, datos...
    salida = [Const.SENSOR_COLOR_DETECT_LINE_ID,  sensorsData[0], sensorsData[1], sensorsData[2]]
    #print "color: ",sensorsData[1]
    return salida
       





# Se publica en sensores un array de Float64 donde los valores son
# En la posicion 0 el id del sensor
# En la posicion 1 un valor entre 0 y 1. 0 indica que el objeto esta lo mas a la izquierda
# posible de la imagen. 1 indica que el objeto esta lo mas a la derecha posible de la imagen.
# En la posicion 2 un valor entero que indica el color del objeto segun las constantes establecidas en Const.
def processHeadVisionSensor(data):
    global calibrarColor
    global dicColores 
    #print "data vision:",data
    if data==None:
        #print "********************   NONE   ****************************"
        return []
    salida=[]
 
    # print "callback: ",data
    strData = str(data.data)
    # rospy.loginfo("comportamiento datos recibidos"+str(data))
    separar= map(str, strData.split('|'))
    print "separar", separar
    
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
                print "dicCol ",dicColores
            else:                
                #se compara con los datos ya calibrados si los hay sino se harcodea
                if len(dicColores) ==0:     
                    dicColores[2]= [[0.0, 0.65882354974747, 0.074509806931019], [0.16078431904316, 0.83137255907059, 0.22352941334248]]
                    dicColores[3]= [[0.61960786581039, 0.0, 0.019607843831182], [0.71764707565308, 0.066666670143604, 0.078431375324726]]
                    dicColores[4]= [[0.69019609689713, 0.69019609689713, 0.054901961237192], [0.99607843160629, 0.99607843160629, 0.28627452254295]]
                    dicColores[5]= [[0.015686275437474, 0.0, 0.67058825492859], [0.2392156869173, 0.2392156869173, 0.87058824300766]] 
                    dicColores[6]= [[0.65882354974747, 0.50588238239288, 0.062745101749897], [0.95294117927551, 0.80392158031464, 0.45490196347237]]
               
               
               
               
               
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
                salida =salida+ [ datos[3], colorCode]
    print "cabeza ",salida
    return salida




def processProximitySensorData(data):
    if data==None:
        return []
    return [Const.SENSOR_NOSE_ULTRASONIC_ID, float(data.data)]
    #msg = Float64MultiArray()
    #msg.data = [Const.SENSOR_NOSE_ULTRASONIC_ID, float(data.data)] 
    #sensores.publish(msg)


def atenderSensorLineDetectColor(data):
    global dataLineDetectColor
    if len(data.data)>0: 
        dataLineDetectColor=data

def atenderProximitySensor(data): 
    global dataProximitySensor 
    if len(data.data)>0:    
        dataProximitySensor=data

def atenderHeadVisionSensor(data):
    global dataHeadVisionSensor
    if len(data.data)>0:
        dataHeadVisionSensor=data 


def envioSensados(): 
    while True:
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
            #print "envio sensores",msg.data
            
        dataLineDetectColor=None
        dataHeadVisionSensor=None
        dataProximitySensor=None
        time.sleep(delay)
    
    
    

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
        
    #solo se podria calibrar si no se esta ahciendo nada
    if estado ==0:    
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
            calibrarColor=-1
            print "fin calibrar"
   
   
    command.publish(msg)


def inputsManual():
    print "Comienzo de la demostracion"
    ingreso=raw_input()
    while ingreso!= "salir":
        # Aca se debe leer sensores     
	
        msg = Float64MultiArray()
        if ingreso == "negro":
            msg.data = [0,0,0,0]
            sensores.publish(msg)
        elif ingreso == "blanco":
            msg.data = [0,1,1,1]
            sensores.publish(msg)
        elif ingreso == "verde":
            msg.data = [0,2,2,2]
            sensores.publish(msg)            
        elif ingreso == "rojo":
            msg.data = [0,3,3,3]
            sensores.publish(msg)
        ingreso=raw_input()
    print "Fin del ingreso de datos"


#se detiene el envio de sensores si el estado es nada               
def setEstado(data):   
       global detener
       global estado
       estado=data.data[0]
       detener = estado == 0            
       print "Llego estado detener> " , detener 



if __name__ == '__main__':
    print "sensado"
    rospy.init_node('inputs', anonymous=True)
    
    proximitySensorData = rospy.Publisher('proximitySensorData', Float64, queue_size=50)
    sensores = rospy.Publisher('topicoSensores', String, queue_size=20)
    sensorLineDetectColorData = rospy.Publisher('sensorLineDetectedColorData', Float64MultiArray, queue_size=10)    
    command = rospy.Publisher('command', String, queue_size=10)    
    #processHeadVisionSensor = rospy.Publisher('processHeadVisionSensor', Float64MultiArray, queue_size=10)   
    
    rospy.Subscriber("topicoEstado", Int32MultiArray, setEstado)  
    rospy.Subscriber("/vrep/command", String, processCommand) # interprete de comandos
    rospy.Subscriber("/vrep/sensorLineDetectColorData", String, atenderSensorLineDetectColor) # Color en el piso (sensores de piso)
    rospy.Subscriber("/vrep/headSensor", String,atenderHeadVisionSensor) # vision color y angulo ("casquito")
    rospy.Subscriber("/vrep/proximitySensorData", String, atenderProximitySensor ) # distancia
    envioSensados()	
    rospy.spin()
    


     
    
       
 
