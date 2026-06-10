import csv
import struct
import zlib
from datetime import datetime

import mysql.connector


DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'welcome1',
    'database': 'mars_db'
}

CSV_FILE = 'mars_weathers_data.csv'
PNG_FILE = 'mars_weather_summary.png'


class MySQLHelper:
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = mysql.connector.connect(**self.config)
        self.cursor = self.connection.cursor()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params)

    def commit(self):
        if self.connection is not None:
            self.connection.commit()

    def rollback(self):
        if self.connection is not None:
            self.connection.rollback()

    def close(self):
        if self.cursor is not None:
            self.cursor.close()

        if self.connection is not None:
            self.connection.close()


def create_table(db_helper):
    sql = '''
        CREATE TABLE IF NOT EXISTS mars_weather (
            weather_id INT AUTO_INCREMENT PRIMARY KEY,
            mars_date DATETIME NOT NULL,
            temp INT,
            storm INT
        )
    '''
    db_helper.execute(sql)


def parse_datetime(value):
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%Y/%m/%d %H:%M:%S',
        '%Y/%m/%d'
    ]

    for date_format in formats:
        try:
            return datetime.strptime(value, date_format)
        except ValueError:
            pass

    raise ValueError('지원하지 않는 날짜 형식입니다: ' + value)


def read_weather_data(csv_file):
    weather_data = []

    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            mars_date = parse_datetime(row['mars_date'])
            temp = int(row['temp'])
            storm = int(row['storm'])

            weather_data.append((mars_date, temp, storm))

    return weather_data


def insert_weather_data(db_helper, weather_data):
    sql = '''
        INSERT INTO mars_weather (mars_date, temp, storm)
        VALUES (%s, %s, %s)
    '''

    for weather in weather_data:
        db_helper.execute(sql, weather)


def get_summary(weather_data):
    total_count = len(weather_data)
    storm_count = 0
    temp_sum = 0

    for weather in weather_data:
        temp_sum += weather[1]

        if weather[2] == 1:
            storm_count += 1

    average_temp = 0

    if total_count > 0:
        average_temp = temp_sum / total_count

    return total_count, storm_count, average_temp


def make_png_chunk(chunk_type, data):
    chunk = chunk_type + data
    checksum = zlib.crc32(chunk) & 0xffffffff

    return (
        struct.pack('>I', len(data))
        + chunk
        + struct.pack('>I', checksum)
    )


def save_summary_png(file_name, total_count, storm_count):
    width = 400
    height = 200
    pixels = []

    storm_bar_width = 0

    if total_count > 0:
        storm_bar_width = int((storm_count / total_count) * 300)

    for y in range(height):
        row = bytearray()
        row.append(0)

        for x in range(width):
            red = 255
            green = 255
            blue = 255

            if 50 <= x <= 350 and 80 <= y <= 120:
                red = 220
                green = 220
                blue = 220

            if 50 <= x <= 50 + storm_bar_width and 80 <= y <= 120:
                red = 120
                green = 120
                blue = 120

            row.extend([red, green, blue])

        pixels.append(bytes(row))

    raw_data = b''.join(pixels)
    compressed_data = zlib.compress(raw_data)

    png_signature = b'\x89PNG\r\n\x1a\n'
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)

    with open(file_name, 'wb') as file:
        file.write(png_signature)
        file.write(make_png_chunk(b'IHDR', ihdr_data))
        file.write(make_png_chunk(b'IDAT', compressed_data))
        file.write(make_png_chunk(b'IEND', b''))


def main():
    db_helper = MySQLHelper(DB_CONFIG)

    try:
        db_helper.connect()
        create_table(db_helper)

        weather_data = read_weather_data(CSV_FILE)

        print('CSV 데이터 확인')
        for weather in weather_data:
            print(weather)

        insert_weather_data(db_helper, weather_data)
        db_helper.commit()

        total_count, storm_count, average_temp = get_summary(weather_data)

        print('전체 데이터 수:', total_count)
        print('모래 폭풍 발생 수:', storm_count)
        print('평균 온도:', round(average_temp, 2))

        save_summary_png(PNG_FILE, total_count, storm_count)
        print('PNG 파일 저장 완료:', PNG_FILE)

    except mysql.connector.Error as error:
        db_helper.rollback()
        print('MySQL 오류 발생:', error)

    except FileNotFoundError:
        db_helper.rollback()
        print('CSV 파일을 찾을 수 없습니다:', CSV_FILE)

    except Exception as error:
        db_helper.rollback()
        print('오류 발생:', error)

    finally:
        db_helper.close()


if __name__ == '__main__':
    main()