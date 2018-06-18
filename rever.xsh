$PROJECT = 'libcflib'
$ACTIVITIES = ['version_bump', 'changelog',
               'tag', 'push_tag', 
               'ghrelease',
               'pypi', 
               'conda_forge',
]

$VERSION_BUMP_PATTERNS = [
    ($PROJECT+'/__init__.py', '__version__\s*=.*', "__version__ = '$VERSION'"),
    ('setup.py', 'version\s*=.*,', "version='$VERSION',")
    ]
$CHANGELOG_FILENAME = 'CHANGELOG.rst'
$CHANGELOG_TEMPLATE = 'TEMPLATE.rst'
$PUSH_TAG_REMOTE = 'git@github.com:regro/libcflib.git'

$GITHUB_ORG = 'regro'

