import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtCore import QUrl, QPoint
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaMetaData

import pyqtgraph as pg
import numpy as np

class AudioPlayer(QMainWindow):
    def __init__(self):
        super(AudioPlayer, self).__init__()
        loadUi('gui_audio_player.ui', self)

        #Variables
        self.clic_position = QPoint()
        self.estado = True
        self.play_lista = []
        self.posicion = 0
        self.indice = ""
        self.num = 0

        #Botones
        self.btn_buscar.clicked.connect(self.abrir_archivo)
        self.btn_pausar.hide()
        self.btn_bajvol.hide()
        self.btn_subvol.hide()
        self.btn_reproducir.setEnabled(False)

        # Objeto Player
        self.player = QMediaPlayer()
        self.player.setVolume(50)

        #Control sliders y botones de musica
        self.slider_tiempo.sliderMoved.connect(lambda x: self.player.setPosition(x))
        self.slider_volumen.valueChanged.connect(self.variar_volumen)
        self.player.positionChanged.connect(self.posicion_cancion)
        self.player.durationChanged.connect(self.duracion_cancion)
        self.player.stateChanged.connect(self.estado_tiempo)

        #Control barra titulos
        self.btn_minimizar.clicked.connect(lambda :self.showMinimized())
        self.btn_cerrar.clicked.connect(lambda :self.close())

        #Control de musica
        self.btn_reproducir.clicked.connect(self.reproducir_musica)
        self.btn_pausar.clicked.connect(self.pausar_musica)
        self.btn_ant.clicked.connect(self.retroceder_cancion)
        self.btn_sig.clicked.connect(self.adelantar_cancion)

        self.list_musica.doubleClicked.connect(self.reproducir_musica)
        self.list_musica.clicked.connect(self.seleccion_canciones)

        #Eliminar barra y titulo - opacidad
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(0.95)

        #Sizegrip
        self.gripSize = 10
        self.grip = QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)

        #mover ventana
        #self.frame_superior.mouseMoveEvent = self.mover_ventana

        #grafica
        self.graphWidget = pg.PlotWidget(title = 'SPECTRUM')
        self.grafica_layout.addWidget(self.graphWidget)
        self.espectrum_grafica()
        self.update_datos()

    #Funcion que limpia la lista y el arreglo antes de abrir archivos nuevos
    def abrir_archivo(self):
        if len(self.play_lista) > 0:
            self.play_lista.clear()
            self.list_musica.clear()
            self.btn_reproducir.setEnabled(False)

        archivo = QFileDialog()
        archivo.setFileMode(QFileDialog.ExistingFiles)
        nombres, _ = archivo.getOpenFileNames(self, 'Abrir Archivos de Audio', filter='Audio Files (*.mp3 *.m4a *.wav)')

        if nombres:
            self.musica = nombres
            self.dir = '/'.join(self.musica[0].split('/')[:-1])  # Obtener la carpeta del primer archivo
            nombres_musica = [n.split('/')[-1] for n in nombres]  # Obtener solo los nombres de archivo

            # Agregar nombres de archivo a la lista
            for nombre in nombres_musica:
                item = QListWidgetItem(nombre)
                self.list_musica.addItem(item)

    def reproducir_musica(self):
        if not self.estado:
            self.estado = True
            self.btn_reproducir.hide()
            self.btn_pausar.show()

            if self.list_musica.currentRow() >= 0:
                # Obtener la información de la canción seleccionada
                path = self.list_musica.currentItem().text()
                cancion_x = f'{self.dir}/{path}'

                # print(cancion_x)
                # Crear la URL y la contenido multimedia
                url = QUrl.fromLocalFile(cancion_x)
                content = QMediaContent(url)

                # Configurar la música en el reproductor
                self.player.setMedia(content)
                self.player.setPosition(self.posicion)
                self.play_lista.append(path)

                # Mantener la lista de reproducción con un máximo de 2 elementos
                if len(self.play_lista) > 2:
                    self.play_lista.pop(0)

                # Reiniciar la posición si la canción seleccionada no es la misma que la primera en la lista
                if self.list_musica.currentItem().text() != self.play_lista[0]:
                    self.posicion = 0
                    self.player.setPosition(self.posicion)

                # Reproducir la música
                self.player.play()
        else:
            self.pausar_musica()
            self.estado = False

    #Funciona para obtener informacion de la cancion y mostrarla en los label
    def metadata_cancion(self):
        if self.player.isMetaDataAvailable():
            titulo = self.player.metaData(QMediaMetaData.Title)
            artista = self.player.metaData(QMediaMetaData.AlbumArtist)
            genero = self.player.metaData(QMediaMetaData.Genre)
            anio = self.player.metaData(QMediaMetaData.Year)

            self.lbl_titulo.setText(f'TITULO: {titulo}')
            self.lbl_artista.setText(f'ARTISTA: {artista}')
            self.lbl_genero.setText(f'GENERO: {genero}')
            self.lbl_anio.setText(f'AÑO: {anio}')

    #Pausa la musica
    def pausar_musica(self):
        if self.estado:
            self.estado = False
            self.player.pause()
            self.posicion = self.player.position()
            self.btn_reproducir.show()
            self.btn_pausar.hide()

    #Seleccion de cancion en el Qlista
    def seleccion_canciones(self):
        self.estado = True
        self.btn_reproducir.show()
        self.btn_pausar.hide()
        self.btn_reproducir.setEnabled(True)

    #Adelanta la cancion incrementando en 1 el indice de fila la lista
    def adelantar_cancion(self):
        try:

            nueva_fila = self.list_musica.currentRow() + 1
            if nueva_fila < self.list_musica.count():
                self.list_musica.setCurrentRow(nueva_fila)
                self.reproducir_musica()
            else:
                print("Ya estás en la última canción.")
        except AttributeError:
            pass

    #Retrocede la cancion reduciendo en 1 el indice de fila
    def retroceder_cancion(self):
        try:
            nueva_fila = self.list_musica.currentRow() - 1
            if nueva_fila < self.list_musica.count():
                self.list_musica.setCurrentRow(nueva_fila)
                self.reproducir_musica()
            else:
                print("Ya estás en la primera canción.")
        except AttributeError:
            pass

    #Se verifica el tiempo de la cancion y el estado para mostrar o esconder el boton de reproducir y pausar
    def estado_tiempo(self, estado):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.btn_reproducir.hide()
            self.btn_pausar.show()
            self.estado = True
        else:
            self.btn_reproducir.show()
            self.btn_pausar.hide()
            self.estado = False
        if self.player.position() == self.player.duration() and not self.player.position()==0:
            try:
                self.estado = True
                self.lista_musica.setCurrentRow(self.indice+1)
                self.reproducir_musica()
            except :
                pass

    #Actualiza el tiempo de duracion de la cancion
    def duracion_cancion(self, t):
        self.slider_tiempo.setRange(0, t)
        m, s = (divmod(t*0.001, 60))
        self.indicador_tiempo.setText(str(f'{int(m)}:{int(s)}'))

    #Actualiza tiempo actual de la cancion
    def posicion_cancion(self, t):
        self.slider_tiempo.setValue(t)
        m, s = divmod(t*0.001, 60)
        self.indicador_posicion.setText(str(f'{int(m)}:{int(s)}'))

    def variar_volumen(self, valor):
        self.player.setVolume(valor)
        self.lbl_volumen.setText(str(valor))
        if valor == 0:
            self.btn_sil.show()
            self.btn_bajvol.hide()
            self.btn_subvol.hide()
        elif valor > 0 and valor < 50:
            self.btn_sil.hide()
            self.btn_bajvol.show()
            self.btn_subvol.hide()
        elif valor >= 50:
            self.btn_sil.hide()
            self.btn_bajvol.hide()
            self.btn_subvol.show()

    #Funcion para la grafica espectral (utiliza numeros aleatorios)
    def espectrum_grafica(self):
        x = np.linspace(0, 100,10)
        self.data = np.random.normal(size=(10,100))

        self.curva = self.graphWidget.plot(x, np.sin(x),symbol='o',
            color= '#1a5fb4', pen = '#1a5fb4', width = 2, brush ='g',
            symbolBrush= '#1a5fb4',symbolPen='#1a5fb4', symbolSize=10)
        self.graphWidget.hideAxis('left')
        self.graphWidget.hideAxis('bottom')

    #Actualizacion de los labels y la grafica spectrum constantemente
    def update_datos(self):
        self.metadata_cancion()
        self.curva.setData(self.data[self.num%10])
        if self.num == 0:
            self.graphWidget.enableAutoRange('xy', False)
        self.num +=1
        QtCore.QTimer.singleShot(100, self.update_datos)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mi_app = AudioPlayer()
    mi_app.show()
    sys.exit(app.exec_())
