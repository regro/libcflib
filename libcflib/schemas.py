SCHEMAS = {
    'artifact': {
        '_description': 'Schema for the package artifact',
        'type': 'dict',
        'schema':
            {'name': {'_description': 'Name of the package',
                      'type': 'dict'},
             'rendered':
                 {
                     '_description': 'The rendered meta.yaml, this is usually '
                                     'rendered on linux',
                     'type': 'dict'},
             'raw_recipe': {
                 '_description': 'The raw meta.yaml used in the package',
                 'type': 'string'},
             'files': {
                 '_description': 'Files written by conda-build',
                 'type': 'set'},
             'version': {'_description': 'Version of the code for this node, '
                                         'notethat "latest" is the latest '
                                         'version',
                         'type': 'string'},
             'about': {
                 '_description': 'metadata about the package',
                 'type': 'dict'},
             'index': {
                 '_description': 'Core file, name verson '
                                 'deps',
                 'type': 'dict'},
             }},
    'package': {'_description': 'Schema for the package',
                'type': 'dict',
                'schema': {
                    'PRed': {'_description': 'For each migrator which'
                                             'track which PRs have'
                                             'been issued',
                             'type': 'list',
                             'schema': {'type': 'tuple'}},
                    'name': {'_description': 'Package name',
                             'type': 'string'},
                    'archived': {'_description': 'If the package is '
                                                 'archived',
                                 'type': 'bool'},
                    'artifacts': {'_description': 'Links to the artifacts',
                                  'type': 'list'},
                    'bad': {'_description': 'Reason why the packages is bad',
                            'type': 'string'},
                    'harvest_time': {'_description': 'UTC time when the '
                                                     'artifacts were '
                                                     'harvested',
                                     'type': 'int'},
                    'req': {'_description': 'The requirements. Note that this'
                                            'is a superset of all the latest'
                                            'artifacts dependencies',
                            'type': 'set'},
                    'versions': {'_description': 'The versions for this '
                                                 'package',
                                 'type': 'list'}
                }}}
