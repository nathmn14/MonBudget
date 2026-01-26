from kivy.clock import Clock
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, ColorProperty, NumericProperty
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.factory import Factory

from kivymd.uix.dialog import MDDialog,BaseDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView

# Import du modèle pour accéder à la BDD
from models.categorie import CategorieModel


# VOICI LA CLASSE QUI VA SERVIR DE MODÈLE POUR CHAQUE CATÉGORIE
class Categorie_Card(MDCard):
    # Déclaration de mes variables de classe
    id_categorie = NumericProperty(0)  # ID de la catégorie dans la BDD
    nom = StringProperty('')
    icon = StringProperty('')
    couleur = ColorProperty([1, 1, 1, 1])

    # Fonction pour supprimer une catégorie (icon poubelle)
    def supprimer_categorie(self):
        # Supprimer de la BDD
        if self.id_categorie > 0:
            resultat = CategorieModel.delete_by_id(self.id_categorie)

            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            # On cible précisément l'écran qui possède la logique de notification
            app_target = app.root.get_screen('app_screen')

            if resultat == "INTEGRITY_ERROR":
                app_target.notifier(
                    "Impossible : cette catégorie est utilisée par des transactions.",
                    "error"
                )
                return

            if resultat:
                self.parent.remove_widget(self)
                app_target.notifier("Catégorie supprimée avec succès.", "success")


# BOITE DE DIALOGUE POUR AJOUTER UNE NOUVELLE CATÉGORIE
class Contenu_Dialog(MDBoxLayout):
    couleur = ColorProperty([0.2, 0.2, 0.2, 1])
    color_dialog = None  # Pour stocker la petite popup des couleurs
    icon_choisie = StringProperty("plus-box-multiple")  # Icône par défaut

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        palette = [
            (0.1, 0.1, 0.9, 1), (0.2, 0.6, 0.9, 1), (0, 0.8, 0.8, 1), (0.1, 0.4, 0.5, 1),
            (0.1, 0.8, 0.1, 1), (0.18, 0.8, 0.44, 1), (0.1, 0.5, 0.1, 1), (0.7, 0.9, 0.1, 1),
            (0.9, 0.1, 0.1, 1), (0.9, 0.3, 0.5, 1), (1, 0.4, 0.7, 1), (0.6, 0.1, 0.1, 1),
            (0.6, 0.3, 0.7, 1), (0.4, 0.1, 0.6, 1), (0.2, 0.1, 0.4, 1), (0.8, 0.5, 1, 1),
            (1, 0.5, 0, 1), (1, 0.7, 0, 1), (0.5, 0.3, 0.1, 1), (0.3, 0.2, 0.1, 1),
            (0.2, 0.2, 0.2, 1), (0.5, 0.5, 0.5, 1), (0.7, 0.7, 0.7, 1), (0, 0, 0, 1)
        ]
        import random
        self.couleur = random.choice(palette)
        # On attend un peu que les IDS soient chargés
        Clock.schedule_once(self.actualiser_bouton_couleur, 0.1)

    def actualiser_bouton_couleur(self, dt):
        if hasattr(self.ids, "btn_couleur"):
            self.ids.btn_couleur.md_bg_color = self.couleur

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

        layout_grille = MDGridLayout(
            cols=4,
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
        scroll.add_widget(layout_grille)


        # 2. IMPORTANT : On met le scroll dans un BoxLayout
        # C'est ce conteneur qui sera le content_cls du Dialog
        container = MDBoxLayout(orientation="vertical", adaptive_height=True)
        container.add_widget(scroll)

        for c in palette:
            btn = MDIconButton(
                icon="circle",
                theme_text_color="Custom",
                text_color=c,
                icon_size="36sp",
            )

            # On lie le clic à la fonction de sélection
            btn.bind(on_release=lambda x, col=c: self.appliquer_couleur(col))
            layout_grille.add_widget(btn)

        self.color_dialog = MDDialog(
            title="Choisir une couleur",
            type="custom",
            content_cls=container,  # On utilise le container ici
        )

        self.color_dialog.open()

    # APPLIQUER UNE COULEUR
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

        layout_grille = MDGridLayout(cols=4, spacing="10dp", padding="10dp", adaptive_height=True)

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

    # APPLIQUER L'ICONE
    def appliquer_icone(self, icone_nom):
        self.icon_choisie = icone_nom
        # On met à jour l'icône du bouton dans le dialogue
        self.ids.btn_icon.icon = icone_nom
        self.icon_dialog.dismiss()

# LA CLASSE POUR LA PAGE 'CATÉGORIE'
class CategorieScreen(MDBoxLayout):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.afficher_categories)       ## On demande à Kivy d'exécuter la fonction juste après l'initialisation

    # Affichage dynamique des catégories depuis la BDD
    def afficher_categories(self, dt=None):
        """Charge et affiche les catégories depuis la base de données"""
        self.ids.box_categories.clear_widgets()
        
        # Récupérer toutes les catégories depuis la BDD
        categories = CategorieModel.get_all()
        
        for cat in categories:
            # Convertir la couleur du format "0.18,0.8,0.44,1" en tuple (0.18, 0.8, 0.44, 1)
            couleur_str = cat['couleur']
            couleur_tuple = tuple(float(x) for x in couleur_str.split(','))
            
            self.ids.box_categories.add_widget(
                Categorie_Card(
                    id_categorie=cat['id_categorie'],
                    nom=cat['nom_categorie'],
                    icon=cat['icone'],
                    couleur=couleur_tuple,
                )
            )

    # CRÉATION DE NOTRE BOITE DE DIALOGUE POUR AJOUTER UNE CATÉGORIE
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

    # FERMER LA BOITE DE DIALOGUE
    def fermer_dialogue(self, *args):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog=None

    def notifier(self, message, type="info"):
        """Appelle la notification globale de l'application"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app_screen = app.root.get_screen('app_screen')

        if hasattr(app_screen, 'notifier'):
            app_screen.notifier(message, type)

    # AJOUTER UNE NOUVELLE CATÉGORIE
    def ajouter_categorie(self, *args):
        """Ajoute une nouvelle catégorie dans la BDD et rafraîchit l'affichage"""
        contenu_dialog = self.dialog.content_cls
        nom = contenu_dialog.ids.nom_categorie.text.strip()
        
        if not nom:
            self.notifier("Veuillez entrer un nom pour la catégorie.", "error")
            return
        
        # Récupérer la couleur et l'icône choisies
        couleur_tuple = contenu_dialog.couleur
        icone = contenu_dialog.icon_choisie
        
        # Convertir la couleur en format texte pour la BDD
        couleur_str = ','.join(str(x) for x in couleur_tuple)
        
        # Par défaut, on crée une catégorie de type SORTIE
        # TODO: Ajouter un sélecteur dans le dialogue pour choisir ENTREE/SORTIE
        type_transaction = 'SORTIE'
        
        # Sauvegarder dans la BDD
        CategorieModel.create(nom, type_transaction, icone, couleur_str)
        
        # Message de succès
        self.notifier(f"Catégorie '{nom}' créée !", "success")
        
        # Fermer le dialogue et rafraîchir l'affichage
        self.fermer_dialogue()
        self.afficher_categories()

