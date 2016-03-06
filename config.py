#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Copyright 2011 Jonathan Ferreyra <jalejandroferreyra@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import ConfigParser
import pathtools
import os

class Configurations :

    empty_cfg = '''\
[main]
main_url = http://www.telam.com.ar/multimedia/audios/programa/1/
host = http://www.telam.com.ar/
frag = ajax_player_audio_destacado('Boletin
minute_time = 50
ouput_folder = 
hours = 
zara_file = 
last_downloaded = '''
    
    def __init__(self):
        self._cfgFile = pathtools.convertPath(
            pathtools.getPathProgramFolder() + '/config.cfg')
        self._config = ConfigParser.RawConfigParser()
        self._config.read(self._cfgFile)
        if not os.path.exists(self._cfgFile) :
            cfg = open(self._cfgFile,'w')
            cfg.write(self.empty_cfg)
            cfg.close()
                    
    def get(self, section, key):
        return self._config.get(section, key)

    def set(self, section, key, value):
        self._config.set(section,value,key)
        self._config.write(open(self._cfgFile,'w'))
        return True
