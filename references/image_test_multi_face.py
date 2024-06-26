
import paddle
import argparse
import cv2
import numpy as np
import os
from models.model import FaceSwap, l2_norm
from models.arcface import IRBlock, ResNet
from utils.align_face import back_matrix, dealign, align_img
from utils.util import paddle2cv, cv2paddle
from utils.prepare_data import LandmarkModel

from gfpgan import GFPGANer
from PIL import Image

from insightface.app import FaceAnalysis

import datetime

def image_test_multi_face(args, source_aligned_images, target_aligned_images):
    #paddle.set_device("gpu" if args.use_gpu else 'cpu')
    paddle.set_device("cpu" if args.use_gpu else 'cpu')
    faceswap_model = FaceSwap(args.use_gpu)

    id_net = ResNet(block=IRBlock, layers=[3, 4, 23, 3])
    id_net.set_dict(paddle.load('./checkpoints/arcface.pdparams'))

    id_net.eval()

    weight = paddle.load('./checkpoints/MobileFaceSwap_224.pdparams')

    #target_path = args.target_img_path.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')

    start_idx = args.target_img_path.rfind('/')
    if start_idx > 0:
        target_name = args.target_img_path[args.target_img_path.rfind('/'):]
    else:
        target_name = args.target_img_path
    origin_att_img = cv2.imread(args.target_img_path) # align 작업을 거치지 않은 원본 target image
    #id_emb, id_feature = get_id_emb(id_net, base_path + '_aligned.png')

    # print('source_aligned_images : ',source_aligned_images)
    # print('target_aligned_images : ',target_aligned_images)

    for idx, target_aligned_image in enumerate(target_aligned_images):
        
        id_emb, id_feature = get_id_emb_from_image(id_net, source_aligned_images[idx % len(source_aligned_images)][0])
        faceswap_model.set_model_param(id_emb, id_feature, model_weight=weight)
        faceswap_model.eval()
        # print(target_aligned_image.shape)

        # genderModel = FaceAnalysis(name='buffalo_l')
        # genderModel.prepare(ctx_id=0, det_size=(640, 640))
        # faces = genderModel.get(target_aligned_image[0])
        # # cv2.imshow('img', target_aligned_image)
        # # cv2.waitKey(0)
        # print(faces)

        att_img = cv2paddle(target_aligned_image[0])

        #import time
        #start = time.perf_counter()

        res, mask = faceswap_model(att_img)
        #print('process time :{}', time.perf_counter() - start)
        res = paddle2cv(res)
        #dest[landmarks[idx][0]:landmarks[idx][1],:] =

        back_matrix = target_aligned_images[idx % len(target_aligned_images)][1]
        mask = np.transpose(mask[0].numpy(), (1, 2, 0))
        origin_att_img = dealign(res, origin_att_img, back_matrix, mask)
        
    cv2.imwrite(os.path.join(args.output_dir, os.path.basename(target_name.format(idx))), origin_att_img)
    result_img_path = os.path.join(args.output_dir, os.path.basename(target_name.format(idx)))
    # gfpgan_gogo(result_img_path)

def get_id_emb_from_image(id_net, id_img):
    id_img = cv2.resize(id_img, (112, 112))
    id_img = cv2paddle(id_img)
    mean = paddle.to_tensor([[0.485, 0.456, 0.406]]).reshape((1, 3, 1, 1))
    std = paddle.to_tensor([[0.229, 0.224, 0.225]]).reshape((1, 3, 1, 1))
    id_img = (id_img - mean) / std
    id_emb, id_feature = id_net(id_img)
    id_emb = l2_norm(id_emb)

    return id_emb, id_feature

def faces_align(landmarkModel, image_path, image_size=224):
    aligned_imgs =[]
    if os.path.isfile(image_path):
        img_list = [image_path]
    else:
        img_list = [os.path.join(image_path, x) for x in os.listdir(image_path) if x.endswith('png') or x.endswith('jpg') or x.endswith('jpeg')]
    
    # print('img_list : ', img_list)
    for path in img_list:
        # print('img_path : ', path)
        img = cv2.imread(path)
        landmarks = landmarkModel.gets(img)
        for landmark in landmarks:
            if landmark is not None:
                aligned_img, back_matrix = align_img(img, landmark, image_size)
                aligned_imgs.append([aligned_img, back_matrix])
    return aligned_imgs

def gfpgan_gogo(img):
    img = Image.open(img)
    original_img = img.copy()
    np_img = np.array(img)

    device = 'cpu'
    model = GFPGANer(model_path='./models/GFPGANv1.4.pth', upscale=1, arch='clean', channel_multiplier=2, bg_upsampler=None, device=device)
    np_img_bgr = np_img[:, :, ::-1]
    _, _, gfpgan_output_bgr = model.enhance(np_img_bgr, has_aligned=False, only_center_face=False, paste_back=True)
    np_img = gfpgan_output_bgr[:, :, ::-1]

    restored_img = Image.fromarray(np_img)
    # restored_img.show()
    result_img = Image.blend(
        original_img, restored_img, 1
    )

    # result_img.show()
    base_path = './results/'
    result_img_np = np.array(result_img)
    result_img_rgb = result_img_np[:, :, ::-1]

    suffix = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
    fileName = suffix + '.png'

    cv2.imwrite(base_path + fileName, result_img_rgb)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="MobileFaceSwap Test")
    parser.add_argument('--source_img_path', type=str, help='path to the source image')
    parser.add_argument('--source_img_path2', type=str, help='path to the source image')
    parser.add_argument('--target_img_path', type=str, help='path to the target images')
    parser.add_argument('--output_dir', type=str, default='results', help='path to the output dirs')
    parser.add_argument('--image_size', type=int, default=224,help='size of the test images (224 SimSwap | 256 FaceShifter)')
    parser.add_argument('--merge_result', type=bool, default=True, help='output with whole image')
    parser.add_argument('--need_align', type=bool, default=True, help='need to align the image')
    parser.add_argument('--use_gpu', type=bool, default=False)


    args = parser.parse_args()
    if args.need_align:
        landmarkModel = LandmarkModel(name='landmarks')
        landmarkModel.prepare(ctx_id= 0, det_thresh=0.6, det_size=(640,640))

        face = landmarkModel.get_faces(args.target_img_path)
        print(face)

        source_aligned_images = faces_align(landmarkModel, args.source_img_path)
        target_aligned_images = faces_align(landmarkModel, args.target_img_path, args.image_size)

        # for idx, target_aligned_image in enumerate(target_aligned_images):
        #     face = landmarkModel.get_faces(target_aligned_image[0])
            

        # source_aligned_images2 = faces_align(landmarkModel, args.source_img_path2)
        # os.makedirs(args.output_dir, exist_ok=True)
        # image_test_multi_face(args, source_aligned_images, target_aligned_images)
