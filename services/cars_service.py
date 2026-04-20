from datetime import date
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from database import get_connection


class Details (BaseModel):
    name: str

class Car (BaseModel):
    model : str
    color : str
    year : date
    details : List[Details]



class CarService:
    def get_cars(self):
        connect = get_connection()
        cursor = connect.cursor()

        try:
            cursor.execute(
                """
                SELECT c.car_id, c.model, c.color, c.year,
                json_agg(
                    json_build_object(
                    'id' , d.details_id,
                    'name' , d.name
                    )) as details
                FROM car c JOIN details d ON c.car_id = d.car_id
                GROUP BY c.car_id
                ORDER BY c.car_id
                """
                )
            cars = cursor.fetchall()
            return cars
        finally:
            cursor.close()
            connect.close()

    def create_car(self, car: Car):
        connect = get_connection()
        cursor = connect.cursor()
        try:
            cursor.execute(
                "INSERT INTO car (model, color, year) VALUES (%s, %s, %s) RETURNING car_id",
                (car.model, car.color, car.year),
            )
            car_id = cursor.fetchone()['car_id']
            for detail in car.details:
                cursor.execute(
                    "INSERT INTO details (car_id, name) VALUES (%s, %s)",
                    (car_id, detail.name)
                )
            connect.commit()
            return car
        finally:
            cursor.close()
            connect.close()

    def get_car_by_id(self, car_id: int):
        connect = get_connection()
        cursor = connect.cursor()
        try:
            cursor.execute("SELECT * FROM car WHERE car_id = %s", (car_id,))
            car = cursor.fetchone()
            return car
        finally:
            cursor.close()
            connect.close()

    def update_car(self, car_id: int, car: Car):
        connect = get_connection()
        cursor = connect.cursor()
        try:
            cursor.execute(
                """
                UPDATE car
                SET model = %s, color = %s, year = %s
                WHERE car_id = %s
                RETURNING car_id
                """,
                (car.model, car.color, car.year, car_id),
            )
            car_id = cursor.fetchone()['car_id']

            cursor.execute(
                "DELETE FROM details WHERE car_id = %s",
                (car_id,)
            )

            for detail in car.details:
                cursor.execute(
                    "INSERT INTO details (car_id, name) VALUES (%s, %s)",
                    (car_id, detail.name)
                )

            connect.commit()
            return car

        finally:
            cursor.close()
            connect.close()


    def delete_car(self, car_id: int):
        connect = get_connection()
        cursor = connect.cursor()
        try:
            cursor.execute("DELETE FROM car WHERE car_id = %s", (car_id,))
            connect.commit()
            return JSONResponse(status_code=204, content={"message": "Car deleted successfully"})
        finally:
            cursor.close()
            connect.close()

