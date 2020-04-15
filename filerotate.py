import sys
import os
import glob
import getopt
import time
import re
import hashlib
import collections

PID = str(os.getpid())
PIDFILE = "/tmp/FILEROTATE-RUNNING-.pid"


def can_it_run():
    # Check wether lock PIDFILE exists
    if os.path.isfile(PIDFILE):
        return False
    else:
        return True


def run(argv):
    filepattern = count = maxsize = None
    interval = {}

    try:
        opts, args = getopt.getopt(
            argv, "hf:c:s:i:", ["file=", "count=", "size=", "interval="])
    except getopt.GetoptError:
        print('rotate.py -f /test/test*.log -c 10 -s 100M')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(
                'rotate.py -f <filepattern> -c <max count: more 0> -s <max summary in 1M 1K 1G 1T> -i <intervals for file keeping: 1d:* 1m:10>')
            sys.exit()
        elif opt in ("-f", "--file"):
            filepattern = arg
        elif opt in ("-c", "--count"):
            count = int(arg)
        elif opt in ("-s", "--size"):
            maxsize = arg.lower()
            size = int(re.sub("\D", "", maxsize))

            if maxsize.find('k') != -1:
                maxsize = int(size) * 1024.0
            elif maxsize.find('m') != -1:
                maxsize = int(size) * 1024.0 * 1024.0
            elif maxsize.find('g') != -1:
                maxsize = int(size) * 1024.0 * 1024.0 * 1024.0
            elif maxsize.find('t') != -1:
                maxsize = int(size) * 1024.0 * 1024.0 * 1024.0 * 1024.0
            else:
                maxsize = int(size)

        elif opt in ("-i", "--interval"):
            interval = arg.lower()
            interval = arg.split(' ')

            tmp_int = {}
            total_range = None

            for i in interval:
                split = i.split(':')

                if len(split) < 2 or (not split[0] or not split[1]):
                    continue

                range, fcount = split
                range_size = int(re.sub("\D", "", range))

                if fcount == '*':
                    fcount = -1
                else:
                    fcount = int(re.sub("\D", "", fcount))

                interval_info = {'range': range,
                                 'count': fcount, 'files': [], 'oldfiles': []}

                if range.find('min') != -1:
                    range = int(range_size) * 60
                elif range.find('h') != -1:
                    range = int(range_size) * 60 * 60
                elif range.find('d') != -1:
                    range = int(range_size) * 60 * 60 * 24
                elif range.find('w') != -1:
                    range = int(range_size) * 60 * 60 * 24 * 7
                elif range.find('m') != -1:
                    range = int(range_size) * 60 * 60 * 24 * 7 * 4
                elif range.find('y') != -1:
                    range = int(range_size) * 60 * 60 * 24 * 7 * 4 * 12
                else:
                    range = range_size

                interval_info['rangetime'] = range

                total_range = range if not total_range else total_range + range

                if total_range in tmp_int:
                    tmp_int[total_range] = interval_info
                else:
                    tmp_int[total_range] = interval_info

            interval = collections.OrderedDict(sorted(tmp_int.items()))

    if not((filepattern and (count or maxsize or len(interval) > 0))):
        print('One of the parameters must be: -s <maxsize megabytes> or -c <count> or -i <interval>')
        sys.exit(2)

    if not(count):
        count = 0

    open(PIDFILE, 'w').write(PID)

    try:
        files = glob.glob(filepattern)
        files.sort(key=os.path.getmtime, reverse=True)

        if len(files) > 0:

            if count > 0:
                print('Found %d files, last %s' % (len(files), time.strftime(
                    '%b %d %Y %H:%M:%S', time.localtime(os.path.getmtime(files[0])))))

                oldfiles = files[count:]

                for oldfile in oldfiles:
                    os.unlink(oldfile)

                if oldfiles:
                    print('Deleted %d files by count limit' % len(oldfiles))

                files = files[:len(files) - len(oldfiles)]

            if maxsize > 0:
                total_size = 0
                files_with_size = {}

                for file in files:
                    files_with_size[file] = os.path.getsize(file)
                    total_size += files_with_size[file]

                print('Total size %s limit %s' %
                      (sizeof_fmt(total_size), sizeof_fmt(maxsize)))

                if total_size > maxsize:
                    realsize = 0
                    countd = 0

                    for file in files_with_size:
                        realsize += files_with_size[file]

                        if realsize > maxsize:
                            countd += 1

                    oldfiles = files[len(files) - countd:]

                    for oldfile in oldfiles:
                        os.unlink(oldfile)

                    if oldfiles:
                        print('Deleted %d files by maxsize limit' %
                              len(oldfiles))

                    files = files[:len(files) - len(oldfiles)]

            if len(interval) > 0:
                files_full_out_of_interval = dict.fromkeys(files)

                for f in files:
                    ftime = os.path.getmtime(f)
                    last_start = None

                    for i in interval.keys():
                        start = os.path.getmtime(files[0]) - interval[i]['rangetime']
                        end = last_start if last_start else os.path.getmtime(files[0])

                        #print interval[i]['range'], start, ftime, end, start <= ftime <= end, f

                        if start <= ftime <= end:
                            interval[i]['files'].append(f)

                            if f in files_full_out_of_interval:
                                del files_full_out_of_interval[f]

                        last_start = start

                for i in interval.keys():
                    if interval[i]['count'] != -1 and len(interval[i]['files']) > interval[i]['count']:
                        fd = interval[i]['files'][:len(interval[i]['files']) - interval[i]['count']]
                        interval[i]['oldfiles'].extend(fd)

                        for fd in interval[i]['oldfiles']:
                            os.unlink(fd)

                for fd in files_full_out_of_interval.keys():
                    os.unlink(fd)

                for i in interval.keys():
                    print('Interval %s: found %d files, limit %d, deleted: %d' % (
                        interval[i]['range'],
                        len(interval[i]['files']),
                        interval[i]['count'],
                        len(interval[i]['oldfiles']),
                    ))

                if len(files_full_out_of_interval) > 0:
                    print('Deleted by out of intervals: %d' % len(files_full_out_of_interval))

        else:
            print('Found %d files' % (len(files)))

    finally:
        os.unlink(PIDFILE)


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


if __name__ == '__main__':
    if can_it_run():
        run(sys.argv[1:])
    else:
        old_pid = ''.join(file(PIDFILE))
        print("Script already running under PID %s, skipping execution." % old_pid)
