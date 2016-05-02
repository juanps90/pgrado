# !/bin/bash
echo "Load roscore"
roscore &
sleep 15s
echo "Load V-Rep"
sh /opt/V-REP_PRO_EDU_V3_2_2_64_Linux/vrep.sh -s -q $PGRADO_HOME/scenes/aprender2.ttt &
sleep 20s
echo "Load App"
roslaunch learning_by_imitation pgrado.launch &

