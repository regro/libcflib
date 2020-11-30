import jedi

import os

from tqdm import tqdm


def file_path_to_import(file_path: str):
    return file_path.replace("/__init__.py", "").replace(".py", "").replace("/", ".")


def get_all_symbol_names(top_dir):
    # Note Jedi seems to pick up things that are protected by a
    # __name__ == '__main__' if statement
    # this could cause some over-reporting of viable imports this
    # shouldn't cause issues with an audit since we don't expect 3rd parties
    # to depend on those
    symbols_dict = {}
    module_import = top_dir.split("/")[-1]
    # walk all the files looking for python files
    for root, dirs, files in tqdm(os.walk(top_dir)):
        _files = [f for f in files if f.endswith(".py")]
        for file in _files:
            file_name = os.path.join(root, file)
            import_name = file_path_to_import(
                "".join(file_name.rpartition(module_import)[1:])
            )
            data = jedi.Script(path=file_name).complete()
            symbols_from_script = {
                k.full_name: k.type
                for k in data
                if k.full_name and module_import + "." in k.full_name
            }

            # cull statements within functions and classes, which are not importable
            classes_and_functions = {
                k for k, v in symbols_from_script.items() if v in ["class", "function"]
            }
            for k in list(symbols_from_script):
                for cf in classes_and_functions:
                    if k != cf and k.startswith(cf) and k in symbols_from_script:
                        symbols_from_script.pop(k)

            symbols_dict[import_name] = set(symbols_from_script)

    symbols = set()
    # handle star imports, which don't usually get added but are valid symbols
    for k, v in symbols_dict.items():
        symbols.update(v)
        symbols.update({f"{k}.{vv.rsplit('.', 1)[-1]}" for vv in v})
    return symbols
