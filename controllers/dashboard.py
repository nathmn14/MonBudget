from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty, ColorProperty, ListProperty
from models.transaction import TransactionModel
from models.budget import BudgetModel
from data.connexion_bdd import get_default_account_id
from kivy.clock import Clock
from datetime import datetime
from kivy.factory import Factory
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.metrics import dp
from utils.event_bus import event_bus, EventTypes, subscribe_to_data_changes
from utils.voice_transaction import VoiceTransaction

class StatCard(MDBoxLayout):
    titre = StringProperty("")
    montant = StringProperty("0")
    couleur_texte = ColorProperty([0, 0, 0, 1])

class GraphiqueBarres(MDBoxLayout):
    data = ListProperty([])

    def on_kv_post(self, base_widget):
        self._bind_chart()

    def on_parent(self, widget, parent):
        if parent:
            Clock.schedule_once(lambda dt: self._bind_chart(), 0)

    def _bind_chart(self):
        if not hasattr(self, "ids") or "chart_area" not in self.ids:
            return
        area = self.ids.chart_area
        area.bind(pos=self.draw, size=self.draw)
        self.bind(data=self.draw)
        self.draw()

    def update_data(self, data):
        self.data = data
        if not hasattr(self, "ids"):
            return
        for i in range(3):
            label = self.ids.get(f"month_lbl_{i}")
            if not label:
                continue
            label.text = data[i]["label"] if i < len(data) else ""

    def draw(self, *args):
        if not hasattr(self, "ids") or "chart_area" not in self.ids:
            return
        area = self.ids.chart_area
        area.canvas.before.clear()

        if not self.data:
            return

        max_val = max(max(d.get("revenu", 0), d.get("depense", 0)) for d in self.data)
        if max_val <= 0:
            max_val = 1

        chart_left = area.x + dp(30)
        chart_right = area.right - dp(10)
        chart_bottom = area.y + dp(20)
        chart_top = area.top - dp(20)

        chart_h = max(chart_top - chart_bottom, 1)
        chart_w = max(chart_right - chart_left, 1)

        with area.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            Line(points=[chart_left, area.y + dp(20), chart_right, area.y + dp(20)])
            Line(points=[chart_left, area.y + dp(70), chart_right, area.y + dp(70)])
            Line(points=[chart_left, area.y + dp(120), chart_right, area.y + dp(120)])

            n = len(self.data)
            group_w = chart_w / max(n, 1)
            bar_w = min(dp(14), group_w * 0.25)
            gap = dp(2)

            for i, d in enumerate(self.data):
                cx = chart_left + group_w * (i + 0.5)

                revenu = float(d.get("revenu", 0) or 0)
                depense = float(d.get("depense", 0) or 0)

                h_rev = (revenu / max_val) * chart_h
                h_dep = (depense / max_val) * chart_h

                Color(0.1, 0.7, 0.3, 1)
                Rectangle(pos=(cx - bar_w - gap, chart_bottom), size=(bar_w, h_rev))

                Color(1, 0.3, 0.5, 1)
                Rectangle(pos=(cx + gap, chart_bottom), size=(bar_w, h_dep))

from kivy.uix.widget import Widget
import math
class PieChart(Widget):
    data = ListProperty([]) # Liste de dict: {'total': float, 'couleur': tuple, 'nom': str}
    _last_data = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.draw, size=self.draw, data=self.draw)

    def draw(self, *args):
        # Optimisation : éviter de redessiner si les données ET la taille n'ont pas changé
        if self.data == self._last_data and hasattr(self, '_last_size') and self.size == self._last_size:
            return
            
        self.canvas.clear()
        self._last_data = list(self.data)
        self._last_size = tuple(self.size)

        if not self.data:
            with self.canvas:
                Color(0.9, 0.9, 0.9, 1)
                Ellipse(pos=self.pos, size=self.size)
            return

        total_global = sum(d['total'] for d in self.data)
        if total_global == 0:
            with self.canvas:
                Color(0.9, 0.9, 0.9, 1)
                Ellipse(pos=self.pos, size=self.size)
            return

        angle_actuel = 0
        with self.canvas:
            for d in self.data:
                Color(*d['couleur'])
                pourcentage = d['total'] / total_global
                angle_part = pourcentage * 360
                
                Ellipse(
                    pos=self.pos, 
                    size=self.size,
                    angle_start=angle_actuel,
                    angle_end=angle_actuel + angle_part
                )
                angle_actuel += angle_part

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            center_x = self.x + self.width / 2
            center_y = self.y + self.height / 2
            dx = touch.x - center_x
            dy = touch.y - center_y
            distance = math.sqrt(dx**2 + dy**2)
            
            radius = self.width / 2
            if distance <= radius:
                angle_rad = math.atan2(dy, dx)
                angle_deg = math.degrees(angle_rad)
                if angle_deg < 0:
                    angle_deg += 360
                
                total_global = sum(d['total'] for d in self.data)
                if total_global == 0:
                    return super().on_touch_down(touch)

                angle_actuel = 0
                for d in self.data:
                    pourcentage = d['total'] / total_global
                    angle_part = pourcentage * 360
                    
                    if angle_actuel <= angle_deg <= (angle_actuel + angle_part):
                        from kivymd.app import MDApp
                        app = MDApp.get_running_app()
                        if hasattr(app.root, 'notifier'):
                            app.root.notifier(f"Catégorie : {d['nom']} ({int(d['total'])} FC)")
                        return True
                    
                    angle_actuel += angle_part
        return super().on_touch_down(touch)

class DashboardScreen(MDBoxLayout):
    solde_mois = StringProperty("0 FC")
    total_depenses = StringProperty("0 FC")
    total_revenus = StringProperty("+0 FC")
    _refreshing = False # Verrou pour éviter les refreshs simultanés
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("DEBUG: Initialisation de DashboardScreen")
        try:
            self.voice_transaction = VoiceTransaction()  # Initialiser la transaction vocale
            print("DEBUG: VoiceTransaction initialisé avec succès")
        except Exception as e:
            print(f"DEBUG: Erreur initialisation VoiceTransaction: {e}")
            import traceback
            traceback.print_exc()
            self.voice_transaction = None
        # Charger les données après l'initialisation
        Clock.schedule_once(self.charger_donnees, 0.5)
        # S'abonner aux événements de changement de données
        self._setup_event_listeners()
        print("DEBUG: DashboardScreen initialisé complètement")

    def _setup_event_listeners(self):
        """Configure les écouteurs d'événements pour le rafraîchissement automatique"""
        # S'abonner à tous les changements de données
        subscribe_to_data_changes(self._on_data_changed)
        
        # S'abonner spécifiquement aux changements de budget
        event_bus.subscribe(EventTypes.BUDGET_CHANGED, self._on_data_changed)
        
        # S'abonner aux changements utilisateur
        event_bus.subscribe(EventTypes.USER_CHANGED, self._on_data_changed)
        
        # S'abonner aux changements de catégorie
        event_bus.subscribe(EventTypes.CATEGORY_CHANGED, self._on_data_changed)

    def _on_data_changed(self, event_data=None, *args, **kwargs):
        """Callback appelé quand les données changent"""
        # Rafraîchir les données avec un petit délai pour éviter les conflits
        Clock.schedule_once(lambda dt: self.charger_donnees(), 0.1)

    def on_parent(self, widget, parent):
        """Appelé quand l'écran est ajouté au parent (navigation)"""
        if parent:
            self.charger_donnees()

    def charger_donnees(self, *args):
        """Récupère les statistiques réelles depuis la base de données de manière asynchrone"""
        if self._refreshing:
            return
            
        self._refreshing = True
        import threading
        id_compte = get_default_account_id()
        now = datetime.now()
        month = now.month
        year = now.year

        def _thread_calc():
            try:
                # 1. Calculs lourds en thread
                rev = TransactionModel.get_total_by_type('ENTREE', id_compte, month, year)
                dep = TransactionModel.get_total_by_type('SORTIE', id_compte, month, year)
                
                # Check fallback
                m, y = month, year
                if rev == 0 and dep == 0:
                    latest = TransactionModel.get_latest_transaction_date(id_compte)
                    if latest:
                        try:
                            d_obj = datetime.strptime(latest.split(' ')[0], "%Y-%m-%d")
                            m, y = d_obj.month, d_obj.year
                            rev = TransactionModel.get_total_by_type('ENTREE', id_compte, m, y)
                            dep = TransactionModel.get_total_by_type('SORTIE', id_compte, m, y)
                        except: pass

                # Préparation Graph Barres
                month_labels = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]
                graph_data = []
                curr_m, curr_y = m, y
                for _ in range(3):
                    graph_data.insert(0, {
                        "label": month_labels[curr_m - 1],
                        "revenu": TransactionModel.get_total_by_type('ENTREE', id_compte, curr_m, curr_y),
                        "depense": TransactionModel.get_total_by_type('SORTIE', id_compte, curr_m, curr_y),
                    })
                    curr_m -= 1
                    if curr_m == 0: curr_m = 12; curr_y -= 1

                # Stats catégories
                cat_stats = TransactionModel.get_stats_by_category(id_compte, 'SORTIE', m, y)

                # 2. Mise à jour UI sur le thread principal
                def _ui_update(dt):
                    self.total_revenus = f"+{int(rev):,}".replace(',', ' ')
                    self.total_depenses = f"-{int(dep):,}".replace(',', ' ')
                    self.solde_mois = f"{int(rev - dep):,}".replace(',', ' ') + " FC"
                    
                    if hasattr(self.ids, "graph_barres"):
                        self.ids.graph_barres.update_data(graph_data)
                    
                    self._update_cat_ui(cat_stats)
                    self._refreshing = False

                Clock.schedule_once(_ui_update)
            except Exception as e:
                print(f"DEBUG Dashboard Error: {e}")
                self._refreshing = False

        threading.Thread(target=_thread_calc, daemon=True).start()

    def _update_cat_ui(self, stats):
        if not hasattr(self.ids, 'box_categories_stats'): return
        
        self.ids.box_categories_stats.clear_widgets()
        chart_data = []
        
        for s in stats:
            couleur_vals = s['couleur'].split(',')
            couleur_tuple = tuple(float(x) for x in couleur_vals) if len(couleur_vals) == 4 else (0.5, 0.5, 0.5, 1)
            
            item = Factory.ItemCategorie()
            item.nom = s['nom']
            item.montant = f"{int(s['total']):,}".replace(',', ' ') + " FC"
            item.icone = s['icone']
            item.couleur_icone = couleur_tuple
            self.ids.box_categories_stats.add_widget(item)
            
            chart_data.append({'nom': s['nom'], 'total': float(s['total']), 'couleur': couleur_tuple})
            
        if hasattr(self.ids, 'chart_pie'):
            self.ids.chart_pie.data = chart_data
    
    def ajouter_transaction_vocale(self):
        """Ouvre l'interface pour ajouter une transaction vocale"""
        print("DEBUG: Bouton micro cliqué - ajouter_transaction_vocale appelé")
        
        # Vérifier si VoiceTransaction est disponible
        if not hasattr(self, 'voice_transaction') or self.voice_transaction is None:
            print("DEBUG: VoiceTransaction non initialisé")
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            if hasattr(app.root, 'notifier'):
                app.root.notifier("Le système de transaction n'est pas disponible", "error")
            return
        
        try:
            print("DEBUG: Création du popup de transaction vocale")
            dialog = self.voice_transaction.create_transaction_popup(
                on_close=self._on_transaction_vocale_closed
            )
            print("DEBUG: Ouverture du dialog")
            dialog.open()
            print("DEBUG: Dialog ouvert avec succès")
        except Exception as e:
            print(f"DEBUG: Erreur dans ajouter_transaction_vocale: {e}")
            import traceback
            traceback.print_exc()
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            if hasattr(app.root, 'notifier'):
                app.root.notifier(f"Erreur lors de l'ouverture de l'interface vocale: {e}", "error")
    
    def _on_transaction_vocale_closed(self):
        """Callback appelé à la fermeture de l'interface de transaction vocale"""
        # Rafraîchir les données du dashboard après une transaction
        Clock.schedule_once(lambda dt: self.charger_donnees(), 0.5)
