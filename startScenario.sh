#!/bin/bash
# killall -9 python
killall -9 CarlaUE4 CarlaUE4.sh
clear

run_python=/home/driverleics/opt/python3.6-venv/bin/python

scenario=Town03GasStation
town=Town03;

case $1 in
	town01Restaurant) 
		cenario=Town01Restaurant
		town=Town01
		;;
    town03GasStation)
    	scenario=Town03GasStation
    	town=Town03
    	;;
    *)
		scenario=Town03GasStation
		town=Town03
		;;
esac


/home/driverleics/Downloads/carla/CARLA_0.9.5/CarlaUE4.sh /Game/Carla/Maps/$town > log_server.txt & 

sleep 3s
xdotool windowminimize `wmctrl -l | grep "CarlaUE4 (64-bit Development GLSL_430)"|cut -d\  -f1`

$run_python /home/driverleics/git/scenario_runner-v095/scenario_runner.py --scenario $scenario --res=1280x720 --fullscreen > log_scenario_ui.txt

# $run_python /home/driverleics/git/scenario_runner-v095/scenario_runner.py --scenario $scenario > log_scenario.txt &

# sleep 7s
# $run_python /home/driverleics/git/scenario_runner-v095/manual_control_steeringwheel.py --res=1280x720 --fullscreen > log_client.txt


killall -9 CarlaUE4 CarlaUE4.sh