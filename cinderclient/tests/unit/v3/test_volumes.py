# Copyright 2016 FUJITSU LIMITED
# Copyright (c) 2016 EMC Corporation
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import ddt

from cinderclient import api_versions
from cinderclient.tests.unit import utils
from cinderclient.tests.unit.v3 import fakes
from cinderclient.v3 import volumes

from six.moves.urllib import parse

cs = fakes.FakeClient()


@ddt.ddt
class VolumesTest(utils.TestCase):

    def test_volume_manager_upload_to_image(self):
        expected = {'os-volume_upload_image':
                    {'force': False,
                     'container_format': 'bare',
                     'disk_format': 'raw',
                     'image_name': 'name',
                     'visibility': 'public',
                     'protected': True}}
        api_version = api_versions.APIVersion('3.1')
        cs = fakes.FakeClient(api_version)
        manager = volumes.VolumeManager(cs)
        fake_volume = volumes.Volume(manager,
                                     {'id': 1234, 'name': 'sample-volume'},
                                     loaded=True)
        fake_volume.upload_to_image(False, 'name', 'bare', 'raw',
                                    visibility='public', protected=True)
        cs.assert_called_anytime('POST', '/volumes/1234/action', body=expected)

    def test_create_volume(self):
        vol = cs.volumes.create(1, group_id='1234', volume_type='5678')
        expected = {'volume': {'status': 'creating',
                               'description': None,
                               'availability_zone': None,
                               'source_volid': None,
                               'snapshot_id': None,
                               'size': 1,
                               'user_id': None,
                               'name': None,
                               'imageRef': None,
                               'attach_status': 'detached',
                               'volume_type': '5678',
                               'project_id': None,
                               'metadata': {},
                               'source_replica': None,
                               'consistencygroup_id': None,
                               'multiattach': False,
                               'group_id': '1234'}}
        cs.assert_called('POST', '/volumes', body=expected)
        self._assert_request_id(vol)

    def test_volume_list_manageable(self):
        cs = fakes.FakeClient(api_versions.APIVersion('3.8'))
        cs.volumes.list_manageable('host1', detailed=False)
        cs.assert_called('GET', '/manageable_volumes?host=host1')

    def test_volume_list_manageable_detailed(self):
        cs = fakes.FakeClient(api_versions.APIVersion('3.8'))
        cs.volumes.list_manageable('host1', detailed=True)
        cs.assert_called('GET', '/manageable_volumes/detail?host=host1')

    def test_snapshot_list_manageable(self):
        cs = fakes.FakeClient(api_versions.APIVersion('3.8'))
        cs.volume_snapshots.list_manageable('host1', detailed=False)
        cs.assert_called('GET', '/manageable_snapshots?host=host1')

    def test_snapshot_list_manageable_detailed(self):
        cs = fakes.FakeClient(api_versions.APIVersion('3.8'))
        cs.volume_snapshots.list_manageable('host1', detailed=True)
        cs.assert_called('GET', '/manageable_snapshots/detail?host=host1')

    def test_snapshot_list_with_metadata(self):
        cs = fakes.FakeClient(api_versions.APIVersion('3.22'))
        cs.volume_snapshots.list(search_opts={'metadata': {'key1': 'val1'}})
        expected = ("/snapshots/detail?metadata=%s"
                    % parse.quote_plus("{'key1': 'val1'}"))
        cs.assert_called('GET', expected)

    def test_list_with_image_metadata(self):
        cs = fakes.FakeClient(api_versions.APIVersion('3.0'))
        cs.volumes.list(search_opts={'glance_metadata': {'key1': 'val1'}})
        expected = ("/volumes/detail?glance_metadata=%s"
                    % parse.quote_plus("{'key1': 'val1'}"))
        cs.assert_called('GET', expected)

    @ddt.data(True, False)
    def test_get_pools_filter_by_name(self, detail):
        cs = fakes.FakeClient(api_version=api_versions.APIVersion('3.33'))
        vol = cs.volumes.get_pools(detail, {'name': 'pool1'})
        request_url = '/scheduler-stats/get_pools?name=pool1'
        if detail:
            request_url = '/scheduler-stats/get_pools?detail=True&name=pool1'
        cs.assert_called('GET', request_url)
        self._assert_request_id(vol)
