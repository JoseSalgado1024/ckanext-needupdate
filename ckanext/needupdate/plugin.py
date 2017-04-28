# encoding: utf-8
"""
Implementación del Plugin NeedUpdate.

"""
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
from controller import NeedupdateController

# logs
logger = logging.getLogger(__name__)


def get_plugins_list():
    """
    Retorna la lista de plugins que posee la plataforma.

    Args:
        - None.

    Returns:
        - list()
    """
    c = NeedupdateController()
    return c.get_list_of_repos()


class NeedupdatePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.interfaces.IRoutes, inherit=True)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

    def info(self):
        return {'name': 'NeedUpdate',
                'title': 'NU',
                'icon': 'file-text',
                'default_title': 'NU',
                }

    def update_config(self, config_):
        toolkit.add_ckan_admin_tab(config_, 'ext_status_dashboard', 'My Plugins')
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'needupdate')

    def before_map(self, m):
        return m

    def after_map(self, m):
        m.connect('ext_status_api',
                  '/ext_status.json',
                  controller='ckanext.needupdate.plugin:NeedupdateController',
                  action='ext_status')
        m.connect('ext_status_dashboard',
                  '/my_extensions',
                  controller='ckanext.needupdate.plugin:NeedupdateController',
                  action='dashboard_ext')
        return m

    def get_helpers(self):
        """
        Registrar el helper "get_plugins_list()"

        Returns:
            - list(). Lista de plugins instalados.
        """
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        return {'needupdate_get_plugins_list': get_plugins_list}
