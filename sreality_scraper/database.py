from typing import List

import psycopg2
import psycopg2.extras
from srality_orm import AdvertisingModel


class SrealityDatabase:
    def __init__(self, database: str, user: str, password: str, host='127.0.0.1', port='5432'):
        self.conn = psycopg2.connect(
            database=database, user=user, password=password, host=host, port=port
        )
        self.conn.autocommit = True

    def insert_many(self, advertisments: List[AdvertisingModel]):
        cursor = self.conn.cursor()
        [self._insert(advert, cursor) for advert in advertisments]
        self.conn.commit()

    def insert_one(self, advert: AdvertisingModel):
        cursor = self.conn.cursor()

        self._insert(advert, cursor)
        self.conn.commit()

    @staticmethod
    def _insert(advert: AdvertisingModel, cursor):
        cursor.execute(
            """INSERT INTO sreality(id, title, location, price, living_area, reality_type, building_type, deal_type,
             url, images, created_at, updated_at)
            VALUES (%s, %s, %s, %s,  %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING""",
            (advert.id, advert.title, advert.location, advert.price, advert.living_area, advert.reality_type,
             advert.building_type, advert.deal_type, advert.url, advert.images, advert.created_at, advert.updated_at,))

    def close(self):
        self.conn.close()

    def get_data(self, how_many=20):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(f'SELECT * from sreality LIMIT {how_many}')
        results = cursor.fetchall()
        return [AdvertisingModel(**res) for res in results]


if __name__ == '__main__':
    from main import RealityScraper

    db_ = SrealityDatabase(database='sreality', user='sreality', password='sreality_postgres')
    scraper = RealityScraper(max_advertising=20)
    data = scraper()
    db_.insert_many(data)
    print(db_.get_data(how_many=20))
    db_.close()
