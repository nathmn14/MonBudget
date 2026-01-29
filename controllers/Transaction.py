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
            # On change d'écran tout de suite
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
                        # Garder l'heure actuelle pour le tri précis
                        now = datetime.now()
                        date_bdd = date_obj.replace(hour=now.hour, minute=now.minute, second=now.second).strftime("%Y-%m-%d %H:%M:%S")
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
                            'montant': montant, 'type': 'Revenu' if self.ids.btn_revenu.md_bg_color == [0.45, 1, 0.35, 1] else 'Dépense',
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
    repertoire_transactions = DictProperty()
    dictionnaire_categories = DictProperty()
    list_categories = ListProperty()
    list_mois = ListProperty()
    _refreshing = False 
    _search_event = None 
    _silence_filter = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_event_listeners()
        Clock.schedule_once(lambda dt: self.recharger_transactions())

    def on_pre_enter(self, *args):
        """Chargé AVANT l'affichage : On prépare tout"""
        self.recharger_transactions()
        
        def _initial_populate(dt):
            if self.repertoire_transactions:
                self.afficher_transactions(self.repertoire_transactions)
            
            if hasattr(self, 'ids') and 'barre_recherche' in self.ids:
                self._silence_filter = True
                self.ids.barre_recherche.text = ""
                self.ids.menu_categories.text = "Toutes"
                self.ids.menu_mois.text = "Tous"
                self._silence_filter = False
        
        Clock.schedule_once(_initial_populate, 0.05)

    def afficher_transactions(self, repertoire):
        """Met à jour les données du RecycleView"""
        if hasattr(self.ids, 'nb_transaction'):
            n = len(repertoire)
            self.ids.nb_transaction.text = f"Nous avons trouvé {n} transaction{'s' if n > 1 else ''}"
        
        rv_data = []
        # On trie pour avoir les plus récentes en haut (basé sur l'ordre d'insertion/BDD)
        # Si le répertoire est déjà dans l'ordre de la BDD (desc), on garde cet ordre
        keys = sorted(repertoire.keys())
        
        for k in keys:
            info = repertoire[k]
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

        if hasattr(self.ids, 'rv_transactions'):
            self.ids.rv_transactions.data = rv_data

    def filtrer_transaction(self, *args):
        """Débouclage de la recherche pour éviter les micro-lags"""
        if self._search_event:
            self._search_event.cancel()
        self._search_event = Clock.schedule_once(self._do_filtring, 0.3)

    def _do_filtring(self, dt):
        if self._silence_filter: return
        if not hasattr(self, 'ids'): return

        lettre_saisie = self.ids.barre_recherche.text.lower()
        cat_filtre = self.ids.menu_categories.text
        mois_filtre = self.ids.menu_mois.text

        resultat = {}
        for id_t, info in self.repertoire_transactions.items():
            if (lettre_saisie in info["nom"].lower() and
                (cat_filtre == "Toutes" or info["categorie"] == cat_filtre) and
                (mois_filtre == "Tous" or info["mois"] == mois_filtre)):
                resultat[id_t] = info

        self.afficher_transactions(resultat)

    def ouvrir_menu(self, liste, widget_declencheur):
        Items = [{'viewclass': 'OneLineListItem', 'text': i, 'on_release': lambda x=i: self.selectionner_item(x, widget_declencheur)} for i in liste]
        self.menu = MDDropdownMenu(items=Items, caller=widget_declencheur)
        self.menu.open()

    def selectionner_item(self, x, widget_declencheur):
        widget_declencheur.text = x
        self.filtrer_transaction()
        self.menu.dismiss()

    def reinitialiser_filtres(self):
        self.ids.barre_recherche.text = ''
        self.ids.menu_categories.text = 'Toutes'
        self.ids.menu_mois.text = 'Tous'
        self.afficher_transactions(self.repertoire_transactions)
    
    def recharger_transactions(self, event_data=None, *args):
        """Recharge intelligente : si event_data est là, on ajoute juste la carte"""
        if isinstance(event_data, dict) and 'id' in event_data:
            self._ajouter_une_seule_transaction(event_data)
            return

        if self._refreshing: return
        self._refreshing = True

        try:
            categories = CategorieModel.get_all()
            self.dictionnaire_categories = {c['nom_categorie']: [c['icone'], tuple(float(x) for x in c['couleur'].split(','))] for c in categories}
            self.dictionnaire_categories["Inconnue"] = ["help-circle", (0.5, 0.5, 0.5, 1)]
            self.list_categories = ['Toutes'] + [c['nom_categorie'] for c in categories]

            id_compte = get_default_account_id()
            transactions_bdd = TransactionModel.get_by_account(id_compte) if id_compte else []
            
            self.repertoire_transactions = {}
            for i, trans in enumerate(transactions_bdd, 1):
                try:
                    d_obj = datetime.strptime(trans['date_transaction'], '%Y-%m-%d %H:%M:%S')
                except:
                    try: d_obj = datetime.strptime(trans['date_transaction'], '%Y-%m-%d')
                    except: d_obj = datetime.now()
                
                self.repertoire_transactions[i] = {
                    'id': trans['id_transaction'],
                    'nom': trans['description'],
                    'categorie': trans.get('nom_categorie', 'Inconnue'),
                    'montant': trans['montant'],
                    'type': 'Revenu' if trans['type_transaction'] == 'ENTREE' else 'Dépense',
                    'date': d_obj.strftime('%d %B %Y'),
                    'mois': d_obj.strftime('%B')
                }
            
            self.afficher_transactions(self.repertoire_transactions)
        except Exception as e: print(f"Error rechargement: {e}")
        finally: self._refreshing = False

    def _ajouter_une_seule_transaction(self, info):
        """Injection chirurgicale au sommet de la liste"""
        couleur = (0.1, 0.9, 0.3, 1) if info["type"] == 'Revenu' else (0.9, 0.1, 0.1, 1)
        new_item = {
            'icon_': info.get('icon', 'help-circle'),
            'couleur_': couleur, 'nom_': info["nom"], 'categorie_': info["categorie"],
            'montant_': info["montant"], 'date_': info["date"], 'mois_': info["mois"]
        }
        if hasattr(self.ids, 'rv_transactions'):
            self.ids.rv_transactions.data.insert(0, new_item)
            n = len(self.ids.rv_transactions.data)
            self.ids.nb_transaction.text = f"Nous avons trouvé {n} transaction{'s' if n > 1 else ''}"

    def _setup_event_listeners(self):
        subscribe_to_data_changes(self._on_data_changed)
        event_bus.subscribe(EventTypes.TRANSACTION_ADDED, self.recharger_transactions)
        event_bus.subscribe(EventTypes.TRANSACTION_DELETED, self._on_data_changed)
        event_bus.subscribe(EventTypes.DATA_RESET, self._on_data_changed)

    def _on_data_changed(self, *args, **kwargs):
        Clock.schedule_once(lambda dt: self.recharger_transactions(), 0.1)



