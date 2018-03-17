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


class Logger(object):
    def __init__(self, ydl):
        self.errors = []
        self.ydl = ydl

    def to_stdout(self, message, skip_eol=False, check_quiet=False):
        """Print message to stdout if not in quiet mode."""
        if not check_quiet or not self.ydl.params.get('quiet', False):
            message = self.ydl._bidi_workaround(message)
            terminator = ['\n', ''][skip_eol]
            output = message + terminator
            self.ydl._write_string(output, self.ydl._screen_file)

    def to_stderr(self, message):
        """Print message to stderr."""
        message = self.ydl._bidi_workaround(message)
        output = message + '\n'
        self.ydl._write_string(output, self.ydl._err_file)

    def debug(self, msg):
        skip_eol = ' ETA ' in msg
        self.to_stdout(msg, skip_eol)

    def warning(self, msg):
        self.to_stdout(msg)

    def error(self, msg):
        self.errors.append(msg)
        self.to_stderr(msg)


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


def filterVideos(videosById, requiredPlays):
    print("Filtering out videos with fewer than {} plays.".format(requiredPlays))
    return [v for v in videosById.values() if v.playCount >= requiredPlays and v.source == 'yt']


def performDownload(videosToDownload, targetDirectory):
    pathlib.Path(targetDirectory).mkdir(parents=True, exist_ok=True)
    video = videosToDownload[10]
    urls = ["https://www.youtube.com/watch?v={}".format(v.vidId) for v in videosToDownload]
    options =  {
        'ignoreerrors': True,
        'output': "%(title)s-%(id)s.%(ext)s"
    }
    previousWorkingDirectory = os.getcwd()
    os.chdir(targetDirectory)
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.params['logger'] = Logger(ydl) # done here to reuse the default logger's nifty screen logging
        ydl.download(urls[:10])
    os.chdir(previousWorkingDirectory)


def main():
    targetDirectory = "V:/Media/berrytubeBackup/"
    requiredPlays = 5

    args = parseArgs()
    if args.targetDirectory is not None:
        targetDirectory = args.targetDirectory
    if args.requiredPlays is not None:
        requiredPlays = args.requiredPlays

    if not targetDirectory.endswith('/'):
        targetDirectory += '/'

    videosById = readVidLog()
    print("Found {} unique videos.".format(len(videosById)))
    videosToDownload = filterVideos(videosById, requiredPlays)
    print("Will download {} videos to {}".format(len(videosToDownload), targetDirectory))
    answer = input("Do you want to continue? (yes/no)")
    if answer == 'y' or answer == 'yes':
        performDownload(videosToDownload, targetDirectory)


if __name__ == "__main__":
    main()
