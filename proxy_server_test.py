import sys
import unittest

from mock import MagicMock
from mock import patch
import webtest

from datastore import ProxyServer


# Need to mock the decorator at function definition time, i.e. when the module
# is loaded. http://stackoverflow.com/a/7667621/2830207
def noop_decorator(func):
  return func

def noop_decorator_with_arguments(arg):
  def noop_decorator(func):
    return func
  return noop_decorator

mock_admin = MagicMock()
mock_admin.OAUTH_USER_SCOPE_DECORATOR.oauth_required = noop_decorator
mock_admin.RequireAppAndDomainAdmin = noop_decorator_with_arguments
sys.modules['admin'] = mock_admin

mock_xsrf = MagicMock()
mock_xsrf.XSRFProtect = noop_decorator
sys.modules['xsrf'] = mock_xsrf


import proxy_server

FAKE_ID = 11111
FAKE_NAME = 'US_WEST1'
FAKE_IP_ADDRESS = '111.222.333.444'
FAKE_SSH_PRIVATE_KEY = '4444333222111'
FAKE_FINGERPRINT = '11:22:33:44'


class ProxyServerTest(unittest.TestCase):

  def setUp(self):
    self.testapp = webtest.TestApp(proxy_server.APP)

  @patch('proxy_server._RenderListProxyServerTemplate')
  def testListProxyServersHandler(self, mock_render_list_template):
    self.testapp.get('/proxyserver/list')
    mock_render_list_template.assert_called_once_with()

  @patch('proxy_server._RenderProxyServerFormTemplate')
  def testAddProxyServerGetHandler(self, mock_render_add_template):
    self.testapp.get('/proxyserver/add')
    mock_render_add_template.assert_called_once_with(None)

  @patch('datastore.ProxyServer.Insert')
  def testAddProxyServerPostHandler(self, mock_insert):
    response = self.testapp.post('/proxyserver/add')

    mock_insert.assert_called_once_with('', '', '', '')
    self.assertEqual(response.status_int, 302)
    self.assertTrue('/proxyserver/list' in response.location)

  @patch('proxy_server._RenderProxyServerFormTemplate')
  @patch('datastore.ProxyServer.Get')
  def testEditProxyServerGetHandler(self, mock_get, mock_render_edit_template):
    fake_proxy_server = GetFakeProxyServer()
    mock_get.return_value = fake_proxy_server
    self.testapp.get('/proxyserver/edit?id=' + str(FAKE_ID))

    mock_get.assert_called_once_with(FAKE_ID)
    mock_render_edit_template.assert_called_once_with(fake_proxy_server)

  @patch('datastore.ProxyServer.Update')
  def testEditProxyServerPostHandler(self, mock_update):
    params = {'id': str(FAKE_ID),
              'name': FAKE_NAME,
              'ip_address': FAKE_IP_ADDRESS,
              'ssh_private_key': FAKE_SSH_PRIVATE_KEY,
              'fingerprint': FAKE_FINGERPRINT}
    response = self.testapp.post('/proxyserver/edit', params)

    mock_update.assert_called_once_with(FAKE_ID, FAKE_NAME, FAKE_IP_ADDRESS,
                                        FAKE_SSH_PRIVATE_KEY, FAKE_FINGERPRINT)
    self.assertEqual(response.status_int, 302)
    self.assertTrue('/proxyserver/list' in response.location)

  @patch('proxy_server._RenderListProxyServerTemplate')
  @patch('datastore.ProxyServer.Delete')
  def testDeleteProxyServerHandler(self, mock_delete,
                                   mock_render_list_template):
    self.testapp.get('/proxyserver/delete?id=' + str(FAKE_ID))
    mock_delete.assert_called_once_with(FAKE_ID)
    mock_render_list_template.assert_called_once_with()

  @patch('proxy_server._MakeKeyString')
  @patch('httplib2.Http.request')
  @patch('datastore.ProxyServer.GetAll')
  def testDistributeKeyHandler(self, mock_get_all, mock_request,
                               mock_make_key_string):
    fake_proxy_server = GetFakeProxyServer()
    fake_proxy_servers = [fake_proxy_server]
    mock_get_all.return_value = fake_proxy_servers

    mock_response = MagicMock()
    mock_response.status = 200
    fake_content = ''
    mock_request.return_value = mock_response, fake_content

    fake_key_string = 'ssh-rsa public_key email'
    mock_make_key_string.return_value = fake_key_string

    self.testapp.get('/cron/proxyserver/distributekey')
    mock_request.assert_called_once_with(
        'http://%s/key' % fake_proxy_server.ip_address,
        headers={'content-type': 'text/plain'},
        method='PUT',
        body=fake_key_string)

  def testRenderAddProxyServerTemplate(self):
    add_form = proxy_server._RenderProxyServerFormTemplate(None)
    self.assertTrue('/proxyserver/add' in add_form)
    self.assertFalse('/proxyserver/edit' in add_form)
    self.assertTrue('Name' in add_form)
    self.assertTrue('IP Address' in add_form)

  def testRenderEditProxyServerTemplate(self):
    fake_proxy_server = GetFakeProxyServer()
    edit_form = proxy_server._RenderProxyServerFormTemplate(fake_proxy_server)
    self.assertFalse('/proxyserver/add' in edit_form)
    self.assertTrue('/proxyserver/edit' in edit_form)
    # TODO(henryc): We need better asserts on the exact elements and their
    # values.  Will circle back once the UI is in shape.
    self.assertTrue('Name' in edit_form)
    self.assertTrue(FAKE_NAME in edit_form)
    self.assertTrue('IP Address' in edit_form)
    self.assertTrue(FAKE_IP_ADDRESS in edit_form)

  @patch('datastore.ProxyServer.GetAll')
  def testRenderListProxyServerTemplate(self, mock_get_all):
    fake_proxy_server = GetFakeProxyServer()
    fake_proxy_servers = [fake_proxy_server]
    mock_get_all.return_value = fake_proxy_servers
    list_proxy_server_template = proxy_server._RenderListProxyServerTemplate()

    self.assertTrue('Add New Proxy Server' in list_proxy_server_template)
    self.assertTrue(FAKE_NAME in list_proxy_server_template)
    self.assertTrue(FAKE_IP_ADDRESS in list_proxy_server_template)
    self.assertTrue(FAKE_SSH_PRIVATE_KEY in list_proxy_server_template)
    self.assertTrue(FAKE_FINGERPRINT in list_proxy_server_template)

  @patch('datastore.User.GetAll')
  def testMakeKeyString(self, mock_get_all):
    fake_email_1 = 'foo@bar.com'
    fake_public_key_1 = '123abc'
    fake_user_1 = MagicMock(email=fake_email_1, public_key=fake_public_key_1)
    fake_result_1 = 'ssh-rsa ' + fake_public_key_1 + ' ' + fake_email_1 + '\n'
    fake_email_2 = 'bar@baz.com'
    fake_public_key_2 = 'def456'
    fake_user_2 = MagicMock(email=fake_email_2, public_key=fake_public_key_2)
    fake_result_2 = 'ssh-rsa ' + fake_public_key_2 + ' ' + fake_email_2 + '\n'
    fake_users = [fake_user_1, fake_user_2]
    mock_get_all.return_value = fake_users

    key_string = proxy_server._MakeKeyString()

    mock_get_all.assert_called_once_with()

    self.assertEqual(fake_result_1 + fake_result_2, key_string)


def GetFakeProxyServer():
  return ProxyServer(id=FAKE_ID,
                     name=FAKE_NAME,
                     ip_address=FAKE_IP_ADDRESS,
                     ssh_private_key=FAKE_SSH_PRIVATE_KEY,
                     fingerprint=FAKE_FINGERPRINT)

if __name__ == '__main__':
  unittest.main()
