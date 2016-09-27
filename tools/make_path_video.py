#!/usr/bin/env python
import os
from push_planner_benchmarks.tools import play_path
from push_planner_benchmarks.tools import make_video
from or_pushing.push_planner_module import PushPlannerModule

import logging
logger = logging.getLogger('make_path_video')
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser(description="Play a path at a new resolution and create a video")

    parser.add_argument("--query", default=None, required = True,
                        help="The yaml file that describes the start scene")
    parser.add_argument("--path", type=str, required=True,
                        help="The path to turn to video")
    parser.add_argument("--belief", action="store_true",
                        help="Flag the path as a belief state path")
    parser.add_argument("--outfile", type=str, required=True,
                        help="The name of the .mp4 or .mov file to create")
    parser.add_argument("--stepsize", type=float, default=0.1,
                        help="The timestep to playback the path")
    parser.add_argument("--intermediate-dir", type=str, default="/tmp",
                        help="The directory to dump intermediate files such as the new path and the images used to create the final video")
    
    args = parser.parse_args()
    idir = args.intermediate_dir

    # Check if the intermediate directory exists, if so prompt and then delete
    if os.path.isdir(idir):
        v = raw_input('The intermediate directory %s exists. Press enter to delete all .png files in this directory and continue (q to quit).' % idir)
        if v == 'q':
            exit()
        for f in os.listdir(idir):
            if f.endswith('.png'):
                filename = os.path.join(idir, f)
                logger.info('Deleting file %s' % filename)
                os.remove(filename)
    else:
        os.makedirs(idir)


    
    # Load the module
    if not args.belief:
        from console import initialize_module
        module, query = initialize_module(args.query, args.path)
        results = module.ExecutePath(args.path, stepsize=args.stepsize, num_executions=1, subsample=True)
        new_path = results['rollout_metadata'][0]['path']

        # Save the path            
        new_path_file = os.path.join(idir, 'new_path.ompl')
        with open(new_path_file, 'w') as f:
            import yaml
            f.write(yaml.dump(new_path))
    else:
        new_path_file = args.path


    # Play the path back and make images from it
    play_path(args.query, new_path_file, belief=args.belief, save=True, outdir=idir)

    # Now load those images and make a video
    pattern = os.path.join(idir, '%3d.png')
    make_video(pattern, args.outfile, fps=1./args.stepsize)
