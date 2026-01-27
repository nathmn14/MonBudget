from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivy.clock import Clock
from datetime import datetime
import calendar
from decimal import Decimal

# Import des modèles pour accéder à la BDD
from models.transaction import TransactionModel
from models.budget import BudgetModel
from data.connexion_bdd import get_default_account_id
from utils.event_bus import event_bus, EventTypes, subscribe_to_data_changes, notify_budget_changed

# PAGE 'BUDGET'
class BudgetScreen(MDBoxLayout):
    titre_page=StringProperty('Budget')


    # Propriétés réactives (acceptent maintenant les décimaux)
    budget_total = NumericProperty(60000.0)
    montant_utilise = NumericProperty(0.0)
    jours_restants = NumericProperty(20)

    montant_restant = NumericProperty(0.0)
    pourcentage_utilise = NumericProperty(0.0)
    depenses_journalieres = NumericProperty(0.0)
    
    # Propriétés formatées pour l'affichage
    budget_total_formate = StringProperty("60 000 FC")
    montant_utilise_formate = StringProperty("0 FC")
    montant_restant_formate = StringProperty("60 000 FC")
    depenses_journalieres_formate = StringProperty("3 000 FC")

#cette partie vas nous permettre de rendre le calcule du montan restant, pourcentage, et depenses journalières plus facile
    def on_budget_total(self, instance, value):
        self.budget_total_formate = self.format_montant(value)
        self.recalculer_depenses()

    def on_montant_utilise(self, instance, value):
        self.montant_utilise_formate = self.format_montant(value)
        self.recalculer_depenses()

    def on_jours_restants(self, instance, value):
        self.recalculer_depenses()

    def format_montant(self, montant):
        """Formate un montant pour l'affichage : avec décimales si nécessaire, sinon entier"""
        if montant == int(montant):
            # Pas de partie décimale, afficher en entier
            return f"{int(montant):,} FC"
        else:
            # Partie décimale présente, afficher avec 2 décimales
            return f"{montant:,.2f} FC"

    def calculer_jours_restants_reels(self):
        """Calcule le nombre de jours réels restants dans le mois actuel"""
        now = datetime.now()
        dernier_jour = calendar.monthrange(now.year, now.month)[1]
        jours_restants = dernier_jour - now.day
        return max(0, jours_restants)  # Ne pas retourner de valeurs négatives

    def calculer_argent_par_jour_reel(self):
        """Calcule l'argent disponible par jour en fonction du mois actuel"""
        if self.jours_restants <= 0:
            return 0.0
        
        # Si le montant restant est négatif, on ne peut rien dépenser
        if self.montant_restant <= 0:
            return 0.0
            
        # Calculer l'argent disponible par jour avec décimaux
        argent_par_jour = self.montant_restant / self.jours_restants
        return round(float(argent_par_jour), 2)

    def recalculer_depenses(self):
        self.montant_restant = self.budget_total - self.montant_utilise
        
        # Calcul du pourcentage (borné entre 0 et 100)
        if self.budget_total > 0:
            calc_pourcent = (self.montant_utilise / self.budget_total) * 100
            self.pourcentage_utilise = max(0, min(100, round(calc_pourcent, 2)))
        else:
            self.pourcentage_utilise = 0
            
        # Utiliser le calcul réel d'argent par jour
        self.depenses_journalieres = self.calculer_argent_par_jour_reel()
        
        # Mettre à jour les propriétés formatées
        self.montant_restant_formate = self.format_montant(self.montant_restant)
        self.depenses_journalieres_formate = self.format_montant(self.depenses_journalieres)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.charger_donnees_depuis_bdd()  # Charger les données depuis la BDD
        self.recalculer_depenses()  # Calcul initial dès le départ
        # S'abonner aux événements pour le rafraîchissement automatique
        self._setup_event_listeners()

    def _setup_event_listeners(self):
        """Configure les écouteurs d'événements pour le rafraîchissement automatique"""
        # S'abonner à tous les changements de données
        subscribe_to_data_changes(self._on_data_changed)
        
        # S'abonner spécifiquement aux changements de budget
        event_bus.subscribe(EventTypes.BUDGET_CHANGED, self._on_data_changed)
        
        # S'abonner aux changements de transactions
        event_bus.subscribe(EventTypes.TRANSACTION_ADDED, self._on_data_changed)
        event_bus.subscribe(EventTypes.TRANSACTION_DELETED, self._on_data_changed)
        
        # S'abonner à la réinitialisation des données
        event_bus.subscribe(EventTypes.DATA_RESET, self._on_data_changed)

    def _on_data_changed(self, event_data=None, *args, **kwargs):
        """Callback appelé quand les données changent"""
        # Rafraîchir les données avec un petit délai pour éviter les conflits
        Clock.schedule_once(lambda dt: self.charger_donnees_depuis_bdd(), 0.1)

    def rafraichir_instantane(self):
        """Force un rafraîchissement immédiat des données"""
        self.charger_donnees_depuis_bdd()
        self.recalculer_depenses()
    
    def charger_donnees_depuis_bdd(self):
        """Charge les données du budget et des transactions depuis la BDD"""
        id_compte = get_default_account_id()
        if id_compte:
            # Charger le budget depuis la BDD (ou créer un par défaut)
            budget_data = BudgetModel.get_or_create(id_compte, default_budget=60000, default_jours=20)
            
            if budget_data:
                self.budget_total = budget_data['budget_total']
                # Utiliser les vrais jours restants calculés dynamiquement
                self.jours_restants = self.calculer_jours_restants_reels()
            
            # Calculer le budget net utilisé (Dépenses - Revenus)
            # Récupérer toutes les transactions sans filtre de mois pour avoir le total réel
            montant_depenses = TransactionModel.get_total_by_type('SORTIE', id_compte)
            montant_revenus = TransactionModel.get_total_by_type('ENTREE', id_compte)
            
            # Le montant "utilisé" net est la différence. 
            # Si Revenus > Dépenses, montant_utilise sera négatif, donc budget_restant (total - utilise) augmentera.
            self.montant_utilise = montant_depenses - montant_revenus
            
            # Mettre à jour les propriétés formatées
            self.budget_total_formate = self.format_montant(self.budget_total)
            self.montant_utilise_formate = self.format_montant(self.montant_utilise)

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
            hint_text="Entrez un montant valide (ex: 59300.50)",
            helper_text_mode="on_error",
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
                
            # Accepter les décimaux avec Decimal pour plus de précision
            new_budget = float(text_value.replace(',', '.'))
            if new_budget < 0:
                self.notifier("Le budget ne peut pas être négatif.", "error")
                return
                
            print(f"Tentative de mise à jour du budget vers: {new_budget}")
                
            # Sauvegarder dans la BDD d'abord
            id_compte = get_default_account_id()
            if id_compte:
                success = BudgetModel.update_by_account(id_compte, budget_total=new_budget)
                print(f"Mise à jour BDD réussie: {success}")
                
                if success:
                    self.notifier(f"Nouveau budget : {new_budget:,.2f} FC", "success")
                    # Notifier que le budget a changé
                    notify_budget_changed(new_budget, id_compte)
                    
                    # Mettre à jour le budget total localement
                    self.budget_total = new_budget
                    
                    # Recharger les données de transactions pour conserver les montants utilisés
                    self.charger_donnees_depuis_bdd()
                    
                    # Recalculer les dépenses avec les nouvelles valeurs
                    self.recalculer_depenses()
                    
                    print(f"Budget après mise à jour: {self.budget_total}")
                else:
                    self.notifier("Erreur lors de la mise à jour du budget.", "error")
            
            self.popup.dismiss()

        except ValueError:
            self.notifier("Veuillez entrer un nombre valide.", "error")

    def notifier(self, message, type="info"):
        """Appelle la notification globale de l'application"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        if hasattr(app.root, 'notifier'):
            app.root.notifier(message, type)

    # FONCTION POUR RÉINITIALISER LE BUDGET
    def reinitialiser_budget(self):
        # Sauvegarder dans la BDD
        id_compte = get_default_account_id()
        if id_compte:
            BudgetModel.update_by_account(id_compte, budget_total=0, jours_restants=20)
            self.notifier("Le budget a été réinitialisé !", "success")
            
            # Recharger toutes les données depuis la BDD
            self.charger_donnees_depuis_bdd()
            self.recalculer_depenses()

    # FERMER LA BOITE DE DIALOGUE
    def fermer_popup(self, button):
        if self.popup:
            self.popup.dismiss()

    def nettoyer_popup(self, *args):
        self.popup = None
        self.textfield = None
        self.box_input = None





