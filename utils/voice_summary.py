# Utilitaires pour la synthèse vocale
import pyttsx3
import threading
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import MDScrollView
from kivymd.app import MDApp

class VoiceSummary:
    """Classe pour gérer la synthèse vocale des résumés budgétaires"""
    
    def __init__(self):
        self.engine = None
        self.is_speaking = False
        self.current_dialog = None
        print("DEBUG: Initialisation de VoiceSummary")
        self._init_engine()
        print(f"DEBUG: VoiceSummary initialisé, engine={self.engine is not None}")
    
    def _init_engine(self):
        """Initialise le moteur de synthèse vocale"""
        try:
            self.engine = pyttsx3.init()
            # Configuration pour une belle voix en français
            voices = self.engine.getProperty('voices')
            
            # Choisir une voix française si disponible
            french_voice_found = False
            for voice in voices:
                if 'french' in voice.name.lower() or 'français' in voice.name.lower() or 'fr' in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    french_voice_found = True
                    break
            
            # Si pas de voix française, utiliser la première voix féminine disponible
            if not french_voice_found:
                for voice in voices:
                    if 'female' in voice.name.lower() or 'femme' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            # Ajuster la vitesse et le volume pour une écoute agréable en français
            self.engine.setProperty('rate', 140)  # Vitesse modérée pour le français
            self.engine.setProperty('volume', 0.9)  # Volume élevé mais pas maximum
            
        except Exception as e:
            print(f"Erreur d'initialisation de la synthèse vocale: {e}")
            self.engine = None
    
    def generate_budget_summary(self, budget_data):
        """Génère le texte du résumé budgétaire en français CDF"""
        try:
            budget_total = budget_data.get('budget_total', 0)
            montant_utilise = budget_data.get('montant_utilise', 0)
            montant_restant = budget_data.get('montant_restant', 0)
            pourcentage_utilise = budget_data.get('pourcentage_utilise', 0)
            depenses_journalieres = budget_data.get('depenses_journalieres', 0)
            jours_restants = budget_data.get('jours_restants', 0)
            
            # Formater les montants pour la lecture en français
            def format_montant_vocal(montant):
                if montant == int(montant):
                    return f"{int(montant):,}".replace(",", " ")
                else:
                    return f"{montant:,.2f}".replace(",", " ").replace(".", ",")
            
            budget_formate = format_montant_vocal(budget_total)
            utilise_formate = format_montant_vocal(montant_utilise)
            restant_formate = format_montant_vocal(montant_restant)
            journalier_formate = format_montant_vocal(depenses_journalieres)
            
            # Construire le résumé en français naturel
            summary = f"""
Bonjour ! Voici le résumé de votre budget en Francs Congolais.

Votre budget mensuel total est de {budget_formate} Francs Congolais.

Vous avez déjà utilisé {utilise_formate} Francs Congolais, 
ce qui représente {pourcentage_utilise:.1f} pour cent de votre budget.

Il vous reste {restant_formate} Francs Congolais à dépenser.

Avec {jours_restants} jours restants dans le mois, 
votre budget journalier disponible est de {journalier_formate} Francs Congolais par jour.

{"Attention, votre budget est presque épuisé !" if pourcentage_utilise > 80 else "Votre budget est bien géré."}

Merci d'avoir consulté votre résumé budgétaire.
            """.strip()
            
            return summary
            
        except Exception as e:
            return f"Erreur lors de la génération du résumé: {e}"
    
    def create_summary_popup(self, budget_data, on_close=None):
        """Crée un popup élégant pour le résumé vocal"""
        
        # Générer le texte du résumé
        summary_text = self.generate_budget_summary(budget_data)
        
        # Créer le contenu du popup avec un design amélioré et support du thème
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        is_dark_theme = app.theme_cls.theme_style == "Dark"
        
        # Couleurs adaptatives selon le thème
        if is_dark_theme:
            bg_color = (0.2, 0.2, 0.2, 1)  # Gris foncé pour thème sombre
            card_bg_color = (0.15, 0.15, 0.15, 1)  # Gris plus foncé pour la carte
            text_color = (1, 1, 1, 1)  # Texte blanc
        else:
            bg_color = (1, 1, 1, 1)  # Blanc pour thème clair
            card_bg_color = (0.95, 0.95, 0.95, 1)  # Gris clair pour la carte
            text_color = (0, 0, 0, 1)  # Texte noir
        
        # Layout principal (pas de MDCard ici)
        content = MDBoxLayout(
            orientation="vertical",
            spacing="15dp",
            padding="20dp",
            size_hint_y=None,
            height="420dp",
            md_bg_color=bg_color
        )
        
        # Titre avec icône
        title_label = MDLabel(
            text="Résumé Vocal du Budget",
            font_style="H6",
            theme_text_color="Primary",
            bold=True,
            halign="center",
            size_hint_y=None,
            height="50dp"
        )
        
        # Texte du résumé dans une carte avec scroll et couleurs adaptatives
        summary_card = MDCard(
            orientation="vertical",
            padding="15dp",
            size_hint_y=None,
            height="180dp",
            md_bg_color=card_bg_color,
            elevation=2,
            radius=[10, 10, 10, 10]
        )
        
        # Créer le scrollview pour le texte
        scroll_view = MDScrollView(
            size_hint_y=None,
            height="150dp"
        )
        
        # Layout pour le contenu scrollable
        scroll_content = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            adaptive_height=True
        )
        
        summary_label = MDLabel(
            text=summary_text,
            theme_text_color="Secondary",  # Utilise le thème automatiquement
            text_size=(280, None),  # Largeur maximale pour le texte
            halign="left",  # Aligné à gauche pour meilleure lisibilité
            valign="top",
            font_style="Body1",
            adaptive_height=True,
            padding=(10, 5),
            color=text_color  # Couleur explicite pour garantir la lisibilité
        )
        
        scroll_content.add_widget(summary_label)
        scroll_view.add_widget(scroll_content)
        summary_card.add_widget(scroll_view)
        
        # Boutons de contrôle dans une layout horizontale
        button_layout = MDBoxLayout(
            orientation="horizontal",
            spacing="10dp",
            size_hint_y=None,
            height="50dp"
        )
        
        play_button = MDRaisedButton(
            text="Lire",
            icon="volume-high",
            on_release=lambda x: self.speak_summary(summary_text),
            md_bg_color=(0.1, 0.7, 0.3, 1),  # Vert pour l'action
            size_hint_x=0.5
        )
        
        stop_button = MDRaisedButton(
            text="Arrêter",
            icon="stop",
            on_release=lambda x: (
                print("DEBUG: Bouton Arrêter cliqué"),
                self.stop_speaking()
            ),
            md_bg_color=(0.9, 0.3, 0.3, 1),  # Rouge pour l'arrêt
            size_hint_x=0.5
        )
        
        button_layout.add_widget(play_button)
        button_layout.add_widget(stop_button)
        
        # Bouton fermer
        close_button = MDFlatButton(
            text="Fermer",
            on_release=lambda x: self.close_dialog(on_close),
            theme_text_color="Primary",
            size_hint_y=None,
            height="40dp"
        )
        
        # Assembler le contenu
        content.add_widget(title_label)
        content.add_widget(summary_card)
        content.add_widget(button_layout)
        content.add_widget(close_button)
        
        # Créer le dialog avec un design moderne (pas de double MDCard)
        self.current_dialog = MDDialog(
            title="",  # Pas de titre dans le dialog, titre dans le contenu
            type="custom",
            content_cls=content,
            size_hint=(0.9, None),
            height="460dp",
            radius=[20, 20, 20, 20]
        )
        
        return self.current_dialog
    
    def speak_summary(self, text):
        """Lit le résumé à voix haute"""
        print(f"DEBUG: speak_summary appelé, is_speaking={self.is_speaking}")
        if not self.engine:
            self._show_error("Moteur vocal non disponible")
            return
        
        if self.is_speaking:
            print("DEBUG: Arrêt de la lecture en cours avant de commencer")
            self.stop_speaking()
            # Attendre un court instant pour que l'arrêt soit effectif
            import time
            time.sleep(0.05)  # Très court pour éviter le blocage
        
        def speak_in_thread():
            try:
                print("DEBUG: Début de la lecture dans le thread")
                self.is_speaking = True
                self.engine.say(text)
                self.engine.runAndWait()
                self.is_speaking = False
                print("DEBUG: Lecture terminée avec succès")
            except Exception as e:
                self.is_speaking = False
                print(f"DEBUG: Erreur lors de la lecture: {e}")
        
        # Lancer dans un thread séparé pour ne pas bloquer l'UI
        thread = threading.Thread(target=speak_in_thread, daemon=True)
        thread.start()
        print("DEBUG: Thread de lecture démarré")
    
    def stop_speaking(self):
        """Arrête la lecture en cours"""
        print(f"DEBUG: stop_speaking appelé, engine={self.engine is not None}, is_speaking={self.is_speaking}")
        
        if self.engine is None:
            print("DEBUG: Moteur vocal non initialisé")
            return
            
        try:
            # Forcer l'arrêt de toutes les lectures en cours
            self.engine.stop()
            self.is_speaking = False
            print("DEBUG: Commande stop envoyée au moteur vocal")
            
            # Pas de time.sleep() pour ne pas bloquer l'interface
            # La méthode stop() de pyttsx3 est synchrone et rapide
            
            print("DEBUG: Lecture arrêtée avec succès")
            
        except Exception as e:
            print(f"DEBUG: Erreur lors de l'arrêt: {e}")
            self.is_speaking = False
    
    def close_dialog(self, on_close=None):
        """Ferme le popup"""
        if self.current_dialog:
            self.stop_speaking()
            self.current_dialog.dismiss()
            self.current_dialog = None
        
        if on_close:
            on_close()
    
    def _show_error(self, message):
        """Affiche un message d'erreur"""
        app = MDApp.get_running_app()
        if hasattr(app.root, 'notifier'):
            app.root.notifier(message, "error")
