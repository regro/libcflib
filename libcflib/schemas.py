SCHEMAS = {
    "feedstock": {
        "_description": "Schema for the conda-forge feedstock",
        "type": "dict",
        "schema": {
            "name": {"type": "string", "_description": "name of feedstock"},
            "bad": {
                "_description": "Reason why the packages are bad",
                "type": "string",
            },
            "archived": {
                "_description": "If the package is " "archived",
                "type": "bool",
            },
            "PRed": {
                "_description": "For each migrator which"
                "track which PRs have"
                "been issued",
                "type": "list",
                "schema": {"type": "string"},
            },
            "packages": {
                "_description": "Links to the packages",
                "type": "list",
                "schema": {"type": "string"},
            },
            "commit": {"type": "string", "_description": "The latest commit"},
            "new_version": {
                "anyof_type": ["string", "bool"],
                "_description": "The new version",
            },
            "meta_yaml": {"type": "dict", "_description": "The meta_yaml"},
        },
    },
    "artifact": {
        "_description": "Schema for the package artifact",
        "type": "dict",
        "schema": {
            "about": {
                "schema": {
                    "channels": {"schema": {"type": "string"}, "type": "list"},
                    "conda_build_version": {"type": "string"},
                    "conda_private": {"type": "bool"},
                    "conda_version": {"type": "string"},
                    "env_vars": {
                        "schema": {
                            "CIO_TEST": {"type": "string"},
                            "CONDA_DEFAULT_ENV": {"type": "string"},
                            "CONDA_ENVS_PATH": {"type": "string"},
                            "LD_LIBRARY_PATH": {"type": "string"},
                            "PATH": {"type": "string"},
                            "PYTHONHOME": {"type": "string"},
                            "PYTHONPATH": {"type": "string"},
                        },
                        "type": "dict",
                    },
                    "home": {"type": "string"},
                    "license": {"type": "string"},
                    "license_file": {"type": "string"},
                    "root_pkgs": {"schema": {"type": "string"}, "type": "list"},
                    "summary": {"type": "string"},
                },
                "type": "dict",
            },
            "conda_build_config": {
                "schema": {
                    "c_compiler": {"type": "string"},
                    "cpu_optimization_target": {"type": "string"},
                    "cran_mirror": {"type": "string"},
                    "cxx_compiler": {"type": "string"},
                    "fortran_compiler": {"type": "string"},
                    "ignore_build_only_deps": {"type": "string"},
                    "lua": {"type": "string"},
                    "numpy": {"type": "string"},
                    "perl": {"type": "string"},
                    "pin_run_as_build": {
                        "schema": {
                            "python": {
                                "schema": {
                                    "max_pin": {"type": "string"},
                                    "min_pin": {"type": "string"},
                                },
                                "type": "dict",
                            },
                            "r-base": {
                                "schema": {
                                    "max_pin": {"type": "string"},
                                    "min_pin": {"type": "string"},
                                },
                                "type": "dict",
                            },
                        },
                        "type": "dict",
                    },
                    "python": {"type": "string"},
                    "r_base": {"type": "string"},
                    "target_platform": {"type": "string"},
                },
                "type": "dict",
            },
            "files": {"schema": {"type": "string"}, "type": "list"},
            "index": {
                "schema": {
                    "arch": {"type": "string"},
                    "build": {"type": "string"},
                    "build_number": {"type": "integer"},
                    "depends": {"schema": {"type": "string"}, "type": "list"},
                    "license": {"type": "string"},
                    "name": {"type": "string"},
                    "platform": {"type": "string"},
                    "subdir": {"type": "string"},
                    "timestamp": {"type": "integer"},
                    "version": {"type": "string"},
                },
                "type": "dict",
            },
            "name": {"type": "string"},
            "metadata_version": {"type": "integer"},
            "raw_recipe": {"type": "string"},
            "rendered_recipe": {
                "schema": {
                    "about": {
                        "schema": {
                            "home": {"type": "string"},
                            "license": {"type": "string"},
                            "license_file": {"type": "string"},
                            "summary": {"type": "string"},
                        },
                        "type": "dict",
                    },
                    "build": {
                        "schema": {
                            "entry_points": {
                                "schema": {"type": "string"},
                                "type": "list",
                            },
                            "number": {"type": "string"},
                            "script": {"type": "string"},
                            "string": {"type": "string"},
                        },
                        "type": "dict",
                    },
                    "extra": {
                        "schema": {
                            "copy_test_source_files": {"type": "bool"},
                            "final": {"type": "bool"},
                            "recipe-maintainers": {
                                "schema": {"type": "string"},
                                "type": "list",
                            },
                        },
                        "type": "dict",
                    },
                    "package": {
                        "schema": {
                            "name": {"type": "string"},
                            "version": {"type": "string"},
                        },
                        "type": "dict",
                    },
                    "requirements": {
                        "schema": {
                            "build": {"schema": {"type": "string"}, "type": "list"},
                            "run": {"schema": {"type": "string"}, "type": "list"},
                        },
                        "type": "dict",
                    },
                    "source": {
                        "schema": {
                            "fn": {"type": "string"},
                            "sha256": {"type": "string"},
                            "url": {"type": "string"},
                        },
                        "type": "dict",
                    },
                    "test": {
                        "schema": {
                            "commands": {"schema": {"type": "string"}, "type": "list"},
                            "imports": {"schema": {"type": "string"}, "type": "list"},
                        },
                        "type": "dict",
                    },
                },
                "type": "dict",
            },
            "version": {"type": "string"},
        },
    },
    "package": {
        "_description": "Schema for the package",
        "type": "dict",
        "schema": {
            "name": {"_description": "Package name", "type": "string"},
            "artifacts": {
                "_description": "Links to the artifacts",
                "type": "list",
                "schema": {"type": "string"},
            },
            "req": {
                "_description": "The requirements. Note that this"
                "is a superset of all the latest"
                "artifacts dependencies",
                "type": "set",
                "schema": {"type": "string"},
            },
            "versions": {
                "_description": "The versions for this package",
                "type": "list",
                "schema": {"type": "string"},
            },
        },
    },
}
