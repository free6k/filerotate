import sys, os, glob, getopt, time, re, hashlib

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
  interval = []

  try:
    opts, args = getopt.getopt(argv,"hf:c:s:i:",["file=","count=","size=","interval="])
  except getopt.GetoptError:
    print 'rotate.py -f /test/test*.log -c 10 -s 100M'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
       print 'rotate.py -f <filepattern> -c <max count: more 0> -s <max summary in 1M 1K 1G 1T>'
       sys.exit()
    elif opt in ("-f", "--file"):
       filepattern = arg
    elif opt in ("-c", "--count"):
       count = int(arg)
    elif opt in ("-s", "--size"):
       maxsize = arg.lower()
       size = int(re.sub("\D", "", maxsize));

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

        for i in interval:
            range, count = i.split(':')
            range_size = int(re.sub("\D", "", range))
            count = int(re.sub("\D", "", count))

            if range.find('m') != -1:
                range = int(range_size) * 60
            elif range.find('h') != -1:
                range = int(range_size) * 60 * 60
            elif range.find('d') != -1:
                range = int(range_size) * 60 * 60 * 24
            elif range.find('w') != -1:
                range = int(range_size) * 60 * 60 * 24 * 7
            elif range.find('mon') != -1:
                range = int(range_size) * 60 * 60 * 24 * 7 * 4
            elif range.find('y') != -1:
                range = int(range_size) * 60 * 60 * 24 * 7 * 4 * 12
            else:
                range = range_size

            tmp_int[range] = count

        interval = sorted(tmp_int)

  if not((filepattern and (count or maxsize))):
    print 'One of the parameters must be: -s <maxsize megabytes> or -c <count>'
    sys.exit(2)

  if not(count):
    count = 0

  open(PIDFILE, 'w').write(PID);

  try:
    files = glob.glob(filepattern)
    files.sort(key=os.path.getmtime, reverse = True)

    if count > 0:
      print 'Found %d files, last %s' % (len(files), time.strftime('%b %d %Y %H:%M:%S', time.localtime(os.path.getmtime(files[0]))))

      oldfiles = files[count:]

      for oldfile in oldfiles:
        os.unlink(oldfile)

      if oldfiles:
        print 'Deleted %d files by count limit' % len(oldfiles)

      files = files[:len(files) - len(oldfiles)]

    if maxsize > 0:
      total_size = 0
      files_with_size = {}

      for file in files:
        files_with_size[file] = os.path.getsize(file)
        total_size += files_with_size[file]

      print 'Total size %s limit %s' % (sizeof_fmt(total_size), sizeof_fmt(maxsize))

      if total_size > maxsize:
        realsize = 0
        count = 0

        for file in files_with_size:
          realsize += files_with_size[file]

          if realsize > maxsize:
            count += 1

        oldfiles = files[count:]

        for oldfile in oldfiles:
          os.unlink(oldfile)

        if oldfiles:
          print 'Deleted %d files by maxsize limit' % len(oldfiles)

        files = files[:len(files) - len(oldfiles)]

    else:
      print 'Found %d files' % (len(files))


  #  for file in files:

  finally:
    os.unlink(PIDFILE)

def sizeof_fmt(num, suffix='B'):
  for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
      if abs(num) < 1024.0:
          return "%3.1f%s%s" % (num, unit, suffix)
      num /= 1024.0
  return "%.1f%s%s" % (num, 'Yi', suffix)

if __name__ == '__main__':
  if can_it_run():
    run(sys.argv[1:]);
  else:
    old_pid = ''.join(file("RUNNING.pid"))
    print "Script already running under PID %s, skipping execution." % old_pid
