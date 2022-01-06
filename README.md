# jinjagen

[jinjagen](jinjagen) is a short simple extensible Python script using `jinja2`
to generate files from source template files. I use this to generate simple
static websites.


## Usage

```
cd srcdir
jinjagen destdir
```

Filenames `XYZ.jinja` under `srcdir` generate files called `XYZ` under
`destdir`.
Any file or folder whose name starts with `.` or `_` is ignored.
You want to pair `jinja` with other tools to deal with files and folders that
are not jinja templates.
See [this example](example/) for my approach of using `rsync` and
`make`.

To hook in extra functionality from any Python module do:

```
cd srcdir
jinjagen -m a_python_module destdir
```
where `a_python_module` is the name of a Python module.

This package includes the module [jinjagenadd](jinjagenadd/__init__.py) which
can be used for some basic functionality and as an example of how to create
alternative modules.
For details and usage see [this example](example/).


## Install

```
python3 -m pip install git+https://github.com/castedo/jinjagen.git
```

