import boto3
import cv2
import numpy as np
import io
from botocore.client import Config
from threading import Thread
import time
import requests

from swap_faces import swap_faces

# aws --profile test_aws s3 ls
# aws --profile test_aws s3 ls --endpoint-url https://s3.msk.3hcloud.com

def make_request(target_image, index):
    print(f'start {index}')
    url = 'https://face-swap.dscs.pro/api/swap_faces'
    # url = 'https://d4dd-82-179-36-204.ngrok-free.app/api/swap_faces'
    myobj = {
        "image_with_face": "https://xn----7sbbaazuatxpyidedi7gqh.xn--p1ai/i/personalii/Eltsin/1.jpg",
        "image_with_character": target_image,
    }

    start_time = time.time()
    res = requests.post(url, json=myobj, verify=False)
    print(f"{index}: {time.time() - start_time:.2f}s. {res.json()}")
#

if __name__ == '__main__':
    # s3 = boto3.client('s3', endpoint_url="https://s3.msk.3hcloud.com")
    # response = s3.get_object(
    #     Bucket='myfirst',
    #     Key='14c404.jpg',
    # )

    # Output the bucket names
    # url = 'https://static8.depositphotos.com/1192060/916/i/600/depositphotos_9164210-stock-photo-two-colleagues-smiling-at-camera.jpg'
    # file_name = 'kek.jpg'
    # raw = requests.get(url, stream=True).raw
    # image = np.asarray(bytearray(raw.read()), dtype="uint8")
    # swapped_image_data = cv2.imdecode(image, cv2.IMREAD_COLOR)
    #
    # _, swapped_image_buffer_array = cv2.imencode(".jpg", swapped_image_data)
    # # swapped_image_bytes = swapped_image_buffer_array.tobytes()
    #
    # swapped_image_bytes = io.BytesIO(swapped_image_buffer_array)
    #
    # print(file_name)
    # s3.upload_fileobj(swapped_image_bytes, 'myfirst', file_name)
    second_images = [
        'https://cdn-media.tass.ru/width/1020_b9261fa1/tass/m2/uploads/i/20180621/4726066.jpg',
        'https://84a68b47b1344f5bba45d50d97c8c4b7.storage.msk.3hcloud.com/psychotest-static-images/%D0%90%D0%BB%D0%B0%D1%8F%20%D0%B2%D0%B5%D0%B4%D1%8C%D0%BC%D0%B0539.png',
        'https://84a68b47b1344f5bba45d50d97c8c4b7.storage.msk.3hcloud.com/psychotest-static-images/%D0%92%D0%B8%D1%82%D0%BE%D0%9A%D0%BE%D1%80%D0%BB%D0%B5%D0%BE%D0%BD%D0%B5856.png',
        'https://www.film.ru/sites/default/files/people/1457526-2185715.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/George-W-Bush.jpeg/800px-George-W-Bush.jpeg',
        'https://cdn.iz.ru/sites/default/files/news-2020-11/TASS_21211995.jpg',
        'https://globalmsk.ru/usr/person/big-person-15629946451.jpg',
        'https://www.krugosvet.ru/sites/krugosvet.ru/files/img08/1008610_8610_101.jpg',
        'https://interaffairs.ru/i/2022/05/ca4a8873993818606a95ba2a8ec28bc8.jpeg',
        'https://s0.rbk.ru/v6_top_pics/media/img/7/11/755436414282117.jpeg'
    ]

    threads = [Thread(target=make_request, args=(second_images[i], i)) for i in range(len(second_images))]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    # url = 'https://face-swap.dscs.pro/api/swap_faces'
    # # url = 'https://d4dd-82-179-36-204.ngrok-free.app/api/swap_faces'
    # myobj = {
    #     "image_with_face": "https://xn----7sbbaazuatxpyidedi7gqh.xn--p1ai/i/personalii/Eltsin/1.jpg",
    #     "image_with_character": "https://cdn-media.tass.ru/width/1020_b9261fa1/tass/m2/uploads/i/20180621/4726066.jpg",
    # }
    #
    # res = requests.post(url, json=myobj, verify=False)
    # # res = requests.get('https://face-swap.dscs.pro', verify=False)
    # print(res.status_code)
    # print(res.text)
    # print(res.json())

    # swap_faces(
    #     'https://static8.depositphotos.com/1192060/916/i/600/depositphotos_9164210-stock-photo-two-colleagues-smiling-at-camera.jpg',
    #     # 'https://www.imgonline.com.ua/examples/bee-on-daisy.jpg',
    #     'https://n1s1.elle.ru/b0/c8/1f/b0c81f4f4355103bdda4a27787aaf4a8/728x711_1_96cb6f11570473b0be90042dd6c1bee7@940x918_0xc0a839a4_338479401491300945.jpeg',
    #     './images/temp/',
    #     'kek.jpg'
    # )
