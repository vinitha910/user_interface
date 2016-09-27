#!/usr/bin/env python
import argparse, os, yaml

def initialize_module(queryfile, env=None, robot=None):
    """
    @param queryfile The file that contains a BenchmarkQuery
    @param env The environment to deserialize the query into
    @param robot The robot to deserialize
    """

    # Load the query
    from prpy_benchmarks.query import BenchmarkQuery
    query = BenchmarkQuery()
    with open(queryfile, 'r') as f:
        query.from_yaml(yaml.load(f.read()), env=env, robot=robot)

    # Initialize the module
    from or_pushing.push_planner_module import PushPlannerModule
    module = PushPlannerModule(query.env, query.args[0])

    module.Initialize(**query.kwargs)

    return module, query

def set_viewer(viewer, query):
    """ 
    Helper hack because loading visualize
    breaks on some 14.04 instances
    """
    query.env.SetViewer(viewer)

    from push_planner_benchmarks.benchmark_utils import draw_goal, draw_sbounds
    handles = []
    handles.append(draw_goal(query))
    handles.append(draw_sbounds(query))
    return handles

def save_query(filename):
    with open(filename, 'w') as f:
        f.write(yaml.dump(query.to_yaml()))

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Test console for running individual components of the system")
    parser.add_argument("--query", default=None,
                        help="The yaml file that describes the query")
    parser.add_argument("--savefile", default=None,
                        help="The file to save the query to")
    parser.add_argument("--viewer", dest="viewer", default=None,
                        help="Set the viewer")
    
    args = parser.parse_args()
    if not args.query or not args.savefile:
        print 'Must provide a query and savefile'
        parser.print_help()
        exit(0)

    queryfile = args.query
    savefile = args.savefile

    env = None
    robot = None

    module, query = initialize_module(queryfile, robot=robot, env=env)
    if args.viewer:
        handles = set_viewer(args.viewer, query)

    env = query.env
    robot = query.args[0]

    print 'You can now make changes to you query'

    import IPython; IPython.embed()
    
    save_query(savefile)

    print 'Your query was saved to {}'.format(savefile)
