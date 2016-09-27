#!/usr/bin/env python
import herbpy
import yaml

# Load the query
from prpy_benchmarks.query import BenchmarkQuery
from push_planner_benchmarks.benchmark_utils import draw_goal, draw_sbounds

from or_pushing.push_planner_module import PushPlannerModule

class Module():
    def initialize_module(self, queryfile, pathfile=None, env=None, robot=None):
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
