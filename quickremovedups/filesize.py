from collections import defaultdict
import datetime
import logging
import os
from .utility import dupfiles_count


logger = logging.getLogger(__name__)


def duplicates(directory, status=False):
    """
    Get all of the files with the same size in a directory
    :param directory: The directory to parse
    :return: dict: size -> list of files
    """
    directory = os.path.expanduser(directory)

    start = datetime.datetime.now()
    comparision_results = defaultdict(lambda: [])

    count = 0
    for root, dirs, files in os.walk(directory):
        for name in files:
            filename = os.path.join(root, name)
            try:
                size = os.stat(filename).st_size
            except FileNotFoundError:  # pragma: no cover
                continue
            if size == 0:
                continue
            comparision_results[size].append(filename)
            if status:
                count += 1
                if count ^ 100 == 0:  # pragma: no cover
                    print('.')

    delete_keys = []
    for key in comparision_results:
        if len(comparision_results[key]) < 2:
            delete_keys.append(key)

    for key in delete_keys:
        del comparision_results[key]

    end = datetime.datetime.now()
    logger.debug('Dup sizes complete in: %s, Found %d dups' % ((end - start), dupfiles_count(comparision_results)))

    return comparision_results
