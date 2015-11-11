from mock import MagicMock
from mock import patch
import sys

from datastore import ProxyServer

import unittest
import webapp2
import webtest

# Need to mock the decorator at function definition time, i.e. when the module
# is loaded. http://stackoverflow.com/a/7667621/2830207
def noop_decorator(func):
  return func

mock_admin = MagicMock()
mock_admin.require_admin = noop_decorator
sys.modules['admin'] = mock_admin

mock_xsrf = MagicMock()
mock_xsrf.xsrf_protect = noop_decorator
sys.modules['xsrf'] = mock_xsrf


import proxy_server


FAKE_IP_ADDRESS = '111.222.333.444'
FAKE_SSH_PRIVATE_KEY = '4444333222111'
FAKE_FINGERPRINT = '11:22:33:44'


class ProxyServerTest(unittest.TestCase):

  def setUp(self):
    self.testapp = webtest.TestApp(proxy_server.app)

  @patch('proxy_server._RenderListProxyServerTemplate')
  def testListProxyServersHandler(self, mock_render_list_template):
    self.testapp.get('/proxyserver/list')
    mock_render_list_template.assert_called_once_with()

  @patch('proxy_server._RenderAddProxyServerTemplate')
  def testAddProxyServersGetHandler(self, mock_render_add_template):
    self.testapp.get('/proxyserver/add')
    mock_render_add_template.assert_called_once_with()

  @patch('datastore.ProxyServer.CreateEntity')
  def testAddProxyServersPostHandler(self, mock_create_entity):
    response = self.testapp.post('/proxyserver/add')

    mock_create_entity.assert_called_once_with('', '', '')
    self.assertEqual(response.status_int, 302)
    self.assertTrue('/proxyserver/list' in response.location)


  def testRenderAddProxyServerTemplate(self):
    add_proxy_server_template = proxy_server._RenderAddProxyServerTemplate()
    self.assertTrue('ip address:' in add_proxy_server_template)

  @patch('datastore.ProxyServer.GetAll')
  def testRenderListProxyServerTemplate(self, mock_get_all):
    fake_proxy_server = ProxyServer(id='11111',
                                    ip_address=FAKE_IP_ADDRESS,
                                    ssh_private_key=FAKE_SSH_PRIVATE_KEY,
                                    fingerprint=FAKE_FINGERPRINT)
    fake_proxy_servers = [fake_proxy_server]
    mock_get_all.return_value = fake_proxy_servers
    list_proxy_server_template = proxy_server._RenderListProxyServerTemplate()

    self.assertTrue('add new proxy server' in list_proxy_server_template)
    self.assertTrue(FAKE_IP_ADDRESS in list_proxy_server_template)
    self.assertTrue(FAKE_SSH_PRIVATE_KEY in list_proxy_server_template)
    self.assertTrue(FAKE_FINGERPRINT in list_proxy_server_template)


if __name__ == '__main__':
    unittest.main()
