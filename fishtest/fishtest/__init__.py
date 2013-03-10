import os, sys
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import NewRequest
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from fishtest.security import groupfinder

from rundb import RunDb

def main(global_config, **settings):
  """ This function returns a Pyramid WSGI application.
  """
  session_factory = UnencryptedCookieSessionFactoryConfig('fishtest')
  config = Configurator(settings=settings,
                        session_factory=session_factory,
                        root_factory='fishtest.models.RootFactory')

  # Authentication
  with open(os.path.expanduser('~/fishtest.secret'), 'r') as f:
    secret = f.read()
  config.set_authentication_policy(AuthTktAuthenticationPolicy(secret, callback=groupfinder, hashalg='sha512'))
  config.set_authorization_policy(ACLAuthorizationPolicy())

  rundb = RunDb()
  def add_rundb(event):
    event.request.rundb = rundb
  config.add_subscriber(add_rundb, NewRequest)

  config.add_static_view('css', 'static/css', cache_max_age=3600)
  config.add_static_view('js', 'static/js', cache_max_age=3600)
  config.add_static_view('img', 'static/img', cache_max_age=3600)
  config.add_route('home', '/')
  config.add_route('login', '/login')
  config.add_route('tests', '/tests')
  config.add_route('tests_run', '/tests/run')
  config.add_route('tests_run_more', '/tests/run_more')
  config.add_route('tests_view', '/tests/view/{id}')
  config.add_route('tests_delete', '/tests/delete')
  config.add_route('tests_stop', '/tests/stop')

  # API
  config.add_route('api_request_task', '/api/request_task')
  config.add_route('api_update_task', '/api/update_task')
  config.add_route('api_failed_task', '/api/failed_task')

  config.scan()
  return config.make_wsgi_app()
