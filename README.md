# File Rotate
A tiny script for rotation big files. by next limits: size,count

## Install

`git checkout git@github.com:free6k/filerotate.git`

## How it use

`python filerotate.py -f '/backups/dump_*.sql.gz'' -c 30 -s 100M`

## Params

- -f --file - pattern for find files to rotate
- -c --count - minimal count files, unnecessary will be delete
- -s --size - max summary size, unnecessary will be delete

## Example

`python filerotate.py -f '/backups/dump_*.sql.gz' -c 30 -s 100M`

script will find files by `<pattern: /backups/dump_*.sql.gz>` 
next `if count > 30`, will be delete old files over 30  
after `summary files size > 100M`, will be delete old files until summary size will be equal 100M
