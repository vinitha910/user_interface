#!/usr/bin/env python
from push_planner_benchmarks.tools import play_path

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Test playing a path")
    parser.add_argument("--query", type=str, required=True, 
                        help="The yaml file that specifies the query to load")
    parser.add_argument("--path", type=str, required=True,
                        help="The yaml file that specifies the ompl path to play")
    parser.add_argument("--save", action="store_true",
                        help="If true, each state on the path will be written to file")
    parser.add_argument("--outdir", type=str,
                        help="The directory to save files to, if None the current directory is used")
    parser.add_argument('--extension', type=str, default='png',
                        help="The extension for the images files (default: png)")
    parser.add_argument("--interact", action="store_true",
                        help="If true, user is prompted after each state is rendered")
    parser.add_argument("--belief", action="store_true",
                        help="Flag the path as a belief state path")
    parser.add_argument("--reverse", action="store_true",
			help="Play path in reverse")
    args = parser.parse_args()

    if args.outdir is not None:
        import os
        if not os.path.exists(args.outdir):
            os.makedirs(args.outdir)

    play_path(args.query, args.path, path_obj='manip',
              reverse=args.reverse, extension=args.extension, 
              belief=args.belief, save=args.save, 
              interact=args.interact, outdir=args.outdir)
    raw_input('Press enter to quit')
