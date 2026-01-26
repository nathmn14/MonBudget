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
        """Sauvegarde la transaction dans la BDD"""
        try:
            # Récupérer les données du formulaire
            montant_text = self.ids.montant_transac.text
            if not montant_text or montant_text == "0":
                self.notifier("Veuillez entrer un montant valide.", "error")
                return
                
            montant = float(montant_text)
            categorie_nom = self.ids.menu_categories2.text
            description = self.ids.description_transac.text
            date_str = self.ids.date_transac.text
            
            # Conversion de la date pour la BDD (DD/MM/YYYY -> YYYY-MM-DD)
            try:
                date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                date_bdd = date_obj.strftime("%Y-%m-%d")
            except:
                date_bdd = datetime.now().strftime("%Y-%m-%d")
            
            # Validation : montant doit être > 0
            if montant <= 0:
                self.notifier("Le montant doit être supérieur à 0.", "error")
                return
            
            # Validation : catégorie doit être sélectionnée
            if categorie_nom == "Sélectionner une catégorie":
                self.notifier("Veuillez sélectionner une catégorie.", "error")
                return
            
            # Déterminer le type de transaction
            if self.ids.btn_revenu.md_bg_color == [0.45, 1, 0.35, 1]:
                type_transaction = 'ENTREE'
            else:
                type_transaction = 'SORTIE'
            
            # Récupérer l'ID de la catégorie par son nom (rafraîchir avant au cas où)
            categories = CategorieModel.get_all()
            id_categorie = None
            for cat in categories:
                if cat['nom_categorie'] == categorie_nom:
                    id_categorie = cat['id_categorie']
                    break
            
            if not id_categorie:
                self.notifier("Catégorie introuvable dans la base de données.", "error")
                return
            
            # Récupérer l'ID du compte par défaut
            id_compte = get_default_account_id()
            
            # Sauvegarder dans la BDD
            TransactionModel.create(
                id_compte=id_compte,
                id_categorie=id_categorie,
                montant=montant,
                type_transaction=type_transaction,
                description=description,
                date_transaction=date_bdd
            )
            
            # Message de succès
            self.notifier(f"Transaction '{description}' ajoutée !", "success")
            
            # Réinitialiser les champs
            self.ids.montant_transac.text = "0"
            self.ids.description_transac.text = ""
            self.ids.menu_categories2.text = "Sélectionner une catégorie"
            
            # Retourner à l'écran précédent et rafraîchir
            self.parent.current = 'list_screen'
            
            # Rafraîchir l'écran TransacScreen
            transac_screen = self.parent.get_screen('list_screen')
            if hasattr(transac_screen, 'recharger_transactions'):
                transac_screen.recharger_transactions()
            
            # Rafraîchir l'écran Budget (impact automatique sur le solde)
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            # Accès direct via les IDs définis dans Template.kv
            if hasattr(app.root, 'ids'):
                if 'budget_screen' in app.root.ids:
                    budget_screen = app.root.ids.budget_screen
                    budget_screen.charger_donnees_depuis_bdd()
                    budget_screen.recalculer_depenses()
                
                if 'dashboard_screen' in app.root.ids:
                    dashboard_screen = app.root.ids.dashboard_screen
                    dashboard_screen.charger_donnees()
            
        except ValueError as e:
            self.notifier(f"Montant invalide : {str(e)}", "error")

# LA CLASSE QUI VA SERVIR DE MODEL POUR CHAQUE TRANSACTION
class Transaction_card(MDCard):
    id_transaction = NumericProperty(0)  # ID de la transaction dans la BDD
    nom_=StringProperty('')
    type_= OptionProperty("Dépense",options=["Dépense", "Revenu"])
    montant_= NumericProperty(0)
    devise=StringProperty('FC')
    date_= StringProperty('')
    mois_=StringProperty('')
    note_= StringProperty('')
    categorie_=StringProperty('')
    icon_=StringProperty('')
    couleur_=ColorProperty([0, 0, 0, 1])


# LA PAGE TRANSACATION
class TransacScreen(MDScreen):
    # On définit nos propriétés
    repertoire_transactions=DictProperty()
    dictionnaire_categories= DictProperty()
    list_categories= ListProperty()
    list_mois= ListProperty()

    # On initialise nos propriétés
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
        # Charger les catégories depuis la BDD
        categories = CategorieModel.get_all()
        self.dictionnaire_categories = {}
        for cat in categories:
            couleur_tuple = tuple(float(x) for x in cat['couleur'].split(','))
            self.dictionnaire_categories[cat['nom_categorie']] = [cat['icone'], couleur_tuple]
        
        self.list_categories = ['Toutes'] + [cat['nom_categorie'] for cat in categories]
        self.list_mois = ['Tous','Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Aout','Septembre','Octobre','Novembre','Décembre']
        
        # Charger les transactions depuis la BDD
        id_compte = get_default_account_id()
        transactions_bdd = TransactionModel.get_by_account(id_compte) if id_compte else []
        
        # Convertir les transactions BDD en format dict pour affichage
        self.repertoire_transactions = {}
        for i, trans in enumerate(transactions_bdd, 1):
            # Récupérer la catégorie
            cat = CategorieModel.get_by_id(trans['id_categorie'])
            cat_nom = cat['nom_categorie'] if cat else 'Inconnu'
            
            # Extraire le mois de la date
            date_str = trans['date_transaction']
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                mois = date_obj.strftime('%B')  # Nom du mois en anglais
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
        Clock.schedule_once(lambda dt: self.afficher_transactions(self.repertoire_transactions))

    # AFFICHAGE DES TRANSACTION (CARD)
    def afficher_transactions(self, repertoire):

        nbr_transaction=len(repertoire)
        if nbr_transaction <=1:
            self.ids.nb_transaction.text=f'Nous avons trouvé {nbr_transaction} transaction '
        else:
            self.ids.nb_transaction.text=f'Nous avons trouvé {nbr_transaction} transactions '

        conteneur_transaction= self.ids.conteneur_transaction
        conteneur_transaction.clear_widgets()


        for id_transac, info_transac in repertoire.items():
            nom= info_transac["nom"]
            montant= info_transac["montant"]
            date= info_transac["date"]
            mois= info_transac["mois"]

            categorie= info_transac["categorie"]
            icon= self.dictionnaire_categories[categorie][0]

            type= info_transac["type"]
            if type=='Revenu':
                couleur=(0.1, 0.9, 0.3, 1)
            else:
                couleur=(0.9, 0.1, 0.1, 1)

            transaction=Transaction_card(
                icon_=icon,
                couleur_= couleur,
                nom_= nom,
                categorie_= categorie,
                montant_= montant,
                date_= date,
                mois_= mois
            )

            conteneur_transaction.add_widget(transaction)

    # FILTRER LES TRANSACTION (barre de recherche, catégorie, mois)
    def  filtrer_transaction(self):
        # 1. Récupérer le contenu de la barre de recherche et des différents filtres
        lettre_saisie= self.ids.barre_recherche.text.lower()
        categorie_filtre= self.ids.menu_categories.text
        mois_filtre= self.ids.menu_mois.text


        # 2. Comparer les éléments avec aux filtres

        resultat_filtre={}
        for id_transac, info_transac in self.repertoire_transactions.items():
            lettre_trouvee=False
            categorie_trouvee=False
            mois_trouvee=False
            if lettre_saisie in info_transac["nom"].lower():
                lettre_trouvee= True

            if categorie_filtre == "Toutes" or info_transac["categorie"] == categorie_filtre:
                categorie_trouvee=True

            if mois_filtre == "Tous" or info_transac["mois"] == mois_filtre:
                mois_trouvee=True


            # 3. Récupérer les éléments qui respectent au filtre
            if lettre_trouvee and categorie_trouvee and mois_trouvee:
                resultat_filtre[id_transac]= info_transac

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

    # RÉINITIALISER LES FILTRES ( barre de recherche, categories, mois)
    def reinitialiser_filtres(self):
        self.ids.barre_recherche.text=''
        self.ids.menu_categories.text='Toutes'
        self.ids.menu_mois.text='Tous'
        self.afficher_transactions(self.repertoire_transactions)
    
    # RECHARGER LES TRANSACTIONS DEPUIS LA BDD
    def recharger_transactions(self):
        """Recharge les transactions depuis la base de données et rafraîchit l'affichage"""
        # CRITICAL: Recharger AUSSI le dictionnaire des catégories pour éviter KeyError
        categories = CategorieModel.get_all()
        self.dictionnaire_categories = {}
        for cat in categories:
            couleur_tuple = tuple(float(x) for x in cat['couleur'].split(','))
            self.dictionnaire_categories[cat['nom_categorie']] = [cat['icone'], couleur_tuple]
        
        self.list_categories = ['Toutes'] + [cat['nom_categorie'] for cat in categories]

        # Charger les transactions depuis la BDD
        id_compte = get_default_account_id()
        transactions_bdd = TransactionModel.get_by_account(id_compte) if id_compte else []
        
        # Convertir les transactions BDD en format dict pour affichage
        self.repertoire_transactions = {}
        for i, trans in enumerate(transactions_bdd, 1):
            # Récupérer la catégorie
            cat = CategorieModel.get_by_id(trans['id_categorie'])
            cat_nom = cat['nom_categorie'] if cat else 'Inconnu'
            
            # Extraire le mois de la date
            date_str = trans['date_transaction']
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                # Utiliser le nom du mois en français si possible, sinon garder datetime.strftime
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
        
        # Rafraîchir l'affichage
        self.afficher_transactions(self.repertoire_transactions)
        
        # Réinitialiser les filtres
        self.ids.barre_recherche.text = ''
        self.ids.menu_categories.text = 'Toutes'
        self.ids.menu_mois.text = 'Tous'



