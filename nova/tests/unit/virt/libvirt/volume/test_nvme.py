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

import mock
from os_brick.initiator import connector

from nova.tests.unit.virt.libvirt.volume import test_volume
from nova.virt.libvirt.volume import nvme


class LibvirtNVMEVolumeDriverTestCase(test_volume.LibvirtVolumeBaseTestCase):

    @mock.patch('os.path.exists', return_value=True)
    def test_libvirt_nvme_driver(self, exists):
        libvirt_driver = nvme.LibvirtNVMEVolumeDriver(self.fake_conn)
        self.assertIsInstance(libvirt_driver.connector,
                              connector.NVMeConnector)

    def test_libvirt_nvme_driver_connect(self):
        nvme_con = nvme.LibvirtNVMEVolumeDriver(self.fake_conn)
        config = {'server_ip': '127.0.0.1', 'server_port': 9898}
        disk_info = {'id': '1234567', 'name': 'aNVMEVolume', 'conf': config}
        connection_info = {'data': disk_info}
        with mock.patch.object(nvme_con.connector,
                               'connect_volume',
                               return_value={'path': '/dev/dms1234567'}):
            nvme_con.connect_volume(connection_info, None)
            self.assertEqual('/dev/dms1234567',
                             connection_info['data']['device_path'])

    def test_libvirt_nvme_driver_disconnect(self):
        nvme_con = nvme.LibvirtNVMEVolumeDriver(self.fake_conn)
        nvme_con.connector.disconnect_volume = mock.MagicMock()
        disk_info = {'path': '/dev/dms1234567', 'name': 'aNVMEVolume',
                     'type': 'raw', 'dev': 'vda1', 'bus': 'pci0',
                     'device_path': '/dev/dms123456'}
        connection_info = {'data': disk_info}
        nvme_con.disconnect_volume(connection_info, disk_info)
        nvme_con.connector.disconnect_volume.assert_called_once_with(
            disk_info, None)

    def test_libvirt_disco_driver_get_config(self):
        nvme_con = nvme.LibvirtNVMEVolumeDriver(self.fake_conn)

        disk_info = {'path': '/dev/dms1234567', 'name': 'aNVMEVolume',
                     'type': 'raw', 'dev': 'vda1', 'bus': 'pci0',
                     'device_path': '/dev/dms1234567'}
        connection_info = {'data': disk_info}
        conf = nvme_con.get_config(connection_info, disk_info)
        self.assertEqual('block', conf.source_type)
        self.assertEqual('/dev/dms1234567', conf.source_path)
