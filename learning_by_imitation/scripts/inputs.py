#!/usr/bin/env python
import sys
import rospy
from std_msgs.msg import String, Float64, Float64MultiArray
import Const

def messageSensorsLineDetectColor(data):
    msgSensorLineDetectColorData = Float64MultiArray()
    sensorsData = []
    for it in data:
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

    msgSensorLineDetectColorData.data = [Const.SENSOR_COLOR_DETECT_LINE_ID, sensorsData[0], sensorsData[1], sensorsData[2]]
    return msgSensorLineDetectColorData
       
def processSensorLineDetectColorData(data): 
    ingreso = map(float, data.data.split('|'))
    sensores.publish(messageSensorsLineDetectColor(ingreso))

# Se publica en sensores un array de Float64 donde los valores son
# En la posicion 0 el id del sensor
# En la posicion 1 un valor entre 0 y 1. 0 indica que el objeto esta lo mas a la izquierda
# posible de la imagen. 1 indica que el objeto esta lo mas a la derecha posible de la imagen.
# En la posicion 2 un valor entero que indica el color del objeto segun las constantes establecidas en Const.
def processHeadVisionSensor(data):
    msgVisionSensorData = Float64MultiArray()
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

    msgVisionSensorData.data = [Const.SENSOR_VISION_HEAD_ID, dataSensor[0], codeColor]
    sensores.publish(msgVisionSensorData)
    print "processHeadVisionSensor = ", data.data

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

def processProximitySensorData(data):
    msg = Float64MultiArray()
    msg.data = [Const.SENSOR_NOSE_ULTRASONIC_ID, float(data.data)]
    sensores.publish(msg)

if __name__ == '__main__':
    print "sensado"
    rospy.init_node('inputs', anonymous=True)
    sensores = rospy.Publisher('topicoSensores', Float64MultiArray, queue_size=20)
    sensorLineDetectColorData = rospy.Publisher('sensorLineDetectedColorData', Float64MultiArray, queue_size=10)    
    
    #Me suscribo a datos de los sensores de vision que detectan colores en el suelo
    rospy.Subscriber("/vrep/sensorLineDetectColorData", String, processSensorLineDetectColorData)
    
    #Me suscribo a datos del sensor de vision que detectan color y angulo
    rospy.Subscriber("/vrep/headSensor", String, processHeadVisionSensor)
    processHeadVisionSensor = rospy.Publisher('processHeadVisionSensor', Float64MultiArray, queue_size=10)
    
    #Me suscribo a datos de los sensores de distancia
    rospy.Subscriber("/vrep/proximitySensorData", String, processProximitySensorData)
    proximitySensorData = rospy.Publisher('proximitySensorData', Float64, queue_size=50)
    
    if ((len(sys.argv) == 1) or ((len(sys.argv) > 1) and sys.argv[1] == "manual")):
        inputsManual()
    elif (len(sys.argv) > 1) and (sys.argv[1] == "vrep"):
        rospy.spin()
    else:
        print "El parametro debe ser el string 'manual' o el string 'vrep'"

    


 
