# conf.py
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

# Project information
project = "Streamlit Rich Message History"
copyright = "2025, Ethan Christensen"
author = "Ethan Christensen"
release = "0.1.4"

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "myst_parser",
]

# Templates
templates_path = ["_templates"]
exclude_patterns = []

# HTML output
html_theme = "furo"
html_static_path = ["_static"]

# Auto-document special members
autodoc_default_options = {
    "members": True,
    "special-members": "__init__",
    "undoc-members": True,
    "show-inheritance": True,
}

# Support Markdown
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
