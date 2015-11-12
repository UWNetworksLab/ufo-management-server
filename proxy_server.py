"""The module for handling proxy servers."""

import admin
from appengine_config import JINJA_ENVIRONMENT
from datastore import ProxyServer
from google.appengine.api import app_identity
import xsrf
import webapp2


def _RenderAddProxyServerTemplate():
  """Render the page to add a proxy server."""
  template_values = {
      'host': app_identity.get_default_version_hostname(),
      'xsrf_token': xsrf.xsrf_token(),
  }
  template = JINJA_ENVIRONMENT.get_template('templates/add_proxy_server.html')
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


class AddProxyServerHandler(webapp2.RequestHandler):

  @admin.require_admin
  def get(self):
    self.response.write(_RenderAddProxyServerTemplate())

  @admin.require_admin
  @xsrf.xsrf_protect
  def post(self):
    ProxyServer.Insert(
      self.request.get('ip_address'),
      self.request.get('ssh_private_key'),
      self.request.get('fingerprint'))
    self.redirect('/proxyserver/list')


class ListProxyServersHandler(webapp2.RequestHandler):

  @admin.require_admin
  def get(self):
    self.response.write(_RenderListProxyServerTemplate())


app = webapp2.WSGIApplication([
    ('/proxyserver/add', AddProxyServerHandler),
    ('/proxyserver/list', ListProxyServersHandler),
], debug=True)
