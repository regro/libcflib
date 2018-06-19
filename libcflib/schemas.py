SCHEMAS = {
    "artifact": {
        "_description": "Schema for the package artifact",
        "type": "dict",
        "schema": {
            "about": {
                "schema": {
                    "channels": {"schema": {"type": "string"}, "type": "list"},
                    "conda_build_version": {
                        "schema": {"type": "string"},
                        "type": "list",
                    },
                    "conda_private": {"type": "bool"},
                    "conda_version": {"schema": {"type": "string"}, "type": "list"},
                    "env_vars": {
                        "schema": {
                            "CIO_TEST": {"schema": {"type": "string"}, "type": "list"},
                            "CONDA_DEFAULT_ENV": {
                                "schema": {"type": "string"},
                                "type": "list",
                            },
                            "CONDA_ENVS_PATH": {
                                "schema": {"type": "string"},
                                "type": "list",
                            },
                            "LD_LIBRARY_PATH": {
                                "schema": {"type": "string"},
                                "type": "list",
                            },
                            "PATH": {"schema": {"type": "string"}, "type": "list"},
                            "PYTHONHOME": {
                                "schema": {"type": "string"},
                                "type": "list",
                            },
                            "PYTHONPATH": {
                                "schema": {"type": "string"},
                                "type": "list",
                            },
                        },
                        "type": "dict",
                    },
                    "home": {"schema": {"type": "string"}, "type": "list"},
                    "license": {"schema": {"type": "string"}, "type": "list"},
                    "license_file": {"schema": {"type": "string"}, "type": "list"},
                    "root_pkgs": {"schema": {"type": "string"}, "type": "list"},
                    "summary": {"schema": {"type": "string"}, "type": "list"},
                },
                "type": "dict",
            },
            "conda_build_config": {
                "schema": {
                    "c_compiler": {"schema": {"type": "string"}, "type": "list"},
                    "cpu_optimization_target": {
                        "schema": {"type": "string"},
                        "type": "list",
                    },
                    "cran_mirror": {"schema": {"type": "string"}, "type": "list"},
                    "cxx_compiler": {"schema": {"type": "string"}, "type": "list"},
                    "fortran_compiler": {"schema": {"type": "string"}, "type": "list"},
                    "ignore_build_only_deps": {
                        "schema": {"type": "string"},
                        "type": "list",
                    },
                    "lua": {"schema": {"type": "string"}, "type": "list"},
                    "numpy": {"schema": {"type": "string"}, "type": "list"},
                    "perl": {"schema": {"type": "string"}, "type": "list"},
                    "pin_run_as_build": {
                        "schema": {
                            "python": {
                                "schema": {
                                    "max_pin": {
                                        "schema": {"type": "string"},
                                        "type": "list",
                                    },
                                    "min_pin": {
                                        "schema": {"type": "string"},
                                        "type": "list",
                                    },
                                },
                                "type": "dict",
                            },
                            "r-base": {
                                "schema": {
                                    "max_pin": {
                                        "schema": {"type": "string"},
                                        "type": "list",
                                    },
                                    "min_pin": {
                                        "schema": {"type": "string"},
                                        "type": "list",
                                    },
                                },
                                "type": "dict",
                            },
                        },
                        "type": "dict",
                    },
                    "python": {"schema": {"type": "string"}, "type": "list"},
                    "r_base": {"schema": {"type": "string"}, "type": "list"},
                    "target_platform": {"schema": {"type": "string"}, "type": "list"},
                },
                "type": "dict",
            },
            "files": {"schema": {"type": "string"}, "type": "list"},
            "index": {
                "schema": {
                    "arch": {"schema": {"type": "string"}, "type": "list"},
                    "build": {"schema": {"type": "string"}, "type": "list"},
                    "build_number": {"type": "integer"},
                    "depends": {"schema": {"type": "string"}, "type": "list"},
                    "license": {"schema": {"type": "string"}, "type": "list"},
                    "name": {"schema": {"type": "string"}, "type": "list"},
                    "platform": {"schema": {"type": "string"}, "type": "list"},
                    "subdir": {"schema": {"type": "string"}, "type": "list"},
                    "timestamp": {"type": "integer"},
                    "version": {"schema": {"type": "string"}, "type": "list"},
                },
                "type": "dict",
            },
            "name": {"schema": {"type": "string"}, "type": "list"},
            "metdata_version": {"schema": {"type": "integer"}, "type": "integer"},
            "raw_recipe": {"schema": {"type": "string"}, "type": "list"},
            "rendered_recipe": {
                "schema": {
                    "about": {
                        "schema": {
                            "home": {"schema": {"type": "string"}, "type": "list"},
                            "license": {"schema": {"type": "string"}, "type": "list"},
                            "license_file": {
                                "schema": {"type": "string"},
                                "type": "list",
                            },
                            "summary": {"schema": {"type": "string"}, "type": "list"},
                        },
                        "type": "dict",
                    },
                    "build": {
                        "schema": {
                            "entry_points": {
                                "schema": {"type": "string"},
                                "type": "list",
                            },
                            "number": {"schema": {"type": "string"}, "type": "list"},
                            "script": {"schema": {"type": "string"}, "type": "list"},
                            "string": {"schema": {"type": "string"}, "type": "list"},
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
                            "name": {"schema": {"type": "string"}, "type": "list"},
                            "version": {"schema": {"type": "string"}, "type": "list"},
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
                            "fn": {"schema": {"type": "string"}, "type": "list"},
                            "sha256": {"schema": {"type": "string"}, "type": "list"},
                            "url": {"schema": {"type": "string"}, "type": "list"},
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
            "version": {"schema": {"type": "string"}, "type": "list"},
        },
    },
    "package": {
        "_description": "Schema for the package",
        "type": "dict",
        "schema": {
            "PRed": {
                "_description": "For each migrator which"
                "track which PRs have"
                "been issued",
                "type": "list",
                "schema": {"type": "string"},
            },
            "name": {"_description": "Package name", "type": "string"},
            "archived": {
                "_description": "If the package is " "archived",
                "type": "bool",
            },
            "artifacts": {
                "_description": "Links to the artifacts",
                "type": "list",
                "schema": {"type": "string"},
            },
            "bad": {"_description": "Reason why the packages is bad", "type": "string"},
            "harvest_time": {
                "_description": "UTC time when the " "artifacts were " "harvested",
                "type": "float",
            },
            "req": {
                "_description": "The requirements. Note that this"
                "is a superset of all the latest"
                "artifacts dependencies",
                "type": "set",
                "schema": {"type": "string"},
            },
            "versions": {
                "_description": "The versions for this " "package",
                "type": "list",
                "schema": {"type": "string"},
            },
        },
    },
}
