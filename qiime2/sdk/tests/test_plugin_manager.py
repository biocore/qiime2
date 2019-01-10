# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import qiime2.plugin
import qiime2.sdk
from qiime2.plugin.plugin import SemanticTypeRecord, FormatRecord

from qiime2.core.testing.type import (IntSequence1, IntSequence2, Mapping,
                                      FourInts, Kennel, Dog, Cat, SingleInt)
from qiime2.core.testing.format import (IntSequenceDirectoryFormat,
                                        MappingDirectoryFormat,
                                        IntSequenceV2DirectoryFormat,
                                        IntSequenceFormatV2,
                                        FourIntsDirectoryFormat,
                                        IntSequenceFormat,
                                        RedundantSingleIntDirectoryFormat)
from qiime2.core.testing.util import get_dummy_plugin


class TestPluginManager(unittest.TestCase):
    def setUp(self):
        self.plugin = get_dummy_plugin()
        # PluginManager is a singleton so there's no issue creating it again.
        self.pm = qiime2.sdk.PluginManager()

    def test_plugins(self):
        plugins = self.pm.plugins

        exp = {'dummy-plugin': self.plugin}
        self.assertEqual(plugins, exp)

    def test_semantic_types(self):
        types = self.pm.semantic_types

        exp = {
            'IntSequence1': SemanticTypeRecord(semantic_type=IntSequence1,
                                               plugin=self.plugin),
            'IntSequence2': SemanticTypeRecord(semantic_type=IntSequence2,
                                               plugin=self.plugin),
            'Mapping': SemanticTypeRecord(semantic_type=Mapping,
                                          plugin=self.plugin),
            'FourInts': SemanticTypeRecord(semantic_type=FourInts,
                                           plugin=self.plugin),
            'Kennel': SemanticTypeRecord(semantic_type=Kennel,
                                         plugin=self.plugin),
            'Dog': SemanticTypeRecord(semantic_type=Dog,
                                      plugin=self.plugin),
            'Cat': SemanticTypeRecord(semantic_type=Cat,
                                      plugin=self.plugin),
            'SingleInt': SemanticTypeRecord(semantic_type=SingleInt,
                                            plugin=self.plugin)
        }

        self.assertEqual(types, exp)

    def test_importable_types(self):
        types = self.pm.importable_types

        exp = {IntSequence1, IntSequence2, FourInts, Mapping, Kennel[Dog],
               Kennel[Cat], SingleInt}
        self.assertEqual(types, exp)

    # TODO: add tests for type/directory/transformer registrations

    def test_importable_formats(self):
        obs = self.pm.importable_formats
        exp = {
            'IntSequenceDirectoryFormat':
                FormatRecord(format=IntSequenceDirectoryFormat,
                             plugin=self.plugin),
            'MappingDirectoryFormat':
                FormatRecord(format=MappingDirectoryFormat,
                             plugin=self.plugin),
            'IntSequenceV2DirectoryFormat':
                FormatRecord(format=IntSequenceV2DirectoryFormat,
                             plugin=self.plugin),
            'IntSequenceFormatV2':
                FormatRecord(format=IntSequenceFormatV2,
                             plugin=self.plugin),
            'FourIntsDirectoryFormat':
                FormatRecord(format=FourIntsDirectoryFormat,
                             plugin=self.plugin),
            'IntSequenceFormat':
                FormatRecord(format=IntSequenceFormat,
                             plugin=self.plugin),
            'RedundantSingleIntDirectoryFormat':
                FormatRecord(format=RedundantSingleIntDirectoryFormat,
                             plugin=self.plugin)
        }
        self.assertEqual(obs, exp)

    def test_importable_formats_excludes_unimportables(self):
        obs = self.pm.importable_formats
        self.assertNotIn('UnimportableFormat', obs)
        self.assertNotIn('UnimportableDirectoryFormat', obs)

        obs = self.pm.formats
        self.assertIn('UnimportableFormat', obs)
        self.assertIn('UnimportableDirectoryFormat', obs)


if __name__ == '__main__':
    unittest.main()
