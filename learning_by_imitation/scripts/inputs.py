#!/usr/bin/env python
import sys
import rospy
from std_msgs.msg import Float32, String, Int32MultiArray, Float64

def processInput(data): 
    msg = Int32MultiArray()   
    ingreso=data.data
    #negro
    if ingreso > 0.2 and ingreso < 0.3:
        msg.data = [0]
        print "negro = ", data.data
        input.publish(msg)
    #blanco
    elif ingreso > 0.6 and ingreso < 0.8:
        msg.data = [1]
	print "blanco = ", data.data
        input.publish(msg)
    #verde
    elif ingreso > 0.4 and ingreso < 0.5:
        msg.data = [2]
	print "verde = ", data.data
        input.publish(msg)
    else:
        print "no Color = ", data.data

if __name__ == '__main__':
    print "sensado"
    rospy.init_node('inputs', anonymous=True)
    input = rospy.Publisher('input', Int32MultiArray, queue_size=10)
    rospy.Subscriber("/sensorLineDetectData", Float32, processInput)
    
   
    
    rospy.spin()


 
def processInput(input):
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
        ingreso=raw_input()
    print "Fin del ingreso de datos"
