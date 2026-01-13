from __future__ import annotations

import csv
import json
import os
from datetime import datetime

from kivy.properties import BooleanProperty, ColorProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout

from models.budget import BudgetModel
from models.categorie import CategorieModel
from models.compte import CompteModel
from models.transaction import TransactionModel


class PrefItem(MDCard):
    text = StringProperty("")
    secondary_text = StringProperty("")
    icon = StringProperty("information")
    tertiary_icon = StringProperty("chevron-right")
    icon_color = ColorProperty([0.1, 0.5, 0.8, 1])


class PrefSwitchItem(MDBoxLayout):
    text = StringProperty("")
    icon = StringProperty("information")
    icon_color = ColorProperty([0.1, 0.5, 0.8, 1])
    active = BooleanProperty(False)

    def on_switch_active(self, _switch, value):
        app = getattr(self, "app", None)
        if app is None:
            from kivy.app import App

            app = App.get_running_app()

        if not app or not hasattr(app, "theme_cls"):
            return

        app.theme_cls.theme_style = "Dark" if value else "Light"


class ParametreScreen(MDBoxLayout):
    def on_export_csv(self):
        try:
            transactions = TransactionModel.get_all()
            if not transactions:
                self._notify("Aucune transaction à exporter", "info")
                return

            os.makedirs("exports", exist_ok=True)
            filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join("exports", filename)

            fieldnames = [
                "id_transaction",
                "id_compte",
                "id_categorie",
                "montant",
                "type_transaction",
                "description",
                "date_transaction",
            ]

            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for t in transactions:
                    writer.writerow({k: t.get(k) for k in fieldnames})

            self._notify(f"Export CSV réussi : {filename}", "success")
        except Exception as e:
            self._notify(f"Erreur lors de l'export CSV : {e}", "error")

    def on_export_json(self):
        try:
            transactions = TransactionModel.get_all()
            categories = CategorieModel.get_all()

            budgets = []
            for account in CompteModel.get_all():
                budget = BudgetModel.get_by_account(account["id_compte"])
                if budget:
                    budgets.append(budget)

            os.makedirs("exports", exist_ok=True)
            filename = f"donnees_completes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join("exports", filename)

            data = {
                "export_date": datetime.now().isoformat(),
                "transactions": transactions,
                "categories": categories,
                "budgets": budgets,
            }

            with open(filepath, "w", encoding="utf-8") as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)

            self._notify(f"Export JSON réussi : {filename}", "success")
        except Exception as e:
            self._notify(f"Erreur lors de l'export JSON : {e}", "error")

    def _notify(self, message: str, type: str = "info"):
        node = self
        while node is not None and not hasattr(node, "notifier"):
            node = getattr(node, "parent", None)

        if node is not None and hasattr(node, "notifier"):
            node.notifier(message, type)
