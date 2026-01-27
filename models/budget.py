# Modèle pour la table Budget

import sqlite3
from data.connexion_bdd import get_connection


class BudgetModel:
    """
    Modèle pour la table Budget dans la base de données
    Gère les paramètres du budget (budget total et jours restants)
    """
    
    @staticmethod
    def create(id_compte, budget_total=0, jours_restants=30):
        """
        Créer un nouveau budget pour un compte
        
        Args:
            id_compte (int): ID du compte
            budget_total (float): Budget total alloué
            jours_restants (int): Nombre de jours restants dans la période
            
        Returns:
            int: ID du budget créé
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Budget (id_compte, budget_total, jours_restants)
            VALUES (?, ?, ?)
        """, (id_compte, budget_total, jours_restants))
        
        budget_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return budget_id
    
    @staticmethod
    def get_by_account(id_compte):
        """
        Récupérer le budget d'un compte (un seul budget par compte)
        
        Args:
            id_compte (int): ID du compte
            
        Returns:
            dict: Dictionnaire contenant le budget ou None
        """
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Budget WHERE id_compte = ? LIMIT 1",
            (id_compte,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id_budget': row['id_budget'],
                'id_compte': row['id_compte'],
                'budget_total': row['budget_total'],
                'jours_restants': row['jours_restants'],
                'date_creation': row['date_creation'],
                'date_modification': row['date_modification']
            }
        return None
    
    @staticmethod
    def update_by_account(id_compte, budget_total=None, jours_restants=None):
        """
        Mettre à jour le budget d'un compte (crée ou met à jour selon le cas)
        
        Args:
            id_compte (int): ID du compte
            budget_total (float, optional): Nouveau budget total
            jours_restants (int, optional): Nouveaux jours restants
            
        Returns:
            bool: True si la mise à jour a réussi
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Vérifier si un budget existe pour ce compte
        cursor.execute("SELECT id_budget FROM Budget WHERE id_compte = ?", (id_compte,))
        existing = cursor.fetchone()
        
        if existing:
            # Mettre à jour le budget existant
            updates = []
            params = []
            
            if budget_total is not None:
                updates.append("budget_total = ?")
                params.append(budget_total)
            if jours_restants is not None:
                updates.append("jours_restants = ?")
                params.append(jours_restants)
            
            if updates:
                updates.append("date_modification = CURRENT_TIMESTAMP")
                params.append(id_compte)
                
                query = f"UPDATE Budget SET {', '.join(updates)} WHERE id_compte = ?"
                cursor.execute(query, params)
        else:
            # Créer un nouveau budget
            if budget_total is not None and jours_restants is not None:
                cursor.execute("""
                    INSERT INTO Budget (id_compte, budget_total, jours_restants)
                    VALUES (?, ?, ?)
                """, (id_compte, budget_total, jours_restants))
            elif budget_total is not None:
                cursor.execute("""
                    INSERT INTO Budget (id_compte, budget_total, jours_restants)
                    VALUES (?, ?, 30)
                """, (id_compte, budget_total))
            elif jours_restants is not None:
                cursor.execute("""
                    INSERT INTO Budget (id_compte, budget_total, jours_restants)
                    VALUES (?, 60000, ?)
                """, (id_compte, jours_restants))
            else:
                conn.close()
                return False
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_or_create(id_compte, default_budget=60000, default_jours=20):
        """
        Récupérer le budget ou en créer un par défaut s'il n'existe pas
        
        Args:
            id_compte (int): ID du compte
            default_budget (float): Budget par défaut si création
            default_jours (int): Jours par défaut si création
            
        Returns:
            dict: Dictionnaire contenant le budget
        """
        budget = BudgetModel.get_by_account(id_compte)
        if not budget:
            BudgetModel.create(id_compte, default_budget, default_jours)
            budget = BudgetModel.get_by_account(id_compte)
        return budget
