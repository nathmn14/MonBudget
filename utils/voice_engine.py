
import threading
from kivy.utils import platform
from kivy.clock import Clock

# Cross-platform TTS via Plyer
try:
    from plyer import tts
    HAS_PLYER_TTS = True
except Exception:
    HAS_PLYER_TTS = False

# Fallback TTS for Desktop (pyttsx3)
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

# Desktop STT
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

# Android imports (only if on Android)
if platform == 'android':
    try:
        from jnius import autoclass, cast
        from android.permissions import request_permissions, Permission
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        RecognizerIntent = autoclass('android.speech.RecognizerIntent')
        HAS_ANDROID_SPEECH = True
    except Exception as e:
        print(f"Error importing Android speech libs: {e}")
        HAS_ANDROID_SPEECH = False
else:
    HAS_ANDROID_SPEECH = False


class VoiceEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VoiceEngine, cls).__new__(cls)
            cls._instance.init_engine()
        return cls._instance

    def init_engine(self):
        self.is_listening = False
        self.recognizer = None
        self.on_result_callback = None
        self.on_error_callback = None
        self.on_status_callback = None # Nouveau : pour notifier les changements d'état
        if HAS_SR:
            self.recognizer = sr.Recognizer()
            
    def handle_android_result(self, text):
        """Reçoit le texte d'Android et appelle le callback"""
        if self.on_result_callback:
            Clock.schedule_once(lambda dt: self.on_result_callback(text))
        self.is_listening = False

    def speak(self, text):
        """Synthèse vocale cross-plateforme"""
        if not text:
            return
            
        print(f"Speaking: {text}")
        
        def _speak_task():
            try:
                # Try Plyer first (good for mobile)
                if HAS_PLYER_TTS and platform == 'android':
                    tts.speak(text)
                # Fallback to pyttsx3 for Desktop (usually more reliable on Win/Linux)
                elif HAS_PYTTSX3:
                    engine = pyttsx3.init()
                    
                    # Tenter de trouver une voix française
                    voices = engine.getProperty('voices')
                    for voice in voices:
                        if "fr" in voice.id.lower() or "french" in voice.name.lower():
                            engine.setProperty('voice', voice.id)
                            break
                    
                    engine.setProperty('rate', 150) # Vitesse ajustable
                    engine.say(text)
                    engine.runAndWait()
                    # Indispensable sur certains systèmes pour libérer les ressources
                    del engine
                # Last resort: Plyer on desktop
                elif HAS_PLYER_TTS:
                    tts.speak(text)
                else:
                    print("TTS failure: No TTS engine available")
            except Exception as e:
                print(f"TTS Error: {e}")

        threading.Thread(target=_speak_task, daemon=True).start()

    def listen(self, on_result, on_error=None, on_status=None):
        """Démarre l'écoute selon la plateforme"""
        if self.is_listening:
            return
            
        self.is_listening = True
        self.on_result_callback = on_result
        self.on_error_callback = on_error
        self.on_status_callback = on_status
        
        if platform == 'android':
            self._listen_android(on_result, on_error)
        elif platform == 'win' or platform == 'linux' or platform == 'macosx':
            threading.Thread(target=self._listen_desktop, args=(on_result, on_error), daemon=True).start()
        else:
            if on_error:
                on_error("Plateforme non supportée pour l'écoute.")
            self.is_listening = False

    def _listen_desktop(self, on_result, on_error):
        """Reconnaissance vocale pour Desktop (Windows/Linux) via SpeechRecognition"""
        if not HAS_SR:
            if on_error:
                Clock.schedule_once(lambda dt: on_error("Désolé, la reconnaissance vocale n'est pas installée sur cet ordinateur."))
            self.is_listening = False
            return

        try:
            with sr.Microphone() as source:
                # Étape 1 : Ajustement au bruit (On informe l'UI)
                print("Ajustement au bruit...")
                if self.on_status_callback:
                    Clock.schedule_once(lambda dt: self.on_status_callback("listening"))
                
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                
                # Étape 2 : Écoute active
                print("Listening (Desktop)...")
                if self.on_status_callback:
                    Clock.schedule_once(lambda dt: self.on_status_callback("listening_active"))
                
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=10)
                
            print("Processing (Desktop)...")
            if self.on_status_callback:
                Clock.schedule_once(lambda dt: self.on_status_callback("processing"))
                
            # Utilisation de Google Web Speech API
            text = self.recognizer.recognize_google(audio, language="fr-FR")
            
            Clock.schedule_once(lambda dt: on_result(text))
            
        except sr.UnknownValueError:
            if on_error:
                Clock.schedule_once(lambda dt: on_error("Désolé, je n'ai pas compris l'audio."))
        except sr.RequestError as e:
            if on_error:
                error_msg = f"Erreur de service : {e}"
                Clock.schedule_once(lambda dt: on_error(error_msg))
        except Exception as e:
            if on_error:
                error_msg = f"Erreur : {str(e)}"
                Clock.schedule_once(lambda dt: on_error(error_msg))
        finally:
            self.is_listening = False

    def _listen_android(self, on_result, on_error):
        """Reconnaissance vocale pour Android via Intent (Standard Google Assistant)"""
        if not HAS_ANDROID_SPEECH:
            if on_error:
                on_error("Android Speech non disponible.")
            self.is_listening = False
            return

        try:
            # Demander les permissions microphone si besoin
            request_permissions([Permission.RECORD_AUDIO])
            
            # Note: Pour une implémentation complète sur Android, il faudrait gérer 
            # l'ActivityResult via une classe PythonActivityListener.
            # Pour faire simple dans un premier temps, on utilise l'Intent standard 
            # qui ouvre une fenêtre Google.
            
            current_activity = PythonActivity.mActivity
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "fr-FR")
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Parlez maintenant...")
            
            # Ceci nécessiterait d'enregistrer un listener dans le manifest ou via du code Kivy spécifique
            # Pour cet assistant, on va supposer que l'infrastructure Kivy est prête.
            # En réalité, sans le boilerplate ActivityResult, text ne reviendra pas ici directement.
            # Mais c'est la voie à suivre.
            
            current_activity.startActivityForResult(intent, 7001)
            # Le résultat devrait être capturé dans une méthode globale on_activity_result
            # que nous devrions ajouter à l'App.
            
            self.is_listening = False # L'intent gère sa propre UI
            
        except Exception as e:
            if on_error:
                on_error(f"Erreur Android : {str(e)}")
            self.is_listening = False

voice_engine = VoiceEngine()
