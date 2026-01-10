# Import des classes
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window

# import la la logique python (pour chaque page de l'app)

from Controllers.Template import AppScreen
from Controllers.Budget import BudgetScreen
from Controllers.Categorie import CategorieScreen
from Controllers.Transaction import TransacScreen
from Controllers.Dashboard import DashboardScreen



#--- CONFIGUER LA TAILLE DE L'ÉCRAN (MOBILE)---
#Window.size = (360, 640)
Window.size = (288, 640)



class MainApp(MDApp):
    def build(self):
        #--- CHARGER LES FICHIER .KV---
        #a. Charger le parrent d'abord !!

        Builder.load_file("Views/Template.kv")
        # 2. Charger les enfants
        Builder.load_file("Views/Budget_Screen.kv")
        Builder.load_file("Views/Categorie_Screen.kv")
        Builder.load_file("Views/Transac_Screen.kv")
        Builder.load_file("Views/Dashboard_Screen.kv")


        return AppScreen()


if __name__ == "__main__":
    MainApp().run()