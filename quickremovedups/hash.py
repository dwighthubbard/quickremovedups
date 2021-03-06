from collections import defaultdict
import datetime
import hashlib
import logging
import multiprocessing
import sys
from .utility import dupfiles_count


logger = logging.getLogger(__name__)


def file_hash(filename, hasher=None, limit=None):
    try:
        blocksize = 128
        if not hasher:
            hasher = hashlib.md5()
        count = 0
        with open(filename, 'rb') as afile:
            while True:
                buf = afile.read(blocksize)
                if not buf:
                    break
                count += len(buf)
                if limit and count > limit:
                    break
                hasher.update(buf)
        return hasher.hexdigest()
    except FileNotFoundError:
        return "0"


def duplicates_in_list(filename_list, limit=None):
    """
    list of filenames to check
    :param filename_list:
    :return: dict of hash -> duplicates
    """
    if isinstance(filename_list, tuple):
        filename_list, limit = filename_list
    if len(filename_list) < 2:
        filename_list = []
    comparision_results = defaultdict(lambda: [])
    for filename in filename_list:
        # logger.debug('hashing file: %s', filename)
        hash = file_hash(filename, limit=limit)
        comparision_results[hash].append(filename)

    delete_keys = []
    for key in comparision_results:
        if len(comparision_results[key]) < 2:
            delete_keys.append(key)

    for key in delete_keys:
        del comparision_results[key]

    return dict(comparision_results)


def duplicates_in_dict(dup_dict, limit=None):
    start = datetime.datetime.now()
    start_matches = float(dupfiles_count(dup_dict))
    new_dup_dict = defaultdict(lambda: [])
    pool = multiprocessing.Pool()
    try:
        for update_dict in pool.imap(duplicates_in_list, zip(dup_dict.values(), [limit] * len(dup_dict.values())), chunksize=multiprocessing.cpu_count()):
            new_dup_dict.update(update_dict)
            complete_count = dupfiles_count(new_dup_dict)
            complete_percent = (float(complete_count) / start_matches) * 100
            sys.stdout.write('Found Matches: %s Completion: %2.0f%%\r' % (complete_count, complete_percent))
            sys.stdout.flush()
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating workers")
        pool.terminate()
        pool.join()
        sys.exit(0)

    sys.stdout.write('\n')
    sys.stdout.flush()

    end = datetime.datetime.now()
    logger.debug('Dup hash complete in: %s, Found %d dups' % ((end - start), len(new_dup_dict)))
    return new_dup_dict
