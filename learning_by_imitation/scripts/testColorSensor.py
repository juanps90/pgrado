#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from std_msgs.msg import String

def atenderSensores(data):
    print data.data
    
if __name__ == '__main__':
    print "iniciando test de sensores"  

    rospy.init_node('testColor', anonymous=True)

    rospy.Subscriber("topic_sensors", String, atenderSensores)
    rospy.spin()

