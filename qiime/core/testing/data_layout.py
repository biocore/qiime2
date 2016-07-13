# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

import collections
import os
import os.path

from qiime.plugin import FileFormat, DataLayout

###############################################################################
#
# int-sequence:
#
#     A sequence of integers stored in a single file. Since this is a sequence,
#     the integers have an order and repetition of elements is allowed.
#
###############################################################################


class IntSequenceFormat(FileFormat):
    name = 'int-sequence'

    @classmethod
    def sniff(cls, filepath):
        with open(filepath, 'r') as fh:
            for line, _ in zip(fh, range(5)):
                try:
                    int(line.rstrip('\n'))
                except (TypeError, ValueError):
                    return False
            return True

int_sequence_data_layout = DataLayout('int-sequence', 1)
int_sequence_data_layout.register_file('ints.txt', IntSequenceFormat)


def int_sequence_to_list(data_dir):
    with open(os.path.join(data_dir, 'ints.txt'), 'r') as fh:
        view = []
        for line in fh:
            view.append(int(line.rstrip('\n')))
        return view


def list_to_int_sequence(view, data_dir):
    with open(os.path.join(data_dir, 'ints.txt'), 'w') as fh:
        for int_ in view:
            fh.write('%d\n' % int_)


# There isn't a writer for collections.Counter to int-sequence because the view
# is lossy (doesn't preserve order).
def int_sequence_to_counter(data_dir):
    list_view = int_sequence_to_list(data_dir)
    return collections.Counter(list_view)


###############################################################################
#
# mapping:
#
#     A mapping of keys to values stored in a single TSV file. Since this is a
#     mapping, key-value pairs do not have an order and duplicate keys are
#     disallowed.
#
###############################################################################

class MappingFormat(FileFormat):
    name = 'mapping'

    @classmethod
    def sniff(cls, filepath):
        with open(filepath, 'r') as fh:
            for line, _ in zip(fh, range(5)):
                cells = line.rstrip('\n').split('\t')
                if len(cells) != 2:
                    return False
            return True

mapping_data_layout = DataLayout('mapping', 1)
mapping_data_layout.register_file('mapping.tsv', MappingFormat)


def mapping_to_dict(data_dir):
    with open(os.path.join(data_dir, 'mapping.tsv'), 'r') as fh:
        view = {}
        for line in fh:
            key, value = line.rstrip('\n').split('\t')
            if key in view:
                raise ValueError(
                    "mapping.txt file must have unique keys. Key %r was "
                    "observed more than once." % key)
            view[key] = value
        return view


def dict_to_mapping(view, data_dir):
    with open(os.path.join(data_dir, 'mapping.tsv'), 'w') as fh:
        for key, value in view.items():
            fh.write('%s\t%s\n' % (key, value))


###############################################################################
#
# four-ints:
#
#     A sequence of exactly four integers stored across multiple files, some of
#     which are in a nested directory. Each file contains a single integer.
#     Since this is a sequence, the integers have an order (corresponding to
#     filename) and repetition of elements is allowed.
#
###############################################################################

class SingleIntFormat(FileFormat):
    name = 'single-int'

    @classmethod
    def sniff(cls, filepath):
        with open(filepath, 'r') as fh:
            try:
                int(fh.readline().rstrip('\n'))
            except (TypeError, ValueError):
                return False
            return True

four_ints_data_layout = DataLayout('four-ints', 1)
four_ints_data_layout.register_file('file1.txt', SingleIntFormat)
four_ints_data_layout.register_file('file2.txt', SingleIntFormat)
four_ints_data_layout.register_file('nested/file3.txt', SingleIntFormat)
four_ints_data_layout.register_file('nested/file4.txt', SingleIntFormat)


def four_ints_to_list(data_dir):
    view = []
    view.append(_read_single_int(os.path.join(data_dir, 'file1.txt')))
    view.append(_read_single_int(os.path.join(data_dir, 'file2.txt')))

    nested_dir = os.path.join(data_dir, 'nested')
    view.append(_read_single_int(os.path.join(nested_dir, 'file3.txt')))
    view.append(_read_single_int(os.path.join(nested_dir, 'file4.txt')))
    return view


def _read_single_int(filepath):
    with open(filepath, 'r') as fh:
        line, _ = fh.read().split('\n')
        return int(line)


def list_to_four_ints(view, data_dir):
    if len(view) != 4:
        raise ValueError(
            "four-ints only supports writing exactly four integers.")

    _write_single_int(view[0], os.path.join(data_dir, 'file1.txt'))
    _write_single_int(view[1], os.path.join(data_dir, 'file2.txt'))

    nested_dir = os.path.join(data_dir, 'nested')
    os.mkdir(nested_dir)
    _write_single_int(view[2], os.path.join(nested_dir, 'file3.txt'))
    _write_single_int(view[3], os.path.join(nested_dir, 'file4.txt'))


def _write_single_int(int_, filepath):
    with open(filepath, 'w') as fh:
        fh.write('%d\n' % int_)
