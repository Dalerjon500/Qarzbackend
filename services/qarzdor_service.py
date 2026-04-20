from contextlib import contextmanager
from pydantic import BaseModel
from database import get_connection


# ================= BASE SERVICE =================
class BaseService:
    @contextmanager
    def get_cursor(self):
        connect = get_connection()
        cursor = connect.cursor()
        try:
            yield cursor
            connect.commit()
        except Exception:
            connect.rollback()
            raise
        finally:
            cursor.close()
            connect.close()


# ================= Pydantic MODELS =================
class Qarzdor(BaseModel):
    full_name: str
    phone_number: str


class Qarz(BaseModel):
    miqdor: int
    holati: bool = False


# ================= SERVICE =================
class QarzdorService(BaseService):

    # -------- QARZDORLAR --------
    def get_qarzdorlar(self):
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    q.qarzdor_id,
                    q.full_name,
                    q.phone_number,
                    COALESCE(SUM(qz.miqdor), 0) AS total_qarz
                FROM qarzdor q
                LEFT JOIN qarz qz ON q.qarzdor_id = qz.qarzdor_id
                GROUP BY q.qarzdor_id, q.full_name, q.phone_number
                ORDER BY q.qarzdor_id
            """)
            return cursor.fetchall()

    def get_qarzdor_by_id(self, qarzdor_id: int):
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    q.qarzdor_id,
                    q.full_name,
                    q.phone_number,
                    COALESCE(SUM(qz.miqdor), 0) AS total_qarz
                FROM qarzdor q
                LEFT JOIN qarz qz ON q.qarzdor_id = qz.qarzdor_id
                WHERE q.qarzdor_id = %s
                GROUP BY q.qarzdor_id, q.full_name, q.phone_number
            """, (qarzdor_id,))
            return cursor.fetchone()

    def create_qarzdor(self, qarzdor: Qarzdor):
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO qarzdor (full_name, phone_number)
                VALUES (%s, %s)
                RETURNING qarzdor_id
            """, (qarzdor.full_name, qarzdor.phone_number))
            return {"qarzdor_id": cursor.fetchone()["qarzdor_id"]}

    # -------- QARZ --------
    def add_qarz_to_qarzdor(self, qarzdor_id: int, qarz: Qarz):
        with self.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO qarz (qarzdor_id, miqdor, holati)
                VALUES (%s, %s, %s)
                RETURNING qarz_id
            """, (qarzdor_id, qarz.miqdor, qarz.holati))
            return {"qarz_id": cursor.fetchone()["qarz_id"]}

    def get_qarz_by_qarzdor_id(self, qarzdor_id: int):
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    qarz_id,
                    datetime,
                    miqdor,
                    holati
                FROM qarz
                WHERE qarzdor_id = %s
                ORDER BY datetime DESC
            """, (qarzdor_id,))
            return cursor.fetchall()

    # -------- REPAYMENT --------
    def repayment(self, qarzdor_id: int, qarz_id: int, miqdor: int):
        with self.get_cursor() as cursor:
            # to‘lov yozish
            cursor.execute("""
                INSERT INTO tulovlar_tarixi (qarz_id, miqdor)
                VALUES (%s, %s)
            """, (qarz_id, miqdor))

            # agar qarz yopilsa holati true
            cursor.execute("""
                UPDATE qarz
                SET holati = TRUE
                WHERE qarz_id = %s
                  AND (
                    SELECT COALESCE(SUM(t.miqdor), 0)
                    FROM tulovlar_tarixi t
                    WHERE t.qarz_id = %s
                  ) >= (
                    SELECT q.miqdor
                    FROM qarz q
                    WHERE q.qarz_id = %s
                  )
            """, (qarz_id, qarz_id, qarz_id))

            return {"message": "Repayment muvaffaqiyatli"}

    # -------- HISTORY --------
    def get_qarzlar_history(self, qarzdor_id: int):
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    t.tulov_id,
                    t.datetime,
                    t.miqdor,
                    t.qarz_id
                FROM tulovlar_tarixi t
                JOIN qarz q ON q.qarz_id = t.qarz_id
                WHERE q.qarzdor_id = %s
                ORDER BY t.datetime DESC
            """, (qarzdor_id,))
            return cursor.fetchall()
