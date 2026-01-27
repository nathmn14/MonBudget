"""
Gestion des préférences de l'application (thème, etc.)
Utilise un fichier JSON pour sauvegarder les préférences utilisateur
"""

import json
import os
from pathlib import Path


class PreferencesManager:
    """Gestionnaire des préférences de l'application"""
    
    def __init__(self):
        self.preferences_file = Path("preferences.json")
        self.preferences = self._load_preferences()
    
    def _load_preferences(self):
        """Charge les préférences depuis le fichier JSON"""
        default_preferences = {
            "theme": "Light",
            "window_size": [360, 640],  # Taille mobile par défaut
            "language": "fr"
        }
        
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    loaded_prefs = json.load(f)
                    # Fusionner avec les préférences par défaut
                    default_preferences.update(loaded_prefs)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erreur lors du chargement des préférences: {e}")
        
        return default_preferences
    
    def _save_preferences(self):
        """Sauvegarde les préférences dans le fichier JSON"""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Erreur lors de la sauvegarde des préférences: {e}")
            return False
    
    def get_theme(self):
        """Récupère le thème sauvegardé"""
        return self.preferences.get("theme", "Light")
    
    def set_theme(self, theme):
        """Définit et sauvegarde le thème"""
        if theme in ["Light", "Dark"]:
            self.preferences["theme"] = theme
            return self._save_preferences()
        return False
    
    def get_window_size(self):
        """Récupère la taille de fenêtre sauvegardée"""
        return self.preferences.get("window_size", [360, 640])
    
    def set_window_size(self, width, height):
        """Définit et sauvegarde la taille de fenêtre"""
        self.preferences["window_size"] = [width, height]
        return self._save_preferences()
    
    def get_preference(self, key, default=None):
        """Récupère une préférence spécifique"""
        return self.preferences.get(key, default)
    
    def set_preference(self, key, value):
        """Définit et sauvegarde une préférence spécifique"""
        self.preferences[key] = value
        return self._save_preferences()


# Instance globale du gestionnaire de préférences
preferences_manager = PreferencesManager()
