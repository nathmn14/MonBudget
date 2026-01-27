from data.connexion_bdd import get_connection
from datetime import datetime
import sqlite3

def migrate():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id_transaction, date_transaction FROM "Transaction"')
    rows = cursor.fetchall()
    
    updates = []
    for trans_id, date_str in rows:
        # Tenter de convertir DD/MM/YYYY vers YYYY-MM-DD
        try:
            # On gère le cas où c'est déjà bon ou a un format différent
            if '/' in date_str:
                date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                new_date = date_obj.strftime("%Y-%m-%d")
                updates.append((new_date, trans_id))
                print(f"Migrating {date_str} -> {new_date}")
        except Exception as e:
            print(f"Skipping {date_str}: {e}")
            
    if updates:
        cursor.executemany('UPDATE "Transaction" SET date_transaction = ? WHERE id_transaction = ?', updates)
        conn.commit()
        print(f"Migration terminée: {len(updates)} transactions mises à jour.")
    else:
        print("Aucune migration nécessaire.")
        
    conn.close()

if __name__ == "__main__":
    migrate()
