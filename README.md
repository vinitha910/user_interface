# User Interface
This package provides a user interface for collecting workspace trajectories using HERB's end effector

## Installation
You need to install the rosbridge_suite. It  includes a WebSocket server for web browser to interact with. 
```
cmd> sudo apt-get install ros-indigo-rosbridge-server
```

##Queries
To execute queries the following additional installation steps are necessary:
```
cmd> apt-get install ros-indigo-gperftools-21
```
Then checkout [randomized_rearrangement_planning](https://github.com/personalrobotics/randomized_rearrangement_planning), [or_fcl](https://github.com/personalrobotics/or_fcl) and the branch ```feature/new_planning_benchmarks``` of repository [benchmarks](https://github.com/personalrobotics/benchmarks) into your catkin workspace.

### Query properties
One component the query is comprised of is env: the OpenRAVE environment. These queries are scenes that we want the users to complete. 