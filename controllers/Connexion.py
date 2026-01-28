from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from models.utilisateur import UtilisateurModel


class LoginScreen(MDScreen):
    # On définit pin_code comme une propriété Kivy pour qu'elle soit surveillée
    pin_code = StringProperty("")

    def on_enter(self):
        """Appelé quand on arrive sur l'écran"""
        # S'assurer que la fenêtre est bien à la taille mobile
        from kivy.core.window import Window
        Window.size = (360, 640)
        
        self.check_default_password()
        self.reset_screen()

    def check_default_password(self):
        """Vérifie si le mot de passe par défaut est encore utilisé"""
        try:
            from data.connexion_bdd import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            # On vérifie si un utilisateur a encore le PIN 0000
            cursor.execute("SELECT COUNT(*) FROM Utilisateur WHERE mot_de_passe = '0000'")
            count = cursor.fetchone()[0]
            conn.close()
            
            if 'change_pwd_label' in self.ids:
                label = self.ids.change_pwd_label
                if count > 0:
                    label.opacity = 1
                else:
                    label.opacity = 0
        except Exception as e:
            print(f"Erreur check_default_password: {e}")

    def add_digit(self, digit):
        # On limite la saisie à 4 chiffres
        if len(self.pin_code) < 4:
            self.pin_code += str(digit)
            self.update_indicators()

            # Si on atteint 4 chiffres, on vérifie automatiquement
            if len(self.pin_code) == 4:
                # Petit délai pour voir le dernier point s'allumer
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.check_pin(), 0.15)

    def delete_digit(self):
        # On supprime le dernier caractère
        if len(self.pin_code) > 0:
            self.pin_code = self.pin_code[:-1]
            self.update_indicators()

    def update_indicators(self):
        # On met à jour la couleur des points selon la longueur du pin_code
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        is_dark = app.theme_cls.theme_style == "Dark"
        
        for i in range(1, 5):
            dot = self.ids[f"dot_{i}"]
            if len(self.pin_code) >= i:
                # Couleur bleue quand le chiffre est saisi
                dot.md_bg_color = (0.12, 0.53, 0.9, 1)
            else:
                # Couleur grise adaptée au thème quand c'est vide
                dot.md_bg_color = (0.8, 0.8, 0.8, 0.5) if not is_dark else (0.5, 0.5, 0.5, 0.5)

    def check_pin(self):
        # Logique de vérification contre la base de données
        user = UtilisateurModel.verify_pin(self.pin_code)
        if user:
            print("Accès autorisé")
            self.manager.current = "app_screen"
            
            # Notification si c'est encore le mdp par défaut
            if self.pin_code == "0000":
                from kivymd.app import MDApp
                app = MDApp.get_running_app()
                def notify_delayed(dt):
                    app.notify("🛡️ Sécurité : Pensez à changer votre code PIN (actuellement 0000)", "warning")
                from kivy.clock import Clock
                Clock.schedule_once(notify_delayed, 1)
                
            self.reset_screen()
        else:
            print("Code erroné")
            # Notification d'erreur visuelle
            self.show_error("🚫 Code PIN incorrect")
            self.flash_error()

    def flash_error(self):
        """Fait clignoter les points en rouge pour signaler l'erreur"""
        for i in range(1, 5):
            self.ids[f"dot_{i}"].md_bg_color = (1, 0.2, 0.2, 1)
        
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.reset_screen(), 0.6)

    def show_error(self, message):
        """Affiche un message d'erreur sur la page de connexion"""
        if 'error_label' in self.ids:
            error_label = self.ids.error_label
            error_label.text = message
            error_label.opacity = 1
            
            # Animation de secousse (optionnel, simple print pour debug ici)
            print(f"UI NOTIFICATION: {message}")
            
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.hide_error(), 3)
    
    def hide_error(self):
        """Cache le message d'erreur"""
        if 'error_label' in self.ids:
            error_label = self.ids.error_label
            error_label.opacity = 0

    def reset_screen(self):
        # On vide le code pour la prochaine utilisation
        self.pin_code = ""
        self.update_indicators()