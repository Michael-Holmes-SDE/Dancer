import os  
import json
import pygame
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QHBoxLayout, QPushButton, QSlider, QGraphicsDropShadowEffect
from PyQt5.QtGui import QMovie, QIntValidator
from PyQt5.QtCore import Qt


SETTINGS_FILE = os.path.join('config', 'settings.json')

def save_settings(self):
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
    else:
        settings = {
            'config': {
                'current_gif': '',
                'gifs_folder': 'GIFs',
                'music_folder': 'music',
            },
            'gifs': {}
        }

    # Update config settings
    settings['config']['current_gif'] = os.path.relpath(self.current_gif)
    settings['config']['gifs_folder'] = self.gifs_folder
    settings['config']['music_folder'] = self.music_folder

    # Save settings for the current GIF
    gif_path = os.path.relpath(self.current_gif)
    settings['gifs'][gif_path] = {
        'gif_speed': self.gif_speed,
        'music': {
            'current_song': os.path.relpath(self.current_song),
            'music_enabled': self.music_enabled,
        },
        'window': {
            'transparency': self.transparency,
            'shadow': self.shadow,
        },
    }

    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def load_settings(self):
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            config_settings = settings.get('config', {})
            self.gifs_folder = config_settings.get('gifs_folder', 'GIFs')
            self.current_gif = os.path.normpath(config_settings.get('current_gif', os.path.join(self.gifs_folder, 'default.gif')))
            self.music_folder = config_settings.get('music_folder', 'music')
    else:
        self.gifs_folder = 'GIFs'
        self.current_gif = os.path.join(self_gifs_folder, 'default.gif')
        self.music_folder = 'music'
    load_gif_settings(self) 

def load_gif_settings(self):
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            gif_settings = settings.get('gifs', {}).get(os.path.relpath(self.current_gif), {})
            self.gif_speed = gif_settings.get('gif_speed', 100)
            music_settings = gif_settings.get('music', {})
            self.current_song = os.path.normpath(music_settings.get('current_song', os.path.join(self.music_folder, 'default.mp3')))
            self.music_enabled = music_settings.get('music_enabled', True)
            window_settings = gif_settings.get('window', {})
            self.transparency = window_settings.get('transparency', 0)
            self.shadow = window_settings.get('shadow', 0)
    else:
        self.gif_speed = 100
        self.current_song = os.path.join(self.music_folder, 'default.mp3')
        self.music_enabled = True
        self.transparency = 0
        self.shadow = 0

def apply_settings(self):
    self.set_transparency()
    self.set_shadow()


class BaseSelectionDialog(QDialog):
    def __init__(self, title, folder, current_item, file_extension, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.folder = folder
        self.current_item = os.path.basename(current_item) if current_item else None
        self.file_extension = file_extension

        main_layout = QVBoxLayout()
        content_layout = QHBoxLayout()

        self.list_widget = QListWidget()
        files = [f for f in os.listdir(self.folder) if f.endswith(self.file_extension)]
        for file in files:
            item = QListWidgetItem(file)
            self.list_widget.addItem(item)

        content_layout.addWidget(self.list_widget)

        self.preview_label = QLabel()
        content_layout.addWidget(self.preview_label)

        main_layout.addLayout(content_layout)

        self.button = QPushButton('OK')
        self.button.clicked.connect(self.accept)
        main_layout.addWidget(self.button)

        self.setLayout(main_layout)

        self.list_widget.currentItemChanged.connect(self.update_preview)

        # Set the current item if provided
        if self.current_item:
            items = self.list_widget.findItems(self.current_item, Qt.MatchExactly)
            if items:
                self.list_widget.setCurrentItem(items[0])

    def update_preview(self, current):
        raise NotImplementedError("Subclasses should implement this method")

    def get_selected_item(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return None

    def closeEvent(self, event):
        raise NotImplementedError("Subclasses should implement this method")
    
class GifSelectionDialog(BaseSelectionDialog):
    def __init__(self, dancer):
        super().__init__('Select GIF', dancer.gifs_folder, dancer.current_gif, '.gif', dancer)

    def update_preview(self, current):
        if current:
            gif_path = os.path.join(self.folder, current.text())
            movie = QMovie(gif_path)
            self.preview_label.setMovie(movie)
            movie.start()
        else:
            self.preview_label.clear()

    def closeEvent(self, event):
        event.accept()

class SongSelectionDialog(BaseSelectionDialog):
    def __init__(self, dancer):
        super().__init__('Select song', dancer.music_folder, dancer.current_song, '.mp3', dancer)
        self.dancer = dancer

    def update_preview(self, current):
        if current:
            music_path = os.path.join(self.folder, current.text())
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play()
        else:
            self.preview_label.clear()

    def closeEvent(self, event):
        pygame.mixer.music.stop()
        self.dancer.play_song(self.dancer.current_song)
        event.accept()




from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QSpinBox
from PyQt5.QtCore import Qt

class BaseSliderDialog(QDialog):
    def __init__(self, title, min_value, max_value, current_value, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_value)
        self.slider.setMaximum(max_value)
        self.slider.setValue(current_value)
        self.original_value = current_value
        self.slider.valueChanged.connect(self.update_value_from_slider)

        self.value_spinbox = QSpinBox()
        self.value_spinbox.setMinimum(min_value)
        self.value_spinbox.setMaximum(max_value)
        self.value_spinbox.setValue(current_value)
        self.value_spinbox.valueChanged.connect(self.update_value_from_spinbox)

        main_layout = QVBoxLayout()
        slider_layout = QHBoxLayout()

        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.value_spinbox)

        main_layout.addLayout(slider_layout)

        self.button = QPushButton('OK')
        self.button.clicked.connect(self.accept)
        main_layout.addWidget(self.button)

        self.setLayout(main_layout)

    def update_value_from_slider(self, value):
        self.value_spinbox.setValue(value)
        self.apply_value(value)

    def update_value_from_spinbox(self, value):
        self.slider.setValue(value)
        self.apply_value(value)

    def closeEvent(self, event):
        self.apply_value(self.original_value)

    def apply_value(self, value):
        raise NotImplementedError("Subclasses should implement this method")
    
    
class TransparencySliderDialog(BaseSliderDialog):
    def __init__(self, dancer):
        super().__init__('Adjust Transparency (%)', 0, 100, dancer.transparency, dancer)
        self.dancer = dancer

    def apply_value(self, value):
        self.dancer.setWindowOpacity((100 - value) / 100)

class ShadowSliderDialog(BaseSliderDialog):
    def __init__(self, dancer):
        super().__init__('Adjust Shadow', 0, 100, dancer.shadow, dancer)
        self.dancer = dancer

    def apply_value(self, value):
        if value > 0:
            self.dancer.shadow = value
            shadow_float = value / 100
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(shadow_float)
            shadow.setColor(Qt.black)
            offset = value / 10
            shadow.setOffset(offset, offset)
            self.dancer.setGraphicsEffect(shadow)
        else:
            self.dancer.setGraphicsEffect(None)
            self.dancer.shadow = 0
        self.dancer.update()  # Reapply the effect # TEST

class GifSpeedSliderDialog(BaseSliderDialog):
    def __init__(self, dancer):
        super().__init__('Adjust GIF Speed (%)', 50, 150, dancer.gif_speed, dancer)
        self.dancer = dancer

    def apply_value(self, value):
        self.dancer.set_gif_speed(value)