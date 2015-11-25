"""The module for handling proxy servers."""

import logging

import httplib2
import webapp2

import admin
from appengine_config import JINJA_ENVIRONMENT
from datastore import ProxyServer
from datastore import User
import xsrf

from google.appengine.api import app_identity



def _RenderProxyServerFormTemplate(proxy_server):
  """Render the form to add or edit a proxy server."""
  template_values = {
      'host': app_identity.get_default_version_hostname(),
      'proxy_server': proxy_server,
      'xsrf_token': xsrf.xsrf_token(),
  }
  template = JINJA_ENVIRONMENT.get_template('templates/proxy_server_form.html')
  return template.render(template_values)


def _RenderListProxyServerTemplate():
  """Render a list of proxy servers."""
  proxy_servers = ProxyServer.GetAll()
  template_values = {
      'host': app_identity.get_default_version_hostname(),
      'proxy_servers': proxy_servers
  }
  template = JINJA_ENVIRONMENT.get_template('templates/proxy_server.html')
  return template.render(template_values)


def _MakeKeyString():
  """Generate the key string for pushing to proxy servers.

    Returns:
      key_string: A string of users with associated key."""
  users = User.GetAll()
  key_string = ''
  ssh_starting_portion = 'ssh-rsa'
  space = ' '
  endline = '\n'
  for user in users:
    user_string = ssh_starting_portion + space + user.public_key + space + user.email + endline
    key_string += user_string

  return key_string


class AddProxyServerHandler(webapp2.RequestHandler):

  @admin.require_admin
  def get(self):
    self.response.write(_RenderProxyServerFormTemplate(None))

  @admin.require_admin
  @xsrf.xsrf_protect
  def post(self):
    ProxyServer.Insert(
        self.request.get('ip_address'),
        self.request.get('ssh_private_key'),
        self.request.get('fingerprint'))
    self.redirect('/proxyserver/list')


class EditProxyServerHandler(webapp2.RequestHandler):

  @admin.require_admin
  def get(self):
    proxy_server = ProxyServer.Get(int(self.request.get('id')))
    self.response.write(_RenderProxyServerFormTemplate(proxy_server))

  @admin.require_admin
  @xsrf.xsrf_protect
  def post(self):
    ProxyServer.Update(
        int(self.request.get('id')),
        self.request.get('ip_address'),
        self.request.get('ssh_private_key'),
        self.request.get('fingerprint'))
    self.redirect('/proxyserver/list')


class DeleteProxyServerHandler(webapp2.RequestHandler):

  @admin.require_admin
  def get(self):
    ProxyServer.Delete(int(self.request.get('id')))
    self.response.write(_RenderListProxyServerTemplate())


class ListProxyServersHandler(webapp2.RequestHandler):

  @admin.require_admin
  def get(self):
    self.response.write(_RenderListProxyServerTemplate())


class DistributeKeyHandler(webapp2.RequestHandler):

  # This is accessed by the cron service, which only has appengine admin access.
  # So if the admin check changes here, we might have to move this to a
  # different module.
  @admin.require_admin
  def get(self):
    # TODO(henry): See if we can use threading to parallelize the put requests.
    key_string = _MakeKeyString()
    proxy_servers = ProxyServer.GetAll()
    for proxy_server in proxy_servers:
      http = httplib2.Http()
      # TODO(henry): Make the request secure.  The http object
      # supports add_certificate() method.  http://goo.gl/mjU4Mh
      # TODO(henry): Increase robustness here, e.g. add exception handling
      # and retries.
      response, content = http.request(
          'http://%s/key' % proxy_server.ip_address,
          headers={'content-type': 'text/plain'},
          method='PUT',
          body=key_string)
      logging.info('Distributed keys to %s. Response: %s, Content: %s',
                   proxy_server.ip_address, response.status, content)
    self.response.write('all done!')


app = webapp2.WSGIApplication([
    ('/proxyserver/add', AddProxyServerHandler),
    ('/proxyserver/delete', DeleteProxyServerHandler),
    ('/proxyserver/distributekey', DistributeKeyHandler),
    ('/proxyserver/edit', EditProxyServerHandler),
    ('/proxyserver/list', ListProxyServersHandler),
], debug=True)
