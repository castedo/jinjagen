#!/usr/bin/python -t

import importlib, jinja2, os, shutil
from pathlib import Path


class JinjaGenerator:
    def __init__(self, source_dir_path):
        self.source = Path(source_dir_path)
        self._filesys = jinja2.FileSystemLoader(source_dir_path)
        self.env = jinja2.Environment(
            loader=jinja2.ChoiceLoader([self._filesys]),
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=["jinja2.ext.do"],
        )

    def render_file(self, tmpl_path, dest_path, ctx):
        tmpl = self.env.get_template(str(tmpl_path))
        tmpl.stream(**ctx).dump(str(dest_path), "utf-8")

    def render_dir(self, rel_path: Path, dest_root, ctx):
        rel_path = Path(rel_path)
        for entry in os.listdir(self.source / rel_path):
            if not entry.startswith((".", "_")):
                src_path = self.source / rel_path / entry
                if src_path.is_dir():
                    self.render_dir(rel_path / entry, dest_root, ctx)
                elif entry.endswith(".jinja"):
                    ctx = dict(ctx, this=self.site_ctx(rel_path))
                    dest_path = dest_root / rel_path / entry[:-6]
                    os.makedirs(dest_root / rel_path, exist_ok=True)
                    self.render_file(rel_path / entry, dest_path, ctx)
                else:
                    shutil.copy(src_path, dest_root / rel_path / entry)

    def render_site(self, dest_root, ctx=None):
        self.render_dir(".", dest_root, ctx if ctx else {})

    def site_ctx(self, rel_path):
        depth = len(rel_path.parents) - 1
        ret = {
            "filename": rel_path.name,
            "dirpath": str(rel_path.parent),
            "relroot": "../" * depth if depth > 0 else "./",
        }
        # when rel_path ends in "FOO/." we want path to also end in "FOO/."
        ret["path"] = "{}/{}".format(rel_path.parent, rel_path.name)
        return ret

    def hook_module(self, modname, subparam=""):
        m = importlib.import_module(modname)
        if hasattr(m, "jinjagen_hook"):
            m.jinjagen_hook(self, subparam)
        else:
            self.env.globals.update({modname: m})


def module_param(string):
    a = string.split(":", 1)
    return (a[0], a[1] if len(a) > 1 else None)


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="Generate files from Jinja templates")
    parser.add_argument("output", help="Path to ouput directory")
    parser.add_argument("-r", "--root", default=".", help="Source root")
    parser.add_argument("-m", "--module", default=[],
        dest="modules",
        action="append",
        type=module_param,
        metavar="MODULE_NAME[:SUBPARAM]",
        help="add globals from module or much more!",
    )
    args = parser.parse_args()
    gen = JinjaGenerator(args.root)
    for (modname, subparam) in args.modules:
        gen.hook_module(modname, subparam)
    gen.render_site(args.output)

