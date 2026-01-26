from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, ColorProperty, NumericProperty
from kivy.animation import Animation
from kivy.clock import Clock
from kivymd.uix.card import MDCard
from kivy.metrics import dp

from kivy.lang import Builder

class TopNotification(MDCard):
    text = StringProperty("")
    icon = StringProperty("information")
    bg_color = ColorProperty([0.1, 0.5, 0.8, 1])

class AppScreen(MDScreen):
    title = StringProperty("Titre par défaut")
    subtitle = StringProperty("Sous-titre par défaut")

    def notifier(self, message, type="info"):
        """
        Affiche une notification en haut de l'écran
        type: 'info', 'success', 'error'
        """
        notif = self.ids.top_notif
        notif.text = message
        
        # Couleurs très distinctes
        if type == "success":
            notif.bg_color = [0, 0.7, 0.1, 1] # Vert vif
            notif.icon = "check-circle"
        elif type == "error":
            notif.bg_color = [0.9, 0, 0, 1] # Rouge vif
            notif.icon = "alert-circle"
        else:
            notif.bg_color = [0.1, 0.5, 0.8, 1] # Bleu
            notif.icon = "information"
            
        # Animation : Glisser vers le bas depuis le haut avec un effet de rebond
        anim = Animation(pos_hint={"center_x": 0.5, "top": 0.98}, duration=0.6, t='out_bounce')
        anim.start(notif)
        
        # Disparaître après 3.5 secondes
        Clock.schedule_once(lambda dt: self.cacher_notification(), 3.5)

    def cacher_notification(self, *args):
        notif = self.ids.top_notif
        # Animation : Remonter vers le haut
        anim = Animation(pos_hint={"center_x": 0.5, "top": 1.5}, duration=0.5, t='in_back')
        anim.start(notif)
