from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton

# Import des modèles pour accéder à la BDD
from models.transaction import TransactionModel
from models.budget import BudgetModel
from data.connexion_bdd import get_default_account_id

# PAGE 'BUDGET'
class BudgetScreen(MDBoxLayout):
    titre_page=StringProperty('Budget')


    # Propriétés réactives
    budget_total = NumericProperty(60000)
    montant_utilise = NumericProperty(40000)
    jours_restants = NumericProperty(20)

    montant_restant = NumericProperty(0)
    pourcentage_utilise = NumericProperty(0)
    depenses_journalieres = NumericProperty(0)

#cette partie vas nous permettre de rendre le calcule du montan restant, pourcentage, et depenses journalières plus facile
    def on_budget_total(self, instance, value):
        self.recalculer_depenses()

    def on_montant_utilise(self, instance, value):
        self.recalculer_depenses()

    def on_jours_restants(self, instance, value):
        self.recalculer_depenses()

    # RECALCULER LES DEPENSES APRÈS AVOIR MODIFIER LE BUDGET
    def recalculer_depenses(self):
        self.montant_restant = self.budget_total - self.montant_utilise
        
        # Calcul du pourcentage (borné entre 0 et 100)
        if self.budget_total > 0:
            calc_pourcent = (self.montant_utilise / self.budget_total) * 100
            self.pourcentage_utilise = max(0, min(100, round(calc_pourcent, 2)))
        else:
            self.pourcentage_utilise = 0
            
        if self.jours_restants > 0:
            # On utilise le montant restant pour estimer ce qu'on peut dépenser par jour
            # Si restant < 0, on met 0
            self.depenses_journalieres = max(0, self.montant_restant // self.jours_restants)
        else:
            self.depenses_journalieres = 0


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.charger_donnees_depuis_bdd()  # Charger les données depuis la BDD
        self.recalculer_depenses()  # Calcul initial dès le départ
    
    def charger_donnees_depuis_bdd(self):
        """Charge les données du budget et des transactions depuis la BDD"""
        id_compte = get_default_account_id()
        if id_compte:
            # Charger le budget depuis la BDD (ou créer un par défaut)
            budget_data = BudgetModel.get_or_create(id_compte, default_budget=60000, default_jours=20)
            
            if budget_data:
                self.budget_total = budget_data['budget_total']
                self.jours_restants = budget_data['jours_restants']
            
            # Calculer le budget net utilisé (Dépenses - Revenus)
            montant_depenses = TransactionModel.get_total_by_type('SORTIE', id_compte)
            montant_revenus = TransactionModel.get_total_by_type('ENTREE', id_compte)
            
            # Le montant "utilisé" net est la différence. 
            # Si Revenus > Dépenses, montant_utilise sera négatif, donc budget_restant (total - utilise) augmentera.
            self.montant_utilise = montant_depenses - montant_revenus

    # CRÉATION D'UNE BOITE DE DIALOGUE POUR MODIFIER LE BUDGET
    popup = None
    textfield = None
    box_input = None

    def modifier_budget(self):
        # Si un popup existe déjà alors la fonction ne renvoie rien  (cela nous évite de se retrouver avec plusieurs fenêtres ouvertes
        if self.popup:
            return

        self.box_input = MDBoxLayout(
            orientation="vertical",
            #spacing="20dp",
            adaptive_height= True,
            size_hint_y=None,
            height="300dp",
            #padding=["10dp", "0dp", "10dp", "0dp"],
        )

        self.textfield = MDTextField(
            text=f"{self.budget_total}",  # Prépare la valeur pour l'édition
            mode="line",
            #input_type='number',  # Force le clavier numérique si possible
            input_filter="int",
            hint_text="Entrez un montant valide",
            helper_text_mode="on_error",
            #size_hint_y=None,
            #height="56dp"
        )

        self.box_input.add_widget(self.textfield)   # On ajoute notre textfield à notre conteneur (MDBoxlayout)

        self.popup = MDDialog(
            title="Modifier le Budget",
            type="custom",
            #size_hint_y=None,
            #height=400,
            content_cls=self.box_input,
            buttons=[
                MDRaisedButton(
                    text="Confirmer",
                    on_release=self.action_modifier,
                    #md_bg_color= app.custom_colors[app.theme_cls.theme_style]["bg_secondary"]
                ),
                MDRaisedButton(
                    text="Annuler",
                    on_release=self.fermer_popup
                )
            ],
            on_dismiss=self.nettoyer_popup
        )
        self.popup.open()

    def action_modifier(self, button):
        try:
            text_value = self.textfield.text.strip()
            if not text_value:
                self.notifier("Veuillez entrer un montant.", "error")
                return
                
            new_budget = int(text_value)
            if new_budget < 0:
                self.notifier("Le budget ne peut pas être négatif.", "error")
                return
                
            self.budget_total = new_budget
            
            # Sauvegarder dans la BDD
            id_compte = get_default_account_id()
            if id_compte:
                BudgetModel.update_by_account(id_compte, budget_total=new_budget)
                self.notifier(f"Nouveau budget : {new_budget} FC", "success")
            
            self.popup.dismiss()

        except ValueError:
            self.notifier("Veuillez entrer un nombre entier valide.", "error")

    def notifier(self, message, type="info"):
        """Appelle la notification globale de l'application"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        if hasattr(app.root, 'notifier'):
            app.root.notifier(message, type)

    # FONCTION POUR RÉINITIALISER LE BUDGET
    def reinitialiser_budget(self):
        # Réinitialiser les valeurs
        self.budget_total = 0
        self.montant_utilise = 0
        self.jours_restants = 20
        
        # Sauvegarder dans la BDD
        id_compte = get_default_account_id()
        if id_compte:
            BudgetModel.update_by_account(id_compte, budget_total=0, jours_restants=20)
            self.notifier("Le budget a été réinitialisé !", "success")

    # FERMER LA BOITE DE DIALOGUE
    def fermer_popup(self, button):
        if self.popup:
            self.popup.dismiss()

    def nettoyer_popup(self, *args):
        self.popup = None
        self.textfield = None
        self.box_input = None





