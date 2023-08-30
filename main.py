import cv2
import io

from swap_faces import swap_faces
import boto3
from botocore.config import Config
from PIL import Image

# curl -d "param1=value1&param2=value2" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://localhost:3000/data
if __name__ == '__main__':
    # swapped_image_data = swap_faces(
    #     'https://globalmsk.ru/usr/person/2-big-15033093510.jpg',
    #     'https://mf.b37mrtl.ru/russian/images/2023.06/article/6499e32e02e8bd19850e6e87.png'
    # )
    # cv2.imshow('image', swapped_image_data)
    # cv2.waitKey(0)  # waits until a key is pressed cv2.destroyAllWindows()
    # cv2.destroyAllWindows()
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
    print(s3.list_buckets())

# torch~=1.13.1 +
# Pillow~=9.5.0 (9.4.0)
# torchvision~=0.14.1 +
# numpy~=1.21.6 +
# scipy~=1.10.1 (1.7.3)
# matplotlib~=3.7.1 (3.5.3)
# opencv-python~=4.1.2.30
# boto3~=1.26.163
# Flask~=2.3.2
# requests~=2.31.0
# botocore~=1.29.163
# scikit-image~=0.21.0
# insightface~=0.2.1