#!/usr/bin/python -t

import importlib, jinja2, os, shutil
from pathlib import Path


class JinjaGeneratorCore:
    def __init__(self, source_dir_path):
        self.source = Path(source_dir_path)
        self._filesys = jinja2.FileSystemLoader(source_dir_path)
        self.env = jinja2.Environment(
            loader=jinja2.ChoiceLoader([self._filesys]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            extensions=["jinja2.ext.do"],
        )

    def render_file(self, tmpl_subpath, dest_filepath, ctx=dict()):
        tmpl = self.env.get_template(str(tmpl_subpath))
        tmpl.stream(**ctx).dump(str(dest_filepath), "utf-8")

    def hook_module(self, modname, subparam=""):
        m = importlib.import_module(modname)
        if hasattr(m, "jinjagen_hook"):
            m.jinjagen_hook(self, subparam)
        else:
            self.env.globals.update({modname: m})

    def get_exported(self, file_path):
        """Get variables and macros of template, but without compiling
        template blocks"""

        tmpl_path = file_path.relative_to(self.source)
        t = self.env.get_template(str(tmpl_path))
        # create context WITHOUT template blocks
        ctx = jinja2.runtime.new_context(t.environment, t.name, blocks={})
        # need to run render function to calc exported
        list(t.root_render_func(ctx))
        return ctx.get_exported()


class JinjaGenerator(JinjaGeneratorCore):
    def __init__(self, source_dir_path, dest_dir_path):
        super().__init__(source_dir_path)
        self.dest = Path(dest_dir_path)

    def gen_file(self, src_subpath, dest_subpath=None, ctx=dict()):
        if dest_subpath is None:
            dest_subpath = self.dest / Path(src_subpath).stem
        os.makedirs(self.dest / dest_subpath.parent, exist_ok=True)
        ctx = dict(ctx, this=self.site_ctx(dest_subpath))
        self.render_file(src_subpath, self.dest / dest_subpath, ctx)
        return self.dest / dest_subpath

    def gen_site(self):
        self.gen_dir(Path(), dict())

    def gen_dir(self, subpath, ctx=dict()):
        for entry in os.listdir(self.source / subpath):
            if not entry.startswith((".", "_")):
                src_path = self.source / subpath / entry
                if src_path.is_dir():
                    self.gen_dir(subpath / entry, ctx)
                elif entry.endswith(".jinja"):
                    self.gen_file(subpath / entry, subpath / entry[:-6], ctx)
                else:
                    os.makedirs(self.dest / subpath, exist_ok=True)
                    shutil.copy(src_path, self.dest / subpath / entry)

    def site_ctx(self, subpath):
        depth = len(subpath.parents) - 1
        ret = {
            "filename": subpath.name,
            "dirpath": str(subpath.parent),
            "relroot": "../" * depth if depth > 0 else "./",
        }
        # when subpath ends in "FOO/." we want path to also end in "FOO/."
        ret["path"] = "{}/{}".format(subpath.parent, subpath.name)
        return ret


def module_param(string):
    a = string.split(":", 1)
    return (a[0], a[1] if len(a) > 1 else None)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Generate files from Jinja templates")
    parser.add_argument("output", help="Path to ouput directory")
    parser.add_argument("-r", "--root", default=".", help="Source root")
    parser.add_argument(
        "-m",
        "--module",
        default=[],
        dest="modules",
        action="append",
        type=module_param,
        metavar="MODULE_NAME[:SUBPARAM]",
        help="add globals from module or much more!",
    )
    args = parser.parse_args()
    gen = JinjaGenerator(args.root, args.output)
    for (modname, subparam) in args.modules:
        gen.hook_module(modname, subparam)
    gen.gen_site()
