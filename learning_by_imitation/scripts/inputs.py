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
    
    ingreso = map(float, data.data.split('|'))
    
    sensores.publish(messageSensorsLineDetectColor(ingreso))




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
    msg.data = [1,float(data.data)]
    sensores.publish(msg)
    print "Distancia = ", data.data


if __name__ == '__main__':
    print "sensado"
    rospy.init_node('inputs', anonymous=True)
    sensores = rospy.Publisher('topicoSensores', Float64MultiArray, queue_size=20)
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

    


 
