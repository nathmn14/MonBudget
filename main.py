# Import des classes
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.screenmanager import MDScreenManager
# import la la logique python (pour chaque page de l'app)

from Controllers.Template import  AppScreen
from Controllers.Connexion import LoginScreen
from Controllers.Budget import BudgetScreen
from Controllers.Categorie import CategorieScreen
from Controllers.Transaction import TransacScreen
from Controllers.dashboard import DashboardScreen
from Controllers.parametre import ParametreScreen


# Import de la base de donnees

from data.initialiser_bdd import init_database
from data.connexion_bdd import init_default_user_and_account
from models.categorie import CategorieModel
from models.parametre import ParametreModel


#--- CONFIGUER LA TAILLE DE L'ÉCRAN (MOBILE)---
#Window.size = (360, 640)
Window.size = (288, 640)


class WindowManager(MDScreenManager):
    pass


class MainApp(MDApp):
    def build(self):
        # 1. Configurer le thème d'abord
        self.theme_cls.theme_style = "Light"  # ou Dark
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
        Builder.load_file("Views/Dashboard_Screen.kv")
        Builder.load_file("Views/Budget_Screen.kv")
        Builder.load_file("Views/Categorie_Screen.kv")
        Builder.load_file("Views/Transac_Screen.kv")
        Builder.load_file("Views/Parametre_Screen.kv")


        #a. Charger le parrent d'abord !!
        Builder.load_file("Views/Connexion.kv")
        Builder.load_file("Views/Template.kv")

        sm = WindowManager()
        sm.add_widget(LoginScreen(name="login_screen"))
        sm.add_widget(AppScreen(name="app_screen"))


        return sm

    def notify(self, message, type="info"):
        """Fonction universelle appelable partout"""
        # On récupère l'instance du template
        screen = self.root.get_screen('app_screen')
        screen.notifier(message, type)


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