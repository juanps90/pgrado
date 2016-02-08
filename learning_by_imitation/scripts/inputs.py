#!/usr/bin/env python
import sys
import rospy
from std_msgs.msg import String, Int32MultiArray, Float64, Float64MultiArray
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

    msgSensorLineDetectColorData.data = [Const.SENSOR_COLOR_DETECT_LINE_ID, sensorsData[0], sensorsData[1], sensorsData[2]]
    return msgSensorLineDetectColorData
       
def processSensorLineDetectColorData(data): 
    msgInput = Int32MultiArray()
    
    ingreso = map(float, data.data.split('|'))
    print ingreso
    
    #negro
    if ingreso[1] > 0.2 and ingreso[1] < 0.3:
        msgInput.data = [0]
        print "negro = ", data.data
        input.publish(msgInput)
        sensorLineDetectColorData.publish(messageSensorsLineDetectColor(ingreso))
    #blanco
    elif ingreso[1] > 0.6 and ingreso[1] < 0.8:
        msgInput.data = [1]
        print "blanco = ", data.data
        input.publish(msgInput)
        sensorLineDetectColorData.publish(messageSensorsLineDetectColor(ingreso))
    #verde
    elif ingreso[1] > 0.4 and ingreso[1] < 0.5:
        msgInput.data = [2]
        print "verde = ", data.data
        input.publish(msgInput)
        sensorLineDetectColorData.publish(messageSensorsLineDetectColor(ingreso))        
    else:
        print "no Color = ", data.data

def inputsManual():
    print "Comienzo de la demostracion"
    ingreso=raw_input()
    while ingreso!= "salir":
        # Aca se debe leer sensores     
	
        msg = Int32MultiArray()
        if ingreso == "negro":
            msg.data = [0]
            input.publish(msg)
        elif ingreso == "blanco":
            msg.data = [1]
            input.publish(msg)
        elif ingreso == "verde":
            msg.data = [2]
            input.publish(msg)            
        elif ingreso == "rojo":
            msg.data = [3]
            input.publish(msg)
        ingreso=raw_input()
    print "Fin del ingreso de datos"

def processProximitySensorData(data):
    msg = Float64()
    msg.data = float(data.data)
    proximitySensorData.publish(msg)
    print "Distancia = ", data.data


if __name__ == '__main__':
    print "sensado"
    rospy.init_node('inputs', anonymous=True)
    input = rospy.Publisher('input', Int32MultiArray, queue_size=10)
    sensorLineDetectColorData = rospy.Publisher('sensorLineDetectedColorData', Float64MultiArray, queue_size=10)    
    
    #Me suscribo a datos de los sensores de vision que detectan colores en el suelo
    rospy.Subscriber("/vrep/sensorLineDetectColorData", String, processSensorLineDetectColorData)
    
    #Me suscribo a datos de los sensores de distancia
    rospy.Subscriber("/vrep/proximitySensorData", String, processProximitySensorData)
    proximitySensorData = rospy.Publisher('proximitySensorData', Float64, queue_size=50)
    
    if ((len(sys.argv) == 1) or ((len(sys.argv) > 1) and sys.argv[1] == "manual")):
        inputsManual()
    elif (len(sys.argv) > 1) and (sys.argv[1] == "vrep"):
        rospy.spin()
    else:
        print "El parametro debe ser el string 'manual' o el string 'vrep'"

    


 
