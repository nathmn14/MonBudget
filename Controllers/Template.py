from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty

class AppScreen(MDScreen):
    title = StringProperty("Titre par défaut")
    subtilte = StringProperty("Sous-titre par défaut")

    pass
