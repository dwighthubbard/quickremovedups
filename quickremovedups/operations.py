import multiprocessing
import os
import sys
import signal


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def remove_dup_file_list(dup_list, log=False):
    if len(dup_list) > 1:
        for item in dup_list[1:]:
            if log:
                print('Removing item: %s' % item)
            else:
                os.unlink(item)
    return len(dup_list) - 1


def remove(dup_dict):
    pool = multiprocessing.Pool()
    try:
        count = 0
        for result in pool.imap(remove_dup_file_list, dup_dict.values(), chunksize=64):
            count += result
            sys.stdout.write('Removed Duplications: %d\r' % count)
            sys.stdout.flush()
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating workers")
        pool.terminate()
        pool.join()
        sys.exit(0)
    sys.stdout.write('                                                               \r')
    sys.stdout.flush()
