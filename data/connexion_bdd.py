# Ce fichier sert uniquement a la connexion a la base de donnees qui est une bdd sqlite

import sqlite3

DB_NAME = "data/monbudget.db" # defini le nom et l'emplacement de la base de donnees

def get_connection():
    """
Fonction de connexion a la base de donnees sqlite aue je vais appeler dans le fichier de creation de la base de donnees et dans les fichiers ou j'ai besoin d'acceder a la base de donnees.
    """
       # C'est ici que se cree la bdd, lorsqu'on va appeler la fonction (Si elle n'existe pas)
    conn = sqlite3.connect(DB_NAME)   
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_default_user_and_account():
    """
    Crée un utilisateur et un compte par défaut si ils n'existent pas.
    Utilisé au démarrage de l'application.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Vérifier si l'utilisateur par défaut existe
    cursor.execute("SELECT id_utilisateur FROM Utilisateur WHERE email = ?", ("default@monbudget.app",))
    user = cursor.fetchone()
    
    if not user:
        # Créer l'utilisateur par défaut
        cursor.execute("""
            INSERT INTO Utilisateur (email, mot_de_passe)
            VALUES (?, ?)
        """, ("default@monbudget.app", "default_password"))
        user_id = cursor.lastrowid
        
        # Créer le compte par défaut
        cursor.execute("""
            INSERT INTO Compte (id_utilisateur, intitule_compte, devise, type_compte)
            VALUES (?, ?, ?, ?)
        """, (user_id, "Mon Compte Principal", "FC", "cash"))
        
        conn.commit()
    
    conn.close()


def get_default_user_id():
    """Récupère l'ID de l'utilisateur par défaut"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_utilisateur FROM Utilisateur WHERE email = ?", ("default@monbudget.app",))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_default_account_id():
    """Récupère l'ID du compte par défaut"""
    conn = get_connection()
    cursor = conn.cursor()
    user_id = get_default_user_id()
    if user_id:
        cursor.execute("SELECT id_compte FROM Compte WHERE id_utilisateur = ? LIMIT 1", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    conn.close()
    return None
