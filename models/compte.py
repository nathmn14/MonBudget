# Modèle pour la table Compte

from data.connexion_bdd import get_connection


class CompteModel:
    """
    Modèle pour la table Compte dans la base de données
    Gère les comptes bancaires/cash des utilisateurs
    """
    
    @staticmethod
    def create(id_utilisateur, intitule_compte, devise, type_compte):
        """
        Créer un nouveau compte
        
        Args:
            id_utilisateur (int): ID de l'utilisateur propriétaire
            intitule_compte (str): Nom du compte
            devise (str): Devise (ex: FC, USD, EUR)
            type_compte (str): Type (cash, banque, mobile money...)
            
        Returns:
            int: ID du compte créé
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Compte (id_utilisateur, intitule_compte, devise, type_compte)
            VALUES (?, ?, ?, ?)
        """, (id_utilisateur, intitule_compte, devise, type_compte))
        
        account_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return account_id
    
    @staticmethod
    def get_all():
        """
        Récupérer tous les comptes
        
        Returns:
            list: Liste de dictionnaires contenant les comptes
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Compte")
        rows = cursor.fetchall()
        conn.close()
        
        accounts = []
        for row in rows:
            accounts.append({
                'id_compte': row[0],
                'id_utilisateur': row[1],
                'intitule_compte': row[2],
                'devise': row[3],
                'type_compte': row[4],
                'date_creation': row[5],
                'date_modification': row[6]
            })
        return accounts
    
    @staticmethod
    def get_by_id(id_compte):
        """
        Récupérer un compte par son ID
        
        Args:
            id_compte (int): ID du compte
            
        Returns:
            dict: Dictionnaire contenant le compte ou None
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Compte WHERE id_compte = ?", (id_compte,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id_compte': row[0],
                'id_utilisateur': row[1],
                'intitule_compte': row[2],
                'devise': row[3],
                'type_compte': row[4],
                'date_creation': row[5],
                'date_modification': row[6]
            }
        return None
    
    @staticmethod
    def get_by_user(id_utilisateur):
        """
        Récupérer tous les comptes d'un utilisateur
        
        Args:
            id_utilisateur (int): ID de l'utilisateur
            
        Returns:
            list: Liste de dictionnaires contenant les comptes
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Compte WHERE id_utilisateur = ?", (id_utilisateur,))
        rows = cursor.fetchall()
        conn.close()
        
        accounts = []
        for row in rows:
            accounts.append({
                'id_compte': row[0],
                'id_utilisateur': row[1],
                'intitule_compte': row[2],
                'devise': row[3],
                'type_compte': row[4],
                'date_creation': row[5],
                'date_modification': row[6]
            })
        return accounts
    
    @staticmethod
    def update_by_id(id_compte, intitule_compte=None, devise=None, type_compte=None):
        """
        Mettre à jour un compte
        
        Args:
            id_compte (int): ID du compte
            intitule_compte (str, optional): Nouveau nom
            devise (str, optional): Nouvelle devise
            type_compte (str, optional): Nouveau type
            
        Returns:
            bool: True si la mise à jour a réussi
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if intitule_compte is not None:
            updates.append("intitule_compte = ?")
            params.append(intitule_compte)
        if devise is not None:
            updates.append("devise = ?")
            params.append(devise)
        if type_compte is not None:
            updates.append("type_compte = ?")
            params.append(type_compte)
        
        if not updates:
            conn.close()
            return False
        
        updates.append("date_modification = CURRENT_TIMESTAMP")
        params.append(id_compte)
        
        query = f"UPDATE Compte SET {', '.join(updates)} WHERE id_compte = ?"
        cursor.execute(query, params)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    @staticmethod
    def delete_by_id(id_compte):
        """
        Supprimer un compte
        
        Args:
            id_compte (int): ID du compte
            
        Returns:
            bool: True si la suppression a réussi
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Compte WHERE id_compte = ?", (id_compte,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
