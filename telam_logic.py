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

import telam_api as telam
import sched, threading
import time, datetime

class Logic :

    def __init__(self, status_func, remain_func, update_gui_func):

        self.horarios = []
        self.proximo_descargar = None

        self.downloadingNow = False

        # self.actualizarValorDeHorarios()

        # minuto es que se realizara la descarga
        self.minute_time = int(telam.cfgInstance().get('main','minute_time'))

        self.status_func = status_func
        self.remain_func = remain_func
        self.update_gui_func = update_gui_func

        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.listener = self.scheduler.enter(1, 1, self.listenerHour, (self.scheduler,))

        # Start a thread to run the events
        self.t_stop = threading.Event()
        self.t = threading.Thread(target=self.scheduler.run)

    def startScheduler(self):
        self.t.start()

    def stopScheduler(self):
        self.t_stop.set()

    def obtenerConfiguraciones(self):
        cfg = telam.cfgInstance()
        return {
        'ouput_folder':cfg.get('main', 'ouput_folder'),
        'zara_file':cfg.get('main', 'zara_file')
        }

    def obtenerProximoDescargar(self):
        hora_actual = datetime.datetime.today().hour
        cfg_minuto = int(telam.cfgInstance().get('main','minute_time'))
        hora_proximo = None
        if len(self.horarios) > 1:
            for hora in self.horarios:
                minuto_actual = datetime.datetime.today().minute
                if hora_actual < hora :
                    hora_proximo = hora
                    break
                elif hora_actual == hora :
                    if minuto_actual < cfg_minuto:
                        hora_proximo = hora
                        break
        self.proximo_descargar = \
            hora_proximo if hora_proximo else self.horarios[0]
        # print 'proximo a descargar...', self.proximo_descargar
        self.status_func('Boletin proximo a descargar - %s Hs' % self.proximo_descargar)
        return self.proximo_descargar

    def actualizarValorDeHorarios(self):
        '''
        Cuando se agrega/quita un horario este guarda los
        cambios en el archivo de configuracion, y
        actualiza los valores cargados en RAM.
        '''
        self.horarios = telam.getHours()

    def almacenarHorarios(self, horarios):
        '''
        Guardad en el CFG los horarios pasados
        por parametro.
        Se asume que [horarios] ya viene en formato array.
        '''
        st_horarios = ''
        if len(horarios) > 0:
            st_horarios = ','.join([str(x) for x in horarios])
        telam.cfgInstance().set('main', st_horarios, 'hours')

    def actualizarRutaArchivoLSTZara(self, hora):
        '''
        Una vez descargado correctamente el boletin, este
        actualiza el archivo .lst respectivo en el ZaraRadio
        para referenciarlo con la ubicacion de descarga.
        '''
        zara_file = telam.cfgInstance().get('main','zara_file')
        ouput_file = telam.getOutputNameFile(hora)

        from mutagen.mp3 import MP3
        audio = MP3(ouput_file)
        file_length = str(audio.info.length).replace('.','')

        file_content = '[playlist]\nfile0=%s\nlength0=%s\nnumberofentries=1\nnextindex=0' % \
            (ouput_file, file_length)

        _f = open(zara_file, 'w')
        _f.write(file_content)
        _f.close()
        return True

    def limpiarArchivoZara(self):
        zara_file = telam.cfgInstance().get('main','zara_file')
        file_content = '[playlist]\nfile0=\nlength0=\nnumberofentries=0\nnextindex=0'
        _f = open(zara_file, 'w')
        _f.write(file_content)
        _f.close()

    def __internet_on():
        ''' Return True if internet conecttion is conected. '''
        import urllib2
        try:
            response=urllib2.urlopen('http://www.google.com')
            return True
        except urllib2.URLError as err: pass
        return False

    def __getRemainTime(self, limit_time, now_time):
        t1 = str(limit_time)
        t2 = str(now_time)
        FMT = '%H:%M:%S'
        tdelta = datetime.datetime.strptime(t1, FMT) - datetime.datetime.strptime(t2, FMT)
        hours, remainder = divmod(tdelta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '%s:%s:%s' % (hours, minutes, seconds)

    def listenerHour(self, sc):
        limit_time = datetime.time(self.proximo_descargar,self.minute_time,00)
        t = datetime.datetime.today().time()
        now_time = datetime.time(t.hour,t.minute,t.second)
        isTheTime = now_time == limit_time
        #print now_time , limit_time, (not self.downloadingNow) and isTheTime
        self.remain_func(self.__getRemainTime(limit_time, now_time))

        if (not self.downloadingNow) and isTheTime:
            self.downloadingNow = True
            self.status_func('Iniciando la descarga del boletin de las <%s>' % self.proximo_descargar)
            # print 'por descargar horaria de las <%s>...' % self.proximo_descargar
            result = telam.downloadBoletin(str(self.proximo_descargar))
            if result:
                self.status_func('Descarga del boletin de las <%s> completado correctamente' % self.proximo_descargar)
                self.actualizarRutaArchivoLSTZara(self.proximo_descargar)
            else:
                self.limpiarArchivoZara()
                self.status_func('NO se pudo descarga el boletin de las <%s> :(' % self.proximo_descargar)
            self.obtenerProximoDescargar()
            self.update_gui_func()
            self.downloadingNow = False
            # print 'horaria proxima a descargar >>> <%s>...' % self.proximo_descargar

        sc.enter(1, 1, self.listenerHour, (sc,))

    def establecerUbicacionDescarga(self, path_dir):
        telam.cfgInstance().set('main', path_dir, 'ouput_folder')

    def establecerArchivoZara(self, path_file):
        telam.cfgInstance().set('main', path_file, 'zara_file')

    def convertPath(self, path):
        import os, os.path
        """Convierte el path a el específico de la plataforma (separador)"""
        if os.name == 'posix':
            return "/"+apply( os.path.join, tuple(path.split('/')))
        elif os.name == 'nt':
            return apply( os.path.join, tuple(path.split('/')))

def pprint(t):
    print t

# l = Logic(pprint)
# l.actualizarValorDeHorarios()
# l.obtenerProximoDescargar()
# l.actualizarRutaArchivoLSTZara(str(14))

