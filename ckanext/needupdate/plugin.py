# encoding: utf-8
"""
Implementación del Plugin NeedUpdate.

"""
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.base import BaseController
from pylons import response
import logging


logger = logging.getLogger('needupdate')


def get_plugins_list():
    """
    Retorna la lista de plugins que posee la plataforma.

    Args:
        - None.

    Returns:
        - list()
    """
    # mock
    return [
        {
            'name': 'my_plugin',
            'branch': 'my_branch',
            'commits_ahead': 0,
         }
    ]


class NeedupdatePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        # toolkit.add_public_directory(config_, 'public')
        # toolkit.add_resource('fanstatic', 'needupdate')

    def before_map(self, m):
        return m

    def after_map(self, m):
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
        return {'need_update_get_plugins_list': get_plugins_list}


class NeedupdateController(BaseController):
    """
    Controlador principal del plugin.
    """
    _errors_json = []

    def __init__(self):
        pass

    @staticmethod
    def build_response(_json_data):
        data = {}
        if isinstance(_json_data, (dict, list)):
            data = _json_data
        response.content_type = 'application/json; charset=UTF-8'
        del response.headers["Cache-Control"]
        del response.headers["Pragma"]
        return plugins.toolkit.literal(json.dumps(data))