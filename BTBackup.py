"""
Downloads videos from radio.berrytube.tv/vidlog.txt to a target directory.

Requires youtube-dl to be on your PATH. https://youtube-dl.org/
"""

import argparse
import collections
import os
import pathlib
import urllib.request
import youtube_dl

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


def readVidLog():
    print("Parsing vidlog...")
    vidLogUrl = 'http://radio.berrytube.tv/vidlog.txt'
    vidlog = urllib.request.urlopen(vidLogUrl)
    videosById = {}
    errors = []
    for line in vidlog:
        try:
            video = Video(line)
        except TypeError:
            # TODO: log errored videos
            errors.append(line)
            continue
        if video.vidId in videosById:
            videosById[video.vidId].incrementCount()
        else:
            videosById[video.vidId] = video
    if len(errors) > 0:
        print("Unable to parse {} lines of vidlog.txt".format(len(errors)))
    return videosById


def performDownload(videosToDownload, targetDirectory):
    pathlib.Path(targetDirectory).mkdir(parents=True, exist_ok=True)
    video = videosToDownload[10]
    videoUrl = "https://www.youtube.com/watch?v={}".format(video.vidId)
    options =  {
        'output': "%(title)s-%(id)s.%(ext)s"    
    }
    previousWorkingDirectory = os.getcwd()
    os.chdir(targetDirectory)
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([videoUrl])
    os.chdir(previousWorkingDirectory)


def main():
    targetDirectory = "V:/Media/berrytubeBackup/"
    requiredPlays = 2

    args = parseArgs()
    if args.targetDirectory is not None:
        targetDirectory = args.targetDirectory
    if args.requiredPlays is not None:
        requiredPlays = args.requiredPlays

    if not targetDirectory.endswith('/'):
        targetDirectory += '/'

    videosById = readVidLog()
    print("Found {} unique videos.".format(len(videosById)))
    videosToDownload = [v for v in videosById.values() if v.playCount >= requiredPlays and v.source == 'yt']
    print("Will download {} videos to {}".format(len(videosToDownload), targetDirectory))
    answer = input("Do you want to continue? (yes/no)")
    if answer == 'y' or answer == 'yes':
        performDownload(videosToDownload, targetDirectory)


if __name__ == "__main__":
    main()
