import sqlite3
import os
from interface.interface_save import InterfaceSave
from core.model import Model


class SQLiteStorage(InterfaceSave):
    """
    Usage:
        storage = SQLiteStorage("values.db")
        storage.save_data(model)
        results = search_data("42")
        all_data = load_data()
    """

    def __init__(self, db_path: str = "values.db"):
        self.db_path = db_path
        self._create_table()

    # Initialisation de la table

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    address     TEXT    NOT NULL,
                    formats     TEXT    NOT NULL,
                    temperature REAL,
                    luminosity  REAL,
                    humidity    REAL,
                    pressure    REAL,
                    uv          REAL,
                    end         REAL,
                    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_address
                ON sensor_data (address)
            """)
            conn.commit()

    # CRUD

    def save_data(self, data: Model):
        print(f"[DB] Sauvegarde : {data}")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO sensor_data (address, formats, temperature, luminosity, humidity, pressure, uv, end)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(data.address),
                    str(data.formats).upper(),
                    float(data.temperature),
                    float(data.luminosity),
                    float(data.humidity),
                    float(data.pressure),
                    float(data.uv),
                    float(data.end),
                ),
            )
            conn.commit()

    def search_data(self, query: str, separateur: str = ";") -> list[Model]:
        liste_models = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM sensor_data WHERE address = ? ORDER BY timestamp DESC",
                    (str(query),),
                )
                for row in cursor:
                    liste_models.append(self._row_to_model(row))
        except Exception as e:
            print(f"Erreur de recherche : {e}")
        return liste_models

    # Retourne tous les enregistrements (du plus récent au plus ancien).
    def load_data(self) -> list[Model]:
        liste_models = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM sensor_data ORDER BY timestamp DESC"
                )
                for row in cursor:
                    liste_models.append(self._row_to_model(row))
        except Exception as e:
            print(f"Erreur de chargement : {e}")
        return liste_models

    def delete_data(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM sensor_data")
                conn.commit()
        except Exception as e:
            print(f"Erreur lors de la suppression : {e}")

    # Retourne True si au moins un enregistrement est présent.
    def data_exists(self) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM sensor_data")
                return cursor.fetchone()[0] > 0
        except Exception:
            return False

    # Retourne les n derniers enregistrements. Si address est précisé, filtre par adresse.
    def get_last_n(self, n: int, address: str = None) -> list[Model]:
        liste_models = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                if address:
                    cursor = conn.execute(
                        "SELECT * FROM sensor_data WHERE address = ? ORDER BY timestamp DESC LIMIT ?",
                        (str(address), n),
                    )
                else:
                    cursor = conn.execute(
                        "SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT ?",
                        (n,),
                    )
                for row in cursor:
                    liste_models.append(self._row_to_model(row))
        except Exception as e:
            print(f"Erreur get_last_n : {e}")
        return liste_models

    # Retourne la liste des adresses distinctes présentes en base.
    def get_all_addresses(self) -> list[str]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT DISTINCT address FROM sensor_data ORDER BY address"
                )
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Erreur get_all_addresses : {e}")
            return []

    # Supprime le fichier .db entièrement.
    def drop_database(self):
        try:
            os.remove(self.db_path)
        except FileNotFoundError:
            pass

    # Convertit une ligne SQLite en objet Model
    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> Model:
        return Model(
            address=row["address"],
            formats=row["formats"],
            temperature=str(row["temperature"]),
            luminosity=str(row["luminosity"]),
            humidity=str(row["humidity"]),
            pressure=str(row["pressure"]),
            uv=str(row["uv"]),
            end=str(row["end"]),
        )
