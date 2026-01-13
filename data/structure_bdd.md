# 1. Utilisateur
- id_utilisateur (PK)
- email (unique)
- mot_de_passe
- date_creation
- date_modification

# 2. Compte
- id_compte (PK)
- id_utilisateur (FK)
- intitule_compte
- devise
- type_compte (cash, banque, mobile money…)
- date_creation
- date_modification


# 3. Categorie
- id_categorie (PK)
- nom_categorie
- type_transaction (ENTREE / SORTIE)
- date_creation
- date_modification


# 4. Transaction
- id_transaction (PK)
- id_compte (FK)
- id_categorie (FK)
- montant
- type_transaction (ENTREE / SORTIE)
- description
- date_transaction
- date_creation
- date_modification


# 5. Portefeuille
- id_portefeuille (PK)
- id_compte (FK)
- solde
- date_heure


