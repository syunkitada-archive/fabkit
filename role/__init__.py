# coding: utf-8

from fabric.api import *
import commands, re
import util, conf

@task
def role(role_pattern='*'):
    re_name = re.compile('name +[\'"](.*)[\'"]')
    re_run_list = re.compile('run_list +[\'"](.*)[\'"]')
    re_run_list_following = re.compile('[\'"](.*)[\'"]')
    re_run_list_end = re.compile('^[a-z].*')
    find = commands.getoutput('find {0}/ -name {1}.rb'.format(conf.ROLE_DIR, role_pattern))
    role_paths = find.split('\n')

    name = 'name'
    run_list = 'run_list'
    print '%(name)-40s%(run_list)s' % locals()
    print '-------------------------------------------------------------------------------------------'
    role_infos = []
    for role_path in role_paths:
        is_accept_name = True
        is_accept_run_list = True
        role_info = {}
        with open(role_path, 'r') as f:
            run_list = []
            for line in f:
                if is_accept_name:
                    name = re_name.findall(line)
                    if len(name) == 1:
                        role_info.update({'name':name[0]})
                        is_accept_name = False
                if is_accept_run_list:
                    if len(run_list) == 0:
                        run_element = re_run_list.findall(line)
                        if len(run_element) == 1:
                            run_list.append(run_element[0])
                            is_run_list = True
                    else:
                        if re_run_list_end.match(line):
                            is_accept_run_list = False

                        else:
                            run_element = re_run_list_following.findall(line)
                            if len(run_element) == 1:
                                run_list.append(run_element[0])

            role_info.update({'run_list': run_list})

        print '%(name)-40s%(run_list)s' % {
                'name': role_info.get('name'),
                'run_list': role_info.get('run_list')}
        role_infos.append(role_info)

    return role_infos
