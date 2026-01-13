# Modèle pour la table Transaction

from data.connexion_bdd import get_connection
from datetime import datetime


class TransactionModel:
    """
    Modèle pour la table Transaction dans la base de données
    Gère les transactions (entrées et sorties d'argent)
    """
    
    @staticmethod
    def create(id_compte, id_categorie, montant, type_transaction, description='', date_transaction=None):
        """
        Créer une nouvelle transaction
        
        Args:
            id_compte (int): ID du compte
            id_categorie (int): ID de la catégorie
            montant (float): Montant de la transaction
            type_transaction (str): 'ENTREE' ou 'SORTIE'
            description (str, optional): Description de la transaction
            date_transaction (str, optional): Date au format YYYY-MM-DD, par défaut date actuelle
            
        Returns:
            int: ID de la transaction créée
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        if date_transaction is None:
            date_transaction = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            INSERT INTO "Transaction" (id_compte, id_categorie, montant, type_transaction, description, date_transaction)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_compte, id_categorie, montant, type_transaction, description, date_transaction))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return transaction_id
    
    @staticmethod
    def get_all():
        """
        Récupérer toutes les transactions
        
        Returns:
            list: Liste de dictionnaires contenant les transactions
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Transaction" ORDER BY date_transaction DESC')
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append({
                'id_transaction': row[0],
                'id_compte': row[1],
                'id_categorie': row[2],
                'montant': row[3],
                'type_transaction': row[4],
                'description': row[5],
                'date_transaction': row[6],
                'date_creation': row[7],
                'date_modification': row[8]
            })
        return transactions
    
    @staticmethod
    def get_by_id(id_transaction):
        """
        Récupérer une transaction par son ID
        
        Args:
            id_transaction (int): ID de la transaction
            
        Returns:
            dict: Dictionnaire contenant la transaction ou None
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Transaction" WHERE id_transaction = ?', (id_transaction,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id_transaction': row[0],
                'id_compte': row[1],
                'id_categorie': row[2],
                'montant': row[3],
                'type_transaction': row[4],
                'description': row[5],
                'date_transaction': row[6],
                'date_creation': row[7],
                'date_modification': row[8]
            }
        return None
    
    @staticmethod
    def get_by_account(id_compte):
        """
        Récupérer toutes les transactions d'un compte
        
        Args:
            id_compte (int): ID du compte
            
        Returns:
            list: Liste de dictionnaires contenant les transactions
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Transaction" WHERE id_compte = ? ORDER BY date_transaction DESC', (id_compte,))
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append({
                'id_transaction': row[0],
                'id_compte': row[1],
                'id_categorie': row[2],
                'montant': row[3],
                'type_transaction': row[4],
                'description': row[5],
                'date_transaction': row[6],
                'date_creation': row[7],
                'date_modification': row[8]
            })
        return transactions
    
    @staticmethod
    def get_by_category(id_categorie):
        """
        Récupérer toutes les transactions d'une catégorie
        
        Args:
            id_categorie (int): ID de la catégorie
            
        Returns:
            list: Liste de dictionnaires contenant les transactions
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM "Transaction" WHERE id_categorie = ? ORDER BY date_transaction DESC', (id_categorie,))
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append({
                'id_transaction': row[0],
                'id_compte': row[1],
                'id_categorie': row[2],
                'montant': row[3],
                'type_transaction': row[4],
                'description': row[5],
                'date_transaction': row[6],
                'date_creation': row[7],
                'date_modification': row[8]
            })
        return transactions
    
    @staticmethod
    def get_by_type(type_transaction, id_compte=None):
        """
        Récupérer les transactions par type (ENTREE ou SORTIE)
        
        Args:
            type_transaction (str): 'ENTREE' ou 'SORTIE'
            id_compte (int, optional): Filtrer par compte
            
        Returns:
            list: Liste de dictionnaires contenant les transactions
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        if id_compte:
            cursor.execute(
                'SELECT * FROM "Transaction" WHERE type_transaction = ? AND id_compte = ? ORDER BY date_transaction DESC',
                (type_transaction, id_compte)
            )
        else:
            cursor.execute(
                'SELECT * FROM "Transaction" WHERE type_transaction = ? ORDER BY date_transaction DESC',
                (type_transaction,)
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append({
                'id_transaction': row[0],
                'id_compte': row[1],
                'id_categorie': row[2],
                'montant': row[3],
                'type_transaction': row[4],
                'description': row[5],
                'date_transaction': row[6],
                'date_creation': row[7],
                'date_modification': row[8]
            })
        return transactions
    
    @staticmethod
    def get_by_date_range(start_date, end_date, id_compte=None):
        """
        Récupérer les transactions dans une période donnée
        
        Args:
            start_date (str): Date de début (YYYY-MM-DD)
            end_date (str): Date de fin (YYYY-MM-DD)
            id_compte (int, optional): Filtrer par compte
            
        Returns:
            list: Liste de dictionnaires contenant les transactions
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        if id_compte:
            cursor.execute(
                'SELECT * FROM "Transaction" WHERE date_transaction BETWEEN ? AND ? AND id_compte = ? ORDER BY date_transaction DESC',
                (start_date, end_date, id_compte)
            )
        else:
            cursor.execute(
                'SELECT * FROM "Transaction" WHERE date_transaction BETWEEN ? AND ? ORDER BY date_transaction DESC',
                (start_date, end_date)
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append({
                'id_transaction': row[0],
                'id_compte': row[1],
                'id_categorie': row[2],
                'montant': row[3],
                'type_transaction': row[4],
                'description': row[5],
                'date_transaction': row[6],
                'date_creation': row[7],
                'date_modification': row[8]
            })
        return transactions
    
    @staticmethod
    def update_by_id(id_transaction, id_categorie=None, montant=None, type_transaction=None, description=None, date_transaction=None):
        """
        Mettre à jour une transaction
        
        Args:
            id_transaction (int): ID de la transaction
            id_categorie (int, optional): Nouvelle catégorie
            montant (float, optional): Nouveau montant
            type_transaction (str, optional): Nouveau type
            description (str, optional): Nouvelle description
            date_transaction (str, optional): Nouvelle date
            
        Returns:
            bool: True si la mise à jour a réussi
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if id_categorie is not None:
            updates.append("id_categorie = ?")
            params.append(id_categorie)
        if montant is not None:
            updates.append("montant = ?")
            params.append(montant)
        if type_transaction is not None:
            updates.append("type_transaction = ?")
            params.append(type_transaction)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if date_transaction is not None:
            updates.append("date_transaction = ?")
            params.append(date_transaction)
        
        if not updates:
            conn.close()
            return False
        
        updates.append("date_modification = CURRENT_TIMESTAMP")
        params.append(id_transaction)
        
        query = f'UPDATE "Transaction" SET {", ".join(updates)} WHERE id_transaction = ?'
        cursor.execute(query, params)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    @staticmethod
    def delete_by_id(id_transaction):
        """
        Supprimer une transaction
        
        Args:
            id_transaction (int): ID de la transaction
            
        Returns:
            bool: True si la suppression a réussi
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM "Transaction" WHERE id_transaction = ?', (id_transaction,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    @staticmethod
    def get_total_by_type(type_transaction, id_compte, month=None, year=None):
        """
        Calculer le total des transactions par type pour un compte
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT COALESCE(SUM(montant), 0) FROM "Transaction" WHERE type_transaction = ? AND id_compte = ?'
        params = [type_transaction, id_compte]
        
        if month and year:
            # Format attendu : YYYY-MM
            month_str = f"{year}-{month:02d}"
            query += " AND date_transaction LIKE ?"
            params.append(f"{month_str}%")
            
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result[0]

    @staticmethod
    def get_stats_by_category(id_compte, type_transaction='SORTIE', month=None, year=None):
        """
        Récupère le total des transactions par catégorie pour un compte et un type donné.
        Ne retourne QUE les catégories ayant des transactions pour la période spécifiée.
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT c.nom_categorie, SUM(t.montant) as total, c.icone, c.couleur
            FROM "Transaction" t
            JOIN Categorie c ON t.id_categorie = c.id_categorie
            WHERE t.id_compte = ? AND t.type_transaction = ?
        """
        params = [id_compte, type_transaction]
        
        if month and year:
            # Format attendu : YYYY-MM
            month_str = f"{year}-{month:02d}"
            query += " AND t.date_transaction LIKE ?"
            params.append(f"{month_str}%")
            
        query += """
            GROUP BY c.id_categorie
            ORDER BY total DESC
        """
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        stats = []
        for row in rows:
            stats.append({
                'nom': row[0],
                'total': row[1],
                'icone': row[2],
                'couleur': row[3]
            })
        return stats

    @staticmethod
    def get_latest_transaction_date(id_compte):
        """Récupère la date de la transaction la plus récente pour un compte donné"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date_transaction FROM "Transaction" 
            WHERE id_compte = ? 
            ORDER BY date_transaction DESC LIMIT 1
        """, (id_compte,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
