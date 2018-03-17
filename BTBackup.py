"""
Downloads videos from radio.berrytube.tv/vidlog.txt to a target directory.

Requires youtube-dl to be on your PATH. https://youtube-dl.org/
"""

import argparse
import collections
import urllib.request

Video = collections.namedtuple('Video', 'timestamp source vidId title')

class Video(object):
    def __init__(self, line):
        data = line.decode('utf-8').strip().split('<>')
        self.timestamp = data[0]
        self.source = data[1]
        self.vidId = data[2]
        self.title = data[3]
        self.playCount = 1

    def incrementCount(self):
        self.playCount += 1

def parseArgs():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--target', metavar='<directory>', type=str, dest='targetDirectory', required=False,
            help='directory to put the downloaded videos.  Will be created if it does not exist.')
    parser.add_argument('-r', '--requiredPlays', metavar='<integer>', type=int, dest='requiredPlays', required=False,
            help='number of plays a single video needs to have in vidlog.txt to warrant backing up.')
    #parser.add_argument('-v', '--verbose', help='verbose output')
    return parser.parse_args()


def readVidLog(requiredPlays):
    vidLogUrl = 'http://radio.berrytube.tv/vidlog.txt'
    vidlog = urllib.request.urlopen(vidLogUrl)
    videosById = {}
    errors = 0
    for line in vidlog:
        try:
            video = Video(line)
        except TypeError:
            # TODO: log errored videos
            errors += 1
            continue
        if video.vidId in videosById:
            videosById[video.vidId].incrementCount()
        else:
            videosById[video.vidId] = video
    videosToDownload = [v for v in videosById.values() if v.playCount >= requiredPlays]
    if errors > 0:
        print("Unable to parse {} lines of vidlog.txt".format(errors))
    print("Will download {}/{} videos.".format(len(videosToDownload), len(videosById)))
    return videosToDownload




def main():
    targetDirectory = "V:\Media\Backup"
    requiredPlays = 2

    args = parseArgs()
    if args.targetDirectory is not None:
        targetDirectory = args.targetDirectory
    if args.requiredPlays is not None:
        requiredPlays = args.requiredPlays

    videosToDownload = readVidLog(requiredPlays)


if __name__ == "__main__":
    main()
