# reference_data_repository.py
import os
import sqlite3
import csv

class ReferenceDataRepository:
    @staticmethod
    def ensure_database_and_populate(db_path: str, car_csv_path: str, track_csv_path: str):
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        conn = sqlite3.connect(db_path)
        try:
            ReferenceDataRepository.create_cars_table(conn)
            ReferenceDataRepository.create_tracks_table(conn)
            if ReferenceDataRepository.table_is_empty(conn, "Cars") and os.path.exists(car_csv_path):
                ReferenceDataRepository.import_cars_from_csv(conn, car_csv_path)
            if ReferenceDataRepository.table_is_empty(conn, "Tracks") and os.path.exists(track_csv_path):
                ReferenceDataRepository.import_tracks_from_csv(conn, track_csv_path)
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def create_cars_table(conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Cars(
                Ordinal INTEGER PRIMARY KEY,
                CarName TEXT
            );
        """)

    @staticmethod
    def create_tracks_table(conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS Tracks(
                Ordinal INTEGER PRIMARY KEY,
                TrackName TEXT
            );
        """)

    @staticmethod
    def table_is_empty(conn, table_name: str) -> bool:
        cur = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        return count == 0

    @staticmethod
    def import_cars_from_csv(conn, csv_path: str):
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            is_first = True
            for row in reader:
                if is_first:
                    is_first = False
                    continue
                if not row or len(row) < 2:
                    continue
                try:
                    ordinal = int(row[0].strip())
                except ValueError:
                    continue
                car_name = row[1].strip().strip('"')
                conn.execute("INSERT INTO Cars (Ordinal, CarName) VALUES (?, ?)", (ordinal, car_name))
        conn.commit()

    @staticmethod
    def import_tracks_from_csv(conn, csv_path: str):
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            is_first = True
            for row in reader:
                if is_first:
                    is_first = False
                    continue
                if not row or len(row) < 2:
                    continue
                try:
                    ordinal = int(row[0].strip())
                except ValueError:
                    continue
                track_name = row[1].strip().strip('"')
                conn.execute("INSERT INTO Tracks (Ordinal, TrackName) VALUES (?, ?)", (ordinal, track_name))
        conn.commit()

    @staticmethod
    def load_car_names(db_path: str) -> dict:
        conn = sqlite3.connect(db_path)
        car_names = {}
        try:
            cur = conn.execute("SELECT Ordinal, CarName FROM Cars")
            for row in cur.fetchall():
                car_names[row[0]] = row[1]
        finally:
            conn.close()
        return car_names

    @staticmethod
    def load_track_names(db_path: str) -> dict:
        conn = sqlite3.connect(db_path)
        track_names = {}
        try:
            cur = conn.execute("SELECT Ordinal, TrackName FROM Tracks")
            for row in cur.fetchall():
                track_names[row[0]] = row[1]
        finally:
            conn.close()
        return track_names
