import os
from PyQt5.QtCore import Qt
from pystray import Icon as TrayIcon, Menu as TrayMenu, MenuItem as TrayMenuItem
from PIL import Image

def create_tray_icon(self):
    icon_path = os.path.join('config', 'icon.png')
    if not os.path.exists(icon_path):
        print("icon.png not found")
        return

    image = Image.open(icon_path)
    update_tray_menu(self)
    self.tray_icon = TrayIcon("Dancer", image, "Dancer", self.tray_menu)
    self.tray_icon.run()

def update_tray_menu(self):
    self.hide_menu_item = TrayMenuItem(
        'Show' if self.hide else 'Hide', self.toggle_hide)
    self.music_menu_item = TrayMenuItem(
        'Turn Music Off' if self.music_enabled else 'Turn Music On', self.toggle_music)
    self.gif_speed_menu_item = TrayMenuItem('GIF Speed Control', self.change_gif_speed)
    self.always_on_top_item = TrayMenuItem('Always on Top', self.always_on_top, checked=lambda _: bool(self.windowFlags() & Qt.WindowStaysOnTopHint))
    self.always_below_item = TrayMenuItem('Always Below', self.always_below, checked=lambda _: bool(self.windowFlags() & Qt.WindowStaysOnBottomHint))
    self.normal_item = TrayMenuItem('Normal', self.normal_window, checked=lambda _: not (self.windowFlags() & (Qt.WindowStaysOnTopHint | Qt.WindowStaysOnBottomHint)))
    self.tray_menu = TrayMenu(
        self.hide_menu_item,
        TrayMenuItem('Transparency', self.change_transparency),
        TrayMenuItem('Shadow', self.change_shadow),
        self.music_menu_item,
        TrayMenu.SEPARATOR,
        self.gif_speed_menu_item,
        TrayMenu.SEPARATOR,
        self.always_on_top_item,
        self.always_below_item,
        self.normal_item,
        TrayMenu.SEPARATOR,
        TrayMenuItem('Change GIF', self.change_gif),
        TrayMenuItem('Change Music', self.change_song_dialog),
        TrayMenu.SEPARATOR,
        TrayMenuItem('Quit', self.quit)
    )