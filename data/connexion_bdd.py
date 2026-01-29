import os
from kivy.utils import platform
import sqlite3

# Définir l'emplacement de la base de données selon la plateforme
if platform == 'android':
    from android.storage import app_storage_path
    # Sur Android, on utilise le dossier de données de l'application
    DEFAULT_DB_PATH = os.path.join(os.environ.get('PYTHON_SERVICE_ARGUMENT', ''), 'data')
    # Alternative plus robuste pour Kivy:
    from kivy.app import App
    # Note: On calculera le chemin final dynamiquement si besoin, ou on utilise un chemin relatif 
    # qui sera géré par buildozer (source.dir).
    # Pour faire simple et robuste sur Android :
    db_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    DB_NAME = os.path.join(db_dir, "monbudget.db")
else:
    # Desktop
    DB_NAME = "data/monbudget.db"

def get_connection():
    """
Fonction de connexion a la base de donnees sqlite aue je vais appeler dans le fichier de creation de la base de donnees et dans les fichiers ou j'ai besoin d'acceder a la base de donnees.
    """
    # Ajout de multi-threading support et timeout pour éviter les blocages lors des accès concurrents
    conn = sqlite3.connect(DB_NAME, check_same_thread=False, timeout=10)   
    conn.execute("PRAGMA foreign_keys = ON;")
    # Optimisation pour les perfs et la concurrence
    conn.execute("PRAGMA journal_mode = WAL;") 
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
        """, ("default@monbudget.app", "0000"))
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
