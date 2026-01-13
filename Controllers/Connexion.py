from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty


class LoginScreen(MDScreen):
    # On définit pin_code comme une propriété Kivy pour qu'elle soit surveillée
    pin_code = StringProperty("")

    def add_digit(self, digit):
        # On limite la saisie à 4 chiffres
        if len(self.pin_code) < 4:
            self.pin_code += str(digit)
            self.update_indicators()

            # Si on atteint 4 chiffres, on vérifie automatiquement
            if len(self.pin_code) == 4:
                self.check_pin()

    def delete_digit(self):
        # On supprime le dernier caractère
        if len(self.pin_code) > 0:
            self.pin_code = self.pin_code[:-1]
            self.update_indicators()

    def update_indicators(self):
        # On met à jour la couleur des points selon la longueur du pin_code
        # On accède aux ids dot_1, dot_2, etc. définis dans votre KV
        for i in range(1, 5):
            dot = self.ids[f"dot_{i}"]
            if len(self.pin_code) >= i:
                # Couleur bleue quand le chiffre est saisi
                dot.md_bg_color = (0.12, 0.53, 0.9, 1)
            else:
                # Couleur grise quand c'est vide
                dot.md_bg_color = (0.8, 0.8, 0.8, 0.5)

    def check_pin(self):
        # Logique de vérification
        # Remplacez "1234" par votre code secret ou une vérification BDD
        if self.pin_code == "1234":
            print("Accès autorisé")
            self.manager.current = "app_screen"
            self.reset_screen()
        else:
            print("Code erroné")
            # Optionnel : On peut ajouter une petite vibration ou un flash rouge ici
            self.reset_screen()

    def reset_screen(self):
        # On vide le code pour la prochaine utilisation
        self.pin_code = ""
        self.update_indicators()