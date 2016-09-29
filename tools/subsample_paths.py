#!/usr/bin/env
import argparse, os, yaml

def initialize_module(queryfile, pathfile=None, env=None, robot=None, paramsfile=None, box2d=False, darrt=False):
    """
    @param queryfile The file that contains a BenchmarkQuery
    @param pathfile The file containing a planned path for this query
    @param env The environment to deserialize the query into
    @param robot The robot to deserialize
    @param paramsfile A file containing parameters for the planning instance
      These will override parameters defined in the query
    @param box2d If true, load the OpenRAVE/Box2d integrated module
    @param darrt If true, load the OpenRAVE DARRT module
    """

    # Load the query
    from prpy_benchmarks.query import BenchmarkQuery
    query = BenchmarkQuery()
    with open(queryfile, 'r') as f:
        query.from_yaml(yaml.load(f.read()), env=env, robot=robot)

    if paramsfile is not None:
        with open(paramsfile, 'r') as f:
            params = yaml.load(f.read())
        query.kwargs.update(params)

    # Initialize the module
    if not box2d and not darrt:
        from or_pushing.push_planner_module import PushPlannerModule
        module = PushPlannerModule(query.env, query.args[0])
    elif box2d:
        from or_box2d_pushing.box2d_module import B2Module
        module = B2Module(query.env, query.args[0])
    elif darrt:
        from darrt_push_planner.darrt_module import DARRTModule
        module = DARRTModule(query.env, query.args[0])

    module.Initialize(**query.kwargs)

    if pathfile and os.path.isfile(pathfile):
        with open(pathfile, 'r') as f:
            path = yaml.load(f.read())
        module.SetState(path[0]['state'])
    else:
        print 'Warning: No path file found. Failed test?'

    return module, query

def subsample_path(d, overwrite=False, box2d=False, debug=False):
    
    query = os.path.join(d, 'query.yaml')
    path = os.path.join(d, 'path.ompl')
    path_out = os.path.join(d, 'path_subsample.ompl')

    if not os.path.exists(path):
        print 'Skipping path: %s. Failed trial.' % path
        return
    if os.path.exists(path_out) and not overwrite:
        print 'Skipping path: %s. Subsampled path exists: %s' % (path, path_out)
        return

    module, query = initialize_module(query, path, box2d=box2d)

    with open(path, 'r') as f:
        path_yaml = yaml.load(f.read())

    results = module.ExecutePath(path_yaml, stepsize=0.1, num_executions=1, 
                                 subsample=True, debug=debug)
    new_path = results['rollout_metadata'][0]['path']

    with open(path_out, 'w') as f:
        f.write(yaml.dump(new_path))
    print 'Saved path: %s' % path_out
    

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Subsample a path at a finer resolution")
    parser.add_argument("--dir", default=None, 
                       help="The directory containing the path to subsample")
    parser.add_argument("--batch-dir", default=None, 
                       help="The directory containing the path to subsample")
    parser.add_argument("--debug", action="store_true",
                        help="Run in debug mode")
    parser.add_argument("--box2d", action="store_true",
                        help="Use box2d for the subsampling")
    args = parser.parse_args()

    if args.dir:
        subsample_path(args.dir, box2d=args.box2d, debug=args.debug)
    elif args.batch_dir:
        for d in os.listdir(args.batch_dir):
            dname = os.path.join(args.batch_dir, d)
            if os.path.isdir(dname):
                subsample_path(dname, box2d=args.box2d, debug=args.debug)
    else:
        print 'Must specify either a dir or a batch directory'
        exit(0)




