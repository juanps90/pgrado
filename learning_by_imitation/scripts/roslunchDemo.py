#!/usr/bin/env python

import rospy
import roslaunch

pkg = 'rqt_gui'
exe = 'rqt_gui'

def lanzarNodo():
    global pkg
    global exe   
    print "AAAAAAAAAAAAAAAAAAAAA"
    node = roslaunch.core.Node(pkg, exe)
    print "BBBBBBBBBBBBBBBBBBBBB"
    launch = roslaunch.scriptapi.ROSLaunch()
    print "CCCCCCCCCCCCCCCCCCCCC"
    launch.load() # Aca se lanza roscore. Proque?
    print "DDDDDDDDDDDDDDDDDDDDD"
    process = launch.launch(node)
    print "EEEEEEEEEEEEEEEEEEEEE"
    print process.is_alive()
    print "FFFFFFFFFFFFFFFFFFFFF"
    process.stop()
    print "GGGGGGGGGGGGGGGGGGGGG"
    
    
    
if __name__ == '__main__':
    print "Probando roslunchDemo"
    rospy.init_node('roslunch', anonymous=True)
    print "111111111111111111111"
    lanzarNodo()
    print "222222222222222222222"
    rospy.spin()
