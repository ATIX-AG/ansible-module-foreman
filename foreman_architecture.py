#!/usr/bin/env python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: foreman_architecture
short_description: Manage Foreman Architectures using Foreman API v2
description:
- Create and delete Foreman Architectures using Foreman API v2
options:
  name:
    description: Name of architecture
    required: true
    default: null
    aliases: []
  state:
    description: State of architecture
    required: false
    default: present
    choices: ["present", "absent"]
  foreman_host:
    description: Hostname or IP address of Foreman system
    required: false
    default: 127.0.0.1
  foreman_port:
    description: Port of Foreman API
    required: false
    default: 443
  foreman_user:
    description: Username to be used to authenticate on Foreman
    required: true
    default: null
  foreman_pass:
    description: Password to be used to authenticate user on Foreman
    required: true
    default: null
notes:
- Requires the python-foreman package to be installed. See https://github.com/Nosmoht/python-foreman.
author: Thomas Krahn
'''

EXAMPLES = '''
- name: Ensure ARM Architecture is present
  foreman_architecture:
    name: ARM
    state: present
    foreman_user: admin
    foreman_pass: secret
    foreman_host: foreman.example.com
    foreman_port: 443
'''

try:
    from foreman.foreman import *
except ImportError:
    foremanclient_found = False
else:
    foremanclient_found = True


def ensure(module):
    name = module.params['name']
    state = module.params['state']
    foreman_host = module.params['foreman_host']
    foreman_port = module.params['foreman_port']
    foreman_user = module.params['foreman_user']
    foreman_pass = module.params['foreman_pass']

    theforeman = Foreman(hostname=foreman_host,
                         port=foreman_port,
                         username=foreman_user,
                         password=foreman_pass)

    data = {'name': name}

    try:
        arch = theforeman.search_architecture(data=data)
    except ForemanError as e:
        module.fail_json(msg='Could not get architecture: {0}'.format(e.message))

    if not arch and state == 'present':
        try:
            arch = theforeman.create_architecture(data)
            return True, arch
        except ForemanError as e:
            module.fail_json(msg='Could not create architecture: {0}'.format(e.message))

    if arch and state == 'absent':
        try:
            theforeman.delete_architecture(id=arch.get('id'))
            return True, None
        except ForemanError as e:
            module.fail_json(msg='Could not delete architecture: {0}'.format(e.message))

    return False, arch


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(Type='str', required=True),
            state=dict(Type='str', Default='present', choices=['present', 'absent']),
            foreman_host=dict(Type='str', Default='127.0.0.1'),
            foreman_port=dict(Type='str', Default='443'),
            foreman_user=dict(Type='str', required=True),
            foreman_pass=dict(Type='str', required=True)
        ),
    )

    if not foremanclient_found:
        module.fail_json(msg='python-foreman module is required. See https://github.com/Nosmoht/python-foreman.')

    changed, arch = ensure(module)
    module.exit_json(changed=changed, architecture=arch)

# import module snippets
from ansible.module_utils.basic import *

main()
