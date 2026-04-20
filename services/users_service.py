import numbers

from fastapi import HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
from database import get_connection


class Car(BaseModel):
    model: str = Field(..., max_length=256)
    color: str
    year: str


class CarsService:

    def get_cars(self):
        connect = get_connection()
        cursor = connect.cursor()
        try:
            cursor.execute("SELECT * FROM users ORDER BY id ASC")
            return cursor.fetchall()

        except Exception as e:
            print(e)
            raise HTTPException(status_code=404, detail="Users not found")

        finally:
            cursor.close()
            connect.close()

    def create_car(self, car: Car):
        connect = get_connection()
        cursor = connect.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (model, color, year) VALUES (%s, %s, %s)",
                (car.model, car.color, car.year)
            )
            connect.commit()

            return car

        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Car already exists")

        finally:
            cursor.close()
            connect.close()

    def delete_car(self, car_id: int):
        connect = get_connection()
        cursor = connect.cursor()
        try:
            cursor.execute("DELETE FROM cars WHERE id = %s", (car_id,))
            connect.commit()
            return JSONResponse(status_code=204, content={"message": "Car deleted successfully"})

        except Exception as e:
            print(str(e))
            raise HTTPException(status_code=404, detail="Car not found")
        finally:
            cursor.close()
            connect.close()

    def update_car(self, car_id: int, car: Car):
        connect = get_connection()
        cursor = connect.cursor()
        try:
            cursor.execute(
                "UPDATE cars SET model=%s, color=%s, year=%s WHERE id=%s",
                (car.email, car.phone_number, car.full_name, car_id)
            )
            connect.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Car not found")

            return {
                "id": car_id,
                "model": car.model,
                "color": car.color,
                "year": car.year
            }

        finally:
            cursor.close()
            connect.close()
