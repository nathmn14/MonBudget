# Modèle pour la table Utilisateur

from data.connexion_bdd import get_connection


class UtilisateurModel:
    """
    Modèle pour la table Utilisateur dans la base de données
    Gère les opérations CRUD pour les utilisateurs
    """
    
    @staticmethod
    def create(email, mot_de_passe):
        """
        Créer un nouvel utilisateur
        
        Args:
            email (str): Email de l'utilisateur (unique)
            mot_de_passe (str): Mot de passe (à hasher dans une vraie app)
            
        Returns:
            int: ID de l'utilisateur créé
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Utilisateur (email, mot_de_passe)
            VALUES (?, ?)
        """, (email, mot_de_passe))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    @staticmethod
    def get_all():
        """
        Récupérer tous les utilisateurs
        
        Returns:
            list: Liste de dictionnaires contenant les utilisateurs
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Utilisateur")
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append({
                'id_utilisateur': row[0],
                'email': row[1],
                'mot_de_passe': row[2],
                'date_creation': row[3],
                'date_modification': row[4]
            })
        return users
    
    @staticmethod
    def get_by_id(id_utilisateur):
        """
        Récupérer un utilisateur par son ID
        
        Args:
            id_utilisateur (int): ID de l'utilisateur
            
        Returns:
            dict: Dictionnaire contenant l'utilisateur ou None
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Utilisateur WHERE id_utilisateur = ?", (id_utilisateur,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id_utilisateur': row[0],
                'email': row[1],
                'mot_de_passe': row[2],
                'date_creation': row[3],
                'date_modification': row[4]
            }
        return None
    
    @staticmethod
    def get_by_email(email):
        """
        Récupérer un utilisateur par son email
        
        Args:
            email (str): Email de l'utilisateur
            
        Returns:
            dict: Dictionnaire contenant l'utilisateur ou None
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Utilisateur WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id_utilisateur': row[0],
                'email': row[1],
                'mot_de_passe': row[2],
                'date_creation': row[3],
                'date_modification': row[4]
            }
        return None
    
    @staticmethod
    def update_by_id(id_utilisateur, email=None, mot_de_passe=None):
        """
        Mettre à jour un utilisateur
        
        Args:
            id_utilisateur (int): ID de l'utilisateur
            email (str, optional): Nouvel email
            mot_de_passe (str, optional): Nouveau mot de passe
            
        Returns:
            bool: True si la mise à jour a réussi
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if mot_de_passe is not None:
            updates.append("mot_de_passe = ?")
            params.append(mot_de_passe)
        
        if not updates:
            conn.close()
            return False
        
        updates.append("date_modification = CURRENT_TIMESTAMP")
        params.append(id_utilisateur)
        
        query = f"UPDATE Utilisateur SET {', '.join(updates)} WHERE id_utilisateur = ?"
        cursor.execute(query, params)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    @staticmethod
    def delete_by_id(id_utilisateur):
        """
        Supprimer un utilisateur
        
        Args:
            id_utilisateur (int): ID de l'utilisateur
            
        Returns:
            bool: True si la suppression a réussi
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Utilisateur WHERE id_utilisateur = ?", (id_utilisateur,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
