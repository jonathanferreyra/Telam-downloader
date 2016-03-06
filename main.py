#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Copyright 2011 Ferreyra, Jonathan <jalejandroferreyra@gmail.com>
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

import os,sys, datetime
from PyQt4 import QtCore, QtGui, uic
from telam_logic import Logic

APP_TITLE = "Telam downloader"

class TelamGUI(QtGui.QMainWindow):

    def __init__(self, parent = None):
        FILENAME = 'main.ui'
        QtGui.QMainWindow.__init__(self)
        uifile = self.__getAbsolutePath(FILENAME)
        uic.loadUi(uifile, self)

        self.__centerOnScreen()
        self.__connectSignalsCheckboxs()
        self.lbLogo.setPixmap(QtGui.QPixmap(self.__getAbsolutePath('logo.png')))
        self.setWindowIcon(QtGui.QIcon(self.__getAbsolutePath("logo_fixed.png")))

        self.parent = parent
        self.logic = Logic(
                self.agregarSucesoAlHistorial,
                self.mostrarTiempoRestanteDescarga,
                self.mostrar_proximo_boletin_descargar)

        self.logic.actualizarValorDeHorarios()
        self.proximo_descargar = None

        self.mostrar_proximo_boletin_descargar()
        self.seleccionarChecksHorariosActuales()
        self.cargarEnGUIValoresGuardados()
        self.logic.startScheduler()

    def __getAbsolutePath(self, FILENAME):
        return os.path.join(os.path.abspath(os.path.dirname(__file__)),FILENAME)

    def __centerOnScreen (self):
        '''Centers the window on the screen.'''
        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def __connectSignalsCheckboxs(self):
        hs = [0,1,2,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
        for hora in hs:
            self.__dict__['checkBox_%s' % hora].clicked.connect(
                self.almacenarHorariosSeleccionados)

    @QtCore.pyqtSlot(bool)
    def on_checkBox_23_clicked(self , value):
        pass

    @QtCore.pyqtSlot()
    def on_btExaminarUD_clicked(self):
        # UD = ubicacion descarga
        path = QtGui.QFileDialog.getExistingDirectory(self, u'Seleccione la ubicación de descarga')
        path = unicode(path.toUtf8(), 'utf-8')
        path = self.logic.convertPath(path)
        self.logic.establecerUbicacionDescarga(path)
        self.leUbicacionDescarga.setText(path)

    @QtCore.pyqtSlot()
    def on_btExaminarULST_clicked(self):
        # ULST = ubicacion archivo .lst
        path = QtGui.QFileDialog.getOpenFileName(self, 'Seleccione el archivo de evento ZaraRadio')
        path = unicode(path.toUtf8(), 'utf-8')
        path = self.logic.convertPath(path)
        self.logic.establecerArchivoZara(path)
        self.leUbicacionLST.setText(path)

    @QtCore.pyqtSlot()
    def on_btAcercaDe_clicked(self):
        from acercade import AcercaDe
        w = AcercaDe()
        w.exec_()

    @QtCore.pyqtSlot()
    def on_btSalir_clicked(self):
        #self.logic.stopScheduler()
        self.close()
        sys.exit(0)

###############################################################################

    def agregarSucesoAlHistorial(self, message):
        _time = datetime.datetime.today().strftime('%H:%M:%S')
        self.teLog.append(_time + '  ' + message)
        print _time, message

    def mostrarTiempoRestanteDescarga(self, st_time):
        if st_time != '0:0:0':
            self.lbTiempoRestante.setText(st_time)
        else:
            self.lbTiempoRestante.setText("Descarga en curso...")
        QtGui.QApplication.processEvents()

    def seleccionarChecksHorariosActuales(self):
        for hora in self.logic.horarios:
            self.__dict__['checkBox_%s' % hora].setChecked(True)

    def obtenerHorariosSelecccionados(self):
        horarios = []
        hs = [0,1,2,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
        for hora in hs:
            if self.__dict__['checkBox_%s' % hora].isChecked():
                horarios.append(hora)
        return horarios

    def almacenarHorariosSeleccionados(self):

        horarios = self.obtenerHorariosSelecccionados()
        self.logic.almacenarHorarios(horarios)
        self.logic.actualizarValorDeHorarios()
        self.mostrar_proximo_boletin_descargar()

        self.agregarSucesoAlHistorial('Nuevo(s) horario(s) indicado(s) almacenado')

    def cargarEnGUIValoresGuardados(self):
        cfgs = self.logic.obtenerConfiguraciones()
        self.leUbicacionDescarga.setText(cfgs['ouput_folder'])
        self.leUbicacionLST.setText(cfgs['zara_file'])

    def mostrar_proximo_boletin_descargar(self):
        self.proximo_descargar = self.logic.obtenerProximoDescargar()
        hoy = datetime.datetime.today()
        if hoy.hour > self.proximo_descargar:
            hoy = hoy + datetime.timedelta(days=1)
        _text = "Boletin %s horas %s-%s" % (self.proximo_descargar, hoy.day, self.get_name_month(hoy.month))
        self.lbProximoDescargar.setText(_text)

    def get_name_month(self, num_month):
        return {
            1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',
            7:'Jul',8:'Ago',9:'Sep',10:'Oct',11:'Nov',12:'Dic'
        }[num_month]

###############################################################################

def internet_on():
    ''' Return True if internet conecttion is conected. '''
    import urllib2
    try:
        response=urllib2.urlopen('http://www.google.com')
        return True
    # except urllib2.URLError as err: pass
    except : pass
    return False


###############################################################################

def main():
    app = QtGui.QApplication(sys.argv)
    window = TelamGUI()
    if internet_on():
        print 'conexion a internet OK!'
        window.show()
    else:
        print 'conexion a internet ERROR!'
        QtGui.QMessageBox.warning(None, APP_TITLE,
        "No se encuentra conectado a Internet. El programa se iniciará en modo DESHABILITADO.")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
