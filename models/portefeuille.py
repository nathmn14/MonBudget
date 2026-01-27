# Modèle pour la table Portefeuille

from data.connexion_bdd import get_connection
from datetime import datetime


class PortefeuilleModel:
    """
    Modèle pour la table Portefeuille dans la base de données
    Gère l'historique des soldes des comptes
    """
    
    @staticmethod
    def create(id_compte, solde):
        """
        Créer une nouvelle entrée de solde dans le portefeuille
        
        Args:
            id_compte (int): ID du compte
            solde (float): Solde à enregistrer
            
        Returns:
            int: ID de l'entrée créée
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Portefeuille (id_compte, solde)
            VALUES (?, ?)
        """, (id_compte, solde))
        
        portefeuille_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return portefeuille_id
    
    @staticmethod
    def get_by_account(id_compte):
        """
        Récupérer l'historique des soldes d'un compte
        
        Args:
            id_compte (int): ID du compte
            
        Returns:
            list: Liste de dictionnaires contenant l'historique des soldes
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Portefeuille WHERE id_compte = ? ORDER BY date_heure DESC",
            (id_compte,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'id_portefeuille': row[0],
                'id_compte': row[1],
                'solde': row[2],
                'date_heure': row[3]
            })
        return history
    
    @staticmethod
    def get_latest_balance(id_compte):
        """
        Récupérer le solde actuel d'un compte
        
        Args:
            id_compte (int): ID du compte
            
        Returns:
            float: Solde actuel ou 0.0 si aucun historique
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT solde FROM Portefeuille WHERE id_compte = ? ORDER BY date_heure DESC LIMIT 1",
            (id_compte,)
        )
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0.0
    
    @staticmethod
    def update_balance(id_compte, nouveau_solde):
        """
        Mettre à jour le solde d'un compte (crée une nouvelle entrée dans l'historique)
        
        Args:
            id_compte (int): ID du compte
            nouveau_solde (float): Nouveau solde
            
        Returns:
            int: ID de la nouvelle entrée créée
        """
        return PortefeuilleModel.create(id_compte, nouveau_solde)
    
    @staticmethod
    def delete_by_id(id_portefeuille):
        """
        Supprimer une entrée de portefeuille
        
        Args:
            id_portefeuille (int): ID de l'entrée
            
        Returns:
            bool: True si la suppression a réussi
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Portefeuille WHERE id_portefeuille = ?", (id_portefeuille,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
