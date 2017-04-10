from ckan.lib.base import BaseController
from pylons import response
import logging
import json
from ckan.config.environment import config as ckan_config
import ckan.plugins as plugins
import ckan.authz as authz
import ckan.logic as logic
from ckan.common import _, c, g
import ckan.lib.base as base

# logs
logger = logging.getLogger(__name__)


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

    def _setup_template_variables(self, context, data_dict):
        c.is_sysadmin = authz.is_sysadmin(c.user)
        try:
            user_dict = logic.get_action('user_show')(context, data_dict)
        except logic.NotFound:
            base.abort(404, _('User not found'))
        except logic.NotAuthorized:
            base.abort(401, _('Not authorized to see this page'))

    def get_list_of_repos(self):
        """
        Retorna una lista con los posibles repositorios.

        Args:
            - path_to_repos. Lista de nombres de directorios.
            - prefix: str(). Prefijo con el que empiezan los nombres de las carpetas que son repositorios.
            - sufix: str(). Sufijo con el que terminan los nombres de las carpetas que son repositorios
        """
        my_extensions = {'checked_plugins_names': [],
                         'checked_plugins': [],
                         'unchecked_plugins': [],
                         'checked_plugins_count': 0,
                         'total_plugins_count': 0}
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
            from os import path
            for folder in list_of_folders:
                if [folder[:len(self.ext_prefix)], folder[:-len(self.ext_sufix)]] == [self.ext_prefix, self.ext_sufix]:
                    ext_name = folder.replace(self.ext_sufix, '').replace(self.ext_prefix, '')
                    try:
                        r = Repo(path.join(self.ext_folder, folder))
                        _branch = r.active_branch.name
                        origin_branch = 'origin/{branch}..{branch}'.format(branch=_branch)
                        _git_dir = path.dirname(r.git_dir)
                        commits_ahead = sum(x / x for x in r.iter_commits(origin_branch))
                        commits_behind = sum(
                            x / x for x in list(r.iter_commits('master..master@{{u}}'.format(b=_branch))))
                        my_extensions['checked_plugins'].append({'ext_name': ext_name,
                                                                 'branch': _branch,
                                                                 'last_commit': r.active_branch.commit.message,
                                                                 'description': r.description,
                                                                 'commits_ahead_master': commits_ahead,
                                                                 'git_dir': _git_dir,
                                                                 'commits_behind_master': commits_behind})
                        my_extensions['checked_plugins_names'].append(ext_name)
                        my_extensions['checked_plugins_count'] = len(my_extensions['checked_plugins'])
                        my_extensions['total_plugins_count'] = len(my_extensions['checked_plugins']) + len(
                            my_extensions['unchecked_plugins'])
                    except GitCommandError:
                        my_extensions['unchecked_plugins'].append(ext_name)
                        logger.error('Fallo: \"no upstream configured for branch\"')
        except (TypeError, IOError):
            logger.error('Imposible checkear extension')
        return my_extensions

    def ext_status(self):
        r = self.get_list_of_repos()
        return self.build_response(r)

    def dashboard_ext(self):
        context = {'for_view': True, 'user': c.user or c.author,
                   'auth_user_obj': c.userobj}
        data_dict = {'user_obj': c.userobj}
        self._setup_template_variables(context, data_dict)
        return base.render('user/plugins_dashboard.html')

    @staticmethod
    def build_response(_json_data):
        data = {}
        if isinstance(_json_data, (dict, list)):
            data = _json_data
        response.content_type = 'application/json; charset=UTF-8'
        del response.headers["Cache-Control"]
        del response.headers["Pragma"]
        return plugins.toolkit.literal(json.dumps(data))
