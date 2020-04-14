# File Rotate
A tiny script for rotation big files. By next limits: size, count and intervals

## Install

`git checkout git@github.com:free6k/filerotate.git`

## How it use

`python filerotate.py -f '/backups/dump_*.sql.gz'' -c 30 -s 100M`

## Params

- -f --file - pattern for find files to rotate
- -c --count - minimal count files, unnecessary will be delete
- -s --size - max summary size (format: 100K 100M 100G 1T, base unit byte), unnecessary will be delete
- -i --interval - rotating by intervals, -i '1d:2 1m:2'. seconds (formats: 1min 1h 1d 1w 1d 1m 1y, base unit second), integer count

## Example

### Default case

`python filerotate.py -f '/backups/dump_*.sql.gz' -c 30 -s 100M`

The script will find files by `<pattern: /backups/dump_*.sql.gz>` 
next `if count > 30`, will be delete old files over 30  
after `summary files size > 100M`, will be delete old files until summary size will be equal 100M

### Advanced case

`python filerotate.py -f '/backups/dump_*.sql.gz' -i '1d:* 7d:4 1mon:2 1y:1''`

The script will find files, and stayed files less 1d:(any count) and less 7d:(4 files) and 1mon:(2 files) and 1y:(1 files).
After script working in folder stayed today any count files, oldest 7 days 4 files, oldest 1 month 2 files and oldest 1year 1 files


### Cron example

`* * * * * env python /root/filerotate.py -f '/opt/backups/dump_*.sql.gz' -c 30 -s 100M > /dev/null 2>&1`
