#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © University of Oxford
# Author
# Name: Gary Ballantine
# Email: gary.ballantine at it.ox.ac.uk
# GitHub: AltMeta

"""
list files in the specified path, performs regex and Version checking
The highest version is returned as file
"""

import re, os
from distutils.version import LooseVersion
from autopkglib import Processor, ProcessorError

__all__ = ["FSFileProvider"]

class FSFileProvider(Processor):
    input_variables = {
            're_pattern': {
                'description': 'Regular expression (Python) to match against.',
                'required': True,

                },
            'path': {
                'description': 'provide the afs path',
                'required': True,
                },
            'result_output_var_name': {
                'description': 'desc',
                'required': False,
                'default': 'match',
                },
            'mangle_dmg_iso_filenames': {
                'description': 'Currently, the DmgCopier tries to look inside paths ending .dmg or .iso; setting this flag will change the output filename from file.iso to file.i?o and file.dmg to file.d?g which works around this',
                'required': False,
                'default': 'False',
                },
            }

    output_variables = {
            'result_output_var_name': {
                'description': 'desc',
                },
            }	

    def get_path_and_search(self, path, re_pattern):
        match_pattern = re.compile(re_pattern)
        try:
            software = os.listdir(path)
        except OSError:
            raise ProcessorError('Error Messages will get better with time'(path, re_pattern))
        highestver = ""
        finalmatch = None
        for x in software:
            match = re.match(match_pattern, x)
            if match:
                if highestver == "" or LooseVersion(x) > LooseVersion(highestver):
                    highestver = x
                    finalmatch = match
        if finalmatch:
            return (finalmatch.group(finalmatch.lastindex or 0), finalmatch.groupdict())
        else:
            raise ProcessorError('The regular expression \'%s\' does not match any file in path \'%s\'' % (re_pattern, path))

    def main(self):
        output_var_name = self.env['result_output_var_name']

        if 'path' in self.env:
            path = self.env['path']
        if 're_pattern' in self.env:
            re_pattern = self.env['re_pattern']

        groupmatch, groupdict = self.get_path_and_search(path,re_pattern)

        if output_var_name not in groupdict.keys():
            groupdict[output_var_name] = groupmatch

        self.output('Mangle: %s' % self.env['mangle_dmg_iso_filenames'])
        self.output_variables = {}
        for key in groupdict.keys():
            self.env[key] = groupdict[key]
            self.output('Found matching text (%s): %s' % (key, self.env[key], ))
            if self.env['mangle_dmg_iso_filenames'] == True and key == 'file':
                self.env[key] = re.sub('iso$', 'i?o', self.env[key], flags=re.I)
                self.env[key] = re.sub('dmg$', 'd?g', self.env[key], flags=re.I)
                self.output('Updated: matching text (%s): %s' % (key, self.env[key], ))

            self.output_variables[key] = {
                    'description': 'Matched regular expression group'}


if __name__ == '__main__':
    PROCESSOR = FSFileProvider()
