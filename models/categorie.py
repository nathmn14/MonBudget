# On creer le modele categorie.py pour communiquer avec la base de donnees, plus particulierement la table categorie

import sqlite3
#import de la connexion a la base de donnees
from data.connexion_bdd import get_connection


class CategorieModel : 
    """
    Modele pour la table categorie dans la base de donnees
    Gère les opérations CRUD (Create, Read, Update, Delete)
    """

    # 1. CREATE - Créer une nouvelle catégorie
    @staticmethod
    def create(nom, type_transaction, icone='plus-box-multiple', couleur='0.2,0.2,0.2,1'):
        """
        Créer une nouvelle catégorie dans la base de données
        
        Args:
            nom (str): Nom de la catégorie
            type_transaction (str): 'ENTREE' ou 'SORTIE'
            icone (str): Nom de l'icône Material Design
            couleur (str): Couleur au format RGBA séparé par des virgules
        
        Returns:
            int: ID de la catégorie créée
        """
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Categorie (nom_categorie, type_transaction, icone, couleur)
            VALUES (?, ?, ?, ?)
        """, (nom, type_transaction, icone, couleur))

        category_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return category_id

    # 2. READ - Lire les catégories
    @staticmethod
    def get_all():
        """
        Récupérer toutes les catégories depuis la base de données
        
        Returns:
            list: Liste de dictionnaires contenant les catégories
        """
        conn = get_connection()
        conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Categorie ORDER BY date_creation DESC")
        rows = cursor.fetchall()
        conn.close()
        
        categories = []
        for row in rows:
            categories.append({
                'id_categorie': row['id_categorie'],
                'nom_categorie': row['nom_categorie'],
                'type_transaction': row['type_transaction'],
                'icone': row['icone'],
                'couleur': row['couleur'],
                'date_creation': row['date_creation'],
                'date_modification': row['date_modification']
            })
        return categories

    @staticmethod
    def get_by_id(id_categorie):
        """
        Récupérer une catégorie par son ID
        
        Args:
            id_categorie (int): ID de la catégorie
            
        Returns:
            dict: Dictionnaire contenant la catégorie ou None
        """
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Categorie WHERE id_categorie = ?", (id_categorie,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id_categorie': row['id_categorie'],
                'nom_categorie': row['nom_categorie'],
                'type_transaction': row['type_transaction'],
                'icone': row['icone'],
                'couleur': row['couleur'],
                'date_creation': row['date_creation'],
                'date_modification': row['date_modification']
            }
        return None

    @staticmethod
    def get_by_type(type_transaction):
        """
        Récupérer les catégories par type de transaction
        
        Args:
            type_transaction (str): 'ENTREE' ou 'SORTIE'
            
        Returns:
            list: Liste de dictionnaires contenant les catégories
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Categorie WHERE type_transaction = ?", (type_transaction,))
        rows = cursor.fetchall()
        conn.close()
        
        categories = []
        for row in rows:
            categories.append({
                'id_categorie': row[0],
                'nom_categorie': row[1],
                'type_transaction': row[2],
                'icone': row[3],
                'couleur': row[4],
                'date_creation': row[5],
                'date_modification': row[6]
            })
        return categories

    # 3. UPDATE - Mettre à jour une catégorie
    @staticmethod
    def update_by_id(id_categorie, nom_categorie=None, type_transaction=None, icone=None, couleur=None):
        """
        Mettre à jour une catégorie par son ID
        
        Args:
            id_categorie (int): ID de la catégorie
            nom_categorie (str, optional): Nouveau nom
            type_transaction (str, optional): Nouveau type
            icone (str, optional): Nouvelle icône
            couleur (str, optional): Nouvelle couleur
            
        Returns:
            bool: True si la mise à jour a réussi
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if nom_categorie is not None:
            updates.append("nom_categorie = ?")
            params.append(nom_categorie)
        if type_transaction is not None:
            updates.append("type_transaction = ?")
            params.append(type_transaction)
        if icone is not None:
            updates.append("icone = ?")
            params.append(icone)
        if couleur is not None:
            updates.append("couleur = ?")
            params.append(couleur)
        
        if not updates:
            conn.close()
            return False
        
        updates.append("date_modification = CURRENT_TIMESTAMP")
        params.append(id_categorie)
        
        query = f"UPDATE Categorie SET {', '.join(updates)} WHERE id_categorie = ?"
        cursor.execute(query, params)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    @staticmethod
    def delete_by_id(id_categorie):
        """
        Supprimer une catégorie par son ID.
        Si des transactions sont liées, lève une sqlite3.IntegrityError.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # S'assurer que les clés étrangères sont activées pour cette connexion
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("DELETE FROM Categorie WHERE id_categorie = ?", (id_categorie,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
        except sqlite3.IntegrityError:
            # Cette erreur arrive si id_categorie est utilisé ailleurs (clé étrangère)
            return "INTEGRITY_ERROR"
        finally:
            conn.close()

    # INITIALISATION - Créer les catégories par défaut
    @staticmethod
    def init_default_categories():
        """
        Créer les catégories par défaut si la table est vide
        Cette fonction est appelée au démarrage de l'application
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Vérifier si des catégories existent déjà
        cursor.execute("SELECT COUNT(*) FROM Categorie")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            return  # Des catégories existent déjà
        
        # Catégories par défaut (nom, type, icone, couleur RGBA)
        default_categories = [
            ('Alimentation', 'SORTIE', 'food', '0.18,0.8,0.44,1'),
            ('Transport', 'SORTIE', 'car', '0.2,0.6,0.86,1'),
            ('Logement', 'SORTIE', 'home', '0.9,0.5,0.13,1'),
            ('Loisirs', 'SORTIE', 'controller-classic', '0.6,0.3,0.7,1'),
            ('Courses', 'SORTIE', 'cart', '0.1,0.7,0.7,1'),
            ('Telephone', 'SORTIE', 'phone-settings', '0.5,0.5,0.5,1'),
            ('Café', 'SORTIE', 'coffee', '0.44,0.26,0.13,1'),
            ('Cadeaux', 'SORTIE', 'gift', '0.9,0.3,0.23,1'),
            ('Cinéma', 'SORTIE', 'movie', '0.2,0.2,0.2,1'),
            ('Etudes', 'SORTIE', 'school', '0.12,0.5,0.7,1'),
            ('Santé', 'SORTIE', 'medical-bag', '0.95,0.2,0.4,1'),
            ('Business', 'SORTIE', 'trending-up', '0.1,0.3,0.5,1'),
            ('Énergie', 'SORTIE', 'lightning-bolt', '1,0.8,0.2,1'),
            ('Éducation', 'SORTIE', 'book-open-variant', '0.5,0.4,0.3,1'),
            ('Salaire', 'ENTREE', 'cash-multiple', '0.15,0.68,0.37,1'),
        ]
        
        for nom, type_trans, icon, color in default_categories:
            CategorieModel.create(nom, type_trans, icon, color)
