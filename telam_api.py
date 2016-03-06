#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Copyright 2013 Ferreyra, Jonathan <jalejandroferreyra@gmail.com>
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

import config
import os.path

cfg = config.Configurations()
url = cfg.get('main', 'main_url')
host = cfg.get('main', 'host')
frag = cfg.get('main', 'frag')


def cfgInstance():
    return cfg

def getHours():
    value = cfg.get('main', 'hours')
    value = [int(hour) for hour in value.split(',')]
    value.sort()
    return value

def getContentPage():
    import urllib2
    try:
        usock = urllib2.urlopen(url)
        data = usock.read()
        usock.close()

        chars =  list(data)
        _all = u''
        for uno in chars:
            try:
                _all += unicode(uno,'utf-8')
            except:
                pass
        return _all
    except :
        return ''

def getLines():
    _all = getContentPage()
    lines = _all.split('\n')
    return [line.strip() for line in lines if line.find(frag) != -1]

def parseLinesGetMP3Urls():
    lines = getLines()
    result = {}
    to_find = "Boletin "
    for line in lines:
        values = line.split(',')
        idx_text = values[0].find(to_find)
        inicio = idx_text + len(to_find)
        name_file = values[0][idx_text:-1]
        hora = values[0][inicio : inicio + 2]
        url = values[1].replace("'",'').strip()
        result[hora] = {'url':url, 'name_file':name_file}
    return result


def downloadFile(folder,*lista):
    def __downloadState(bloque, tamano_bloque, tamano_total):
        cant_descargada = bloque * tamano_bloque
        print "Cantidad descargada: %s Bytes de %s Bytes totales" % (cant_descargada, tamano_total)

    import urllib
    # *lista = lista de links de internet desde donde se
    # descargaran los archivos

    for link in lista:
        output = link [link.rfind('/')+1 : ]
        output = os.path.join(folder,output)
        print link, output
        try:
            archivo = urllib.urlretrieve(link, output, reporthook=__downloadState)
        except Exception, e:
            #TODO:buscar nombre excepcion
            print "Error en la descarga: ",e,"  ."
            return False
    print ">> Datos descargados correctamente.\n"
    return True

def getUrl(hora):
    return os.path.join(host,urls[str(hora)]['url'])

def getOutputNameFile(hora):
    outputFolder = cfg.get('main', 'ouput_folder')
    return os.path.join(outputFolder,urls[str(hora)]['name_file'] + '.mp3')

def getDownloadNameFile(hora):
    outputFolder = cfg.get('main', 'ouput_folder')
    return os.path.join(outputFolder,os.path.split(urls[str(hora)]['url'])[1])

def downloadBoletin(hora):
    outputFolder = cfg.get('main', 'ouput_folder')
    result = downloadFile(outputFolder, getUrl(hora))
    if result:
        from os import rename
        rename(getDownloadNameFile(hora),getOutputNameFile(hora))
    #     print 'perfect!!!'
    # else:
    #     print 'NOT perfect!!!'
    return result

urls = parseLinesGetMP3Urls()