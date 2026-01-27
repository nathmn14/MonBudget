# requetes sql

# 1. Inserer les categories sur la table categorie

INSERT INTO Categorie (nom_categorie, type_transaction) VALUES
('Salaire', 'ENTREE'),
('Alimentation', 'SORTIE'),
('Logement', 'SORTIE'),
('Loisirs', 'SORTIE'),
('Business', 'ENTREE'),
('Énergie', 'SORTIE'),
('Transport', 'SORTIE'),
('Santé', 'SORTIE'),
('Éducation', 'SORTIE');


# 2. Ajouter les champs icone et couleur
ALTER TABLE Categorie ADD COLUMN icone TEXT;
ALTER TABLE Categorie ADD COLUMN couleur TEXT;