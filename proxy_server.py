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
  """Generate the key string in open ssh format for pushing to proxy servers.
     This key string includes only the public key for each user in order to
     grant the user access to each proxy server.

    Returns:
      key_string: A string of users with associated key.
    """
  users = User.GetAll()
  key_string = ''
  ssh_starting_portion = 'ssh-rsa'
  space = ' '
  endline = '\n'
  for user in users:
    user_string = (ssh_starting_portion + space + user.public_key + space +
                  user.email + endline)
    key_string += user_string

  return key_string


class AddProxyServerHandler(webapp2.RequestHandler):
  """Handler for adding new proxy servers."""

  @admin.require_admin
  def get(self):
    """Get the form for adding new proxy servers."""

    self.response.write(_RenderProxyServerFormTemplate(None))

  @admin.require_admin
  @xsrf.xsrf_protect
  def post(self):
    """Add a new proxy server with the post parameters passed in."""
    ProxyServer.Insert(
        self.request.get('name'),
        self.request.get('ip_address'),
        self.request.get('ssh_private_key'),
        self.request.get('fingerprint'))
    self.redirect('/proxyserver/list')


class EditProxyServerHandler(webapp2.RequestHandler):
  """Handler for editing an existing proxy server."""

  @admin.require_admin
  def get(self):
    """Get a proxy server's current data and display its edit form."""
    proxy_server = ProxyServer.Get(int(self.request.get('id')))
    self.response.write(_RenderProxyServerFormTemplate(proxy_server))

  @admin.require_admin
  @xsrf.xsrf_protect
  def post(self):
    """Set an existing proxy server with the post parameters passed in."""
    ProxyServer.Update(
        int(self.request.get('id')),
        self.request.get('name'),
        self.request.get('ip_address'),
        self.request.get('ssh_private_key'),
        self.request.get('fingerprint'))
    self.redirect('/proxyserver/list')


class DeleteProxyServerHandler(webapp2.RequestHandler):
  """Handler for deleting an existing proxy server."""

  @admin.require_admin
  def get(self):
    """Delete the proxy server corresponding to the passed in id.

    If we had access to a delete method then we would not use get here.
    """
    ProxyServer.Delete(int(self.request.get('id')))
    self.response.write(_RenderListProxyServerTemplate())


class ListProxyServersHandler(webapp2.RequestHandler):
  """Handler for listing all existing proxy servers."""

  @admin.require_admin
  def get(self):
    """Get all current proxy servers and list them with their metadata."""
    self.response.write(_RenderListProxyServerTemplate())


class DistributeKeyHandler(webapp2.RequestHandler):
  """Handler for distributing authorization keys out to each proxy server."""

  # This handler requires admin login, and is controlled in the app.yaml.
  def get(self):
    """Send the current users and associated key out to each proxy server.

    This handler is not intended primarily for a typical user, but for a cron
    job to periodically trigger.
    """
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
    ('/proxyserver/edit', EditProxyServerHandler),
    ('/proxyserver/list', ListProxyServersHandler),

    ('/cron/proxyserver/distributekey', DistributeKeyHandler),
], debug=True)
