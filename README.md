# berrytube-backup
Downloads videos from the berrytube chat logs to a target directory.

## Dependencies

This project uses pipenv for dependency management (https://pipenv.readthedocs.io/en/latest/)

To run this project, first have pipenv installed, then run

> $ pipenv install
>
> $ pipenv run python3 BTBackup.py <arguments>

## Command Line Arguments

**-t <directory>, --target <directory>**

  directory location to put the downloaded videos.  It will be created if it doesn't exist.
  
**-r <integer>, --requiredPlays <integer>**

  any video with fewer plays than this number will not be downloaded.  Defaults to 5.
  
**-y, --yes**

  automatically say yes to the 'are you sure?' prompt before downloading videos
  
**--no-progress**

  do not print the youtube-dl progress bar while downloading
  
## Example

> $ pipenv run python3 BTBackup.py --target ./berrytubeBackup/ --requiredPlays 3

  Downloads videos with 3 or greater plays into the directory 'berrytubeBackup'
