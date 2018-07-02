$PROJECT = $GITHUB_REPO = 'libcflib'
$ACTIVITIES = [
    'version_bump',
    'changelog',
    'tag',
    'push_tag',
    'ghrelease',
    'pypi',
    #'conda_forge',
    'docker_build',
    'docker_push',
]

$VERSION_BUMP_PATTERNS = [
    ($PROJECT+'/__init__.py', '__version__\s*=.*', "__version__ = '$VERSION'"),
    ('setup.py', 'VERSION\s*=.*', "VERSION = '$VERSION'")
    ]
$CHANGELOG_FILENAME = 'CHANGELOG.rst'
$CHANGELOG_TEMPLATE = 'TEMPLATE.rst'
$PUSH_TAG_REMOTE = 'git@github.com:regro/libcflib.git'

$GITHUB_ORG = 'regro'

# docker config
$DOCKERFILE = 'docker/Dockerfile'
$DOCKERFILE_TAGS = ('condaforge/libcflib:$VERSION',
                    'condaforge/libcflib:latest')