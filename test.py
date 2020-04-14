import os
import sys
import time
import glob
import shutil

import filerotate

PATH = './tests'


def generate_files(count=1, size=1024, delay=None, countOfDelay=1):
    countCreated = 0

    for i in range(0, count):
        f = open(("%s/backup_test_%d.dump" % (PATH, i)), "wb")
        f.seek(size-1)
        f.write("\0")
        f.close()
        countCreated = countCreated + 1

        if delay and countCreated == countOfDelay:
            countCreated = 0
            time.sleep(delay)

def deleteAllFiles(filepattern):
    for f in get_files(filepattern):
        os.unlink(f)


def get_files(filepattern):
    files = glob.glob(filepattern)
    files.sort(key=os.path.getmtime, reverse=True)
    return files


def blockPrint():
    sys.stdout = open(os.devnull, 'w')


def enablePrint():
    sys.stdout = sys.__stdout__


def runscript(args):
    blockPrint()
    filerotate.run(args)
    enablePrint()


if __name__ == '__main__':
    try:
        os.mkdir(PATH, 0o777)

        generate_files(10, 100)
        pattern = ("%s/backup_test_*.dump" % PATH)

        f = get_files(pattern)
        assert len(f) == 10, 'The generated files count is wrong'

        runscript(['-f', pattern, '-c', '5'])
        f2 = get_files(pattern)
        assert len(f2) == 5, 'Run with limit 5 is wrong work'
        assert f[:5] == f2, 'Result is wrong'

        runscript(['-f', pattern, '-s', '500'])
        f2 = get_files(pattern)
        assert len(f2) == 5, 'Run with size limit 500 bytes is wrong work'

        runscript(['-f', pattern, '-s', '100'])
        f2 = get_files(pattern)
        assert len(f2) == 1, 'Run with size limit 100 bytes is wrong work'

        generate_files(100, 1)

        runscript(['-f', pattern, '-i', '1d:*'])
        f = get_files(pattern)
        assert len(f) == 100, 'Run with interval 1d:* is wrong work'

        runscript(['-f', pattern, '-i', '1d:1'])
        f2 = get_files(pattern)
        assert len(f2) == 1, 'Run with interval 1d:1 is wrong work'
        assert f2[0] == f[99], 'Run with interval 1d:1 is wrong work deleted files'

        deleteAllFiles(pattern)
        generate_files(4, 1, 2, 2)

        f = get_files(pattern)
        runscript(['-f', pattern, '-i', '1:2 3:2'])
        f2 = get_files(pattern)
        assert len(f2) == len(f), 'Run with interval 1:2 3:2 is wrong work'

        runscript(['-f', pattern, '-i', '1:1 3:1'])
        f2 = get_files(pattern)
        assert len(f2) == 2, 'Run with interval 1:2 3:2 is wrong work'

        deleteAllFiles(pattern)
        generate_files(2, 1, 3)

        f = get_files(pattern)
        runscript(['-f', pattern, '-i', '1:*'])
        f2 = get_files(pattern)
        assert len(f2) == 1, 'Run with interval 1:* is delete out of interval files'
        assert f2[0] == f[0], 'Run with interval 1:* is delete out of interval files'

        print 'The tests were successful'

    finally:
        if os.path.isdir(PATH):
            shutil.rmtree(PATH)
