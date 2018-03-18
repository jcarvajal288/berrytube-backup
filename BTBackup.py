"""
Downloads videos from radio.berrytube.tv/vidlog.txt to a target directory.

Requires youtube-dl to be on your PATH. https://youtube-dl.org/
"""

import argparse
import os
import pathlib
import urllib.request
import youtube_dl

class Video(object):
    def __init__(self, line):
        data = line.decode('utf-8').strip().split('<>')
        self.timestamp = data[0]
        self.source = data[1]
        self.vidId = data[2]
        self.title = data[3].encode('utf-8')
        self.playCount = 1

    def incrementCount(self):
        self.playCount += 1


class Logger(object):
    def __init__(self):
        self.errors = []
        self.ydl = None

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
        self.to_stdout(msg, skip_eol, check_quiet=True)

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
    parser.add_argument('-y', '--yes', action="store_true", dest='noPrompt', 
            help="automatically say yes to the 'are you sure?' prompt")
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


def getAlreadyDownloadedVidIds(targetDirectory):
    if not os.path.isdir(targetDirectory):
        return []
    return [v.split(' - ')[-1][:11] for v in os.listdir(targetDirectory)]


def filterVideos(videosById, alreadyDownloadedIds, requiredPlays):
    def videoShouldBeDownloaded(v):
        return v.playCount >= requiredPlays \
               and v.source == 'yt' \
               and v.vidId not in alreadyDownloadedIds

    print("Filtering out videos with fewer than {} plays.".format(requiredPlays))
    return [v for v in videosById.values() if videoShouldBeDownloaded(v)]


def performDownload(videosToDownload, targetDirectory):
    pathlib.Path(targetDirectory).mkdir(parents=True, exist_ok=True)
    urls = ["https://www.youtube.com/watch?v={}".format(v.vidId) for v in videosToDownload]
    options =  {
        'ignoreerrors': True,
        'outtmpl': "{}%(title)s - %(id)s.%(ext)s".format(targetDirectory)
    }
    #previousWorkingDirectory = os.getcwd()
    #os.chdir(targetDirectory)
    logger = Logger()
    with youtube_dl.YoutubeDL(options) as ydl:
        logger.ydl = ydl # done here to reuse the default logger's nifty screen logging
        ydl.params['logger'] = logger
        try:
            ydl.download(urls)
        except KeyboardInterrupt:
            pass # let the program finish writing its error log
    #os.chdir(previousWorkingDirectory)
    return logger


def processErrors(logger, videosById):
    print("ERRORS OCCURRED WHILE DOWNLOADING.  Some videos may be unavailable.  Check errorLog.txt for details.")
    with open('errorLog.txt', 'w') as logFile:
        print("UNAVAILABLE VIDEOS:", file=logFile)
        for error in logger.errors:
            if "This video is unavailable." in error or "This video is no longer available" in error:
                vidId = error.split(': ')[1]
                title = videosById[vidId].title
                print("\t{} (https://www.youtube.com/watch?v={})".format(title, vidId), file=logFile)



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
    print("Found {} unique videos in vidlog.".format(len(videosById)))

    alreadyDownloadedIds = getAlreadyDownloadedVidIds(targetDirectory)
    if len(alreadyDownloadedIds) > 0:
        print("Found {} videos already in target directory.".format(len(alreadyDownloadedIds)))

    videosToDownload = filterVideos(videosById, alreadyDownloadedIds, requiredPlays)

    print("Will download {} videos to {}".format(len(videosToDownload), targetDirectory))
    if not args.noPrompt:
        answer = input("Do you want to continue? (yes/no)")
        if not (answer == 'y' or answer == 'yes'):
            return
    logger = performDownload(videosToDownload, targetDirectory)
    processErrors(logger, videosById)


if __name__ == "__main__":
    main()
