# On creer le modele categorie.py pour communiquer avec la base de donnees, plus particulierement la table categorie

import sqlite3
#import de la connexion a la base de donnees
from data.connexion_bdd import get_connection


class ParametreModel : 
    """
    Modele pour les parametres, gestion du mot de passe et du theme de l'application
    """
    