# Import des classes
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import DictProperty

# import la la logique python (pour chaque page de l'app)

from Controllers.Template import AppScreen
from Controllers.Budget import BudgetScreen
from Controllers.Categorie import CategorieScreen
from Controllers.Transaction import TransacScreen
from Controllers.Dashboard import DashboardScreen
from  Controllers.Parametre import ParametreScreen


#--- CONFIGUER LA TAILLE DE L'ÉCRAN (MOBILE)---
#Window.size = (360, 640)
Window.size = (288, 640)



class MainApp(MDApp):
    # Définir les couleurs et les thèmes (Dictionnaire contenant vos couleurs personnalisées)
    custom_colors = DictProperty({
        "Light": {
            "bg_primary": (1, 1, 1, 1),  # Blanc pur
            "bg_secondary": (0.9, 0.9, 0.9, 1),  # Gris très clair (#F5F5F5)
            "text": (0.13, 0.13, 0.13, 1),  # Noir doux (#212121)
            "accent": (0.12, 0.53, 0.9, 1)  # Bleu accent (#1E88E5)
        },
        "Dark": {
            "bg_primary": (0.12, 0.12, 0.12, 1),  # Noir profond (#121212)
            "bg_secondary": (0.07, 0.07, 0.07, 1),  # Gris foncé (#1E1E1E)
            "text": (0.88, 0.88, 0.88, 1),  # Blanc cassé (#E0E0E0)
            "accent": (0.12, 0.53, 0.9, 1)  # Bleu clair (#90CAF9)
        }
    })

    def build(self):
        #--- CHARGER LES FICHIER .KV---
        #1. Charger le parrent d'abord !!
        Builder.load_file("Views/Template.kv")
        # 2. Charger les enfants
        Builder.load_file("Views/Budget_Screen.kv")
        Builder.load_file("Views/Categorie_Screen.kv")
        Builder.load_file("Views/Transac_Screen.kv")
        Builder.load_file("Views/Dashboard_Screen.kv")
        Builder.load_file("Views/Parametre_Screen.kv")

        self.theme_cls.theme_style = "Light"  # Style par défaut

        return AppScreen()


if __name__ == "__main__":
    MainApp().run()