import shutil
from pathlib import Path

import pytest

from litezip.main import (
    extract_metadata,
    parse_collection,
    parse_litezip,
    parse_module,
    update_metadata,
    Collection,
    Module,
)
from litezip.exceptions import MissingFile


def test_Module_struct(datadir):
    id = 'm40645'
    data_path = datadir / 'litezip' / id
    content = data_path / 'index.cnxml'
    resources = (data_path / 'Lab4 Fill Order.png',)

    data_struct = Module(id, content, resources)

    assert len(data_struct) == 3
    assert data_struct.id == id
    assert data_struct.file == content
    assert data_struct.resources == (data_path / 'Lab4 Fill Order.png',)


def test_Collection_struct(datadir):
    id = 'col11405'
    data_path = datadir / 'litezip'
    content = data_path / 'collection.xml'
    resources = tuple()

    data_struct = Collection(id, content, resources)

    assert len(data_struct) == 3
    assert data_struct.id == id
    assert data_struct.file == content
    assert data_struct.resources == tuple()


def test_parse_module(datadir):
    module_id = 'm40645'
    data_path = datadir / 'litezip' / module_id

    data_struct = parse_module(data_path)

    assert data_struct[0] == module_id
    assert data_struct[1] == data_path / 'index.cnxml'
    assert data_struct[2] == (data_path / 'Lab4 Fill Order.png',)


def test_parse_module_without_resources(datadir):
    module_id = 'm42304'
    data_path = datadir / 'litezip' / module_id

    data_struct = parse_module(data_path)

    assert data_struct[0] == module_id
    assert data_struct[1] == data_path / 'index.cnxml'
    assert data_struct[2] == tuple()


def test_parse_module_raises_missing_file(tmpdir):
    module_id = 'm42000'
    data_path = Path(str(tmpdir.mkdir(module_id)))
    missing_file = data_path / 'index.cnxml'

    with pytest.raises(MissingFile) as exc_info:
        parse_module(data_path)

    assert missing_file == exc_info.value.args[0]


def test_parse_collection(datadir):
    col_id = 'col11405'
    data_path = datadir / 'litezip'

    data_struct = parse_collection(data_path)

    assert data_struct[0] == col_id
    assert data_struct[1] == data_path / 'collection.xml'
    assert data_struct[2] == tuple()


def test_parse_collection_raises_missing_file(tmpdir):
    col_id = 'col11405'
    data_path = Path(str(tmpdir.mkdir(col_id)))
    missing_file = data_path / 'collection.xml'

    with pytest.raises(MissingFile) as exc_info:
        parse_collection(data_path)

    assert missing_file == exc_info.value.args[0]


def test_parse_litezip(datadir):
    data_path = datadir / 'litezip'

    data_struct = parse_litezip(data_path)

    assert len(data_struct) == 8
    from litezip.main import Collection, Module
    col = Collection('col11405', data_path / 'collection.xml', tuple())
    assert data_struct[0] == col
    mods = [
        Module('m37154', data_path / 'm37154' / 'index.cnxml', tuple()),
        Module('m40646', data_path / 'm40646' / 'index.cnxml',
               tuple([data_path / 'm40646' / 'Photodiode.png'])),
    ]
    for mod in mods:
        assert mod in data_struct


def test_extract_metadata_for_module(litezip_valid_litezip):
    module_filepath = litezip_valid_litezip / 'm42304'

    expected_metadata = {
        'repository': 'http://cnx.org/content',
        'url': 'http://cnx.org/content/m42304/latest',
        'id': 'm42304',
        'title': 'Lab 1-1: 4-Bit Mux and all NAND/NOR Mux',
        'version': '1.3',
        'created': '2012/01/19 22:11:40 -0600',
        'revised': '2012/01/23 22:20:24 -0600',
        'license_url': 'http://creativecommons.org/licenses/by/3.0/',
        'keywords': ['Altera', 'ELEC 220', 'FPGA', 'multiplexor', 'mux',
                     'NAND', 'NOR', 'Quartus'],
        'subjects': ['Science and Technology'],
        'abstract': ('Briefly describes the tasks for Lab 1.1 '
                     'of Rice University\'s ELEC 220 course.'),
        'language': 'en',
    }
    expected_metadata['people'] = {
        'cavallar': {
            'firstname': 'Joseph',
            'surname': 'Cavallaro',
            'fullname': 'Joseph Cavallaro',
            'email': 'cavallar@rice.edu',
        },
        'jedifan42': {
            'firstname': 'Chris',
            'surname': 'Stevenson',
            'fullname': 'Chris Stevenson',
            'email': 'cms11@rice.edu',
        },
    }
    expected_metadata['authors'] = ['jedifan42', 'cavallar']
    expected_metadata['maintainers'] = ['jedifan42', 'cavallar']
    expected_metadata['licensors'] = ['jedifan42', 'cavallar']

    module = parse_module(module_filepath)
    metadata = extract_metadata(module)

    assert metadata == expected_metadata


def test_extract_metadata_for_collection(litezip_valid_litezip):
    expected_metadata = {
        'repository': 'http://cnx.org/content',
        'url': 'http://cnx.org/content/col11405/1.2',
        'id': 'col11405',
        'title': 'Intro to Computational Engineering: Elec 220 Labs',
        'version': '1.2',
        'created': '2011/05/24 10:31:56.888 GMT-5',
        'revised': '2013/03/11 22:52:33.244 GMT-5',
        'license_url': 'http://creativecommons.org/licenses/by/3.0/',
        'keywords': [
            'Calculator',
            'Cavallaro',
            'Elec 220',
            'Gate',
            'Interrupt',
            'LC-3',
            'Loop',
            'Microcontroller',
            'MSP 430',
            'Rice',
        ],
        'subjects': ['Science and Technology'],
        'abstract': ('This collection houses all the documentation for the '
                     'lab component of Rice Universities Elec 220 lab '
                     'component.  The labs cover topics such as gates, '
                     'simulation, basic digital I/O, interrupt driven '
                     'embedded programming, C language programming, and '
                     'finally a/d interfacing and touch sensors.'),
        'language': 'en',
    }
    expected_metadata['people'] = {
        'cavallar': {
            'firstname': 'Joseph',
            'surname': 'Cavallaro',
            'fullname': 'Joseph Cavallaro',
            'email': 'cavallar@rice.edu',
        },
        'jedifan42': {
            'firstname': 'Chris',
            'surname': 'Stevenson',
            'fullname': 'Chris Stevenson',
            'email': 'cms11@rice.edu',
        },
        'mwjhnsn': {
            'firstname': 'Matthew',
            'surname': 'Johnson',
            'fullname': 'Matthew Johnson',
            'email': 'mwj1@rice.edu',
        },
    }
    expected_metadata['authors'] = ['mwjhnsn', 'jedifan42']
    expected_metadata['maintainers'] = ['mwjhnsn', 'jedifan42', 'cavallar']
    expected_metadata['licensors'] = ['mwjhnsn', 'jedifan42', 'cavallar']

    collection= parse_collection(litezip_valid_litezip)
    metadata = extract_metadata(collection)

    assert metadata == expected_metadata


def test_update_metadata_on_module(tmpdir, litezip_valid_litezip):
    origin_path = litezip_valid_litezip / 'm42304'
    test_dir = Path(tmpdir.mkdir('update-metadata-on-module'))
    test_path = test_dir / origin_path.name
    shutil.copytree(str(origin_path), str(test_path))

    module = parse_module(test_path)
    id = 'm55555'
    version = '5.5'
    update_metadata(module, id=id, version=version)

    with module.file.open('r') as fb:
        contents = fb.read()

    assert '<md:content-id>{}</md:content-id>'.format(id) in contents
    assert '<md:version>{}</md:version>'.format(version) in contents


def test_update_metadata_on_non_mutable_key(tmpdir, litezip_valid_litezip):
    origin_path = litezip_valid_litezip / 'm42304'
    test_dir = Path(tmpdir.mkdir('update-metadata-on-module'))
    test_path = test_dir / origin_path.name
    shutil.copytree(str(origin_path), str(test_path))

    module = parse_module(test_path)
    id = 'm55555'
    version = '5.5'
    with pytest.raises(NotImplementedError) as exc_info:
        update_metadata(module, language='ru')


def test_update_metadata_on_collection(tmpdir, litezip_valid_litezip):
    origin_path = litezip_valid_litezip
    test_dir = Path(tmpdir.mkdir('update-metadata-on-collection'))
    test_path = test_dir / origin_path.name
    shutil.copytree(str(origin_path), str(test_path))

    collection = parse_collection(test_path)
    id = 'col59595'
    version = '9.5'
    update_metadata(collection, id=id, version=version)

    with collection.file.open('r') as fb:
        contents = fb.read()

    assert '<md:content-id>{}</md:content-id>'.format(id) in contents
    assert '<md:version>{}</md:version>'.format(version) in contents
