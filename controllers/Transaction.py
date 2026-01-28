from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, OptionProperty, DictProperty, ListProperty,ColorProperty
from kivymd.uix.menu import MDDropdownMenu


from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen


#from kivymd.uix.picker import MDDatePicker
from kivymd.uix.pickers import MDDatePicker
from datetime import datetime
from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton

# Import des modèles pour accéder à la BDD
from models.transaction import TransactionModel
from models.categorie import CategorieModel
from data.connexion_bdd import get_default_account_id
from utils.event_bus import notify_transaction_added, event_bus, EventTypes, subscribe_to_data_changes

# LE SCREEN MANAGER POUR NAVIGUER ENTRE LES DEUX PAGES (TRANSACTION ET AJOUTER TRANSACTION)
class TransacScreen_Manager(MDScreenManager):
    pass


# LA PAGE POUR AJOUTER UNE NOUVELLE TRANSACTION
class TransacAddScreen(MDScreen):

    # CHOISIR LE TYPE DE LA TRANSACTION
    def choisir_type(self, type_transac):
        from kivy.app import App
        app = App.get_running_app()

        # On récupère les couleurs du dictionnaire selon le thème actuel
        # Cela évite de répéter les conditions if app.theme_cls.theme_style partout
        theme = app.theme_cls.theme_style
        colors = app.custom_colors[theme]

        if type_transac == "Revenu":
            # --- Bouton REVENU (Actif) ---
            self.ids.btn_revenu.md_bg_color = (0.45, 1, 0.35, 1)  # Vert
            self.ids.btn_revenu.text_color = (1, 1, 1, 1)
            self.ids.btn_revenu.elevation = 2
            self.ids.btn_revenu.shadow_color = (0,0,0,0.8) if theme == "Light" else (0.5, 0.5, 0.5, 1)

            # --- Bouton DEPENSE (Inactif) ---
            # Utilise bg_secondary de votre dictionnaire (0.9 ou 0.12 selon le thème)
            self.ids.btn_depense.md_bg_color = colors["bg_secondary"]
            self.ids.btn_depense.text_color = (0.4, 0.4, 0.5, 1)
            self.ids.btn_depense.elevation = 0



        else:
            # --- Bouton DEPENSE (Actif) ---
            self.ids.btn_depense.md_bg_color = (1, 0.35, 0.45, 1)  # Rouge/Rose
            self.ids.btn_depense.text_color = (1, 1, 1, 1)
            self.ids.btn_depense.elevation = 2
            self.ids.btn_depense.shadow_color = (0,0,0,0.8) if theme == "Light" else (0.5, 0.5, 0.5, 1)

            # --- Bouton REVENU (Inactif) ---
            self.ids.btn_revenu.md_bg_color = colors["bg_secondary"]
            self.ids.btn_revenu.text_color = (0.4, 0.4, 0.5, 1)
            self.ids.btn_revenu.elevation = 0

        return type_transac
    # OUVRIR LE MENU DES CATEGORIE (charger depuis la BDD)
    def ouvrir_menu_cat(self):
        # Récupérer les catégories depuis la BDD
        categories = CategorieModel.get_all()
        liste = [cat['nom_categorie'] for cat in categories]
        
        declencheur= self.ids.menu_categories2
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

    # SÉLÉCTIONNER UNE CATÉGORIE
    def select_cat(self, cat, declencheur):
        declencheur.text = cat
        self.menu.dismiss()


    # MISE EN PLACE DE LA BOITE DE DIALOGUE POUR SAISIR LA DATE DE LA TRANSACTION
    dialog=None
    input_date=None

    def saisir_date(self):
        if not self.dialog:
            self.input_date=MDTextField(
            hint_text= "Date de la transaction",
            helper_text= "Enter une date valide (dd/mm/yyyy)",
            validator= "date",
            date_format= "dd/mm/yyyy",
            #max_text_length= 10,
            date_interval= ('01/01/1900', '01/01/2100')
            )

            self.dialog = MDDialog(
                title='Ajouter une Catégorie',
                type='custom',
                content_cls=self.input_date,
                buttons=[
                    MDRaisedButton(
                        text='Annuler',
                        on_release=self.fermer_dialogue,
                    ),
                    MDRaisedButton(
                        text='Confirmer',
                        on_release=self.confirmer_date,
                    )
                ],

            )
            self.dialog.open()

    # CONFIRMER LA DATE DE LA TRANSACTION
    def confirmer_date(self, *args):
        input_date_text=self.input_date.text
        date_transac= self.ids.date_transac
        date_transac.text= input_date_text
        self.dialog.dismiss()
        self.dialog = None
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

    def on_pre_enter(self):
        """Initialisation avant l'affichage de l'écran"""
        if hasattr(self.ids, 'date_transac'):
            self.ids.date_transac.text = datetime.now().strftime("%d/%m/%Y")

    def ajouter_transaction(self):
        """Sauvegarde instantanée avec injection chirurgicale"""
        try:
            # 1. Validation ultra-rapide
            montant_text = self.ids.montant_transac.text
            if not montant_text or montant_text == "0":
                self.notifier("Montant invalide", "error")
                return
                
            montant = float(montant_text)
            categorie_nom = self.ids.menu_categories2.text
            if categorie_nom == "Sélectionner une catégorie":
                self.notifier("Choisissez une catégorie", "error")
                return

            description = self.ids.description_transac.text.strip() or categorie_nom
            date_str = self.ids.date_transac.text
            
            # --- ACTION IMMÉDIATE ---
            self.parent.transition.direction = 'right'
            self.parent.transition.duration = 0.15 
            self.parent.current = 'list_screen'
            
            # --- SAUVEGARDE EN ARRIÈRE-PLAN ---
            import threading
            def _task():
                try:
                    # Préparation date
                    try: 
                        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                        date_bdd = date_obj.replace(hour=datetime.now().hour, minute=datetime.now().minute, second=datetime.now().second).strftime("%Y-%m-%d %H:%M:%S")
                    except: date_bdd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    categories = CategorieModel.get_all()
                    cat_data = next((c for c in categories if c['nom_categorie'] == categorie_nom), None)
                    if not cat_data: return

                    tid = TransactionModel.create(
                        id_compte=get_default_account_id(),
                        id_categorie=cat_data['id_categorie'],
                        montant=montant,
                        type_transaction='ENTREE' if self.ids.btn_revenu.md_bg_color == [0.45, 1, 0.35, 1] else 'SORTIE',
                        description=description,
                        date_transaction=date_bdd
                    )
                    
                    # Injection dans l'UI sans recharger toute la BDD
                    def _ui(*args):
                        new_info = {
                            'id': tid, 'nom': description, 'categorie': categorie_nom,
                            'montant': montant, 'type': 'Revenu' if 'ENTREE' in date_bdd or self.ids.btn_revenu.md_bg_color == [0.45, 1, 0.35, 1] else 'Dépense',
                            'date': datetime.now().strftime("%d %B %Y"), 'mois': datetime.now().strftime("%B"),
                            'icon': cat_data['icone']
                        }
                        notify_transaction_added(new_info)
                    Clock.schedule_once(_ui, 0.2)
                except: pass

            threading.Thread(target=_task, daemon=True).start()
            
            # Reset UI
            self.ids.montant_transac.text = "0"
            self.ids.description_transac.text = ""
        except Exception as e:
            self.notifier(f"Erreur: {str(e)}", "error")

from kivy.uix.recycleview.views import RecycleDataViewBehavior

# LA CLASSE QUI VA SERVIR DE MODEL POUR CHAQUE TRANSACTION - OPTIMISÉE POUR RECYCLEVIEW
class Transaction_card(RecycleDataViewBehavior, MDCard):
    # Propriétés de données (Mêmes noms que dans le KV pour l'auto-mapping)
    id_transaction = NumericProperty(0)
    nom_ = StringProperty('')
    type_ = OptionProperty("Dépense", options=["Dépense", "Revenu"])
    montant_ = NumericProperty(0)
    devise = StringProperty('FC')
    date_ = StringProperty('')
    mois_ = StringProperty('')
    categorie_ = StringProperty('')
    icon_ = StringProperty('')
    couleur_ = ColorProperty([0, 0, 0, 1])

    def refresh_view_attrs(self, rv, index, data):
        """Appelé lorsque le RecycleView réutilise ce widget"""
        for key, value in data.items():
            setattr(self, key, value)
        return super().refresh_view_attrs(rv, index, data)


# LA PAGE TRANSACATION
class TransacScreen(MDScreen):
    # On définit nos propriétés
    repertoire_transactions = DictProperty()
    dictionnaire_categories = DictProperty()
    list_categories = ListProperty()
    list_mois = ListProperty()
    _refreshing = False # Verrou anti-spam/anti-conflict
    _search_event = None # Pour le débouclage de la recherche
    # On initialise nos propriétés
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
        # S'abonner aux événements pour le rafraîchissement automatique
        self._setup_event_listeners()
        
        # Charger les catégories depuis la BDD
        categories = CategorieModel.get_all()
        self.dictionnaire_categories = {}
        for cat in categories:
            couleur_tuple = tuple(float(x) for x in cat['couleur'].split(','))
            self.dictionnaire_categories[cat['nom_categorie']] = [cat['icone'], couleur_tuple]
        
        # Ajouter une catégorie par défaut pour les transactions inconnues
        self.dictionnaire_categories["Inconnue"] = ["help-circle", (0.5, 0.5, 0.5, 1)]
        
        self.list_categories = ['Toutes'] + [cat['nom_categorie'] for cat in categories]
        self.list_mois = ['Tous','Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Aout','Septembre','Octobre','Novembre','Décembre']
        
        # Charger les transactions depuis la BDD
        id_compte = get_default_account_id()
        transactions_bdd = TransactionModel.get_by_account(id_compte) if id_compte else []
        
        # Convertir les transactions BDD en format dict pour affichage
        self.repertoire_transactions = {}
        for i, trans in enumerate(transactions_bdd, 1):
            # Récupérer la catégorie directement depuis les données de la transaction
            cat_nom = trans.get('nom_categorie', 'Inconnue')
            cat_icone = trans.get('icone_categorie', 'help-circle')
            
            # Si la catégorie n'existe pas dans notre dictionnaire, l'ajouter
            if cat_nom not in self.dictionnaire_categories and cat_nom != 'Inconnue':
                cat_couleur = trans.get('couleur_categorie', '0.5,0.5,0.5,1')
                couleur_tuple = tuple(float(x) for x in cat_couleur.split(','))
                self.dictionnaire_categories[cat_nom] = [cat_icone, couleur_tuple]
            
            # Extraire le mois de la date
            date_str = trans['date_transaction']
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                mois = date_obj.strftime('%B')
                date_formatee = date_obj.strftime('%d %B %Y')
            except:
                mois = 'Inconnu'
                date_formatee = date_str
            
            type_display = 'Revenu' if trans['type_transaction'] == 'ENTREE' else 'Dépense'
            
            self.repertoire_transactions[i] = {
                'id': trans['id_transaction'],
                'nom': trans['description'],
                'categorie': cat_nom,
                'montant': trans['montant'],
                'type': type_display,
                'date': date_formatee,
                'mois': mois
            }
        
        self.menu = None

    def on_pre_enter(self, *args):
        """Chargé AVANT l'affichage : On affiche TOUT directement"""
        # 1. Chargement immédiat des données (Back-end)
        self.recharger_transactions()
        
        # 2. Reset visuel des widgets (Front-end) avec sécurité
        def _reset_ui(dt):
            if hasattr(self, 'ids') and 'barre_recherche' in self.ids:
                self._silence_filter = True
                self.ids.barre_recherche.text = ""
                self.ids.menu_categories.text = "Toutes"
                self.ids.menu_mois.text = "Tous"
                self._silence_filter = False
        
        # On attend la fin du frame actuel pour s'assurer que les ids sont liés
        Clock.schedule_once(_reset_ui)

    # AFFICHAGE DES TRANSACTION (RECYCLEVIEW : ULTRA RAPIDE)
    def afficher_transactions(self, repertoire):
        """Met à jour les données du RecycleView"""
        self.ids.nb_transaction.text = f"Nous avons trouvé {len(repertoire)} transaction{'s' if len(repertoire) > 1 else ''}"
        
        # Préparation des données pour le RecycleView
        rv_data = []
        for id_key, info in repertoire.items():
            cat = info["categorie"]
            icon = self.dictionnaire_categories.get(cat, ["help-circle"])[0] if cat in self.dictionnaire_categories else "help-circle"
            couleur = (0.1, 0.9, 0.3, 1) if info["type"] == 'Revenu' else (0.9, 0.1, 0.1, 1)

            rv_data.append({
                'icon_': icon,
                'couleur_': couleur,
                'nom_': info["nom"],
                'categorie_': cat,
                'montant_': info["montant"],
                'date_': info["date"],
                'mois_': info["mois"]
            })

        # Mise à jour directe (atomique et instantanée)
        if hasattr(self.ids, 'rv_transactions'):
            self.ids.rv_transactions.data = rv_data

    # RÉINITIALISER LES FILTRES ( barre de recherche, categories, mois)
    def reinitialiser_filtres(self):
        # 1. Remettre les menus à leur état initial
        if 'menu_categories' in self.ids: self.ids.menu_categories.text = "Toutes"
        if 'menu_mois' in self.ids: self.ids.menu_mois.text = "Tous"
        if 'barre_recherche' in self.ids: self.ids.barre_recherche.text = ""
        self.filtrer_transaction()

    # FILTRER LES TRANSACTION (AVEC DÉBOUCLAGE)
    def filtrer_transaction(self, *args):
        if self._search_event:
            self._search_event.cancel()
        self._search_event = Clock.schedule_once(self._do_filtring, 0.3)

    def _do_filtring(self, dt):
        """Exécute réellement la logique de filtrage"""
        if getattr(self, '_silence_filter', False):
            return

        lettre_saisie = self.ids.barre_recherche.text.lower() if 'barre_recherche' in self.ids else ""
        categorie_filtre = self.ids.menu_categories.text if 'menu_categories' in self.ids else "Toutes"
        mois_filtre = self.ids.menu_mois.text if 'menu_mois' in self.ids else "Tous"

        resultat_filtre = {}
        for id_transac, info_transac in self.repertoire_transactions.items():
            lettre_trouvee = lettre_saisie in info_transac["nom"].lower()
            categorie_trouvee = (categorie_filtre == "Toutes" or info_transac["categorie"] == categorie_filtre)
            mois_trouvee = (mois_filtre == "Tous" or info_transac["mois"] == mois_filtre)

            if lettre_trouvee and categorie_trouvee and mois_trouvee:
                resultat_filtre[id_transac] = info_transac

        self.afficher_transactions(resultat_filtre)

    # OUVIR LES MENUS (catégories ou mois)
    def ouvrir_menu(self,liste, widget_declencheur):
        Items=[]
        for i in liste:
            Items.append({
                'viewclass':'OneLineListItem',
                'text': i,
                'on_release': lambda x=i:self.selectionner_item(x,widget_declencheur)
            })
        self.menu=MDDropdownMenu(
            items=Items,
            caller=widget_declencheur,
            #width_mult=2,
        )
        self.menu.open()

    # SELECTIONNER UN ÉLÉMENTS DANS LE MENU (catégorie ou mois)
    def selectionner_item(self,x,widget_declencheur):
        widget_declencheur.text=x
        self.filtrer_transaction()
        self.menu.dismiss()

    
    def recharger_transactions(self, event_data=None, *args):
        """Recharge les transactions. Si event_data contient une transaction, on l'ajoute chirurgicalement."""
        
        # SI C'EST UN AJOUT UNIQUE (depuis le bus d'événement)
        if isinstance(event_data, dict) and 'id' in event_data:
            self._ajouter_une_seule_transaction(event_data)
            return

        # SINON, RECHARGEMENT GLOBAL (Initialisation, filtres, suppression...)
        if self._refreshing:
             return
        self._refreshing = True

        try:
            categories = CategorieModel.get_all()
            self.dictionnaire_categories = {}
            for cat in categories:
                couleur_vals = cat['couleur'].split(',')
                if len(couleur_vals) == 4:
                    couleur_tuple = tuple(float(x) for x in couleur_vals)
                    self.dictionnaire_categories[cat['nom_categorie']] = [cat['icone'], couleur_tuple]
            
            self.list_categories = ['Toutes'] + [cat['nom_categorie'] for cat in categories]

            id_compte = get_default_account_id()
            transactions_bdd = TransactionModel.get_by_account(id_compte) if id_compte else []
            
            self.repertoire_transactions = {}
            for i, trans in enumerate(transactions_bdd, 1):
                cat_nom = trans.get('nom_categorie', 'Inconnue')
                date_str = trans['date_transaction']
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    mois = date_obj.strftime('%B')
                    date_formatee = date_obj.strftime('%d %B %Y')
                except:
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        mois = date_obj.strftime('%B')
                        date_formatee = date_obj.strftime('%d %B %Y')
                    except: mois = 'Inconnu'; date_formatee = date_str
                
                self.repertoire_transactions[i] = {
                    'id': trans['id_transaction'],
                    'nom': trans['description'],
                    'categorie': cat_nom,
                    'montant': trans['montant'],
                    'type': 'Revenu' if trans['type_transaction'] == 'ENTREE' else 'Dépense',
                    'date': date_formatee,
                    'mois': mois,
                    'icon': trans.get('icone_categorie', 'help-circle')
                }
            
            self.afficher_transactions(self.repertoire_transactions)
            
            # --- Sécurité : Accès aux IDS ---
            if hasattr(self, 'ids') and 'barre_recherche' in self.ids:
                # Si l'utilisateur n'est pas en train de chercher, on nettoie
                if not self.ids.barre_recherche.focus and self.ids.barre_recherche.text != '':
                    self.ids.barre_recherche.text = ''
                    self.ids.menu_categories.text = 'Toutes'
                    self.ids.menu_mois.text = 'Tous'
        except Exception as e:
            print(f"DEBUG TransacScreen Error: {e}")
        finally:
            self._refreshing = False

    def _ajouter_une_seule_transaction(self, info):
        """Ajoute une seule card au sommet visuel via RecycleView"""
        couleur = (0.1, 0.9, 0.3, 1) if info["type"] == 'Revenu' else (0.9, 0.1, 0.1, 1)
        
        new_item = {
            'icon_': info.get('icon', 'help-circle'),
            'couleur_': couleur,
            'nom_': info["nom"],
            'categorie_': info["categorie"],
            'montant_': info["montant"],
            'date_': info["date"],
            'mois_': info["mois"]
        }
        
        # On insère au début pour un tri chronologique inverse
        if hasattr(self.ids, 'rv_transactions'):
            self.ids.rv_transactions.data.insert(0, new_item)
            # Rafraîchir le compteur local
            n = len(self.ids.rv_transactions.data)
            self.ids.nb_transaction.text = f"Nous avons trouvé {n} transaction{'s' if n > 1 else ''}"
    def _setup_event_listeners(self):
        """Configure les écouteurs d'événements pour le rafraîchissement automatique"""
        # S'abonner spécifiquement aux changements de transactions
        event_bus.subscribe(EventTypes.TRANSACTION_ADDED, self.recharger_transactions)
        event_bus.subscribe(EventTypes.TRANSACTION_DELETED, self.recharger_transactions)
        event_bus.subscribe(EventTypes.DATA_RESET, self.recharger_transactions)
        # S'abonner aux changements de catégorie (couleurs/icônes)
        event_bus.subscribe(EventTypes.CATEGORY_CHANGED, self.recharger_transactions)



