# encoding: utf-8
"""
Implementación del Plugin NeedUpdate.

"""
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.base import BaseController
from pylons import response
import logging
import json
from ckan.config.environment import config as ckan_config

# logs
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
    plugins.implements(plugins.interfaces.IRoutes, inherit=True)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'needupdate')

    def before_map(self, m):
        return m

    def after_map(self, m):
        m.connect('ext_status',
                  '/ext_status.json',
                  controller='ckanext.needupdate.plugin:NeedupdateController',
                  action='ext_status')
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
        # return {'need_update_get_plugins_list': get_plugins_list}
        pass


class NeedupdateController(BaseController):
    """
    Controlador principal del plugin.
    """

    def __init__(self):
        """
        Init del Controlador pricipal del plugin NeedUpdate.
        """
        self.ext_folder = ckan_config.get('ckanext.needupdate.ext_folder', '/usr/lib/ckan/default/src')
        self.ext_prefix = ckan_config.get('ckanext.needupdate.ext_folder', 'ckanext-')
        self.ext_sufix = ckan_config.get('ckanext.needupdate.ext_folder', '')

    def get_list_of_repos(self):
        """
        Retorna una lista con los posibles repositorios.

        Args:
            - path_to_repos. Lista de nombres de directorios. 
            - prefix: str(). Prefijo con el que empiezan los nombres de las carpetas que son repositorios.
            - sufix: str(). Sufijo con el que terminan los nombres de las carpetas que son repositorios
        """
        list_of_repos = []
        try:
            if False in [isinstance(self.ext_folder, (str, unicode)),
                         isinstance(self.ext_sufix, (str, unicode)),
                         isinstance(self.ext_prefix, (str, unicode))]:
                raise TypeError('Los tipos de los argumentos provistos no son validos.')
            from os import listdir, path
            if not path.exists(self.ext_folder):
                raise IOError('El directorio {} no existe.'.format(self.ext_folder))
            list_of_folders = listdir(self.ext_folder)
            from git import Repo
            from git.exc import GitCommandError
            for folder in list_of_folders:
                if [folder[:len(self.ext_prefix)], folder[:-len(self.ext_sufix)]] == [self.ext_prefix, self.ext_sufix]:
                    ext_name = folder.replace(self.ext_sufix, '').replace(self.ext_prefix, '')
                    try:
                        r = Repo(path.join(self.ext_folder, folder))
                        _branch = r.active_branch.name
                        origin_branch = 'origin/{branch}..{branch}'.format(branch=_branch)
                        commits_ahead = sum(x / x for x in r.iter_commits(origin_branch))
                        commits_behind = sum(x / x for x in list(r.iter_commits('master..master@{{u}}'.format(b=_branch))))
                        list_of_repos.append({
                            'ext_name': ext_name,
                            'branch': _branch,
                            'last_commit': r.active_branch.commit.message,
                            'description': r.description,
                            'commits_ahead_master': commits_ahead,
                            'commits_behind_master': commits_behind
                        })
                    except GitCommandError:
                        logger.error('Imposible chequear: {}'.format(ext_name))
        except (TypeError, IOError) as e:
            logger.error(e)
        return list_of_repos

    def ext_status(self):
        r = self.get_list_of_repos()
        return self.build_response(r)

    @staticmethod
    def build_response(_json_data):
        data = {}
        if isinstance(_json_data, (dict, list)):
            data = _json_data
        response.content_type = 'application/json; charset=UTF-8'
        del response.headers["Cache-Control"]
        del response.headers["Pragma"]
        return plugins.toolkit.literal(json.dumps(data))
