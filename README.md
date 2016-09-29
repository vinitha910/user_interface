# User Interface
This package provides a user interface for collecting workspace trajectories using HERB's end effector

## Installation
You need to install the rosbridge_suite. Rosbridge server is part of the rosbridge_suite of packages, providing a WebSocket transport layer. By providing a WebSocket connection, rosbridge server allows webpages to send and recieve ros messages and service calls using the rosbridge protocol. 
```
cmd> sudo apt-get install ros-indigo-rosbridge-server
```

##Queries
One component the query is comprised of is env: the OpenRAVE environment. These queries are scenes that we want the users to complete. To execute queries the following additional installation steps are necessary:
```
cmd> apt-get install ros-indigo-gperftools-21
```
Then checkout [randomized_rearrangement_planning](https://github.com/personalrobotics/randomized_rearrangement_planning), [or_fcl](https://github.com/personalrobotics/or_fcl) and the branch ```feature/new_planning_benchmarks``` of repository [benchmarks](https://github.com/personalrobotics/benchmarks) into your catkin workspace.


###Make Queries
A variety of queries are availabe in the ```queries/``` directory. To make a new query, execute an existing query and you can add, remove and move kinbodies. To make a new query:
```bash
$ cd tools
$ python make_query.py --query ../queries/bh280_1movable.query --savefile bh280_temp.yaml \
--viewer interactivemarker
```
After execution an IPython console will have opened from which you can add or remove kinbodies. Open ```rviz```, add ```interactivemarker``` and set ```Update Topic``` to ```/openrave/update```. To move objects around right-click on the object, hover over ```Body``` and click ```Pose Controls```. You can now drag the objects around. When have finished making the query, exit out of the IPython console and your new query will be saved to the file you passed to the savefile argument. 

##Prepare Study for Deployment
There a few things that need to be changed for you to be able to deploy the study. 

First, if you would like to use a different set of queries than those already in the ```queries/``` directory you will need to change the paths in the ```queryfiles``` list in ```user_interface_web/run_back_end.py```.

Next, in ```user_interface_web/site.py``` change ```/home/ubuntu/results/``` in line 65 to the directory you would like to save the results. Change ```app.run(host='0.0.0.0', port="YOUR_PORT_NUMBER")``` in line 74.

If you changed the number of queries in ```user_interface_web/run_back_end.py``` change ```if req.sceneNum < NUM_QUERIES:``` in line 96 of ```user_interface_web/state_updater.py```. Finally, change ```/home/ubuntu/results/``` in line 86 and 105 to the directory you would like to save the results.

##Deploy Study Locally
To the deploy the study on your local computer, first launch the ```rosbridge_server``` in a new screen and then run ```site.py```:
```bash
$ screen -S rosbridge
$ roslaunch rosbridge_server rosbridge_websocket.launch port:=8888
$ <CTRL+a><d> #detach from the screen
$ python site.py
```

To view the study, type ```http://localhost:YOUR_PORT_NUMBER/``` in the browser.

##Deploy Study on Mechanical Turk
Before you can deploy this study on Mechanical Turk, you need to create an ```EC2-Instance``` on Amazon Web Services. See Clint Liddick for details.

