import logging
import os
import quickremovedups.filesize
import quickremovedups.hash
from tempfile import TemporaryDirectory
from unittest import main, TestCase


class TestFilesize(TestCase):

    def create_file_of_size(self, filename, size):
        logging.debug('Creating file: %s of size %d' % (filename, size))
        with open(filename, 'w') as filehandle:
            filehandle.write(' ' * size)

    def test_file_hash_limit(self):
        with TemporaryDirectory() as tempdir:
            filename = os.path.join(tempdir, 'testfile')
            self.create_file_of_size(filename, 10240)
            result = quickremovedups.hash.file_hash(filename, limit=4096)
        self.assertEqual(result, '8a477c1b1d20b2f983a61640b10a9a5e')

    def test_file_hash_file_missing(self):
        with TemporaryDirectory() as tempdir:
            filename = os.path.join(tempdir, 'testfile')
            result = quickremovedups.hash.file_hash(filename)
        self.assertEqual(result, '0')

    def test_file_hash_nolimit(self):
        with TemporaryDirectory() as tempdir:
            filename = os.path.join(tempdir, 'testfile')
            self.create_file_of_size(filename, 10240)
            result = quickremovedups.hash.file_hash(filename)
        self.assertEqual(result, '5795fa7c504e4b99a01644a300e74c66')

    def test_duplicates_in_list(self):
        count = 0
        with TemporaryDirectory() as tempdir:
            for filesize in [100, 1024, 1024, 2048, 2048]:
                count += 1
                self.create_file_of_size(os.path.join(tempdir, str(count)), filesize)
            result = quickremovedups.hash.duplicates_in_list(([os.path.join(tempdir, '2'), os.path.join(tempdir, '3')], 4096))
        self.assertDictEqual(
            result,
            {
                '10801b757893f9edbff42cd92fdd406a': [os.path.join(tempdir, '2'), os.path.join(tempdir, '3')]
            }
        )

    def test_duplicates_in_list_no_dups(self):
        count = 0
        with TemporaryDirectory() as tempdir:
            for filesize in [100, 1024, 1024, 2048, 2048]:
                count += 1
                self.create_file_of_size(os.path.join(tempdir, str(count)), filesize)
            result = quickremovedups.hash.duplicates_in_list(([os.path.join(tempdir, '2')], 4096))
        self.assertDictEqual(
            result,
            {}
        )

    def test_duplicates_in_dict(self):
        count = 0
        with TemporaryDirectory() as tempdir:
            for filesize in [100, 1024, 1024, 2048, 2048]:
                count += 1
                self.create_file_of_size(os.path.join(tempdir, str(count)), filesize)
            dupdict = dict(quickremovedups.filesize.duplicates(tempdir))
            result = quickremovedups.hash.duplicates_in_dict(dupdict)
        self.assertDictEqual(
            result,
            {
                '10801b757893f9edbff42cd92fdd406a': [os.path.join(tempdir, '2'), os.path.join(tempdir, '3')],
                '9598acee9824e6a39d1eda8024fd0846': [os.path.join(tempdir, '5'), os.path.join(tempdir, '4')]
            }
        )

    def test_dupfiles_count(self):
        input_dict = {
            1024: ['/tmp/tmpux_s30x_/2', '/tmp/tmpux_s30x_/3'],
            2048: ['/tmp/tmpux_s30x_/5', '/tmp/tmpux_s30x_/4']
        }
        result = quickremovedups.filesize.dupfiles_count(input_dict)
        self.assertEqual(result, 4)


if __name__ == '__main__':
    main()
