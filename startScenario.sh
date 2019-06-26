#!/bin/bash
# killall -9 python
#killall -9 CarlaUE4 CarlaUE4.sh || echo "CarlaUE4 was not running."
( killall -9 CarlaUE4 CarlaUE4.sh 2>&1 ) > /dev/null
clear

run_python=/home/driverleics/opt/python3.6-venv/bin/python

scenario=Town03GasStation
town=Town03;

case $1 in
	Town01Restaurant) 
		scenario=Town01Restaurant
		town=Town01
		;;
    Town03GasStation)
    	scenario=Town03GasStation
    	town=Town03
    	;;
    Town03TrainTrack)
    	scenario=Town03TrainTrack
    	town=Town03
    	;;
    Town04ParkingLot)
		scenario=Town04ParkingLot
		town=Town04
		;;
	Town07Farm)
		scenario=Town07Farm
		town=Town07
		;;
    *)
		scenario=Town03GasStation
		town=Town03
		;;
esac


/home/driverleics/Downloads/carla/CARLA_0.9.5/CarlaUE4.sh /Game/Carla/Maps/$town > log_server.txt & 

sleep 2s
xdotool windowminimize `wmctrl -l | grep "CarlaUE4"|cut -d\  -f1`

$run_python /home/driverleics/git/scenario_runner-v095/scenario_runner.py --scenario $scenario --res=1280x720 > log_scenario_ui.txt

# $run_python /home/driverleics/git/scenario_runner-v095/scenario_runner.py --scenario $scenario > log_scenario.txt &

# sleep 7s
# $run_python /home/driverleics/git/scenario_runner-v095/manual_control_steeringwheel.py --res=1280x720 --fullscreen > log_client.txt

#cat /home/driverleics/git/scenario_runner-v095/score.csv  >  /home/driverleics/git/driverleics.github.io/_data/score.csv
#cd /home/driverleics/git/driverleics.github.io/
#rm -rf /home/driverleics/git/driverleics.github.io/_site/
#/home/driverleics/.rvm/rubies/default/bin/bundle exec jekyll pagemaster scores

#killall -9 CarlaUE4 CarlaUE4.sh || echo "CarlaUE4 was not running."
( killall -9 CarlaUE4 CarlaUE4.sh 2>&1 ) > /dev/null
