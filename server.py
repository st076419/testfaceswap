import io
import os

import boto3
import cv2
from datetime import datetime
import random
import string
from flask import Flask, request, jsonify, Response
from flask_mysqldb import MySQL
from flask_cors import CORS
from botocore.config import Config

from swap_faces import swap_faces as swap_faces_by_network

application = Flask(__name__)
CORS(application)

PROFILE = "test_aws"

application.config["MYSQL_USER"] = "root"
application.config["MYSQL_PASSWORD"] = "Tanyabor_5!"
application.config["MYSQL_DB"] = "faceswap"

mysql = MySQL(application)

my_config = Config(
    region_name='us-east-1',
    signature_version='s3v4',
    s3={'addressing_style': 'virtual'}
)
s3 = boto3.client(
    's3',
    endpoint_url="https://s3.msk.3hcloud.com",
    config=my_config,
    aws_access_key_id='689e10e13f6840989a5bb246a9bff762',
    aws_secret_access_key='6972d0f0c4f141ad86b6ad4093eb4bcb'
)
storage_prefix = 'https://84a68b47b1344f5bba45d50d97c8c4b7.storage.msk.3hcloud.com/psychotest-generated-images'


@application.route("/", methods=['GET'])
def hello_world():
    # cur = mysql.connection.cursor()
    # cur.execute(f"""
    #     SELECT SwappedFacesImage, ImageWithCharacter FROM Images
    #     WHERE ImageWithFace = 'check1';
    # """)
    # swapped_image_data = cur.fetchall()
    # return str(swapped_image_data)
    return 'Welcome To Image Generator!'


def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def remove_file(path):
    os.remove(path)


def generate_image(image_with_face, image_with_character):
    # Генерируем изображение
    swapped_image_data = swap_faces_by_network(image_with_face, image_with_character)
    if swapped_image_data is None:  # Лица не найдены
        return None

    file_name = f"{generate_random_string(16)}-{datetime.now().date()}.jpg"

    _, swapped_image_buffer_array = cv2.imencode(".jpg", swapped_image_data)
    swapped_image_bytes = io.BytesIO(swapped_image_buffer_array)

    # Загружаем изображение в хранилище
    s3.upload_fileobj(swapped_image_bytes, 'psychotest-generated-images', file_name)
    return f"{storage_prefix}/{file_name}"

# curl -d '{"image_with_face": "https://citaty.info/files/characters/6390.jpg","image_with_character": "https://mf.b37mrtl.ru/russian/images/2023.06/article/6499e32e02e8bd19850e6e87.png"}' -H "Content-Type: application/json" -X POST https://face-swap.dscs.pro/api/swap_faces


# curl -d '{"image_with_face": "https://globalmsk.ru/usr/person/2-big-15033093510.jpg","image_with_character": "https://mf.b37mrtl.ru/russian/images/2023.06/article/6499e32e02e8bd19850e6e87.png"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/api/swap_faces
# { 'image_with_face': url, 'image_with_character': url, 'need_force_update': 0 (default) | 1 }
@application.route("/api/swap_faces", methods=['POST'])
def swap_faces():
    params = request.json

    # TODO: TO DELETE
    # params = {
    #     'image_with_face': 'https://globalmsk.ru/usr/person/2-big-15033093510.jpg',
    #     'image_with_character': 'https://mf.b37mrtl.ru/russian/images/2023.06/article/6499e32e02e8bd19850e6e87.png',
    # }

    # Ищем, был ли ранее такой запрос
    cur = mysql.connection.cursor()
    cur.execute(f"""
        SELECT SwappedFacesImage FROM Images
        WHERE ImageWithFace = '{params["image_with_face"]}' AND ImageWithCharacter = '{params["image_with_character"]}';
    """)
    swapped_image_data = cur.fetchall()
    print(params["image_with_face"])
    print(params["image_with_character"])

    if len(swapped_image_data) > 0:
        if "need_force_update" in params and params["need_force_update"]:
            swapped_image_url = generate_image(params["image_with_face"], params["image_with_character"])
            cur.execute(f"""
                UPDATE Images
                    SET SwappedFacesImage = {f"'{swapped_image_url}'" if swapped_image_url is not None else 'NULL'}
                    WHERE ImageWithFace = '{params["image_with_face"]}'
                        AND ImageWithCharacter = '{params["image_with_character"]}';
            """)
            mysql.connection.commit()
        else:
            swapped_image_url = swapped_image_data[0][0]
    else:
        swapped_image_url = generate_image(params["image_with_face"], params["image_with_character"])
        cur.execute(f"""
            INSERT INTO Images (ImageWithFace, ImageWithCharacter, SwappedFacesImage)
            VALUES ('{params["image_with_face"]}', '{params["image_with_character"]}', {f"'{swapped_image_url}'" if swapped_image_url is not None else 'NULL'});
         """)
        mysql.connection.commit()

    if swapped_image_url is None:
        return "Faces not recognized", 422

    return jsonify({'swapped_image_url': swapped_image_url})


if __name__ == '__main__':
    application.run(debug=True)
