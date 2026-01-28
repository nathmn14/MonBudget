# Import des classes
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.screenmanager import MDScreenManager

# Import du gestionnaire de préférences
from utils.preferences import preferences_manager


# import la la logique python (pour chaque page de l'app)

from controllers.template import  AppScreen
from controllers.Connexion import LoginScreen
from controllers.Budget import BudgetScreen
from controllers.Categorie import CategorieScreen
from controllers.Transaction import TransacScreen
from controllers.dashboard import DashboardScreen
from controllers.parametre import ParametreScreen


# Database handlers (Now handled in Splash)
# from data.initialiser_bdd import init_database
# from data.connexion_bdd import init_default_user_and_account
# from models.categorie import CategorieModel


#--- CONFIGUER LA TAILLE DE L'ÉCRAN (MOBILE)---
#Window.size = (360, 640)  # Taille mobile standard
# La taille sera configurée depuis les préférences sauvegardées


class WindowManager(MDScreenManager):
    pass


class MainApp(MDApp):
    def build(self):
        # 1. Configurer le thème depuis les préférences sauvegardées
        saved_theme = preferences_manager.get_theme()
        self.theme_cls.theme_style = saved_theme
        
        # Configurer la taille de fenêtre
        Window.size = (360, 640)
        
        self.custom_colors = {
            "Light": {
                "bg_primary": [1, 1, 1, 1],
                "bg_secondary": [0.86, 0.86, 0.86, 1],
                "text": [0.1, 0.1, 0.1, 1],
                "accent": [0.1, 0.5, 0.8, 1],
            },
            "Dark": {
                "bg_primary": [0.13, 0.13, 0.13, 1],
                "bg_secondary": [0.08, 0.08, 0.08, 1],
                "text": [0.95, 0.95, 0.95, 1],
                "accent": [0.1, 0.5, 0.8, 1],
            },
        }

        #--- CHARGER LES FICHIER .KV---
        Builder.load_file("views/Dashboard_Screen.kv")
        Builder.load_file("views/Budget_Screen.kv")
        Builder.load_file("views/Categorie_Screen.kv")
        Builder.load_file("views/Transac_Screen.kv")
        Builder.load_file("views/Parametre_Screen.kv")
        Builder.load_file("views/Connexion.kv")
        Builder.load_file("views/Template.kv")

        sm = WindowManager()
        sm.add_widget(LoginScreen(name="login_screen"))
        sm.add_widget(AppScreen(name="app_screen"))

        return sm

    def notify(self, message, type="info"):
        """Fonction universelle appelable partout"""
        try:
            # On cherche l'écran 'app_screen' dans le ScreenManager (root)
            screen = self.root.get_screen('app_screen')
            if hasattr(screen, 'notifier'):
                screen.notifier(message, type)
        except: pass

    def on_stop(self):
        """Appelé quand l'application se ferme - sauvegarde les préférences"""
        # Sauvegarder le thème actuel
        current_theme = self.theme_cls.theme_style
        preferences_manager.set_theme(current_theme)
        print("Préférences sauvegardées")


if __name__ == "__main__":
    # Lancement immédiat de l'app. 
    # L'initialisation se fera sur la page de Splash pour éviter le freeze au démarrage.
    MainApp().run()
