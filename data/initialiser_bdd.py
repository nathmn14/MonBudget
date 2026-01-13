# Je commencer par importer la fonction de connexion a la base de donnees
from .connexion_bdd import get_connection

# Ensuite je peux initialiser cette bdd

def init_database():
    """Fonction d'initialisation de la base de donnees avec les tables necessaires, mentionnnees dans structure_bdd.md"""
    conn = get_connection()   # get_connection() provient du fichier ou du module connexion_bdd
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Utilisateur (
        id_utilisateur INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        mot_de_passe TEXT NOT NULL,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS Compte (
        id_compte INTEGER PRIMARY KEY AUTOINCREMENT,
        id_utilisateur INTEGER NOT NULL,
        intitule_compte TEXT NOT NULL,
        devise TEXT NOT NULL,
        type_compte TEXT NOT NULL,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_utilisateur) REFERENCES Utilisateur(id_utilisateur)
    );

    CREATE TABLE IF NOT EXISTS Categorie (
        id_categorie INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_categorie TEXT NOT NULL,
        type_transaction TEXT CHECK(type_transaction IN ('ENTREE','SORTIE')),
        icone TEXT DEFAULT 'plus-box-multiple',
        couleur TEXT DEFAULT '0.2,0.2,0.2,1',
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS "Transaction" (
        id_transaction INTEGER PRIMARY KEY AUTOINCREMENT,
        id_compte INTEGER NOT NULL,
        id_categorie INTEGER NOT NULL,
        montant REAL NOT NULL,
        type_transaction TEXT CHECK(type_transaction IN ('ENTREE','SORTIE')),
        description TEXT,
        date_transaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_compte) REFERENCES Compte(id_compte),
        FOREIGN KEY (id_categorie) REFERENCES Categorie(id_categorie)
    );

    CREATE TABLE IF NOT EXISTS Portefeuille (
        id_portefeuille INTEGER PRIMARY KEY AUTOINCREMENT,
        id_compte INTEGER NOT NULL,
        solde REAL NOT NULL,
        date_heure TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_compte) REFERENCES Compte(id_compte)
    );
    
    CREATE TABLE IF NOT EXISTS Budget (
        id_budget INTEGER PRIMARY KEY AUTOINCREMENT,
        id_compte INTEGER NOT NULL,
        budget_total REAL NOT NULL DEFAULT 0,
        jours_restants INTEGER NOT NULL DEFAULT 30,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_compte) REFERENCES Compte(id_compte)
    );
    """)

    conn.commit()
    conn.close()
