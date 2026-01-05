#####################################################################################################
# MODULE : Transactions                                                                             #
# DESCRIPTION : Ce module gère l'affichage de l'historique et la logique d'ajout de transactions.   #
# ARCHITECTURE : Pattern MVC (Modèle-Vue-Contrôleur)                                                #
# - Modèle : Transaction_card (Représentation d'une donnée)                                         #
# - Vue : TransacScreen & TransacAddScreen (Interfaces définies dans le KV)                         #
# - Contrôleur : Logique de filtrage, gestion des menus et insertion de données                     #
#####################################################################################################

#

# --- IMPORTATIONS ---
from datetime import datetime
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp

# Propriétés Kivy : Assurent la liaison réactive entre Python et le fichier .kv
from kivy.properties import StringProperty, NumericProperty, OptionProperty, DictProperty, ListProperty, ColorProperty
# Widget KivyMD
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel

# --- DEPENDANCES EXTERNES ---
# Importation du dictionnaire de catégories pour assurer la cohérence visuelle (icônes/couleurs)
from Controllers.Categorie import Categorie_Card


# ============================================================================================================
# A. GESTIONNAIRE DE NAVIGATION
# ============================================================================================================
#    Rôle : Hub de navigation principal pour le module transaction.
#    Responsabilité : Permet de basculer entre la liste des transactions et le formulaire d'ajout.
#    Lien KV : Référence le bloc <TransacScreen_Manager@MDScreenManager> dans le fichier .kv.
# ============================================================================================================
class TransacScreen_Manager(MDScreenManager):

    pass



# ==================================================================================================================
# B. MODÈLE DE WIDGET : Transaction_card
# ==================================================================================================================
class Transaction_card(MDCard):
    """
    Rôle : Composant UI réutilisable représentant une transaction unique.
    Propriétés Kivy :
    - StringProperty/NumericProperty : Permettent au KV de se mettre à jour via root.nom_, root.montant_, etc.
    - ColorProperty : Gère dynamiquement la couleur du texte (Vert/Rouge).
    Lien KV : Voir <Transaction_card@MDCard> pour le layout interne.
    """
    nom_ = StringProperty('')
    type_ = OptionProperty("Dépenses", options=["Dépenses", "Revenu"])
    montant_ = NumericProperty(0)
    date_ = StringProperty('')
    mois_ = StringProperty('')
    categorie_ = StringProperty('')
    icon_ = StringProperty('')
    couleur_ = ColorProperty([0, 0, 0, 1])
    devise = StringProperty('FC')


# =============================================================================================================
# C. PAGE PRINCIPALE : TransacScreen
#==============================================================================================================
#    Rôle : AFFICHAGE DES TRANSACTION ET FILTRAGE DE CELLE-CI
# =============================================================================================================
class TransacScreen(MDScreen):
    """
    Rôle : Vue principale affichant l'historique et les filtres (barre de recherche, catégorie, mois).
    Propriétés :
    - repertoire_transactions (DictProperty) : La source de vérité des données.
    - list_categories/list_mois (ListProperty) : Utilisées pour alimenter les menus déroulants.
    Architecture : Utilise Clock.schedule_once pour différer l'affichage initial après le chargement du KV.
    """
    # Declaration des propriétés
    repertoire_transactions = DictProperty()
    dictionnaire_categories = DictProperty()
    list_categories = ListProperty()
    list_mois = ListProperty()

    def __init__(self, **kwargs):
        """ Initialisation des données statiques et de l'état initial de la page. """
        super().__init__(**kwargs)
        # Mock de données (Simulation de base de données)
        self.repertoire_transactions = {
            1: {"nom": "Salaire Novembre", "categorie": "Salaire", "montant": 450000, "type": "Revenu",
                "date": "25 novembre 2025", "mois": "Novembre"},
            2: {"nom": "Courses Carrefour", "categorie": "Alimentation", "montant": 55000, "type": "Dépense",
                "date": "24 novembre 2025", "mois": "Novembre"},
            3: {"nom": "Loyer Décembre", "categorie": "Logement", "montant": 120000, "type": "Dépense",
                "date": "01 décembre 2025", "mois": "Décembre"},
            4: {"nom": "Abonnement Netflix", "categorie": "Loisirs", "montant": 12500, "type": "Dépense",
                "date": "05 décembre 2025", "mois": "Décembre"},
            5: {"nom": "Vente Ordinateur", "categorie": "Business", "montant": 300000, "type": "Revenu",
                "date": "10 décembre 2025", "mois": "Décembre"},
            6: {"nom": "Facture SNEL", "categorie": "Énergie", "montant": 25000, "type": "Dépense",
                "date": "12 décembre 2025", "mois": "Décembre"},
            7: {"nom": "Taxi Travail", "categorie": "Transport", "montant": 2500, "type": "Dépense",
                "date": "14 décembre 2025", "mois": "Décembre"},
            8: {"nom": "Restaurant Midi", "categorie": "Alimentation", "montant": 15000, "type": "Dépense",
                "date": "15 décembre 2025", "mois": "Décembre"},
            9: {"nom": "Prime de fin d'année", "categorie": "Salaire", "montant": 100000, "type": "Revenu",
                "date": "20 décembre 2025", "mois": "Décembre"},
            10: {"nom": "Achat Pharmacie", "categorie": "Santé", "montant": 8500, "type": "Dépense",
                 "date": "21 décembre 2025", "mois": "Décembre"},
            11: {"nom": "Frais Scolaires", "categorie": "Éducation", "montant": 50000, "type": "Dépense",
                 "date": "02 janvier 2026", "mois": "Janvier"},
            12: {"nom": "Réparation Voiture", "categorie": "Transport", "montant": 85000, "type": "Dépense",
                 "date": "05 janvier 2026", "mois": "Janvier"},
            13: {"nom": "Cadeau Anniversaire", "categorie": "Loisirs", "montant": 20000, "type": "Dépense",
                 "date": "07 janvier 2026", "mois": "Janvier"},
            14: {"nom": "Dividendes Actions", "categorie": "Business", "montant": 15000, "type": "Revenu",
                 "date": "10 janvier 2026", "mois": "Janvier"},
            15: {"nom": "Abonnement Internet", "categorie": "Énergie", "montant": 30000, "type": "Dépense",
                 "date": "12 janvier 2026", "mois": "Janvier"}
        }

        # Chargement des filtres
        self.dictionnaire_categories = dict(Categorie_Card.dictionnaire_cat)
        self.list_categories = ['Toutes'] + list(Categorie_Card.dictionnaire_cat.keys())
        self.list_mois = ['Tous', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Aout', 'Septembre','OCtobre', 'Novembre', 'Décembre']
        self.menu = None

        # Affichage asynchrone pour éviter de bloquer le démarrage de l'app
        Clock.schedule_once(lambda dt: self.afficher_transactions(self.repertoire_transactions))


    # --- GÉNÉRATION DYNAMIQUE DE LA LISTE DES TRANSACTIONS---
    def afficher_transactions(self, repertoire):
        """
        Objectif : Transformer le dictionnaire de données en widgets visuels (MDCard).
        Étapes :
        1. Mise à jour du compteur via l'id 'nb_transaction'.
        2. Nettoyage du conteneur (id: conteneur_transaction).
        3. Parcourir le repertoir et récupérer les infos de chaque transaction
        4. Création physique du widget MDCard personnalisé.
        5. Ajouter notre widget au conteneur
        """
        # 1. Mise à jours du compteur
        nbr_transaction = len(repertoire)       # On récupère la taille du tableau qui correspond au nombre de clés donc le nombre de transactions
        # On conditionne un peut l'affichage
        if nbr_transaction <= 1:
            self.ids.nb_transaction.text = f'Nous avons trouvé {nbr_transaction} transaction '
        else:
            self.ids.nb_transaction.text = f'Nous avons trouvé {nbr_transaction} transactions '

        # 2. Nettoyage du conteneur (vider avant l'affichage, pour éviter les doublons)
        conteneur_transaction = self.ids.conteneur_transaction      # On récupère le conteneur
        conteneur_transaction.clear_widgets()                       # On vide le conteneur

        # 3. Récupération des infos (nom, montant, icons, etc)
        for id_transac, info_transac in repertoire.items():
            # Récupération des infos dans le repertoire
            nom = info_transac["nom"]
            montant = info_transac["montant"]
            date = info_transac["date"]
            mois = info_transac["mois"]
            categorie = info_transac["categorie"]

            # Récupération de l'icône dans le dictionnaire des catégories (voir la classe Categorie_card dans le fichier 'Categorie.py')
            icon = self.dictionnaire_categories[categorie][0]

            # Détermination de la couleur en fonction du type de transaction (Revenu vs Dépense)
            type = info_transac["type"]
            if type == 'Revenu':
                couleur = [0.1, 0.9, 0.3, 1]        # Vert pour les revenus
            else:
                couleur = [0.9, 0.1, 0.1, 1]        # Rouge pour les dépenses

            # 4. Création physique du widget MDCard personnalisé
            transaction = Transaction_card(
                icon_=icon,
                couleur_=couleur,
                nom_=nom,
                categorie_=categorie,
                montant_=montant,
                date_=date,
                mois_=mois
            )
            # 4. On ajoute notre widget au conteneur
            conteneur_transaction.add_widget(transaction)


    # --- GESTIONS DES FILTRES (barre de recherche, categorie, mois) ---
    def filtrer_transaction(self):
        """
        Objectif : Filtrage multi-critères (Nom + Catégorie + Mois).
        Logique :
        1. Capture le contenu des widgets de filtrage (id: barre_recherche, menu_categories, menu_mois).
        2. On parcours le repertoire et place les conditions pour chaque filtre.
        3. Affichage du résultat après filtre.
        """
        # 1. On capture le contenu des widget de filtrage
        lettre_saisie = self.ids.barre_recherche.text.lower()       # On met toutes les lettres en minuscule pour éviter les problèmes liés à la casse lors du traitement
        categorie_filtre = self.ids.menu_categories.text
        mois_filtre = self.ids.menu_mois.text

        # 2. On parcours le repertoire et place les conditions pour chaque filtre
        resultat_filtre = {}
        for id_transac, info_transac in self.repertoire_transactions.items():
            lettre_trouvee = False
            categorie_trouvee = False
            mois_trouvee = False

            # Condition 1 : Recherche textuelle
            if lettre_saisie in info_transac["nom"].lower():
                lettre_trouvee = True

            # Condition 2 : Filtrage catégorie (Gestion de l'option joker 'Toutes')
            if categorie_filtre == "Toutes" or info_transac["categorie"] == categorie_filtre:
                categorie_trouvee = True

            # Condition 3 : Filtrage temporel (Gestion de l'option joker 'Tous')
            if mois_filtre == "Tous" or info_transac["mois"] == mois_filtre:
                mois_trouvee = True

            # Validation du cumul des filtres
            if lettre_trouvee and categorie_trouvee and mois_trouvee:
                resultat_filtre[id_transac] = info_transac

        # 3. Affichage du résultat après filtre
        self.afficher_transactions(resultat_filtre)


    # --- GESTION DES MENUS DROPDOWN ---

    def ouvrir_menu(self, liste, widget_declencheur):
        """
        1. Ouvre un menu MDDropdownMenu pour n'importe quelle liste fournie (Categorie ou Mois).
        Liaison : Associe chaque item à la méthode 'selectionner_item'.
        """
        Items = []

        # On parcour la liste et on convertie chaque élément en Item pour notre menu
        for i in liste:
            Items.append({
                'viewclass': 'OneLineListItem',
                'text': i,
                'on_release': lambda x=i: self.selectionner_item(x, widget_declencheur)     # On associe chaque item (ex : Janvier) à la fonction pour le selectionner
            })
        self.menu = MDDropdownMenu(
            items=Items,
            caller=widget_declencheur,
        )
        self.menu.open()

    # --- SELECTION DES ITEMS ET LANCEMENT DU FILTRE ---
    def selectionner_item(self, x, widget_declencheur):
        """ Met à jour l'étiquette du bouton de filtre et relance immédiatement la recherche. """
        widget_declencheur.text = x         # on récupère l'item
        self.filtrer_transaction()
        self.menu.dismiss()             #  On ferme notre menu après selection


    # --- RÉINITIALISER LES FILTRES ---
    def reinitialiser_filtres(self):
        """ Restaure l'état initial des filtres et affiche l'intégralité du répertoire initial. """
        self.ids.barre_recherche.text = ''
        self.ids.menu_categories.text = 'Toutes'
        self.ids.menu_mois.text = 'Tous'
        self.afficher_transactions(self.repertoire_transactions)




# ===========================================================================================================================
# D. FORMULAIRE POUR 'AJOUTER UNE TRANSACTION'
# ============================================================================================================================
class TransacAddScreen(MDScreen):
    # --- CHOISIR LE TYPE DE LA TRANSACTION ---
    type_transac = ''

    def choisir_type(self, type):
        """
        Objectif : Gérer l'état exclusif entre 'Revenu' et 'Dépense'.
        Logique : Modifie dynamiquement les propriétés visuelles (couleur, élévation) via self.ids.
        """
        self.type_transac = type
        if self.type_transac == "Revenu":
            # Mise en évidence visuelle du bouton sélectionné (Vert)
            btn_revenu = self.ids.btn_revenu
            btn_revenu.md_bg_color = [0.45, 1, 0.35, 1]
            btn_revenu.theme_text_color = "Custom"
            btn_revenu.text_color = [1, 1, 1, 1]
            btn_revenu.elevation = 2

            # Réinitialisation du bouton opposé
            btn_depense = self.ids.btn_depense
            btn_depense.md_bg_color = [0.95, 0.95, 0.95, 1]
            btn_depense.theme_text_color = "Custom"
            btn_depense.text_color = [0.4, 0.4, 0.5, 1]
            btn_depense.elevation = 0

        else:
            # Mise en évidence visuelle du bouton sélectionné (Rouge)
            btn_depense = self.ids.btn_depense
            btn_depense.md_bg_color = [1, 0.35, 0.45, 1]
            btn_depense.theme_text_color = "Custom"
            btn_depense.text_color = [1, 1, 1, 1]
            btn_depense.elevation = 2

            # Réinitialisation du bouton opposé
            btn_revenu = self.ids.btn_revenu
            btn_revenu.md_bg_color = [0.95, 0.95, 0.95, 1]
            btn_revenu.theme_text_color = "Custom"
            btn_revenu.text_color = [0.4, 0.4, 0.5, 1]
            btn_revenu.elevation = 0

        return self.type_transac


    # --- OUVRIR LE MENU DES CATÉGORIE ---
    def ouvrir_menu_cat(self):
        """
        Objectif : Afficher dynamiquement les catégories disponibles.
        Étapes :
        1. Extraction des clés (nom de la catégorie) du dictionnaire Categorie_Card.
        2. Construction des dictionnaires d'items pour le menu (widget: MDDropdownMenu)
        3. Liaison du callback 'select_cat' pour la capture du choix.
        """
        liste = list(Categorie_Card.dictionnaire_cat.keys())
        declencheur = self.ids.menu_categories2
        Items = []
        for i in liste:
            Items.append({
                'viewclass': 'OneLineListItem',
                'text': i,
                'on_release': lambda x=i: self.select_cat(x, declencheur)
            })
        self.menu = MDDropdownMenu(
            items=Items,
            caller=declencheur,
        )
        self.menu.open()


    # --- SELECTIONNER UNE CATÉGORIE ---
    def select_cat(self, cat, declencheur):
        """ Assigne la valeur choisie au widget déclencheur et ferme le menu. """
        declencheur.text = cat
        self.categorie_transac = cat
        self.menu.dismiss()
        return self.categorie_transac


    # --- SAISIR LA DATE ---
    dialog = None
    input_date = None
    def saisir_date(self):
        """
        Objectif : Construction d'une boite de dialogue personnalisée.
        Composants : Utilise un MDTextField avec un validateur 'date' intégré.
        Lien KV : Déclenché par un événement on_release sur le label de date.
        """
        if not self.dialog:
            self.input_date = MDTextField(
                hint_text="Date de la transaction",
                helper_text="Enter une date valide (dd/mm/yyyy)",
                text=datetime.now().strftime('%d/%m/%Y'),
                validator="date",
                date_format="dd/mm/yyyy",
                date_interval=('01/01/1900', '01/01/2100')
            )

            self.dialog = MDDialog(
                title='Ajouter une Catégorie',
                type='custom',                      # Ceci nous permet de personnaliser notre boite de dialogue afin de mettre les widgets de notre choix
                content_cls=self.input_date,        # cette propriété de mettre notre widget input_date dans la boite de dialogue
                buttons=[
                    MDRaisedButton(text='Annuler', on_release=self.fermer_dialogue),
                    MDRaisedButton(text='Confirmer', on_release=self.confirmer_date)
                ],
            )
            self.dialog.open()      # Ouverture de la boite de dialogue


    # --- CONFIRMER LA DATE ---
    date_transac = ''
    def confirmer_date(self, *args):
        """ Transfère la date saisie du dialogue vers le label qui est juste à coté. """
        input_date_text = self.input_date.text              # On recupère le texte de notre input (celui qu'on a crée ci-haut)
        self.ids.date_transac.text = input_date_text        # On copie le text de notre input dans le label qui a l'id 'date_transac'
        self.date_transac = input_date_text                 # On sauvegarde la date pour l'utiliser plus tard
        # On ferme la boite de dialogue puis on la vide
        self.dialog.dismiss()           # Fermer
        self.dialog = None              # Vider


    # --- FERMER LE DIALOGUE ---
    def fermer_dialogue(self, *args):
        # On ferme la boite de dialogue puis on la vide
        self.dialog.dismiss()  # Fermer
        self.dialog = None  # Vider


    # --- DÉCLENCHEMENT DE L'AJOUT ---
    def ajouter_transaction(self):
        """
        Objectif : Initier le processus de sauvegarde avec feedback visuel (spinner pour le chargement).
        Étapes :
        1. Active le MDSpinner (id: chargement_transaction).
        2. Désactive le bouton d'envoi pour prévenir les doublons.
        3. Utilise Clock.schedule_once pour simuler un traitement asynchrone (5s).
        """
        self.ids.chargement_transaction.active = True       # On active le spinner
        self.ids.btn_ajouter.disabled = True
        Clock.schedule_once(self.traitement_ajout, 5)       # On stipuler que le traitement vas commencer après 5s (le temps de permetre au spinner de tourner)


    # --- TRAITEMENT MÉTIER DE L'AJOUT ---
    def traitement_ajout(self, dt):
        """
        Objectif : Récupérer les données et ajouter la transaction dans la page initiale (TransacScreen).
        Étapes :
        1. 1. Récupération des entrées via self.ids.
        2. Accès à l'écran 'transac_screen' via le ScreenManager.
        3. Formatage du mois et de la date.
        4. Calcul de l'ID.
        5. Fusion de la nouvelle donnée dans le DictProperty (réactivité Kivy).
        6. Notification utilisateur (Snackbar) et redirection vers la page initial.
        """
        try:
            # 1. Récupération des entrées (saisis de l'utilisateur)
            nom_t = self.ids.nom_transac.text
            montant_t = int(self.ids.montant_transac.text)
            type_t = self.type_transac
            categorie_t = self.categorie_transac

            # 2. Accès à l'écran 'transac_screen' via le ScreenManager (ça va nous aider à récupérer les variables et les fonctions qui on été crée dans la classe TransacScreen)
            transac_screen = self.manager.get_screen('transac_screen')  # Ici on récupère notre page à l'aide de son nom (name: transac_screen)

            # 3. Formatage du mois et de la date
            date = self.date_transac
            if date:
                d = datetime.strptime(date, '%d/%m/%Y')         # On convertie notre date(text) en objet Date qui respecte le fomrat (dd/mm/yyy)
                mois_t = transac_screen.list_mois[d.month]             # on récupère le nom du mois (janvier, février, etc.) dans la liste des mois qu'on a défini dans la classe TransacScreen
                date_t = f'{d.day} {mois_t} {d.year}'                  # On fais la mise en forme finale. ex: 03 Janvier 2026
            else:
                mois_t = 'Inconnu'
                date_t = 'Date inconnue'

            # 4. Calcule de l'ID
            cles = transac_screen.repertoire_transactions.keys()        # On récupère la liste des ids dans le repertoire des transactions
            id_transac = max(cles) + 1 if cles else 1                   # Pour s'assurer que l'id est unique on va prendre le plus grand puis l'incrémenter de 1 (si la liste n'est pas vide)

            # 5. Ici on crée notre nouvelle transaction (que nous allons ajouter au répertoire plus tard)
            nouvelle_transac = {
                id_transac: {
                    "nom": nom_t,
                    "categorie": categorie_t,
                    "montant": montant_t,
                    "type": type_t,
                    "date": date_t,
                    "mois": mois_t
                }
            }

            # 6. Mise à jour du repertoire (On ajoute notre transaction au repertoire)
            transac_screen.repertoire_transactions = {**nouvelle_transac, **transac_screen.repertoire_transactions}

            # 7. On réaffiche le repertoire avec la nouvelle transaction
            transac_screen.afficher_transactions(transac_screen.repertoire_transactions)        # Ceci nous permet de mettre la transaction en tête du repertoire

            # 8. Arrêter le spinner et reactiver le boutton
            self.ids.chargement_transaction.active = False
            self.ids.btn_ajouter.disabled = False

            # 9. Message de confirmation à l'aide d'une Snackbar
            top_y = Window.height - dp(80)      # On va calculer la position (y) pa rapport à la hauteur de l'écran
            Snackbar(
                MDLabel(
                    text="Transaction ajoutée avec succès !",
                    adaptive_width=True,
                    theme_text_color='Custom',
                    text_color=(1, 1, 1, 1)
                ),
                # Propriétés de la Snackbar
                y=top_y,
                md_bg_color=(0.1, 0.4, 0.9, 1),
                duration=2,
            ).open()

            # 10. Redirection vers la page transac_screen
            self.manager.current = 'transac_screen'
            self.manager.transition.direction = 'right'

        except Exception as e:
            # Gestion d'erreur sécurisée pour ne pas bloquer l'UI
            self.ids.chargement_transaction.active = False
            self.ids.btn_ajouter.disabled = False
            print(f"Erreur : {e}")
