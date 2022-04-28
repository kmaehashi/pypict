from pypict.cmd import from_model


def build_model():
    from pypict.builder import Model, Parameter, IF, ALL, ANY, NOT

    # https://github.com/microsoft/pict/blob/main/doc/pict.md
    type = Parameter('Type', ['Single', 'Span', 'Stripe', 'Mirror', 'RAID-5'])
    size = Parameter('Size', [10, 100, 500, 1000, 5000, 10000, 40000])
    format_method = Parameter('Format method', ['Quick', 'Slow'])
    filesys = Parameter('File System', ['FAT', 'FAT32', 'NTFS'])
    cluster_size = Parameter(
        'Cluster size', [512, 1024, 2048, 4096, 8192, 16384, 32768, 65536])
    compression = Parameter('Compression', ['On', 'Off'])

    model = Model()
    model.parameters(
        type, size, format_method, filesys, cluster_size, compression
    )
    model.constraints(
        IF(filesys == 'FAT').THEN(size <= 4096),

        IF(filesys == 'FAT32').THEN(size <= 32000),

        size < 10000,

        compression == 'OFF',

        NOT(filesys.LIKE('FAT*')),

        IF(cluster_size.IN(512, 1024, 2048)).THEN(compression == 'off'),

        IF(filesys.IN('FAT', 'FAT32')).THEN(compression == 'off'),

        IF(
            ANY(
                filesys != 'NTFS',
                ALL(
                    filesys == 'NTFS',
                    cluster_size > 4096,
                ),
            )
        ).THEN(compression == 'Off'),
    )
    return model


model = build_model().to_string()
print('# --- PICT model --- #')
print(model)
print()
print('# --- Generated cases --- #')
params, rows = from_model(model)
for row in rows:
    print(dict(zip(params, row)))
