# ** -- coding: utf-8 -- **
#!/usr/bin/env python
#
#Copyright (c) 2011 darkdarkfruit <darkdarkfruit@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.
#

'''
jsend test
==========
You should have py.test installed first.
pip install -U pytest

Then, run
>> py.test  test_jsend.py


note:
    ensure weed master-server and at least one volume-server are up
    default:
        master-server: 127.0.0.1:9333
        volume-server: 127.0.0.1:8080

'''
import os
import sys
import urlparse

TEST_PATH = os.path.split(__file__)[0]
WEED_PATH = os.path.split(TEST_PATH)[0]
if WEED_PATH not in sys.path:
    sys.path.insert(0, WEED_PATH)

import weed
from weed import master
from weed.conf import *
from weed.util import *
from weed.master import *
from weed.volume import *
from weed.operation import *


WEED_MASTER_IP = '127.0.0.1'
WEED_MASTER_PORT = 9333


def test_WeedMaster():
    master = WeedMaster()
    assert master.__repr__()

    # assign
    assign_key_dict = master.acquire_assign_info()
    assert isinstance(assign_key_dict, dict)
    assert assign_key_dict.has_key('fid')
    assert assign_key_dict['fid'].replace(',', '') > 0x001
    fid = assign_key_dict['fid']
    volume_id = fid.split(',')[0]

    # lookup
    lookup_dict = master.lookup(fid)
    assert isinstance(lookup_dict, dict)
    assert lookup_dict.has_key('locations')
    locations_list = lookup_dict['locations']
    assert locations_list[0].has_key('url')
    assert locations_list[0].has_key('publicUrl')

    # vacuum
    vacuum_dict = master.vacuum()
    assert isinstance(vacuum_dict, dict)
    assert vacuum_dict.has_key('Topology')


    # status
    status_dict = master.get_status()
    assert isinstance(status_dict, dict)
    assert status_dict.has_key('Topology')


def test_WeedVolume():
    volume = WeedVolume()
    assert volume.__repr__()

    # status
    status_dict = volume.get_status()
    assert isinstance(status_dict, dict)
    assert status_dict.has_key('Version')
    assert status_dict.has_key('Volumes')


def test_WeedAssignKey():
    wak = WeedAssignKey()
    assert wak
    assert wak.__repr__()


def test_WeedAssignKeyExtended():
    wak = WeedAssignKeyExtended()
    assert wak
    assert wak.__repr__()


def test_WeedOperationResponse():
    wor = WeedOperationResponse()
    assert wor
    assert wor.__repr__()


def test_volume_put_get_delete_file():
    master = WeedMaster()
    assert master.__repr__()

    # assign
    assign_key_dict = master.get_assign_key()
    assert isinstance(assign_key_dict, dict)
    assert assign_key_dict.has_key('fid')
    assert assign_key_dict['fid'].replace(',', '') > 0x001
    fid = assign_key_dict['fid']
    volume_id = fid.split(',')[0]

    # lookup
    lookup_dict = master.lookup(fid)
    assert isinstance(lookup_dict, dict)
    assert lookup_dict.has_key('locations')
    locations_list = lookup_dict['locations']
    assert locations_list[0].has_key('url')
    assert locations_list[0].has_key('publicUrl')

    volume_url = 'http://' + locations_list[0]['publicUrl']
    url = urlparse.urlparse(volume_url)

    #volume = WeedVolume(host=url.hostname, port=url.port)
    volume = master.get_volume(fid)
    status_dict = volume.get_status()
    assert isinstance(status_dict, dict)
    assert status_dict.has_key('Version')
    assert status_dict.has_key('Volumes')
    assert isinstance(status_dict['Volumes'], list)

    # file_to_post = './test_file_to_post_to_weed.xml'
    file_to_update = 'test_file_to_post_to_weed.xml'
    file_to_post = os.path.join(TEST_PATH, file_to_update)

    with open(file_to_post, 'wb') as tmp_file:
        tmp_file.write("nonsense " * 1024 * 256)
    put_result = volume.put_file(os.path.abspath(file_to_post),fid)
    assert not 'error' in put_result
    assert 'size' in put_result

    data = volume.get_file(fid)
    assert data
    # print data
    with open(file_to_post, 'r') as fd:
        file_data = fd.read()
    assert data == file_data

    delete_result = volume.delete_file(fid)
    assert delete_result
    assert not 'error' in delete_result
    assert 'size' in delete_result


def test_put_file():
    # test put_file in weed.util
    op = WeedOperation()
    fid = ''
    fname = 'test_opensource_logo.jpg'
    fpath = os.path.join(TEST_PATH, fname)
    master = WeedMaster()
    fid_full_url = master.acquire_new_assign_key()['fid_full_url']
    print('test_weed.py, fid_full_url: %s, fpath: %s' % (fid_full_url, fpath))
    with open(fpath, 'rb') as f:
        LOGGER.info('fp position: %d' % f.tell())
        LOGGER.info('fp info: length: %d' % len(f.read()))
        f.seek(0)

        rsp = put_file(f, fid_full_url, fname)
        assert rsp
        assert rsp.has_key('fid_full_url')
        fid_full_url = rsp['fid_full_url']
        fid = os.path.split(fid_full_url)[1]
        assert rsp['fid_full_url']
        assert rsp['storage_size'] > 0

    # read
    content = op.read(fid, fname, just_url=False).content
    with open(fpath) as _:
        original_content = _.read()
    assert content == original_content



def test_file_operations():
    op = WeedOperation()
    assert op.__repr__()

    # create
    fid = ''
    fname = 'test_opensource_logo.jpg'
    fpath = os.path.join(TEST_PATH, fname)
    with open(fpath, 'r') as f:
        rsp = op.create(f, fname)
        assert rsp
        assert rsp.has_key('fid')
        fid = rsp['fid']
        assert rsp['fid'].replace(',', '') > '01'
        assert rsp['fid_full_url']
        assert rsp['storage_size'] > 0

    # read
    content = op.read(fid, fname, just_url=False).content
    with open(fpath) as _:
        original_content = _.read()
    assert content == original_content

    # update
    file_to_update = 'test_file_to_post_to_weed.xml'
    fpath = os.path.join(TEST_PATH, file_to_update)
    with open(fpath, 'rwb+') as tmp_file:
        tmp_file.write("testdata " * 1024 * 256)
        tmp_file.seek(0)
        rsp = op.update(tmp_file, fid)
        assert rsp
        assert rsp.has_key('fid')
        fid_2 = rsp['fid']
        assert fid_2 == fid
        assert rsp['fid'].replace(',', '') > '01'
        assert rsp['fid_full_url']
        assert rsp['storage_size'] > 0

    # delete
    rsp = op.delete(fid)
    assert rsp.storage_size > 0
    rsp = op.delete('3,20323023') # delete an unexisted file, should return False
    assert rsp.storage_size == 0


if __name__ == '__main__':
    test_WeedMaster()
    test_WeedVolume()
    test_file_operations()
    test_volume_put_get_delete_file()