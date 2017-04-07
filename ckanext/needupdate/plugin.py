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
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'needupdate')

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

    def __init__(self):
        pass

    # coding: utf-8
    from os import path
    import logging
    logging.basicConfig(level=logging.INFO)
    logs = logging.getLogger('need_update')

    def get_list_of_repos(path_to_repos, sufix='', prefix='ckanext_'):
        """
        Retorna una lista con los posibles repositorios.

        Args:
            - path_to_repos. Lista de nombres de directorios. 
            - prefix: str(). Prefijo con el que empiezan los nombres de las carpetas que son repositorios.
            - sufix: str(). Sufijo con el que terminan los nombres de las carpetas que son repositorios
        """
        list_of_repos = []
        try:
            if False in [isinstance(path_to_repos, (str, unicode)),
                         isinstance(sufix, (str, unicode)),
                         isinstance(prefix, (str, unicode))]:
                raise TypeError('Los tipos de los argumentos provistos no son validos.')
            from os import listdir, path
            if not path.exists(path_to_repos):
                raise IOError('El directorio {} no existe.'.format(path_to_repos))
            list_of_folders = listdir(path_to_repos)
            from git import Repo
            for folder in list_of_folders:
                if [folder[:len(prefix)], folder[:-len(sufix)]] == [prefix, sufix]:
                    r = Repo(path.join(path_to_repos, folder))
                    _branch = r.active_branch.name
                    commits_ahead = sum(1 for c in r.iter_commits('origin/master..master'))
                    commits_behind = sum(1 for c in r.iter_commits('master..origin/master'))
                    list_of_repos.append({
                        'ext_name': folder.replace(sufix, '').replace(prefix, ''),
                        'branch': _branch,
                        'last_commit': r.active_branch.commit.message,
                        'description': r.description,
                        'commits_ahead': commits_ahead,
                        'commits_behind': sum(1 for c in list(r.iter_commits('{b}..{b}@{{u}}'.format(b=_branch))))
                    })
        except (TypeError, IOError) as e:
            logs.error(e)
        return list_of_repos

    _folder = path.join(path.dirname(__file__), 'repos')
    repos = get_list_of_repos(_folder, prefix='test_')
    print len(repos)
    print repos
    @staticmethod
    def build_response(_json_data):
        data = {}
        if isinstance(_json_data, (dict, list)):
            data = _json_data
        response.content_type = 'application/json; charset=UTF-8'
        del response.headers["Cache-Control"]
        del response.headers["Pragma"]
        return plugins.toolkit.literal(json.dumps(data))
