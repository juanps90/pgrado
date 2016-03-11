#!/usr/bin/env python
import sys
import rospy
from std_msgs.msg import String, Float64, Float64MultiArray,Int32MultiArray
import Const
import time

delay=0.2
contador=0
topeContador=1


dataLineDetectColor=None
dataHeadVisionSensor=None
dataProximitySensor=None
detener=False
 

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
    if data==None:
        #print "********************   NONE   ****************************"
        return []
    salida=[]
#   print "**************************************************************"
#   print data.data
#   print "**************************************************************"

    dataSensor = map(float, data.data.split('|'))
    
    codeColor = Const.SENSOR_COLOR_DETECT_NONE
    #Rojo
    if dataSensor[1] == 1:
         codeColor = Const.SENSOR_COLOR_DETECT_RED
    #verde
    elif dataSensor[1] == 2:
         codeColor = Const.SENSOR_COLOR_DETECT_GREEN
    #azul
    elif dataSensor[1] == 3:
         codeColor = Const.SENSOR_COLOR_DETECT_BLUE
    #amarillo
    elif dataSensor[1] == 4:
         codeColor = Const.SENSOR_COLOR_DETECT_YELLOW
    #naranja
    elif dataSensor[1] == 5:
         codeColor = Const.SENSOR_COLOR_DETECT_ORANGE

    #msgVisionSensorData.data = [Const.SENSOR_VISION_HEAD_ID,2, dataSensor[0], codeColor]
    salida = [Const.SENSOR_VISION_HEAD_ID,  dataSensor[0], codeColor]
 
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
    
        if not detener:
            sensores.publish(msg) 
            print "envio sensores",msg.data
            
        dataLineDetectColor=None
        dataHeadVisionSensor=None
        dataProximitySensor=None
        time.sleep(delay)
    

def processCommand(data):
    msg = String()
    if data.data == "INIT_LEARNING":
        msg.data = str(Const.COMMAND_INIT_LEARNING)
    elif data.data == "END_LEARNING":
        msg.data = str(Const.COMMAND_END_LEARNING)
    elif data.data == "PLAY":
        msg.data = str(Const.COMMAND_PLAY)
    elif data.data == "STOP":
        msg.data = str(Const.COMMAND_STOP)
    elif data.data == "BAD":
        msg.data = str(Const.COMMAND_BAD)
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
       aux=data.data[0]
       detener = aux == 0            
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
    rospy.Subscriber("/vrep/command", String, processCommand)#colores en el suelo
    rospy.Subscriber("/vrep/sensorLineDetectColorData", String, atenderSensorLineDetectColor) #vision color y angulo
    rospy.Subscriber("/vrep/headSensor", String,atenderHeadVisionSensor)#distancia   
    rospy.Subscriber("/vrep/proximitySensorData", String, atenderProximitySensor )
    envioSensados()	
    if ((len(sys.argv) == 1) or ((len(sys.argv) > 1) and sys.argv[1] == "manual")):
        inputsManual()
    elif (len(sys.argv) > 1) and (sys.argv[1] == "vrep"):
        
        rospy.spin()
    else:
        print "El parametro debe ser el string 'manual' o el string 'vrep'"

    


     
    
       
 
