from bs4 import BeautifulSoup
import requests
import urllib

class ChatLogReader(object):
    chatLogUrl = "https://logs.multihoofdrinking.com/"

    def __listLogFileUrls(self):
        page = requests.get(self.chatLogUrl).text
        soup = BeautifulSoup(page, 'html.parser')
        return (node.get('href') for node in soup.find_all('a') if node.get('href').endswith('log'))

    def __readLogFile(self, logFileUrl):
        logFile = urllib.request.urlopen(logFileUrl)
        for line in logFile:
            yield line

    def listAllLogLines(self):
        logfileUrls = self.__listLogFileUrls()
        for logFileUrl in logfileUrls:
            for line in self.__readLogFile(logFileUrl):
                yield line

    def listAllAdminLines(self):
        """
        List all administrative lines in the berrytube logs.
        These lines all start with '-!-'
        """
        for line in self.listAllLogLines():
            if b'-!-' in line:
                yield line

    def listAllVideoPlayLines(self):
        """
        List all administrative lines showing a new video is playing.
        """
        for line in self.listAllAdminLines():
            if b'Now Playing:' in line:
                yield line

    def listAllLinesByKeyword(self, keyword):
        """
        List all lines that contain a given keyword.
        The keyword must be a binary string e.g. b'foo'.
        """
        for line in self.listAllLogLines():
            if keyword in line:
                yield line


if __name__ == '__main__':
    logReader = ChatLogReader()
    for line in logReader.listAllVideoPlayLines():
        print(line)
