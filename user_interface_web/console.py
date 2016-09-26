#!/usr/bin/env python
import herbpy
#import prpy.rave

# Load the query
from prpy_benchmarks.query import BenchmarkQuery
from push_planner_benchmarks.benchmark_utils import draw_goal, draw_sbounds

from or_pushing.push_planner_module import PushPlannerModule
from datetime import datetime
from state_updater import StateUpdater

def initialize_module(queryfile, pathfile=None, env=None, robot=None):
    """
    @param queryfile The file that contains a BenchmarkQuery
    @param pathfile The file containing a planned path for this query
    @param env The environment to deserialize the query into
    @param robot The robot to deserialize
    """
    query = BenchmarkQuery()
    with open(queryfile, 'r') as f:
        query.from_yaml(yaml.load(f.read()), env=env, robot=robot)

    # Initialize the module
    module = PushPlannerModule(query.env, query.args[0])
    module.Initialize(**query.kwargs)

    print("Done Initialize")

    if pathfile:
        with open(pathfile, 'r') as f:
            path = yaml.load(f.read())
        module.SetState(path[0]['state'])

    return module, query
       
def runBackEnd(namespace):
    queryfiles=['../queries/bh280_practice1.query', '../queries/bh280_practice2.query',
                '../queries/bh280_2movables.query', '../queries/bh280_2movables4.query',
                '../queries/bh280_2movables.query', '../queries/bh280_2movables4.query',
                '../queries/bh280_3movables.query', '../queries/bh280_3movables2.query',
                '../queries/bh280_3movables.query', '../queries/bh280_3movables2.query',
                '../queries/bh280_4movables.query', '../queries/bh280_4movables2.query',
                '../queries/bh280_4movables.query', '../queries/bh280_4movables2.query',
                '../queries/bh280_5movables.query', '../queries/bh280_5movables.query']
    path=None
    env = None
    robot = None
    #controls = []
    #states = []

    module, query = initialize_module(queryfiles[0], pathfile=path,     
                                      robot=robot, env=env)

    env = query.env
    robot = query.args[0]
    #params = query.kwargs
    #goal_object = query.args[1]
    #goal = query.args[2]

    x = StateUpdater(robot,env,module,query,queryfiles,0,namespace)



	
