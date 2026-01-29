
# Utilitaires pour les transactions vocales (Cross-plateforme: Windows, Linux, Android)
import threading
import re
import os
from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFloatingActionButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.app import MDApp
from kivy.animation import Animation
from kivy.metrics import dp

# Modèles et Données
from models.transaction import TransactionModel
from models.categorie import CategorieModel
from data.connexion_bdd import get_default_account_id
from utils.event_bus import notify_transaction_added

# Moteur vocal universel
from utils.voice_engine import voice_engine

class VoiceTransaction:
    """Gestionnaire de transactions vocales avec interface moderne"""
    
    def __init__(self):
        self.engine = None
        self.current_dialog = None
        self.is_listening = False
        self._init_tts_engine()
        
    def _init_tts_engine(self):
        """Initialisé via VoiceEngine maintenant"""
        pass
    
    def create_transaction_popup(self, on_close=None):
        """Crée l'interface utilisateur style Google Assistant"""
        
        # Thème
        app = MDApp.get_running_app()
        is_dark = app.theme_cls.theme_style == "Dark"
        bg_color = (0.12, 0.12, 0.12, 1) if is_dark else (0.98, 0.98, 0.98, 1)
        text_color = (1, 1, 1, 1) if is_dark else (0.1, 0.1, 0.1, 1)
        
        # Conteneur principal
        content = MDFloatLayout(
            size_hint_y=None,
            height="350dp"
        )
        
        # 1. Zone de texte dynamique (Ce que l'utilisateur dit)
        self.lbl_feedback = MDLabel(
            text="Comment puis-je vous aider ?",
            halign="center",
            font_style="H5",
            theme_text_color="Custom",
            text_color=text_color,
            pos_hint={'center_x': .5, 'center_y': .85},
            bold=True
        )
        
        # 2. Sous-titre (Instructions ou Statut)
        self.lbl_status = MDLabel(
            text="Touchez le micro et parlez...",
            halign="center",
            font_style="Body1",
            theme_text_color="Secondary",
            pos_hint={'center_x': .5, 'center_y': .75},
        )
        
        # 3. Suggestions
        self.card_suggestion = MDCard(
            orientation="vertical",
            size_hint=(0.8, None),
            height="50dp",
            pos_hint={'center_x': .5, 'center_y': .55},
            radius=[15,],
            padding="10dp",
            md_bg_color=(0.2, 0.2, 0.2, 0.05) if not is_dark else (1, 1, 1, 0.05)
        )
        self.lbl_suggestion = MDLabel(
            text='"Dépense 5000 pour Restaurant"',
            halign="center",
            font_style="Caption",
            italic=True,
            theme_text_color="Secondary"
        )
        self.card_suggestion.add_widget(self.lbl_suggestion)
        
        # 4. Le bouton Micro Pulsant (Cœur de l'UI)
        self.btn_micro = MDFloatingActionButton(
            icon="microphone",
            type="large",
            md_bg_color=app.theme_cls.primary_color,
            pos_hint={'center_x': .5, 'center_y': .25},
            elevation=4,
            on_release=lambda x: self.toggle_listening()
        )
        
        # Bouton fermer discret
        btn_close = MDIconButton(
            icon="close",
            pos_hint={'top': 1, 'right': 1},
            on_release=lambda x: self.close_dialog(on_close)
        )
        
        # Ajout des widgets
        content.add_widget(btn_close)
        content.add_widget(self.lbl_feedback)
        content.add_widget(self.lbl_status)
        content.add_widget(self.card_suggestion)
        content.add_widget(self.btn_micro)
        
        # Création du dialogue
        self.current_dialog = MDDialog(
            type="custom",
            content_cls=content,
            size_hint=(0.9, None),
            radius=[28, 28, 28, 28]
        )
        
        return self.current_dialog

    def toggle_listening(self):
        """Active ou désactive l'écoute"""
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()

    def start_listening(self):
        """Lance l'écoute via VoiceEngine (Cross-plateforme)"""
        if self.is_listening:
            return
            
        self.is_listening = True
        self.update_ui_state("listening")
        
        # On passe les callbacks à l'engine
        voice_engine.listen(
            on_result=self._on_speech_success,
            on_error=self._on_speech_error,
            on_status=self.update_ui_state
        )

    def _on_speech_success(self, text):
        """Callback quand l'engine a compris du texte"""
        self.is_listening = False
        Clock.schedule_once(lambda dt: self.update_ui_state("processing"))
        # Traitement différé pour laisser l'UI souffler
        Clock.schedule_once(lambda dt: self.process_command(text), 0.5)

    def _on_speech_error(self, error_msg):
        """Callback en cas d'erreur ou non compréhension"""
        self.is_listening = False
        Clock.schedule_once(lambda dt: self.update_ui_state("error", error_msg))

    def stop_listening(self):
        """Arrête l'écoute (le feedback visuel)"""
        self.is_listening = False
        self.update_ui_state("idle")

    # _listen_thread_powershell a été supprimé car remplacé par VoiceEngine logic

    def process_command(self, text):
        """Analyse la commande vocale et extrait les infos"""
        text = text.lower()
        if not text:
            Clock.schedule_once(lambda dt: self.update_ui_state("error", "Rien compris."))
            return
            
        Clock.schedule_once(lambda dt: setattr(self.lbl_feedback, 'text', f'"{text}"'))
        
        # 1. Extraction du Montant
        montant_match = re.search(r'(\d+[\s\.,]?\d*)', text)
        if not montant_match:
            # Essayer de convertir des mots chiffres simples si nécessaire (optionnel)
            Clock.schedule_once(lambda dt: self.update_ui_state("error", "Montant manquant."))
            self.speak("Je n'ai pas compris le montant.")
            return

        montant_str = montant_match.group(1).replace(' ', '').replace(',', '.')
        # Nettoyage additionnel (ex: points multiples)
        if montant_str.count('.') > 1: montant_str = montant_str.replace('.', '', montant_str.count('.')-1)
            
        try:
            montant = float(montant_str)
        except ValueError:
             Clock.schedule_once(lambda dt: self.update_ui_state("error", "Montant invalide."))
             return

        # 2. Extraction du Type
        type_transac = "SORTIE"
        mots_entree = ["revenu", "gagné", "salaire", "ajouté", "reçu", "entrée", "depôt"]
        if any(mot in text for mot in mots_entree):
            type_transac = "ENTREE"

        # 3. Extraction de la Catégorie
        # On définit les mots à ignorer (monnaies, verbes, articles)
        monnaies = ["euros", "fc", "dollars", "francs", "congolais", "franc", "dollar", "euro"]
        stopwords = ["ajouter", "dépense", "depense", "revenu", "pour", "de", "dans", "le", "la", "un", "une", "argent", "budget"] + monnaies
        
        # On récupère toutes les catégories existantes pour tenter un match exact/partiel
        all_categories = CategorieModel.get_all()
        categorie_nom = "Divers"
        
        # Tentative 1 : Chercher si un nom de catégorie existante est présent dans le texte
        text_sans_montant = text.replace(montant_match.group(0), ' ')
        for cat in all_categories:
            nom_cat = cat['nom_categorie'].lower()
            if nom_cat in text_sans_montant and len(nom_cat) > 2:
                categorie_nom = cat['nom_categorie']
                break
        else:
            # Tentative 2 : Extraction par mots-clés si aucune catégorie connue n'est trouvée
            # On nettoie les monnaies spécifiquement pour éviter les résidus (ex: 5000fc)
            clean_text = re.sub(r'|'.join([rf'\b{m}\b' for m in monnaies]), '', text_sans_montant)
            
            tokens = clean_text.split()
            categorie_mots = [word for word in tokens if word not in stopwords and len(word) >= 2]
            
            if categorie_mots:
                # On prend la première suite de mots après le montant ou la plus pertinente
                categorie_nom = " ".join(categorie_mots).capitalize()
            
        id_compte = get_default_account_id()
        categorie_finale = self._get_or_create_category(categorie_nom, id_compte)
        
        if not categorie_finale:
             Clock.schedule_once(lambda dt: self.update_ui_state("error", "Erreur catégorie."))
             return

        # 4. Création
        self._save_transaction(montant, type_transac, categorie_finale, text)

    def _save_transaction(self, montant, type_transac, categorie, description_vocale):
        """Sauvegarde en BDD"""
        id_compte = get_default_account_id()
        try:
            # On utilise le nom de la catégorie comme description (Note)
            desc = categorie['nom_categorie']
            
            TransactionModel.create(
                id_compte=id_compte,
                montant=montant,
                type_transaction=type_transac,
                id_categorie=categorie['id_categorie'],
                description=desc,
                date_transaction=None
            )
            
            msg = f"{'Ajouté' if type_transac == 'ENTREE' else 'Dépensé'} : {montant} FC\nCatégorie : {categorie['nom_categorie']}"
            Clock.schedule_once(lambda dt: self.update_ui_state("success", msg))
            
            notify_transaction_added({
                'montant': montant,
                'type': type_transac,
                'description': desc,
                'categorie': categorie['nom_categorie']
            })
            
            self.speak(f"Compris. {montant} francs pour {categorie['nom_categorie']}.")
            Clock.schedule_once(lambda dt: self.close_dialog(), 2.5)
            
        except Exception as e:
            print(f"Erreur save DB: {e}")
            Clock.schedule_once(lambda dt: self.update_ui_state("error", "Erreur sauvegarde."))

    def _get_or_create_category(self, cat_name, id_compte):
        """Logique catégorie"""
        # Note: Dans votre modèle actuel, get_all() ne prend pas d'arguments (id_compte)
        all_cats = CategorieModel.get_all()
        
        for cat in all_cats:
            if cat['nom_categorie'].lower() == cat_name.lower():
                return cat
        
        for cat in all_cats:
            if cat_name.lower() in cat['nom_categorie'].lower():
                return cat

        import random
        # Palette de couleurs vives
        colors = ["0.9,0.3,0.3,1", "0.3,0.9,0.3,1", "0.3,0.3,0.9,1", "0.9,0.9,0.3,1", "0.9,0.3,0.9,1", "0.3,0.9,0.9,1"]
        
        icon = "tag"
        lname = cat_name.lower()
        if any(x in lname for x in ["resto", "manger", "food", "repas"]): icon = "food"
        elif any(x in lname for x in ["auto", "bus", "train", "uber"]): icon = "car"
        elif any(x in lname for x in ["maison", "loyer", "meuble"]): icon = "home"
        elif any(x in lname for x in ["santé", "medecin", "pharma"]): icon = "medical-bag"
        elif any(x in lname for x in ["jeu", "film", "ciné"]): icon = "gamepad-variant"
        
        CategorieModel.create(
            nom=cat_name, # Changé de nom_categorie à nom selon la signature de CategorieModel.create
            type_transaction="SORTIE", # Ajouté argument obligatoire
            icone=icon,
            couleur=random.choice(colors) # Changé couleur_icone à couleur
        )
        
        all_cats = CategorieModel.get_all()
        for cat in all_cats:
            if cat['nom_categorie'] == cat_name:
                return cat
        return all_cats[-1] if all_cats else None

    def update_ui_state(self, state, message=""):
        """Gère les animations et textes"""
        if not self.current_dialog: 
            return
            
        if state == "idle":
            self.lbl_status.text = "Touchez pour parler"
            self.btn_micro.md_bg_color = (0.2, 0.6, 1, 1)
            self.btn_micro.icon = "microphone"
            self._stop_animations(self.btn_micro)
            
        elif state == "listening":
            self.lbl_status.text = "Préparation..."
            self.lbl_feedback.text = "..."
            self.btn_micro.md_bg_color = (1, 0.7, 0, 1)

        elif state == "listening_active":
            self.lbl_status.text = "Je vous écoute..."
            self.lbl_feedback.text = "Parlez maintenant"
            self.btn_micro.md_bg_color = (0.9, 0.2, 0.2, 1)
            self.btn_micro.icon = "record-circle-outline"
            self._animate_pulse(self.btn_micro)

        elif state == "processing":
            self.lbl_status.text = "Analyse en cours..."
            self.btn_micro.md_bg_color = (0.5, 0.5, 0.5, 1)
            self.btn_micro.icon = "brain"
            self._stop_animations(self.btn_micro)
            
        elif state == "success":
            self.lbl_status.text = "Succès !"
            self.lbl_feedback.text = message
            self.lbl_feedback.theme_text_color = "Custom"
            self.lbl_feedback.text_color = (0, 0.8, 0, 1)
            self.btn_micro.md_bg_color = (0, 0.8, 0, 1)
            self.btn_micro.icon = "check-bold"

        elif state == "error":
            self.lbl_status.text = "Erreur"
            self.lbl_feedback.text = message
            self.lbl_feedback.theme_text_color = "Custom"
            self.lbl_feedback.text_color = (1, 0.2, 0.2, 1)
            self.btn_micro.md_bg_color = (1, 0, 0, 1)
            self.btn_micro.icon = "alert-circle"
            self.speak(message)
            self._stop_animations(self.btn_micro)

    def _animate_pulse(self, widget):
        if hasattr(self, 'anim') and self.anim: self.anim.cancel(widget)
        self.anim = Animation(md_bg_color=(1, 0.3, 0.3, 1), duration=0.8) + Animation(md_bg_color=(0.9, 0.2, 0.2, 1), duration=0.8)
        self.anim.repeat = True
        self.anim.start(widget)

    def _stop_animations(self, widget):
        if hasattr(self, 'anim') and self.anim:
             self.anim.cancel(widget)
             self.anim = None

    def speak(self, text):
        voice_engine.speak(text)

    # _speak_thread n'est plus nécessaire car géré par VoiceEngine

    def close_dialog(self, on_close=None):
        if self.current_dialog:
            self.current_dialog.dismiss()
            self.current_dialog = None
        if on_close:
            on_close()
