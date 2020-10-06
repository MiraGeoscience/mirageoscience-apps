#
# mirageoscience-apps documentation build configuration file, created by
# sphinx-quickstart on Tue Sep 16 16:41:10 2014.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# on_rtd is whether we are on readthedocs.org
import os
import sys
import shutil


sys.path.append(os.path.abspath("./_ext"))
sys.path.append(os.path.abspath(".."))
sys.path.append(os.path.abspath("../apps"))

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('.'))

# -- General configuration ------------------------------------------------
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.githubpages",
    "numpydoc",
    "sphinx_issues",
    "nbsphinx",
    "jupyter_sphinx",
]

nbsphinx_prolog = r"""
.. raw:: html

    <script src='http://cdnjs.cloudflare.com/ajax/libs/require.js/2.1.10/require.min.js'></script>
    <script>require=requirejs;</script>
"""

# Autosummary pages will be generated by sphinx-autogen instead of sphinx-build
autosummary_generate = []

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = True
napoleon_use_param = False
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_custom_sections = None
numpydoc_show_class_members = False
numpydoc_class_members_toctree = False


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "geoapps"

# The short X.Y version.
version = "0.2.0"
# The full version, including alpha/beta/rc tags.
release = "0.2.0"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "AUTHORS.rst", "table_*", "**.ipynb_checkpoints"]

linkcheck_ignore = []
linkcheck_retries = 3
linkcheck_timeout = 2000

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# API doc options
# apidoc_module_dir = "../mirageoscience-apps"
# apidoc_output_dir = "content/api/generated"
# apidoc_toc_file = False
# apidoc_excluded_paths = []
# apidoc_separate_modules = True

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False

# -- Edit on Github Extension ---------------------------------------------

edit_on_github_branch = "master"
edit_on_github_project = "mirageoscience/mirageoscience-apps"
edit_on_github_directory = "docs"

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None
html_theme = "alabaster"

# otherwise, readthedocs.org uses their theme by default, so no need to specify it

# html_theme = 'default'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
# html_theme_options = {
#   'display_github': 'True',
# }

# html_logo = 'images/mirageoscience-apps.png'

check_meta = False

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
# html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = "gpg.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
# html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = False

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = "mirageoscience-apps Documentation"

numfig = True
# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        "index",
        "mirageoscience-apps Documentation.tex",
        "mirageoscience-apps Documentation",
        "MiraGeoscience",
        "manual",
    )
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (
        "index",
        "mirageoscience-apps Documentation",
        "mirageoscience-apps Documentation",
        ["MiraGeoscience"],
        1,
    )
]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "mirageoscience-apps Documentation",
        "mirageoscience-apps Documentation",
        "MiraGeoscience",
        "mirageoscience-apps",
        "API for geoh5 database and Geoscience ANALYST.",
        "Miscellaneous",
    )
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {"http://docs.python.org/": None}


# -- User Defined Methods ------------------------------------------------
sys.path.append(os.getcwd())

# from _ext import edit_on_github
# from _ext import copyImages, supress_nonlocal_image_warn, make_lectures_page

# copyImages()

# -- Strip all notebooks before


# def clean_state():
#     # get relevant directories
#     cwd = os.getcwd()
#
#     # search for images that have been missed
#     for root, dirList, fileList in os.walk(cwd):
#         if "Workspace" not in root:
#             for filename in fileList:
#                 if "ipynb" in filename:
#                     os.system("nbstripout " + os.path.join(root, filename))
#                 if ".geoh5" in filename:
#                     os.remove(os.path.join(root, filename))
#
#
# clean_state()
# print("Copy example notebooks into docs/_examples")


# def all_but_ipynb(dir, contents):
#     result = []
#     for c in contents:
#         if os.path.isfile(os.path.join(dir, c)) and (not c.endswith(".ipynb")):
#             result += [c]
#     return result


# project_root = os.getcwd()
# shutil.rmtree(os.path.join(project_root, "content/_examples"), ignore_errors=True)
# shutil.copytree(
#     os.path.join(project_root, "../geoapps"),
#     os.path.join(project_root, "content/_examples"),
# )

# TODO: build the source
# sphinx-apidoc --templatedir templates/ -o content/api/ ../mirageoscience-apps
