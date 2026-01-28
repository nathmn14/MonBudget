
# Utilitaires pour les transactions vocales (compatible Python 3.13 via PowerShell)
import threading
import re
import subprocess
import os
import logging
# Suppress noisy comtypes logs from pyttsx3
logging.getLogger("comtypes").setLevel(logging.WARNING)

from kivy.clock import Clock
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFloatingActionButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.app import MDApp
from kivymd.toast import toast
from kivy.animation import Animation
from kivy.metrics import dp

# Modèles et Données
from models.transaction import TransactionModel
from models.categorie import CategorieModel
from data.connexion_bdd import get_default_account_id
from utils.event_bus import notify_transaction_added

# Synthèse vocale
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False
    print("WARNING: pyttsx3 non installé.")

# Patch pour Python 3.13 : modules supprimés ou déplacés
import sys

# 1. Distutils (supprimé en 3.12, présent via setuptools)
try:
    import distutils
except ImportError:
    try:
        import setuptools
        import distutils # Maintenant disponible via setuptools
    except ImportError:
        print("WARNING: setuptools non installé (requis pour distutils)")

if sys.version_info >= (3, 13):
    # 2. Audioop (supprimé en 3.13)
    try:
        import audioop
    except ImportError:
        try:
            import audioop_lts as _audioop
            sys.modules['audioop'] = _audioop
        except ImportError:
            print("WARNING: audioop-lts non installé (requis pour SR sur Py3.13)")

    # 3. Aifc (supprimé en 3.13)
    try:
        import aifc
    except ImportError:
         try:
             import standard_aifc as _aifc
             sys.modules['aifc'] = _aifc
         except ImportError:
             print("WARNING: standard-aifc non installé (requis pour SR sur Py3.13)")

# Reconnaissance vocale Google
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False
    print("WARNING: speech_recognition non installé.")

class VoiceTransaction:
    """Gestionnaire de transactions vocales avec interface moderne"""
    
    def __init__(self):
        self.engine = None
        self.current_dialog = None
        self.is_listening = False
        self._init_tts_engine()
        
    def _init_tts_engine(self):
        """Initialise le moteur de synthèse vocale uniquement"""
        if HAS_PYTTSX3:
            try:
                self.engine = pyttsx3.init()
                # Config voix
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if 'fr' in voice.id.lower() or 'french' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                self.engine.setProperty('rate', 150)
                self.engine.setProperty('volume', 0.9)
            except Exception as e:
                print(f"Erreur init pyttsx3: {e}")
    
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
        """Lance le thread d'écoute Google"""
        if not HAS_SR:
            self.update_ui_state("error", "Module Vocal Absent")
            return

        self.is_listening = True
        self.update_ui_state("listening")
        
        threading.Thread(target=self._listen_thread_google, daemon=True).start()

    def stop_listening(self):
        """Arrête l'écoute (ne peut pas vraiment arrêter le subprocess mais reset l'UI)"""
        self.is_listening = False
        self.update_ui_state("idle")

    def _listen_thread_google(self):
        """Reconnaissance vocale via Google Cloud Speech API (gratuit/limité)"""
        recognizer = sr.Recognizer()
        
        # Ajustements pour le bruit ambiant optimisés
        recognizer.energy_threshold = 300  
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8 
        
        try:
            with sr.Microphone() as source:
                Clock.schedule_once(lambda dt: self.update_ui_state("listening_active"))
                # Calibrage rapide
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Écoute avec timeout
                try:
                    audio = recognizer.listen(source, timeout=5.0, phrase_time_limit=10.0)
                except sr.WaitTimeoutError:
                    Clock.schedule_once(lambda dt: self.update_ui_state("error", "Je n'ai rien entendu."))
                    self.is_listening = False
                    return

            # Traitement
            Clock.schedule_once(lambda dt: self.update_ui_state("processing"))
            
            try:
                # Appel à Google - Langue FR forcée
                text = recognizer.recognize_google(audio, language="fr-FR")
                print(f"DEBUG GOOGLE OUT: {text}")
                self.process_command(text)
                
            except sr.UnknownValueError:
                Clock.schedule_once(lambda dt: self.update_ui_state("error", "Pas compris."))
            except sr.RequestError as e:
                print(f"Erreur API Google: {e}")
                Clock.schedule_once(lambda dt: self.update_ui_state("error", "Erreur réseau/service."))
                
        except Exception as e:
            print(f"DEBUG: Erreur thread vocal : {e}")
            error_msg = str(e)
            Clock.schedule_once(lambda dt: self.update_ui_state("error", f"Erreur: {error_msg}"))
        finally:
            self.is_listening = False

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
        # Mots-clés pour les revenus (avec et sans accents)
        mots_entree = ["revenu", "gagné", "gagne", "salaire", "ajouté", "ajoute", "ajout", "reçu", "recu", "entrée", "entree", "depôt", "depot", "virement"]
        
        # Mots-clés explicites pour les dépenses (pour contrer "Ajoute une dépense")
        mots_sortie = ["dépense", "depense", "payé", "paye", "achat", "acheté", "sortie", "course"]

        if any(mot in text for mot in mots_entree):
            type_transac = "ENTREE"
            
        # Si le mot "dépense" est explicitement dit, on force SORTIE même si "Ajoute" est présent
        if any(mot in text for mot in mots_sortie):
             type_transac = "SORTIE"

        # 3. Extraction de la Catégorie
        # D'abord, tentative de reconnaissance directe d'une catégorie existante dans la phrase
        categorie_finale = self._find_existing_category_in_text(text, type_transac)
        
        if not categorie_finale:
            # Sinon, extraction classique des mots-clés
            clean_text = text.replace(montant_match.group(0), '')
            stopwords = ["ajouter", "dépense", "depense", "revenu", "pour", "de", "dans", "le", "la", "un", "une", "euros", "fc", "dollars", "francs", "sur", "mon", "ma"]
            
            tokens = clean_text.split()
            categorie_mots = [word for word in tokens if word not in stopwords and len(word) > 2]
            
            categorie_nom = "Divers"
            if categorie_mots:
                categorie_nom = " ".join(categorie_mots).capitalize()
                
            categorie_finale = self._get_or_create_category(categorie_nom, type_transac)
        
        if not categorie_finale:
             Clock.schedule_once(lambda dt: self.update_ui_state("error", "Erreur catégorie."))
             return

        # 4. Nettoyage de la Description (Note)
        # On part du texte complet et on retire ce qu'on a déjà utilisé (montant, catégorie)
        description_finale = text
        
        # Retirer le montant
        if montant_match:
            description_finale = description_finale.replace(montant_match.group(0), "")
            
        # Retirer le nom de la catégorie si trouvé
        if categorie_finale:
            # Insensible à la casse
            pattern = re.compile(re.escape(categorie_finale['nom_categorie']), re.IGNORECASE)
            description_finale = pattern.sub("", description_finale)
            
        # Retirer les stopwords communs pour ne garder que la "vraie" note
        stopwords = ["ajouter", "dépense", "depense", "revenu", "pour", "de", "dans", "le", "la", "un", "une", "euros", "fc", "dollars", "francs", "sur", "mon", "ma"]
        for word in stopwords:
             # Retirer le mot s'il est isolé (entouré d'espaces ou début/fin)
             pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
             description_finale = pattern.sub("", description_finale)
             
        # Nettoyage final
        description_finale = " ".join(description_finale.split()) # Retire les espaces multiples
        
        # Si aucune note n'est détectée, utiliser le nom de la catégorie
        if not description_finale and categorie_finale:
            description_finale = categorie_finale['nom_categorie']
        
        # 5. Création
        self._save_transaction(montant, type_transac, categorie_finale, description_finale)

    def _save_transaction(self, montant, type_transac, categorie, description_vocale):
        """Sauvegarde en BDD"""
        id_compte = get_default_account_id()
        try:
            # Capitalisation propre
            desc = description_vocale.strip()
            if desc: desc = desc[0].upper() + desc[1:]
            
            # Créer la transaction
            TransactionModel.create(
                id_compte=id_compte,
                montant=montant,
                type_transaction=type_transac,
                id_categorie=categorie['id_categorie'],
                description=desc,
                date_transaction=None
            )
            
            # Mise à jour du Budget si c'est une ENTREE (Augmentation du plafond)
            if type_transac == 'ENTREE':
                from models.budget import BudgetModel
                from utils.event_bus import notify_budget_changed
                
                # Récupérer le budget actuel
                budget = BudgetModel.get_by_account(id_compte)
                if budget:
                    nouveau_total = float(budget['budget_total']) + montant
                    BudgetModel.update_by_account(id_compte, budget_total=nouveau_total)
                    notify_budget_changed(nouveau_total, id_compte)
            
            msg = f"{'Revenu' if type_transac == 'ENTREE' else 'Dépense'} {montant} - {categorie['nom_categorie']}"
            
            def on_success(dt):
                self.update_ui_state("success", msg)

                notify_transaction_added({
                    'montant': montant,
                    'type': type_transac,
                    'description': desc,
                    'categorie': categorie['nom_categorie']
                })

            Clock.schedule_once(on_success)
            
            self.speak(f"C'est noté. {msg}")
            Clock.schedule_once(lambda dt: self.close_dialog(), 2.5)
            
        except Exception as e:
            print(f"Erreur save DB: {e}")
            Clock.schedule_once(lambda dt: self.update_ui_state("error", "Erreur sauvegarde."))

    def _find_existing_category_in_text(self, text, type_transac):
        """Cherche si le nom d'une catégorie existante est prononcé dans le texte"""
        all_cats = CategorieModel.get_all()
        # Filtrer par type pour la pertinence
        candidates = [c for c in all_cats if c['type_transaction'] == type_transac]
        
        # Trier par longueur décroissante pour matcher les noms composés en premier
        candidates.sort(key=lambda x: len(x['nom_categorie']), reverse=True)
        
        lower_text = text.lower()
        for cat in candidates:
            # On cherche le nom de la catégorie (en minuscule) dans le texte parlé
            if cat['nom_categorie'].lower() in lower_text:
                return cat
        return None

    def _get_or_create_category(self, cat_name, type_transac):
        """Logique catégorie avec recherche floue"""
        all_cats = CategorieModel.get_all()
        
        # 1. Correspondance exacte
        for cat in all_cats:
            if cat['nom_categorie'].lower() == cat_name.lower():
                return cat
        
        # 2. Contient
        for cat in all_cats:
            if cat_name.lower() in cat['nom_categorie'].lower():
                return cat

        # 3. Fuzzy Match (Tolérance aux fautes/pluriels)
        import difflib
        # On compare avec les catégories du même type de préférence
        relevant_cats = [c for c in all_cats if c['type_transaction'] == type_transac]
        cat_names = [c['nom_categorie'] for c in relevant_cats]
        
        # Cutoff 0.7 = 70% de ressemblance (ex: "course" matche "Courses")
        matches = difflib.get_close_matches(cat_name, cat_names, n=1, cutoff=0.7)
        if matches:
            match_name = matches[0]
            for cat in relevant_cats:
                if cat['nom_categorie'] == match_name:
                    return cat

        import random
        # Palette étendue de couleurs vives et distinctes
        palette = [
            "0.18,0.8,0.44,1", "0.2,0.6,0.86,1", "0.9,0.5,0.13,1", "0.6,0.3,0.7,1",
            "0.1,0.7,0.7,1", "0.9,0.3,0.23,1", "0.44,0.26,0.13,1", "0.95,0.2,0.4,1",
            "0.1,0.3,0.5,1", "1,0.8,0.2,1", "0.5,0.4,0.3,1", "0.29,0.3,0.4,1",
            "0.8,0.1,0.5,1", "0.1,0.8,0.8,1", "0.5,0.8,0.1,1", "0.8,0.5,0.1,1"
        ]
        
        # Récupérer les couleurs déjà utilisées pour éviter les répétitions
        used_colors = [c['couleur'] for c in all_cats]
        available_colors = [col for col in palette if col not in used_colors]
        
        # Si toutes les couleurs de la palette sont utilisées, on prend une couleur au hasard ou on génère
        if available_colors:
            color_to_use = random.choice(available_colors)
        else:
            # Fallback : couleur aléatoire mais différente (ou juste random choice si vraiment saturé)
            color_to_use = f"{random.random():.2f},{random.random():.2f},{random.random():.2f},1"

        icon = "tag"
        lname = cat_name.lower()
        if any(x in lname for x in ["resto", "manger", "food", "repas"]): icon = "food"
        elif any(x in lname for x in ["auto", "bus", "train", "uber"]): icon = "car"
        elif any(x in lname for x in ["maison", "loyer", "meuble"]): icon = "home"
        elif any(x in lname for x in ["santé", "medecin", "pharma"]): icon = "medical-bag"
        elif any(x in lname for x in ["jeu", "film", "ciné"]): icon = "gamepad-variant"
        
        CategorieModel.create(
            nom=cat_name,
            type_transaction=type_transac,
            icone=icon,
            couleur=color_to_use
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
        if self.engine:
            # Tout passe dans un thread pour ne jamais bloquer le main thread
            threading.Thread(target=self._speak_sequence, args=(text,), daemon=True).start()

    def _speak_sequence(self, text):
        self.stop_speaking()
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except: pass

    def stop_speaking(self):
        """Arrête la synthèse vocale immédiatement"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass

    def close_dialog(self, on_close=None):
        # Arrêter de parler dans un thread séparé pour ne pas freezer l'UI
        threading.Thread(target=self.stop_speaking, daemon=True).start()
        
        if self.current_dialog:
            self.current_dialog.dismiss()
            self.current_dialog = None
        if on_close:
            on_close()
