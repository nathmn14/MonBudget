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
        
        try:
            summary_text = self.generate_budget_summary(budget_data)
            
            from kivymd.app import MDApp
            from kivy.metrics import dp
            from kivymd.uix.floatlayout import MDFloatLayout
            from kivymd.uix.button import MDFillRoundFlatIconButton, MDIconButton
            from kivymd.uix.label import MDLabel
            
            app = MDApp.get_running_app()
            is_dark = app.theme_cls.theme_style == "Dark"
            text_color = (1, 1, 1, 1) if is_dark else (0.1, 0.1, 0.1, 1)
            
            # Récupérer la couleur d'accent du dashboard/app
            accent_color = [0.1, 0.5, 0.8, 1] # Bleu par défaut
            if hasattr(app, 'custom_colors'):
                accent_color = app.custom_colors[app.theme_cls.theme_style].get("accent", accent_color)
            
            # Conteneur principal
            content = MDFloatLayout(size_hint_y=None, height=dp(420))
            
            # Bouton fermer (Haut Droite)
            btn_close = MDIconButton(
                icon="close",
                pos_hint={'top': 1, 'right': 1},
                on_release=lambda x: self.close_dialog(on_close)
            )
            content.add_widget(btn_close)
            
            # Titre
            title_lbl = MDLabel(
                text="Résumé du Budget",
                halign="center",
                font_style="H6",
                bold=True,
                theme_text_color="Primary",
                pos_hint={'center_x': 0.5, 'center_y': 0.85},
                adaptive_height=True
            )
            content.add_widget(title_lbl)
            
            # Zone de texte (Scrollable)
            scroll = MDScrollView(
                size_hint=(0.9, None),
                height=dp(200),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            
            txt_box = MDCard(
                orientation="vertical",
                padding=dp(15),
                size_hint_y=None,
                adaptive_height=True,
                md_bg_color=(0.2, 0.2, 0.2, 0.2) if is_dark else (0, 0, 0, 0.05),
                radius=[15,],
                elevation=0
            )
            
            msg_lbl = MDLabel(
                text=summary_text,
                theme_text_color="Custom",
                text_color=text_color,
                font_style="Body1",
                adaptive_height=True,
                markup=True
            )
            
            txt_box.add_widget(msg_lbl)
            scroll.add_widget(txt_box)
            content.add_widget(scroll)
            
            # BOUTON MODERNE (Pareil que Modifier le budget)
            btn_play = MDFillRoundFlatIconButton(
                text="ÉCOUTER LE RÉSUMÉ",
                icon="volume-high",
                pos_hint={'center_x': 0.5, 'y': 0.05},
                size_hint_x=0.9,
                height=dp(48),
                md_bg_color=accent_color,
                text_color=(1, 1, 1, 1),
                elevation=0.5,
                on_release=lambda x: self.speak_summary(summary_text)
            )
            content.add_widget(btn_play)
            
            self.current_dialog = MDDialog(
                type="custom",
                content_cls=content,
                size_hint=(0.9, None),
                radius=[28, 28, 28, 28]
            )
            
            return self.current_dialog
            
        except Exception as e:
            print(f"ERROR in create_summary_popup: {e}")
            return None
            
        except Exception as e:
            print(f"[BUDGET-RESUME] CRASH: {e}")
            import traceback
            traceback.print_exc()
            return None
            
        except Exception as e:
            print(f"CRITICAL ERROR in create_summary_popup: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
