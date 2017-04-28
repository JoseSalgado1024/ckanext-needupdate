"""Tests for plugin.py."""
import ckanext.needupdate.plugin as plugin


def test_plugin():
    plugin.plugins.unload('needupdate')
