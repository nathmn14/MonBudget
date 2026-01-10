from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty, ColorProperty

class StatCard(MDBoxLayout):
    """Petit composant pour afficher Revenus/Dépenses côte à côte"""
    titre = StringProperty("")
    montant = StringProperty("")
    couleur_texte = ColorProperty([0, 0, 0, 1])

class ItemCategorie(MDBoxLayout):
    """Ligne de légende sous le graphique"""
    nom = StringProperty("")
    montant = StringProperty("")
    icone = StringProperty("")
    couleur_icone = ColorProperty([0, 0, 0, 1])

class SectionDepensesCategorie(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Données basées sur votre maquette [cite: 12, 13, 14, 15, 16, 17, 18, 19]
        self.donnees_categories = [
            {"nom": "Alimentation", "montant": "8 000 FC", "icone": "food", "valeur": 40, "color": [1, 0.4, 0.5, 1]},
            {"nom": "Transport", "montant": "5 000 FC", "icone": "car", "valeur": 25, "color": [0.2, 0.6, 0.9, 1]},
            {"nom": "Logement", "montant": "3 000 FC", "icone": "home", "valeur": 20, "color": [1, 0.8, 0.4, 1]},
            {"nom": "Loisirs", "montant": "2 000 FC", "icone": "cart", "valeur": 15, "color": [0.3, 0.8, 0.7, 1]},
        ]


class GraphiqueBarres(MDBoxLayout):
    """Composant pour le graphique à barres statique"""
    pass


class DashboardScreen(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Variable pour stocker le solde affiché dans le KV
        self.solde_actuel = "25 000 FC"