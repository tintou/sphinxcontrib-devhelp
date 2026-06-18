"""Test for devhelp extension."""

from __future__ import annotations

import gzip
import xml.etree.ElementTree as etree
from time import sleep
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from sphinx.application import Sphinx


@pytest.mark.sphinx('devhelp', testroot='basic')
def test_basic(app: Sphinx) -> None:
    app.builder.build_all()


@pytest.mark.sphinx('devhelp', testroot='basic', freshenv=True)
def test_keyword_types(app: Sphinx) -> None:
    app.builder.build_all()

    outdir = app.outdir
    basename = app.config.devhelp_basename
    xmlfile = outdir / f'{basename}.devhelp.gz'

    with gzip.open(str(xmlfile)) as f:
        tree = etree.parse(f)

    keywords = {
        kw.get('name'): kw.get('type')
        for kw in tree.getroot().find('functions').findall('keyword')
    }

    assert keywords.get('built-in function my_function()') == 'function'
    assert keywords.get('MyClass (built-in class)') == 'struct'
    assert keywords.get('MY_CONSTANT (built-in variable)') == 'id'
    assert keywords.get('my_attr (MyClass attribute)') == 'property'


@pytest.mark.sphinx('devhelp', testroot='basic', freshenv=True)
def test_basic_deterministic_build(app: Sphinx) -> None:
    app.config.devhelp_basename, output_filename = 'testing', 'testing.devhelp.gz'

    app.builder.build_all()
    output_initial = (app.outdir / output_filename).read_bytes()

    sleep(2)

    app.builder.build_all()
    output_repeat = (app.outdir / output_filename).read_bytes()

    msg = f"Content of '{output_filename}' differed between builds."
    assert output_repeat == output_initial, msg
