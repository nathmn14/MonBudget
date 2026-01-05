from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton

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
        self.pourcentage_utilise = (self.montant_utilise / self.budget_total) * 100 if self.budget_total != 0 else 0
        self.pourcentage_utilise = round(self.pourcentage_utilise, 2)
        if self.jours_restants > 0:
            self.depenses_journalieres = self.montant_restant // self.jours_restants
        else:
            self.depenses_journalieres = 0


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recalculer_depenses()  # calcule initial dès le départ

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
            mode="rectangle",
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
                    on_release=self.action_modifier
                ),
                MDRaisedButton(
                    text="Annuler",
                    on_release=self.fermer_popup
                )
            ],
            on_dismiss=self.nettoyer_popup
        )
        self.popup.open()

    # MODIFICATION DU BUDGET
    def action_modifier(self, button):
        try:
            new_budget = int(self.textfield.text)
            self.budget_total = new_budget
            self.popup.dismiss()

        # Ajouter également la logique pour la mise à jours des propriétés restantes (montant_restant, etc)
        except ValueError:
            self.textfield.error = True

    # FONCTION POUR RÉINITIALISER LE BUDGET
    def reinitialiser_budget(self):
        # recalcul automatique des autres propriétés
        self.budget_total = 0
        self.montant_utilise = 0
        self.jours_restants = 20

    # FERMER LA BOITE DE DIALOGUE
    def fermer_popup(self, button):
        if self.popup:
            self.popup.dismiss()

    def nettoyer_popup(self, *args):
        self.popup = None
        self.textfield = None
        self.box_input = None




