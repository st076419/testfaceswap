'''
Author: Naiyuan liu
Github: https://github.com/NNNNAI
Date: 2021-11-23 17:03:58
LastEditors: Naiyuan liu
LastEditTime: 2021-11-24 19:19:43
Description: 
'''

import cv2
import torch
import fractions
import numpy as np
from PIL import Image
import torch.nn.functional as F
from torchvision import transforms
from models.models import create_model
from options.all_options import get_config
from options.test_options import TestOptions
from insightface_func.face_detect_crop_single import Face_detect_crop
from util.reverse2original import reverse2wholeimage
import os
from util.norm import SpecificNorm
from parsing_model.model import BiSeNet
import requests
import os
import warnings
warnings.filterwarnings("ignore")


def lcm(a, b): return abs(a * b) / fractions.gcd(a, b) if a and b else 0


def _totensor(array):
    tensor = torch.from_numpy(array)
    img = tensor.transpose(0, 1).transpose(0, 2).contiguous()
    return img.float().div(255)


def url2cv_image(url):
    raw = requests.get(url, stream=True).raw
    image = np.asarray(bytearray(raw.read()), dtype="uint8")
    return cv2.imdecode(image, cv2.IMREAD_COLOR)


def swap_faces(pic_a_url, pic_b_url):

    # if __name__ == '__main__':
    transformer_Arcface = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    opt = get_config(pic_a_url, pic_b_url)

    if len(opt.gpu_ids) > 0:
        torch.cuda.set_device(opt.gpu_ids[0])
    else:
        torch.cuda.is_available = lambda: False

    crop_size = opt.crop_size

    torch.nn.Module.dump_patches = True
    if crop_size == 512:
        opt.which_epoch = 550000
        opt.name = '512'
        mode = 'ffhq'
    else:
        mode = 'None'
    model = create_model(opt)
    model.eval()

    spNorm = SpecificNorm()
    app = Face_detect_crop(name='antelope', root='./insightface_func/models')
    app.prepare(ctx_id=0, det_thresh=0.6, det_size=(640, 640), mode=mode)

    with torch.no_grad():
        img_b_whole = url2cv_image(opt.pic_b_url)
        img_a_whole = url2cv_image(opt.pic_a_url)

        find_faces_a_res = app.get(img_a_whole, crop_size)
        if find_faces_a_res is None:
            return None

        img_a_align_crop, _ = find_faces_a_res
        img_a_align_crop_pil = Image.fromarray(cv2.cvtColor(img_a_align_crop[0], cv2.COLOR_BGR2RGB))
        img_a = transformer_Arcface(img_a_align_crop_pil)
        img_id = img_a.view(-1, img_a.shape[0], img_a.shape[1], img_a.shape[2])

        # convert numpy to tensor
        img_id = img_id.to(torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'))

        # create latent id
        img_id_downsample = F.interpolate(img_id, size=(112, 112))
        latend_id = model.netArc(img_id_downsample)
        latend_id = F.normalize(latend_id, p=2, dim=1)

        ############## Forward Pass ######################
        find_faces_b_res = app.get(img_b_whole, crop_size)
        if find_faces_b_res is None:
            return None

        img_b_align_crop_list, b_mat_list = find_faces_b_res
        # detect_results = None
        swap_result_list = []

        b_align_crop_tenor_list = []

        for b_align_crop in img_b_align_crop_list:
            b_align_crop_tenor = _totensor(cv2.cvtColor(b_align_crop, cv2.COLOR_BGR2RGB))[None, ...].to(
                torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'))

            swap_result = model(None, b_align_crop_tenor, latend_id, None, True)[0]
            swap_result_list.append(swap_result)
            b_align_crop_tenor_list.append(b_align_crop_tenor)

        if opt.use_mask:
            n_classes = 19
            net = BiSeNet(n_classes=n_classes)
            net.to(torch.device('cuda:0' if torch.cuda.is_available() else 'cpu'))
            save_pth = os.path.join('./parsing_model/checkpoint', '79999_iter.pth')
            net.load_state_dict(torch.load(save_pth)) if torch.cuda.is_available() and len(
                opt.gpu_ids) > 0 else net.load_state_dict(torch.load(save_pth, map_location=torch.device('cpu')))
            net.eval()
        else:
            net = None

        return reverse2wholeimage(b_align_crop_tenor_list, swap_result_list, b_mat_list, crop_size, img_b_whole, \
                           opt.no_simswaplogo, pasring_model=net,
                           use_mask=opt.use_mask, norm=spNorm)


