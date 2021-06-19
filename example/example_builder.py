from ast import Param
from pypict.builder import Model, Parameter, IF, AND, OR, NOT


type = Parameter('Type', ['Single', 'Span', 'Stripe', 'Mirror', 'RAID-5'])
size = Parameter('Size', [10, 100, 500, 1000, 5000, 10000, 40000])
method = Parameter('Format method', ['Quick', 'Slow'])
filesys = Parameter('File System', ['FAT', 'FAT32', 'NTFS'])
cluster = Parameter('Cluster size', [512, 1024, 2048, 4096, 8192, 16384, 32768, 65536])
compression = Parameter('Compression', ['On', 'Off'])

model = Model().parameters(
    type, size, method, filesys, cluster, compression
).constraints(
    IF(filesys == 'FAT').THEN(size <= 4096),
    IF(filesys == 'FAT32').THEN(size <= 32000),
    size < 10000,
    compression == 'OFF',
    filesys.like('FAT*'),
    IF(cluster.in_(512, 1024, 2048)).THEN(compression == 'off'),
    IF(filesys.in_('FAT', 'FAT32')).THEN(compression == 'off'),

    IF(
        OR(
            filesys != 'NTFS',
            AND(filesys == 'NTFS', cluster > 4096),
        )
    ).THEN(compression == 'Off')
)
print(model.to_string())