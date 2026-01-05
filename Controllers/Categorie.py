# --- IMPORTATION ---
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import StringProperty, ColorProperty
# WIDGET
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog,BaseDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView


# ==================================================================================================================
# A. MODÈLE DE WIDGET : Categorie_Card
# ==================================================================================================================
class Categorie_Card(MDCard):
    # Déclaration de mes variables de classe
    nom = StringProperty('')
    icon = StringProperty('')
    couleur = ColorProperty([1, 1, 1, 1])

    #Création d'un dictionnaire avec des catégories prédéfinie. nom : icon, couleur (rgba)
    dictionnaire_cat = {
        'Alimentation': ['food', (0.18, 0.8, 0.44, 1)],  # Vert émeraude
        'Transport': ['car', (0.2, 0.6, 0.86, 1)],  # Bleu belize
        'Logement': ['home', (0.9, 0.5, 0.13, 1)],  # Orange carotte
        'Loisirs': ['controller-classic', (0.6, 0.3, 0.7, 1)],  # Violet
        'Courses': ['cart', (0.1, 0.7, 0.7, 1)],  # Turquoise / Turquoise foncé
        'Telephone': ['phone-settings', (0.5, 0.5, 0.5, 1)],  # Gris béton
        'Café': ['coffee', (0.44, 0.26, 0.13, 1)],  # aBrun café
        'Salaire': ['cash-multiple', (0.15, 0.68, 0.37, 1)],  # Vert financier
        'Cadeaux': ['gift', (0.9, 0.3, 0.23, 1)],  # Rouge doux
        'Cinéma': ['movie', (0.2, 0.2, 0.2, 1)],  # Anthracite
        'Etudes': ['school', (0.12, 0.5, 0.7, 1)],  # Bleu marine doux
        'Santé': ['medical-bag', (0.95, 0.2, 0.4, 1)], # Rose/Rouge médical

        # Nouvelles catégories ajoutées pour correspondre au répertoire
        'Business': ['trending-up', (0.1, 0.3, 0.5, 1)],  # Bleu pétrole
        'Énergie': ['lightning-bolt', (1, 0.8, 0.2, 1)],  # Jaune ambre (SNEL/Internet)
        'Éducation': ['book-open-variant', (0.5, 0.4, 0.3, 1)]  # Marron terre (Frais scolaires)
    }

    # Fonction pour supprimer une catégorie (icon poubelle)
    def supprimer_categorie(self):
        self.parent.remove_widget(self)





# =============================================================================================================
# B. PAGE PRINCIPALE : CategorieScreen
#==============================================================================================================
#    Rôle : Affichage des catégories et boutons pour l'ajout
# =============================================================================================================
class CategorieScreen(MDBoxLayout):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.afficher_categories)       ## On demande à Kivy d'exécuter la fonction juste après l'initialisation

    # --- Affichage dynamique des catégories ---
    def afficher_categories(self, dt=None):     #La fonction on_enter s'exécute à chaque fois que vous arrivez sur l'écran.
        self.ids.box_categories.clear_widgets()     #Effacer la liste précédente .Si vous quittez l'écran "Catégories" et que vous y revenez, votre boucle for va s'exécuter à nouveau et rajouter toute la liste à la suite de l'ancienne.

        for nom, style in Categorie_Card.dictionnaire_cat.items():
            self.ids.box_categories.add_widget(
                Categorie_Card(
                    nom=nom,
                    icon=style[0],
                    couleur=style[1],
                )
            )


    # --- CRÉATION DE NOTRE BOITE DE DIALOGUE POUR AJOUTER UNE CATÉGORIE ---
    dialog= None
    couleur=ColorProperty([0.2, 0.2, 0.2, 1])
    def ouvrir_dialogue(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title='Ajouter une Catégorie',
                type='custom',
                content_cls=Factory.Contenu_Dialog(),
                buttons=[
                    MDRaisedButton(
                        text='Annuler',
                        on_release= self.fermer_dialogue,
                    ),
                    MDRaisedButton(
                        text='Ajouter',
                        on_release= self.ajouter_categorie,
                    )
                ],

            )
            self.dialog.open()

    # --- FERMER LA BOITE DE DIALOGUE ---
    def fermer_dialogue(self, *args):
        self.dialog.dismiss()
        self.dialog=None


    # --- AJOUTER UNE NOUVELLE CATÉGORIE ---
    def ajouter_categorie(self,*args):
        contenu_dialog=self.dialog.content_cls
        nom=contenu_dialog.ids.nom_categorie.text.strip()
        Couleur = contenu_dialog.couleur
        icone = contenu_dialog.icon_choisie  # <--- On récupère l'icône choisie !

        if not nom:     # S'il n'y a pas de nom alors on s'arrête là
            return  self.fermer_dialogue()
        #Ajouter la catégorie au debut du dictionnaire
        nouvelle_categorie = {
            nom: [icone, Couleur]
        }

        Categorie_Card.dictionnaire_cat = (
                nouvelle_categorie | Categorie_Card.dictionnaire_cat
        )
        # Fermer la boite de dialogue et réafficher les catégories
        self.fermer_dialogue()
        self.afficher_categories()






# =============================================================================================================
# C. CONTENU DE LA BOITE DE DIALOGUE POUR AJOUTER UNE NOUVELLE CATÉGORIE
#==============================================================================================================
class Contenu_Dialog(MDBoxLayout):
    # Définition et initialisation de nos propriétés
    couleur = ColorProperty([0.2, 0.2, 0.2, 1])
    color_dialog = None                                 # Pour stocker la petite popup des couleurs
    icon_choisie = StringProperty("plus-box-multiple")  # Icône par défaut

    # SELECTIONNER UNE COULEUR
    def selecteur_couleur(self):
        palette = [
            (0.1, 0.1, 0.9, 1), (0.2, 0.6, 0.9, 1), (0, 0.8, 0.8, 1), (0.1, 0.4, 0.5, 1),
            (0.1, 0.8, 0.1, 1), (0.18, 0.8, 0.44, 1), (0.1, 0.5, 0.1, 1), (0.7, 0.9, 0.1, 1),
            (0.9, 0.1, 0.1, 1), (0.9, 0.3, 0.5, 1), (1, 0.4, 0.7, 1), (0.6, 0.1, 0.1, 1),
            (0.6, 0.3, 0.7, 1), (0.4, 0.1, 0.6, 1), (0.2, 0.1, 0.4, 1), (0.8, 0.5, 1, 1),
            (1, 0.5, 0, 1), (1, 0.7, 0, 1), (0.5, 0.3, 0.1, 1), (0.3, 0.2, 0.1, 1),
            (0.2, 0.2, 0.2, 1), (0.5, 0.5, 0.5, 1), (0.7, 0.7, 0.7, 1), (0, 0, 0, 1)
        ]
        # Création du la grille (MDGridLayout) qui va contenir la palette de couleurs
        grille_couleurs = MDGridLayout(
            cols=3,
            spacing="10dp",
            padding="10dp",
            adaptive_height=True
        )

        # 1. On crée d'abord le ScrollView avec la grille dedans
        scroll = MDScrollView(
            size_hint_y=None,
            height="250dp"
        )
        # On ajoute la grille au scroll APRÈS la création
        scroll.add_widget(grille_couleurs)


        # 2. IMPORTANT : On met le scroll dans un BoxLayout
        # C'est ce conteneur qui sera le content_cls du Dialog
        container = MDBoxLayout(orientation="vertical", adaptive_height=True)
        container.add_widget(scroll)

        for couleur in palette:
            btn = MDIconButton(
                icon="circle",
                theme_text_color="Custom",
                text_color=couleur,
                icon_size="36sp",
            )

            # On lie le clic à la fonction de sélection
            btn.bind(on_release=lambda x, col=couleur: self.appliquer_couleur(col))
            grille_couleurs.add_widget(btn)

        self.color_dialog = MDDialog(
            title="Choisir une couleur",
            type="custom",
            content_cls=container,  # On utilise le container ici
        )

        self.color_dialog.open()

    # --- APPLIQUER UNE COULEUR ---
    def appliquer_couleur(self, couleur_choisie):
        # On met à jour la propriété de Contenu_Dialog
        self.couleur = couleur_choisie
        # On met à jour la couleur du bouton dans le dialogue principal
        self.ids.btn_couleur.md_bg_color = couleur_choisie
        # On ferme le sélecteur
        self.color_dialog.dismiss()

    # SLCTIONNER L'ICONE
    def selecteur_icon(self):
        # Liste d'icônes adaptées à un budget
        liste_icons = [
            "food", "cart", "bus", "car", "home", "phone", "coffee", "gift",
            "movie", "school", "medical-bag", "cash-multiple", "bank", "airplane",
            "tshirt-crew", "dumbbell", "dog", "cat", "water", "lightning-bolt",
            "hammer-wrench", "shield-check", "Account", "briefcase"
        ]

        layout_grille = MDGridLayout(cols=3, spacing="10dp", padding="10dp", adaptive_height=True)

        scroll = MDScrollView(size_hint_y=None, height="250dp")
        scroll.add_widget(layout_grille)

        container = MDBoxLayout(orientation="vertical", adaptive_height=True)
        container.add_widget(scroll)

        self.icon_dialog = MDDialog(
            title="Choisir une icône",
            type="custom",
            content_cls=container,
        )

        for i in liste_icons:
            btn = MDIconButton(
                icon=i,
                icon_size="36sp",
            )
            btn.bind(on_release=lambda x, ico=i: self.appliquer_icone(ico))
            layout_grille.add_widget(btn)

        self.icon_dialog.open()

    # --- APPLIQUER L'ICONE ---
    def appliquer_icone(self, icone_nom):
        self.icon_choisie = icone_nom
        # On met à jour l'icône du bouton dans le dialogue
        self.ids.btn_icon.icon = icone_nom
        self.icon_dialog.dismiss()