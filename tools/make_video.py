#!/usr/bin/env python
import os
from push_planner_benchmarks.tools import make_video

if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser(description="Make a video from a sequence of images")
    parser.add_argument('--image-dir', type=str, required=True,
                        help='The directory to load images from')
    parser.add_argument('--outfile', type=str, required=True,
                        help='The name of the mp4 file to write')
    parser.add_argument('--fps', type=float, default=10.,
                        help='Frames per second')
    args = parser.parse_args()

    pattern = os.path.join(args.image_dir, '%03d.png')
    make_video(pattern, args.outfile, args.fps)
