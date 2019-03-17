from bs4 import BeautifulSoup
import requests
import urllib
import sys
import time
from functools import wraps

def retry(exceptions, tries=4, delay=3, backoff=2, logger=None):
   """
   Retry calling the decorated function using an exponential backoff.

   Args:
       exceptions: The exception to check. may be a tuple of
           exceptions to check.
       tries: Number of times to try (not retry) before giving up.
       delay: Initial delay between retries in seconds.
       backoff: Backoff multiplier (e.g. value of 2 will double the delay
           each retry).
       logger: Logger to use. If None, print.

   Salient note: This may or may not work.  I couldn't get a timeout to happen
   after I added it.  Figures.  Keeping it in on the off chance it does.
   """
   def deco_retry(f):

       @wraps(f)
       def f_retry(*args, **kwargs):
           mtries, mdelay = tries, delay
           while mtries > 1:
               try:
                   return f(*args, **kwargs)
               except exceptions as e:
                   msg = '{}, Retrying in {} seconds...'.format(e, mdelay)
                   if logger:
                       logger.warning(msg)
                   else:
                       print(msg)
                   time.sleep(mdelay)
                   mtries -= 1
                   mdelay *= backoff
           return f(*args, **kwargs)

       return f_retry  # true decorator

   return deco_retry


class ChatLogReader(object):
    chatLogUrl = "https://logs.multihoofdrinking.com/"

    def __listLogFileUrls(self):
        page = requests.get(self.chatLogUrl).text
        soup = BeautifulSoup(page, 'html.parser')
        return (node.get('href') for node in soup.find_all('a') if node.get('href').endswith('log'))

    @retry(TimeoutError, tries=5, delay=3, backoff=2)
    def __readLogFile(self, logFileUrl):
        print("Reading {}...".format(logFileUrl))
        logFile = urllib.request.urlopen(logFileUrl)
        for line in logFile:
            yield line

    def listAllLogLines(self):
        logfileUrls = self.__listLogFileUrls()
        for logFileUrl in logfileUrls:
            try:
                for line in self.__readLogFile(logFileUrl):
                    yield line
            except urllib.error.URLError as error:
                print(error)
                continue

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

