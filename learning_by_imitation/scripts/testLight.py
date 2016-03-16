#!/usr/bin/env python
import rospy
from std_msgs.msg import Int32


if __name__ == '__main__':
    print "test light"  

    rospy.init_node('testLight', anonymous=True)
    light=rospy.Publisher('/vrep/actuatorLed1Topic', Int32, queue_size = 1)

    comando=raw_input("> ")
    msg = Int32()
    
    while comando != "salir":
        if comando=="1" or comando=="0":
            msg.data = int(comando)
            light.publish(msg)
        comando=raw_input("> ")
        
