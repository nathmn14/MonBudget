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


# Import de la base de donnees

from data.initialiser_bdd import init_database
from data.connexion_bdd import init_default_user_and_account
from models.categorie import CategorieModel
from models.parametre import ParametreModel


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
        
        # Configurer la taille de fenêtre depuis les préférences
        saved_size = preferences_manager.get_window_size()
        Window.size = tuple(saved_size)
        
        # Forcer la taille mobile si nécessaire
        if Window.size != (360, 640):
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
        # 2. Charger les enfants
        Builder.load_file("views/Dashboard_Screen.kv")
        Builder.load_file("views/Budget_Screen.kv")
        Builder.load_file("views/Categorie_Screen.kv")
        Builder.load_file("views/Transac_Screen.kv")
        Builder.load_file("views/Parametre_Screen.kv")


        #a. Charger le parrent d'abord !!
        Builder.load_file("views/Connexion.kv")
        Builder.load_file("views/Template.kv")

        sm = WindowManager()
        sm.add_widget(LoginScreen(name="login_screen"))
        sm.add_widget(AppScreen(name="app_screen"))


        return sm

    def notify(self, message, type="info"):
        """Fonction universelle appelable partout"""
        # On récupère l'instance du template
        screen = self.root.get_screen('app_screen')
        screen.notifier(message, type)

    def on_stop(self):
        """Appelé quand l'application se ferme - sauvegarde les préférences"""
        # Forcer la taille mobile avant de sauvegarder
        Window.size = (360, 640)
        
        # Sauvegarder la taille actuelle de la fenêtre
        current_size = list(Window.size)
        preferences_manager.set_window_size(current_size[0], current_size[1])
        
        # Sauvegarder le thème actuel
        current_theme = self.theme_cls.theme_style
        preferences_manager.set_theme(current_theme)
        
        print("Préférences sauvegardées avec succès")


if __name__ == "__main__":

    # 1. Creation de la base donnees si elle n'existe pas
    init_database()

    print("🗄️  Base de donnees initialisee avec succes.")

    # 2. Création de l'utilisateur et du compte par défaut
    init_default_user_and_account()
    
    print("👤 Utilisateur et compte par defaut crees.")
    
    # 3. Création des catégories par défaut
    CategorieModel.init_default_categories()
    
    print("📂 Categories par defaut initialisees.")

    # 4. lancement de l'application 
    MainApp().run()
