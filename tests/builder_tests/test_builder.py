import unittest

from pypict.builder import Model, Parameter
from pypict.builder import IF


class TestBuilder(unittest.TestCase):
    def test_basic_usecase(self):
        type = Parameter(
            'Type', ['Single', 'Span', 'Stripe', 'Mirror', 'RAID-5'])
        size = Parameter('Size', [10, 100, 500, 1000, 5000, 10000, 40000])
        filesys = Parameter('File System', ['FAT', 'FAT32', 'NTFS'])

        m = Model()
        m.parameters(type, size, filesys)
        m.constraints(
            IF(filesys == 'FAT').THEN(size <= 4096),
            IF(filesys == 'FAT32').THEN(size <= 32000),
        )
        print(m.to_string())
