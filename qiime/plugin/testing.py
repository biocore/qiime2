# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pkg_resources
import tempfile
import unittest
import shutil
import pathlib

import qiime

from qiime.plugin.model import DirectoryFormat
from qiime.plugin.model.base import FormatBase


# TODO Split out into more specific subclasses if necessary.
class TestPluginBase(unittest.TestCase):
    package = None
    test_dir_prefix = 'qiime2-plugin'

    def setUp(self):
        try:
            package = self.package.split('.')[0]
        except AttributeError:
            self.fail('Test class must have a package property.')

        # plugins are keyed by their names, so a search inside the plugin
        # object is required to match to the correct plugin
        plugin = None
        for name, plugin_ in qiime.sdk.PluginManager().plugins.items():
            if plugin_.package == package:
                plugin = plugin_

        if plugin is not None:
            self.plugin = plugin
        else:
            self.fail('%s is not a registered QIIME 2 plugin.' % package)

        # TODO use qiime temp dir when ported to framework, and when the
        # configurable temp dir exists
        self.temp_dir = tempfile.TemporaryDirectory(
            prefix='%s-test-temp-' % self.test_dir_prefix)

    def tearDown(self):
        self.temp_dir.cleanup()

    def get_data_path(self, filename):
        return pkg_resources.resource_filename(self.package,
                                               'data/%s' % filename)

    def get_transformer(self, from_type, to_type):
        try:
            transformer_record = self.plugin.transformers[from_type, to_type]
        except KeyError:
            self.fail(
                "Could not find registered transformer from %r to %r." %
                (from_type, to_type))

        return transformer_record.transformer

    def assertRegisteredSemanticType(self, semantic_type):
        try:
            semantic_type_record = self.plugin.types[semantic_type.name]
        except KeyError:
            self.fail(
                "Semantic type %r is not registered on the plugin." %
                semantic_type)

        obs_semantic_type = semantic_type_record.semantic_type

        self.assertEqual(obs_semantic_type, semantic_type)

    def assertSemanticTypeRegisteredToFormat(self, semantic_type, exp_format):
        obs_format = None
        for type_format_record in self.plugin.type_formats:
            if type_format_record.type_expression == semantic_type:
                obs_format = type_format_record.format
                break

        self.assertIsNotNone(
            obs_format,
            "Semantic type %r is not registered to a format." % semantic_type)

        self.assertEqual(
            obs_format, exp_format,
            "Expected semantic type %r to be registered to format %r, not %r."
            % (semantic_type, exp_format, obs_format))

    def transform_format(self, source_format, target, **kwargs):
        # Guard any non-QIIME2 Format sources from being tested
        self.assertTrue(issubclass(source_format, FormatBase))

        transformer = self.get_transformer(source_format, target)

        source_path = None
        if 'filename' in kwargs:
            source_path = kwargs['filename']
        elif 'filenames' in kwargs:
            source_path = self.temp_dir.name
            for filename in kwargs['filenames']:
                filepath = self.get_data_path(filename)
                shutil.copy(filepath, source_path)
        else:
            self.fail("The helper method `transform_format` requires either "
                      "a filename or a sequence of filenames supplied as their"
                      " respective keyword arguments.")
        input = source_format(source_path, mode='r')

        obs = transformer(input)

        if issubclass(target, DirectoryFormat):
            self.assertTrue(type(obs) in (pathlib.Path, str) or
                            issubclass(type(obs), DirectoryFormat))
        else:
            self.assertIsInstance(obs, target)

        return input, obs
