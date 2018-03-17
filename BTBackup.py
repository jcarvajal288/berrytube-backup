"""
Downloads videos from radio.berrytube.tv/vidlog.txt to a target directory.

Requires youtube-dl to be on your PATH. https://youtube-dl.org/
"""

import argparse

def parseArgs():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--target', metavar='<directory>', type=str, dest='targetDirectory', required=False,
            help='directory to put the downloaded videos.  Will be created if it does not exist.')
    parser.add_argument('-r', '--requiredPlays', metavar='<integer>', type=int, dest='requiredPlays', required=False,
            help='number of plays a single video needs to have in vidlog.txt to warrant backing up.')
    return parser.parse_args()


def main():
    targetDirectory = "V:\Media\Backup"
    requiredPlays = 2

    args = parseArgs()
    if args.targetDirectory is not None:
        targetDirectory = args.targetDirectory
    if args.requiredPlays is not None:
        requiredPlays = args.requiredPlays

    


if __name__ == "__main__":
    main()
