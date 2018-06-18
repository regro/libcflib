# XXX: the os specificity of this grinds my gears

schemas = {'node': {'_description': 'Schema for the node',
                    'type': 'dict',
                    'schema':
                        {'name': {'_description': 'Name of the package',
                                  'type': 'dict'},
                         'rendered':
                             {
                                 '_description': 'The rendered meta.yaml, '
                                                 'this is usually rendered '
                                                 'on linux',
                                 'type': 'dict'},
                         'raw_recipe': {
                             '_description': 'The raw meta.yaml used in the '
                                             'package',
                             'type': 'string'},
                         'files': {
                             '_description': 'Files written by conda-build',
                             'type': 'set'},
                         'version': {'_description': 'Version of the code'
                                                     'for this node, note'
                                                     'that "latest" is the'
                                                     'latest version',
                                     'type': 'string'},
                         'about': {'_description': 'metadata about the package',
                                   'type': 'dict'},
                         'index': {'_description': 'Core file, name verson '
                                                   'deps',
                                   'type': 'dict'}
                         }}}
