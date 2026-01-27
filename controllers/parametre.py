from __future__ import annotations

import csv
import json
import os
from datetime import datetime

from kivy.properties import BooleanProperty, ColorProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout

from models.budget import BudgetModel
from models.categorie import CategorieModel
from models.compte import CompteModel
from models.transaction import TransactionModel
from models.utilisateur import UtilisateurModel
from data.connexion_bdd import get_default_user_id, get_default_account_id

#Bibliotheques pour rajouter le md dialog pour le changement de mot de passe
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivy.uix.widget import Widget
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from controllers.template import AppScreen
from utils.event_bus import notify_budget_changed, notify_data_reset, notify_user_changed
from utils.preferences import preferences_manager




class PrefItem(MDCard):
    text = StringProperty("")
    secondary_text = StringProperty("")
    icon = StringProperty("information")
    tertiary_icon = StringProperty("chevron-right")
    icon_color = ColorProperty([0.1, 0.5, 0.8, 1])


class PrefSwitchItem(MDBoxLayout):
    text = StringProperty("")
    icon = StringProperty("information")
    icon_color = ColorProperty([0.1, 0.5, 0.8, 1])
    active = BooleanProperty(False)

    def on_switch_active(self, _switch, value):
        app = getattr(self, "app", None)
        if app is None:
            from kivy.app import App
            app = App.get_running_app()

        if not app or not hasattr(app, "theme_cls"):
            return

        new_theme = "Dark" if value else "Light"
        app.theme_cls.theme_style = new_theme
        
        # Sauvegarder le thème dans les préférences
        preferences_manager.set_theme(new_theme)


class ParametreScreen(MDBoxLayout):
    # Attributs pour la boîte de dialogue mot de passe
    _password_dialog = None
    _password_field_old = None
    _password_field_new = None
    
    # Attributs pour la boîte de dialogue budget
    _budget_dialog = None
    _budget_field = None
    _budget_switch = None
    
    # Attributs pour la boîte de dialogue à propos
    _about_dialog = None

    #Pour la reinitialisation de l'application
    _reset_notice_dialog = None
    _reset_password_dialog = None
    _reset_password_field = None

    def on_export_csv(self):
        try:
            transactions = TransactionModel.get_all()
            if not transactions:
                self._notify("Aucune transaction à exporter", "info")
                return

            os.makedirs("exports", exist_ok=True)
            filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join("exports", filename)

            fieldnames = [
                "id_transaction",
                "id_compte",
                "id_categorie",
                "montant",
                "type_transaction",
                "description",
                "date_transaction",
            ]

            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for t in transactions:
                    writer.writerow({k: t.get(k) for k in fieldnames})

            self._notify(f"Export CSV réussi : {filename}", "success")
        except Exception as e:
            self._notify(f"Erreur lors de l'export CSV : {e}", "error")

    def on_export_json(self):
        try:
            transactions = TransactionModel.get_all()
            categories = CategorieModel.get_all()

            budgets = []
            for account in CompteModel.get_all():
                budget = BudgetModel.get_by_account(account["id_compte"])
                if budget:
                    budgets.append(budget)

            os.makedirs("exports", exist_ok=True)
            filename = f"donnees_completes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join("exports", filename)

            data = {
                "export_date": datetime.now().isoformat(),
                "transactions": transactions,
                "categories": categories,
                "budgets": budgets,
            }

            with open(filepath, "w", encoding="utf-8") as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)

            self._notify(f"Export JSON réussi : {filename}", "success")
        except Exception as e:
            self._notify(f"Erreur lors de l'export JSON : {e}", "error")

    def _notify(self, message: str, type: str = "info"):
        """Affiche une notification à l'utilisateur"""
        node = self
        while node is not None and not hasattr(node, "notifier"):
            node = getattr(node, "parent", None)

        if node is not None and hasattr(node, "notifier"):
            node.notifier(message, type)
        else:
            # Fallback: afficher dans la console
            print(f"NOTIFICATION [{type.upper()}]: {message}")

    #Partie pour modifier le mot de passe=====================================================================================

    def on_modifier_mot_de_passe(self):
        """Affiche la boîte de dialogue pour modifier le mot de passe"""
        if self._password_dialog:
            return  # Évite d'ouvrir plusieurs dialogues

        # Créer les champs de saisie
        self._password_field_old = MDTextField(
            hint_text="Ancien mot de passe",
            password=True,
            mode="line",
            helper_text="Entrez votre mot de passe actuel",
            helper_text_mode="on_focus",
        )

        self._password_field_new = MDTextField(
            hint_text="Nouveau mot de passe",
            password=True,
            mode="line",
            helper_text="Choisissez un nouveau mot de passe",
            helper_text_mode="on_focus",
        )

        # Conteneur pour le contenu du dialogue
        content = MDBoxLayout(
            orientation="vertical",
            spacing="16dp",
            adaptive_height=True,
            size_hint_y=None,
        )
        content.add_widget(Widget(size_hint_y=None, height="10dp"))  # Espace vertical
        content.add_widget(self._password_field_old)
        content.add_widget(self._password_field_new)
        content.add_widget(Widget(size_hint_y=None, height="5dp"))  # Espace vertical

        # Créer le dialogue
        self._password_dialog = MDDialog(
            title="Modifier le mot de passe",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="Annuler",
                    on_release=self._fermer_dialogue_mot_de_passe,
                ),
                MDRaisedButton(
                    text="Confirmer",
                    on_release=self._confirmer_mot_de_passe,
                ),
            ],
            on_dismiss=self._nettoyer_dialogue_mot_de_passe,
        )
        self._password_dialog.open()

    def _confirmer_mot_de_passe(self, instance):
        """Traite la confirmation du changement de mot de passe"""
        old_pwd = self._password_field_old.text.strip()
        new_pwd = self._password_field_new.text.strip()

        if not old_pwd or not new_pwd:
            self._notify("Veuillez remplir les deux champs", "error")
            return

        # Récupérer l'ID de l'utilisateur actuel
        try:
            user_id = get_default_user_id()
            if not user_id:
                self._notify("Erreur: utilisateur non trouvé", "error")
                return
        except Exception as e:
            self._notify(f"Erreur lors de la récupération de l'utilisateur: {e}", "error")
            return
        
        # Récupérer l'utilisateur depuis la BDD
        try:
            utilisateur = UtilisateurModel.get_by_id(user_id)
            if not utilisateur:
                self._notify("Erreur: utilisateur invalide", "error")
                return
        except Exception as e:
            self._notify(f"Erreur lors de la lecture des données utilisateur: {e}", "error")
            return
        
        # Vérifier l'ancien mot de passe
        if old_pwd != utilisateur['mot_de_passe']:
            self._notify("Ancien mot de passe incorrect", "error")
            return
        
        # Mettre à jour le mot de passe
        try:
            success = UtilisateurModel.update_by_id(user_id, mot_de_passe=new_pwd)
            if success:
                self._notify("Mot de passe mis à jour avec succès", "success")
                # Notifier que les données utilisateur ont changé
                notify_user_changed()
                self._fermer_dialogue_mot_de_passe(None)
            else:
                self._notify("Erreur lors de la mise à jour du mot de passe", "error")
        except Exception as e:
            self._notify(f"Erreur lors de la mise à jour: {e}", "error")

    def _fermer_dialogue_mot_de_passe(self, instance):
        """Ferme le dialogue"""
        if self._password_dialog:
            self._password_dialog.dismiss()

    def _nettoyer_dialogue_mot_de_passe(self, *args):
        """Nettoie les références après fermeture"""
        self._password_dialog = None
        self._password_field_old = None
        self._password_field_new = None

    def on_definir_budget(self):
        """Affiche la boîte de dialogue pour définir un nouveau budget"""
        if self._budget_dialog:
            return  # Évite d'ouvrir plusieurs dialogues
        
        # Récupérer le budget actuel
        try:
            account_id = get_default_account_id()
            if not account_id:
                self._notify("Erreur: compte non trouvé", "error")
                return
            
            budget_data = BudgetModel.get_by_account(account_id)
            current_budget = budget_data['budget_total'] if budget_data else 60000
            
            # Calculer le reste du budget actuel
            montant_depenses = TransactionModel.get_total_by_type('SORTIE', account_id)
            montant_revenus = TransactionModel.get_total_by_type('ENTREE', account_id)
            montant_utilise = montant_depenses - montant_revenus
            reste_budget = current_budget - montant_utilise
            
        except Exception as e:
            self._notify(f"Erreur lors de la récupération du budget: {e}", "error")
            return
        
        # Créer le champ de saisie pour le nouveau budget
        self._budget_field = MDTextField(
            text=f"{current_budget}",
            mode="rectangle",
            input_filter="int",
            hint_text="Montant initial",
            helper_text="Montant total du budget mensuel",
            helper_text_mode="on_focus",
        )
        
        self._budget_switch = MDCheckbox(
            active=False,
            size_hint_x=None,
            width="48dp"
        )
        
        switch_label = MDLabel(
            text=f"Ajouter le reste du budget actuel : {reste_budget} FC",
            size_hint_x=1,
            adaptive_height=True,
            font_style="Caption"  # Options : H1, H2, H3, H4, H5, H6, Subtitle1, Subtitle2, Body1, Body2, Caption, Button
        )
        
        # Créer le conteneur pour le switch et le label
        switch_container = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            size_hint_y=None,
            padding="10dp",
            spacing="10dp"
        )
        
        switch_container.add_widget(self._budget_switch)
        switch_container.add_widget(switch_label)
        
        # Conteneur pour le contenu du dialogue
        content = MDBoxLayout(
            orientation="vertical",
            spacing="16dp",
            adaptive_height=True,
            size_hint_y=None,
        )
        content.add_widget(Widget(size_hint_y=None, height="10dp"))  # Espace vertical
        content.add_widget(self._budget_field)
        content.add_widget(switch_container)
        content.add_widget(Widget(size_hint_y=None, height="5dp"))  # Espace vertical
        
        # Créer le dialogue
        self._budget_dialog = MDDialog(
            title="Définir un nouveau budget",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="Annuler",
                    on_release=self._fermer_dialogue_budget,
                ),
                MDRaisedButton(
                    text="Confirmer",
                    on_release=self._confirmer_budget,
                ),
            ],
            on_dismiss=self._nettoyer_dialogue_budget,
        )
        self._budget_dialog.open()
    
    def _confirmer_budget(self, instance):
        """Traite la confirmation du nouveau budget"""
        try:
            new_budget_text = self._budget_field.text.strip()
            if not new_budget_text:
                self._notify("Veuillez entrer un montant", "error")
                return
            
            new_budget = int(new_budget_text)
            if new_budget < 0:
                self._notify("Le budget ne peut pas être négatif", "error")
                return
            
            # Récupérer le compte et le reste actuel
            account_id = get_default_account_id()
            if not account_id:
                self._notify("Erreur: compte non trouvé", "error")
                return
            
            budget_data = BudgetModel.get_by_account(account_id)
            current_budget = budget_data['budget_total'] if budget_data else 60000
            
            montant_depenses = TransactionModel.get_total_by_type('SORTIE', account_id)
            montant_revenus = TransactionModel.get_total_by_type('ENTREE', account_id)
            montant_utilise = montant_depenses - montant_revenus
            reste_budget = current_budget - montant_utilise
            
            # Si la case est cochée, ajouter le reste au nouveau budget
            if self._budget_switch.active:
                new_budget += reste_budget
                message = f"Nouveau budget : {new_budget} FC (incluant {reste_budget} FC restants)"
            else:
                message = f"Nouveau budget : {new_budget} FC"
            
            # Mettre à jour dans la BDD
            success = BudgetModel.update_by_account(account_id, budget_total=new_budget)
            if success:
                # Réinitialiser les dépenses actuelles si défini depuis les paramètres
                # (contrairement à la modification depuis la page Budget qui les conserve)
                self._reinitialiser_depenses_si_necessaire(account_id)
                
                self._notify(message, "success")
                # Notifier que le budget a changé
                notify_budget_changed(new_budget, account_id)
                self._fermer_dialogue_budget(None)
                
                # Rafraîchir la page Budget si elle existe
                self._rafraichir_page_budget()
            else:
                self._notify("Erreur lors de la mise à jour du budget", "error")
                
        except ValueError:
            self._notify("Veuillez entrer un nombre valide", "error")
        except Exception as e:
            self._notify(f"Erreur lors de la mise à jour: {e}", "error")
    
    def _reinitialiser_depenses_si_necessaire(self, account_id):
        """Réinitialise complètement toutes les transactions pour un nouveau budget défini depuis les paramètres"""
        from models.transaction import TransactionModel
        
        # Supprimer TOUTES les transactions (dépenses ET revenus) pour un nouveau départ
        try:
            success = TransactionModel.delete_by_account(account_id)
            if success:
                self._notify("Toutes les transactions ont été réinitialisées pour le nouveau budget", "info")
        except Exception as e:
            self._notify(f"Erreur lors de la réinitialisation des transactions: {e}", "error")

    def _fermer_dialogue_budget(self, instance):
        """Ferme le dialogue budget"""
        if self._budget_dialog:
            self._budget_dialog.dismiss()
    
    def _nettoyer_dialogue_budget(self, *args):
        """Nettoie les références après fermeture"""
        self._budget_dialog = None
        self._budget_field = None
        self._budget_switch = None

    #REINITIALISER L'APPLICATION=====================================================================================
    def demander_confirmation_reinitialisation(self):
        if self._reset_notice_dialog:
            return

        self._reset_notice_dialog = MDDialog(
            title="Réinitialisation du budget",
            text=(
                "⚠️ Attention !\n\n"
                "Cette action va :\n"
                "• Supprimer toutes les transactions\n"
                "• Remettre le solde du compte à zéro\n"
                "• Réinitialiser tous les budgets à 0\n"
                "• Réinitialiser les statistiques et analyses\n\n"
                "Les catégories et le compte seront conservés.\n\n"
                "Souhaitez-vous continuer ?"
            ),
            buttons=[
                MDRaisedButton(
                    text="Annuler",
                    on_release=self._annuler_notice_reset
                ),
                MDRaisedButton(
                    text="Continuer",
                    on_release=self._ouvrir_dialog_mot_de_passe
                ),
            ],
            on_dismiss=self._nettoyer_notice_reset
        )

        self._reset_notice_dialog.open()



    def on_reinitialiser_donnes(self, instance):
        """Réinitialise les transactions et remet le solde à zéro"""
        try:
            success = UtilisateurModel.reinitialiser_donnes()

            if success:
                self._notify(
                    "Le budget a été réinitialisé avec succès. Toutes les données ont été effacées.",
                    "success"
                )

                # Notifier tous les écrans que les données ont été réinitialisées
                notify_data_reset()
                
                # Notifier l'application que les données ont changé
                self._rafraichir_application()
            else:
                self._notify(
                    "La réinitialisation a échoué.",
                    "error"
                )

        except Exception as e:
            print("Erreur ParametreScreen:", e)
            self._notify(
                "Une erreur est survenue lors de la réinitialisation.",
                "error"
            )

    #RAFRAICHIR LES PAGES APRES SURPPRESSION DES DONNEES=====================================================================================================================
    def _rafraichir_application(self):
        """
        Informe les autres écrans que les données ont changé
        """
        from kivy.app import App
        app = App.get_running_app()

        if hasattr(app, "on_budget_reinitialise"):
            app.on_budget_reinitialise()

    def _annuler_notice_reset(self, instance):
        """Annule la notice de réinitialisation"""
        if self._reset_notice_dialog:
            self._reset_notice_dialog.dismiss()

    def _nettoyer_notice_reset(self, *args):
        """Nettoie les références après fermeture de la notice"""
        self._reset_notice_dialog = None

    def _ouvrir_dialog_mot_de_passe(self, instance):
        """Ouvre le dialogue de saisie du mot de passe pour confirmation"""
        if self._reset_password_dialog:
            return  # Évite d'ouvrir plusieurs dialogues

        # Fermer d'abord la notice
        self._annuler_notice_reset(None)

        # Créer le champ de saisie du mot de passe
        self._reset_password_field = MDTextField(
            hint_text="Mot de passe",
            password=True,
            mode="line",
            helper_text="Entrez votre mot de passe pour confirmer",
            helper_text_mode="on_focus",
        )

        # Conteneur pour le contenu du dialogue
        content = MDBoxLayout(
            orientation="vertical",
            spacing="16dp",
            adaptive_height=True,
            size_hint_y=None,
        )
        content.add_widget(Widget(size_hint_y=None, height="10dp"))  # Espace vertical
        content.add_widget(self._reset_password_field)
        content.add_widget(Widget(size_hint_y=None, height="5dp"))  # Espace vertical

        # Créer le dialogue
        self._reset_password_dialog = MDDialog(
            title="Confirmation requise",
            text="Veuillez entrer votre mot de passe pour confirmer la réinitialisation.",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="Annuler",
                    on_release=self._annuler_reset_password,
                ),
                MDRaisedButton(
                    text="Confirmer",
                    on_release=self._confirmer_reset_password,
                ),
            ],
            on_dismiss=self._nettoyer_reset_password,
        )
        self._reset_password_dialog.open()

    def _annuler_reset_password(self, instance):
        """Annule le dialogue de mot de passe"""
        if self._reset_password_dialog:
            self._reset_password_dialog.dismiss()

    def _confirmer_reset_password(self, instance):
        """Vérifie le mot de passe et procède à la réinitialisation"""
        pwd = self._reset_password_field.text.strip()

        if not pwd:
            self._notify("Veuillez entrer votre mot de passe", "error")
            return

        # Récupérer l'ID de l'utilisateur actuel
        try:
            user_id = get_default_user_id()
            if not user_id:
                self._notify("Erreur: utilisateur non trouvé", "error")
                return
        except Exception as e:
            self._notify(f"Erreur lors de la récupération de l'utilisateur: {e}", "error")
            return
        
        # Récupérer l'utilisateur depuis la BDD
        try:
            utilisateur = UtilisateurModel.get_by_id(user_id)
            if not utilisateur:
                self._notify("Erreur: utilisateur invalide", "error")
                return
        except Exception as e:
            self._notify(f"Erreur lors de la lecture des données utilisateur: {e}", "error")
            return
        
        # Vérifier le mot de passe
        if pwd != utilisateur['mot_de_passe']:
            self._notify("Mot de passe incorrect", "error")
            return
        
        # Fermer le dialogue et procéder à la réinitialisation
        self._annuler_reset_password(None)
        self.on_reinitialiser_donnes(None)

    def _nettoyer_reset_password(self, *args):
        """Nettoie les références après fermeture du dialogue mot de passe"""
        self._reset_password_dialog = None
        self._reset_password_field = None

    def _rafraichir_page_budget(self):
        """Rafraîchit la page Budget si elle existe"""
        try:
            from kivy.app import App
            app = App.get_running_app()
            
            # Accès direct et immédiat au BudgetScreen
            if hasattr(app, 'root') and app.root:
                root = app.root
                if hasattr(root, 'ids') and 'budget_screen' in root.ids:
                    budget_screen = root.ids.budget_screen
                    print("BudgetScreen trouvé, rafraîchissement ultra-rapide")
                    # Rafraîchissement direct sans délai
                    budget_screen.charger_donnees_depuis_bdd()
                    budget_screen.recalculer_depenses()
                    # Forcer la mise à jour instantanée de l'affichage
                    if hasattr(budget_screen, 'rafraichir_instantane'):
                        budget_screen.rafraichir_instantane()
                    print("BudgetScreen rafraîchi instantanément")
                    return
                    
        except Exception as e:
            print(f"Erreur lors du rafraîchissement: {e}")

    def on_afficher_a_propos(self):
        """Affiche les informations sur l'application MonBudget"""
        if self._about_dialog:
            return  # Évite d'ouvrir plusieurs dialogues

        # Contenu du dialogue
        content = MDBoxLayout(
            orientation="vertical",
            spacing="16dp",
            adaptive_height=True,
            size_hint_y=None,
            padding="20dp"
        )
        
        # Titre principal
        title_label = MDLabel(
            text="Mon Budget – Version 1",
            font_style="H5",
            theme_text_color="Primary",
            halign="center",
            size_hint_y=None,
            height="40dp"
        )
        content.add_widget(title_label)
        
        # Séparateur simple
        content.add_widget(Widget(size_hint_y=None, height="1dp"))
        
        # Sous-titre Conçu par
        concept_label = MDLabel(
            text="Conçu par :",
            font_style="Subtitle1",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height="30dp"
        )
        content.add_widget(concept_label)
        
        # Liste des développeurs
        developpeurs = [
            "Jean-Charles Nawej",
            "Nathan Monga", 
            "Martha Kalemba",
            "Salem Ohelo",
            "Timothée Mukash"
        ]
        
        for dev in developpeurs:
            dev_label = MDLabel(
                text=f"• {dev}",
                font_style="Body1",
                theme_text_color="Primary",
                halign="center",
                size_hint_y=None,
                height="25dp"
            )
            content.add_widget(dev_label)
        
        # Séparateur simple
        content.add_widget(Widget(size_hint_y=None, height="1dp"))
        
        # Information académique
        info_label = MDLabel(
            text="Étudiants en L3 Sciences Informatiques\nà l'Université Catholique du Congo (UCC)\nDans le cadre du cours de Programmation 3\nAnnée académique : 2025-2026",
            font_style="Body2",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height="80dp"
        )
        content.add_widget(info_label)
        
        # Créer le dialogue
        self._about_dialog = MDDialog(
            title="À propos",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="Fermer",
                    on_release=self._fermer_dialogue_a_propos,
                ),
            ],
            on_dismiss=self._nettoyer_dialogue_a_propos,
        )
        self._about_dialog.open()
    
    def _fermer_dialogue_a_propos(self, instance):
        """Ferme le dialogue à propos"""
        if self._about_dialog:
            self._about_dialog.dismiss()
    
    def _nettoyer_dialogue_a_propos(self, *args):
        """Nettoie les références après fermeture"""
        self._about_dialog = None
