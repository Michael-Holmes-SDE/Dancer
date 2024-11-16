import json
import sys
import os
import pygame
from PyQt5.QtWidgets import QApplication, QGraphicsDropShadowEffect, QLabel, QMainWindow, QInputDialog, QDialog
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QPoint
from tray_icon import create_tray_icon, update_tray_menu
from utils import apply_settings, load_settings, load_gif_settings, save_settings, GifSelectionDialog, SongSelectionDialog, TransparencySliderDialog, ShadowSliderDialog, GifSpeedSliderDialog

class Dancer(QMainWindow):
    ###### Init block
    def __init__(self):
        super().__init__()
        self.moving = False
        self.hide = False
        self.offset = QPoint()
        self.init_pygame_mixer()
        load_settings(self)
        self.initUI()
        create_tray_icon(self)

    def init_pygame_mixer(self):
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"Error initializing pygame mixer: {e}")
            self.music_enabled = False

    def initUI(self):
        self.label = QLabel(self)
        self.setCentralWidget(self.label)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 300, 300)
        apply_settings(self) # Apply saved transparency and shadow settings
        self.play_gif(self.current_gif)
        self.show()

    ###### End Init block

    ####### Music block
    def play_song(self, music_path):
        if self.music_enabled:
            if not os.path.exists(music_path):
                return
            self.current_song = music_path
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)  # Loop the music indefinitely
            # Restart the gif to sync with the music
            self.movie.stop()
            self.movie.start()
        else:
            pygame.mixer.music.stop()

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        self.play_song(self.current_song)
        update_tray_menu(self)
        save_settings(self)
        self.tray_icon.menu = self.tray_menu

    ####### End Music block


    ####### Hide block
    def toggle_hide(self):
        self.hide = not self.hide
        self.set_hidden()
        update_tray_menu(self)
        self.tray_icon.menu = self.tray_menu

    def set_hidden(self):
        if self.hide:
            self.showMinimized()
        else:
            self.showNormal()

    ####### End Hide block

    ####### Transparent block
    def toggle_transparent(self):
        self.transparent = not self.transparent
        self.set_transparency()
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.show()
        update_tray_menu(self)
        self.tray_icon.menu = self.tray_menu

    def change_transparency(self):
        dialog = TransparencySliderDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.transparency = dialog.slider.value()
            self.set_transparency()

    def set_transparency(self):
        self.setWindowOpacity((100 - self.transparency) / 100)
        save_settings(self)


    ####### End Transparent block

    ####### Shadow block
    def change_shadow(self):
        dialog = ShadowSliderDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.shadow = dialog.slider.value()
            print(f"Setting value for Shadow: {self.shadow}")  # Debugging
            self.set_shadow()

    def set_shadow(self):
        if self.shadow > 0:
            shadow_float = self.shadow / 100
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(shadow_float)
            shadow.setColor(Qt.black)
            offset = self.shadow / 10
            shadow.setOffset(offset, offset)
            self.setGraphicsEffect(shadow)
        else:
            self.setGraphicsEffect(None)
        save_settings(self)
        self.update() # TEST, Reapply the effect

    ####### End Shadow block

    ####### Window order block
    def always_on_top(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.show()
        update_tray_menu(self)
        self.tray_icon.menu = self.tray_menu

    def always_below(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint)
        self.show()
        update_tray_menu(self)
        self.tray_icon.menu = self.tray_menu

    def normal_window(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.show()
        update_tray_menu(self)
        self.tray_icon.menu = self.tray_menu

    ####### End Window order block

    ####### GIF block
    def play_gif(self, gif_path):
        if not os.path.exists(gif_path):
            print(f"GIF path does not exist: {gif_path}")  # Debugging
            return
        self.current_gif = gif_path
        load_gif_settings(self) # Load settings for the GIF
        apply_settings(self) # Apply saved transparency and shadow settings
        self.movie = QMovie(gif_path)
        if not self.movie.isValid():
            print(f"Invalid GIF file: {gif_path}")  # Debugging
            return
        self.movie.setSpeed(self.gif_speed)
        self.label.setMovie(self.movie)
        self.movie.start()
        music_path = self.current_song
        self.play_song(music_path)

    def change_gif(self):
        dialog = GifSelectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            gif_name = dialog.get_selected_item()
            if gif_name:
                gif_path = os.path.join(self.gifs_folder, gif_name)
                if os.path.exists(gif_path):
                    self.play_gif(gif_path)
                    save_settings(self)

    def set_gif_speed(self, speed):
        self.gif_speed = speed
        if hasattr(self, 'movie'):
            self.movie.setSpeed(speed)
        save_settings(self)

    def change_gif_speed(self):
        dialog = GifSpeedSliderDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            speed = dialog.slider.value()
            self.set_gif_speed(speed)
        

    ####### End GIF block

    ####### Change song block
    def change_song_dialog(self):
        dialog = SongSelectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            music_name = dialog.get_selected_item()
            if music_name:
                self.change_song(music_name)

    def change_song(self, music_name):
        music_path = os.path.join(self.music_folder, music_name)
        if os.path.exists(music_path):
            self.play_song(music_path)
            save_settings(self)

    ####### End Change song block

    ####### Bottom block
    def quit(self):
        save_settings(self)
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.close()
        QApplication.quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.moving:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dancer = Dancer()
    sys.exit(app.exec_())