from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, ColorProperty, NumericProperty,BooleanProperty


class PrefSwitchItem(MDCard):
    text = StringProperty("")
    icon = StringProperty("")
    icon_color = ColorProperty([0, 0, 0, 1])
    active = BooleanProperty(False)
    selected_alpha = NumericProperty(0)

    def on_switch_active(self, instance, value):
        # On met à jour la propriété de la classe pour qu'elle soit synchrone
        if self.active != value:
            self.active = value
            print(f"Le mode sombre est maintenant : {value}")

            # Ici, on accède à l'application pour changer le thème
            from MonBudget_App import MainApp
            app = MainApp.get_running_app()
            app.theme_cls.theme_style = "Dark" if value else "Light"



class PrefItem(MDCard):
    """
    Composant renommé de 'SettingItem' à 'PrefItem' pour éviter
    le conflit avec la classe système de Kivy.
    """
    text = StringProperty("")
    secondary_text = StringProperty("")
    icon = StringProperty("")
    icon_color = ColorProperty([0, 0, 0, 1])
    tertiary_icon = StringProperty("chevron-right")

    # Indispensable pour la stabilité KivyMD
    selected_alpha = NumericProperty(0)


class ParametreScreen(MDBoxLayout):
    def on_mode_sombre_click(self):
        print("Changement du mode sombre")

    def on_export_csv(self):
        print("Exportation en CSV lancée")

    def on_export_json(self):
        print("Exportation en JSON lancée")