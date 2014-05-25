# coding: utf-8
#
# This module do initial configuration.
# And provide setting value that read the configuration file.

import os, sys, re
import ConfigParser
from fabric.api import env
import commands
import json
import util
import uuid
import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler

# setup fabric env
env.forward_agent   = True
env.is_test         = False
env.use_ssh_config  = True
env.warn_only       = True
env.colorize_errors = True

STDOUT_LOG_FILE = 'stdout.log'

# for prefix of tmpfile
UUID = uuid.uuid4()


# append module dir to sys.path
def init(chefrepo_dir=None, test_chefrepo_dir=None):
    env.cmd_history   = [] # for debug

    global CHEFREPO_DIR, TEST_CHEFREPO_DIR
    global STORAGE_DIR, LOG_DIR, PACKAGE_DIR, CHEF_RPM, TMP_CHEF_RPM
    global FABSCRIPT_MODULE, FABSCRIPT_MODULE_DIR
    global COOKBOOKS_DIRS, NODE_DIR, ROLE_DIR, ENVIRONMENT_DIR
    global HTTP_PROXY, HTTPS_PROXY
    global LOGGER_LEVEL, LOGGER_FORMATTER, NODE_LOGGER_MAX_BYTES, NODE_LOGGER_BACKUP_COUNT

    if test_chefrepo_dir:
        TEST_CHEFREPO_DIR = test_chefrepo_dir
    if chefrepo_dir:
        CHEFREPO_DIR = chefrepo_dir
    elif TEST_CHEFREPO_DIR:
        if not TEST_CHEFREPO_DIR in sys.path:
            sys.path.remove(CHEFREPO_DIR)
            sys.path.append(TEST_CHEFREPO_DIR)
        CHEFREPO_DIR = TEST_CHEFREPO_DIR

    # complement to absolute path from path relative to the chef-repo
    def complement_path(path, is_check_dir=False):
        if path == '':
            return None
        if path.find('/') != 0:
            return os.path.join(CHEFREPO_DIR, path)
        return path

    # create directory, if directory not exists
    def create_dir(directory, is_create_init_py=False):
        if not os.path.exists(directory):
            if util.confirm('"{0}" is not exists. do you want to create?'.format(directory), 'Canceled.'):
                os.mkdir(directory)
                print '"{0}" is created.'.format(directory)
                if is_create_init_py:
                    init_py = os.path.join(directory, '__init__.py')
                    with open(init_py, 'w') as f:
                        f.write('# coding: utf-8')
                        print '"{0} is created."'.format(init_py)
            else:
                exit(0)

    KNIFERB_FILE = os.path.join(CHEFREPO_DIR, '.chef/knife.rb')
    INIFILE = os.path.join(CHEFREPO_DIR, 'fabfile.ini')

    CONFIG  = ConfigParser.SafeConfigParser()
    CONFIG.read(INIFILE)

    # read common settings
    STORAGE_DIR          = complement_path(CONFIG.get('common', 'storage_dir'))
    LOG_DIR              = os.path.join(STORAGE_DIR, CONFIG.get('common', 'log_dir'))
    PACKAGE_DIR          = os.path.join(STORAGE_DIR, CONFIG.get('common', 'package_dir'))
    CHEF_RPM_NAME        = CONFIG.get('common', 'chef_rpm')
    CHEF_RPM             = os.path.join(PACKAGE_DIR, CHEF_RPM_NAME)
    TMP_CHEF_RPM         = '/tmp/{0}-{1}'.format(UUID, CHEF_RPM_NAME)
    FABSCRIPT_MODULE     = CONFIG.get('common', 'fabscript_module')
    FABSCRIPT_MODULE_DIR = os.path.join(CHEFREPO_DIR, FABSCRIPT_MODULE)
    FABLIB_MODULE        = CONFIG.get('common', 'fablib_module')
    FABLIB_MODULE_DIR    = os.path.join(CHEFREPO_DIR, FABLIB_MODULE)

    create_dir(STORAGE_DIR)
    create_dir(LOG_DIR)
    create_dir(PACKAGE_DIR)
    create_dir(FABSCRIPT_MODULE_DIR, True)
    create_dir(FABLIB_MODULE_DIR, True)

    fablib_options = CONFIG.options('fablib')
    for fablib_name in fablib_options:
        fablib = os.path.join(FABLIB_MODULE, fablib_name)
        if not os.path.exists(fablib):
            cmd_gitclone = 'git clone {0} {1}'.format(CONFIG.get('fablib', fablib_name), fablib)
            if util.confirm('{0} is not exists in fablib.\nDo you want to run "{1}"?'.format(fablib_name, cmd_gitclone), 'Canceled.'):
                (status, output) = commands.getstatusoutput(cmd_gitclone)
                print output
                if status != 0:
                    exit(0)
            else:
                exit(0)

    ALL_LOG_FILE_NAME   = 'all.log'
    ALL_LOG_FILE        = os.path.join(LOG_DIR, ALL_LOG_FILE_NAME)
    ERROR_LOG_FILE_NAME = 'error.log'
    ERROR_LOG_FILE      = os.path.join(LOG_DIR, ERROR_LOG_FILE_NAME)
    LOGGER_LEVEL        = CONFIG.get('logger', 'level')
    LOGGER_LEVEL        = getattr(logging, LOGGER_LEVEL.upper())
    LOGGER_FORMAT       = CONFIG.get('logger', 'format', True)
    LOGGER_FORMATTER     = logging.Formatter(fmt=LOGGER_FORMAT)
    LOGGER_CONSOLE_LEVEL        = CONFIG.get('logger', 'console_level')
    LOGGER_CONSOLE_LEVEL        = getattr(logging, LOGGER_CONSOLE_LEVEL.upper())
    LOGGER_CONSOLE_FORMAT       = CONFIG.get('logger', 'console_format', True)
    LOGGER_CONSOLE_FORMATTER     = logging.Formatter(fmt=LOGGER_CONSOLE_FORMAT)
    LOGGER_MAX_BYTES    = CONFIG.getint('logger', 'max_bytes')
    LOGGER_BACKUP_COUNT = CONFIG.getint('logger', 'backup_count')
    NODE_LOGGER_MAX_BYTES    = CONFIG.getint('node_logger', 'max_bytes')
    NODE_LOGGER_BACKUP_COUNT = CONFIG.getint('node_logger', 'backup_count')

    root_logger = logging.getLogger()
    root_logger.setLevel(LOGGER_LEVEL)

    stream_handler = StreamHandler()
    stream_handler.setFormatter(LOGGER_CONSOLE_FORMATTER)
    stream_handler.setLevel(LOGGER_CONSOLE_LEVEL)
    root_logger.addHandler(stream_handler)

    file_rotaiting_handler = RotatingFileHandler(ALL_LOG_FILE, 'a', LOGGER_MAX_BYTES, LOGGER_BACKUP_COUNT)
    file_rotaiting_handler.setFormatter(LOGGER_FORMATTER)
    root_logger.addHandler(file_rotaiting_handler)

    error_file_rotaiting_handler = RotatingFileHandler(ERROR_LOG_FILE, 'a', LOGGER_MAX_BYTES, LOGGER_BACKUP_COUNT)
    error_file_rotaiting_handler.setFormatter(LOGGER_FORMATTER)
    error_file_rotaiting_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_file_rotaiting_handler)


    # read .chef/knife.rb
    COOKBOOKS_DIRS  = []
    NODE_DIR        = ''
    ROLE_DIR        = ''
    ENVIRONMENT_DIR = ''
    HTTP_PROXY      = ''
    HTTPS_PROXY     = ''

    __RE_STRIP = re.compile('[ \'"]')
    __RE_KNIFERB_COOKBOOK_PATH    = re.compile('cookbook_path +\[(.+)\]')
    __RE_KNIFERB_NODE_PATH        = re.compile('node_path +[\'"](.+)[\'"]')
    __RE_KNIFERB_ROLE_PATH        = re.compile('role_path +[\'"](.+)[\'"]')
    __RE_KNIFERB_ENVIRONMENT_PATH = re.compile('environment_path +[\'"](.+)[\'"]')
    __RE_KNIFERB_HTTP_PROXY       = re.compile('http_proxy +[\'"](.+)[\'"]')
    __RE_KNIFERB_HTTPS_PROXY      = re.compile('https_proxy +[\'"](.+)[\'"]')
    with open(KNIFERB_FILE) as f:
        matched_cookbook_path    = False
        matched_node_path        = False
        matched_role_path        = False
        matched_environment_path = False
        matched_http_proxy       = False
        matched_https_proxy      = False
        for line in f:
            match_cookbook_path = None if matched_cookbook_path else __RE_KNIFERB_COOKBOOK_PATH.match(line)
            match_node_path = None if matched_node_path else __RE_KNIFERB_NODE_PATH.match(line)
            match_role_path = None if matched_role_path else __RE_KNIFERB_ROLE_PATH.match(line)
            match_environment_path = None if matched_environment_path else __RE_KNIFERB_ENVIRONMENT_PATH.match(line)
            match_http_proxy  = None if matched_http_proxy else __RE_KNIFERB_HTTP_PROXY.match(line)
            match_https_proxy = None if matched_https_proxy else __RE_KNIFERB_HTTPS_PROXY.match(line)

            if match_cookbook_path:
                cookbooks_dirs = __RE_STRIP.sub('', match_cookbook_path.group(1)).split(',')
                for cookbooks_dir in cookbooks_dirs:
                    COOKBOOKS_DIRS.append(complement_path(cookbooks_dir))
                matched_cookbook_path = True
            elif match_node_path:
                NODE_DIR = complement_path(match_node_path.group(1))
                matched_node_path = True
            elif match_role_path:
                ROLE_DIR = complement_path(match_role_path.group(1))
                matched_role_path = True
            elif match_environment_path:
                ENVIRONMENT_DIR = complement_path(match_environment_path.group(1))
                matched_environment_path = True
            elif match_http_proxy:
                HTTP_PROXY = match_http_proxy.group(1)
                matched_http_proxy = True
            elif match_https_proxy:
                HTTPS_PROXY = match_https_proxy.group(1)
                matched_https_proxy = True



# proxy setting
env.is_proxy = False
def is_proxy(option=None):
    if option and option.find('p') != -1:
        if HTTP_PROXY and HTTPS_PROXY:
            env.is_proxy = True
            return True
        else:
            raise Exception('http_proxy is bad')
    else:
        env.is_proxy = False
        return False

# chef-server setting
env.is_server = False
def is_server(option=None):
    if option and option.find('s') != -1:
        env.is_server = True
        return True
    else:
        env.is_server = False
        return False

def get_initial_json(host):
    return get_node_json({ 'name': host })

def get_node_json(dict_obj):
    return {
        'name'          : dict_obj.get('name', ''),
        'run_list'      : dict_obj.get('run_list', []),
        'ipaddress'     : dict_obj.get('ipaddress', ''),
        'ssh'           : dict_obj.get('ssh', ''),
        'uptime'        : dict_obj.get('uptime', ''),
        'last_cook'     : dict_obj.get('last_cook', ''),
        'fab_run_list'  : dict_obj.get('fab_run_list', []),
        'last_fabcooks' : dict_obj.get('last_fabcooks', []),
        'last_check'    : dict_obj.get('last_check', ''),
    }


# chef-solo用のjson文字列を作成し、返します
# chef-serverのjsonをマージすると、chef-soloで利用できなくなるため必要
def get_jsonstr_for_chefsolo(host=None):
    host_json = util.load_json(host)
    json_obj = {
        'run_list': host_json['run_list'],
    }
    return json.dumps(json_obj)

def get_tmp_password_file(host=None):
    if not host:
        host = env.host
    return os.path.expanduser('~/.{0}-{1}'.format(UUID, host))


