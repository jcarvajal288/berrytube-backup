from bs4 import BeautifulSoup
import requests
import urllib

multihoofUrl = "https://logs.multihoofdrinking.com/"


def listLogFileUrls():
    page = requests.get(multihoofUrl).text
    soup = BeautifulSoup(page, 'html.parser')
    return (node.get('href') for node in soup.find_all('a') if node.get('href').endswith('log'))


def readLogFile(logFileUrl):
    logFile = urllib.request.urlopen(logFileUrl)
    for line in logFile:
        print(line)


def main():
    logfileUrls = listLogFileUrls()
    for logFileUrl in logfileUrls:
        readLogFile(logFileUrl) 


if __name__ == '__main__':
    main()
