from data.connexion_bdd import get_connection
import sqlite3

def diag():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    with open('diag_result.txt', 'w', encoding='utf-8') as f:
        f.write("--- CATEGORIES ---\n")
        cursor.execute("SELECT id_categorie, nom_categorie, type_transaction FROM Categorie")
        for r in cursor.fetchall():
            f.write(str(dict(r)) + "\n")
            
        f.write("\n--- TRANSACTIONS ---\n")
        cursor.execute('SELECT * FROM "Transaction"')
        rows = cursor.fetchall()
        f.write(f"Total Transactions: {len(rows)}\n")
        for r in rows:
            f.write(str(dict(r)) + "\n")

        f.write("\n--- COMPTES ---\n")
        cursor.execute('SELECT * FROM Compte')
        for r in cursor.fetchall():
            f.write(str(dict(r)) + "\n")
        
    conn.close()
    print("Diagnostic terminé, voir diag_result.txt")

if __name__ == "__main__":
    diag()
