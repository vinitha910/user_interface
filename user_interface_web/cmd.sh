screen -d -m bash -c "source /opt/ros/indigo/setup.bash; roslaunch rosbridge_server rosbridge_websocket.launch port:=8888"
python site.py 
