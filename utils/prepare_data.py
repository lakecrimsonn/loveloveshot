import os
import cv2
import numpy as np
import glob
import os.path as osp
from insightface.model_zoo import model_zoo
from .face_analysis import Face


class LandmarkModel():
    def __init__(self, name, root='./checkpoints'):
        self.models = {}
        root = os.path.expanduser(root)
        onnx_files = glob.glob(osp.join(root, name, '*.onnx'))
        onnx_files = sorted(onnx_files)
        for onnx_file in onnx_files:
            if onnx_file.find('_selfgen_')>0:
                continue
            model = model_zoo.get_model(onnx_file)
            # print(model)
            if model.taskname not in self.models:
                # print('find model:', onnx_file, model.taskname)
                self.models[model.taskname] = model
            else:
                # print('duplicated model task type, ignore:', onnx_file, model.taskname)
                del model
        assert 'detection' in self.models
        self.det_model = self.models['detection']

    def prepare(self, ctx_id, det_thresh=0.2, det_size=(640, 640), mode ='None'): #det_thresh=0.5
        self.det_thresh = det_thresh
        self.mode = mode
        assert det_size is not None
        # print('set det-size:', det_size)
        self.det_size = det_size
        for taskname, model in self.models.items():
            # print('taskname & model :', taskname, model)
            if taskname=='detection':
                model.prepare(ctx_id, input_size=det_size)
            else:
                model.prepare(ctx_id)


    def get_faces(self, img, max_num=0):
        # img = cv2.imread(img)
        bboxes, kpss = self.det_model.detect(img,
                                             max_num=max_num,
                                             metric='default')
        if bboxes.shape[0] == 0:
            return []
        ret = []
        for i in range(bboxes.shape[0]):
            bbox = bboxes[i, 0:4]
            det_score = bboxes[i, 4]
            kps = None
            if kpss is not None:
                kps = kpss[i]
            face = Face(bbox=bbox, kps=kps, det_score=det_score)
            for taskname, model in self.models.items():
                if taskname=='detection':
                    continue
                model.get(img, face)
            ret.append(face)
        return ret
    
    def get_faces_male(self, img, max_num=0):
        img = cv2.imread(img)
        bboxes, kpss = self.det_model.detect(img,
                                             max_num=max_num,
                                             metric='default')
        if bboxes.shape[0] == 0:
            return []
        ret = []
        for i in range(bboxes.shape[0]):
            bbox = bboxes[i, 0:4]
            det_score = bboxes[i, 4]
            kps = None
            if kpss is not None:
                kps = kpss[i]
            face = Face(bbox=bbox, kps=kps, det_score=det_score)
            for taskname, model in self.models.items():
                if taskname=='detection':
                    continue
                # print(taskname)
                model.get(img, face)
            ret.append(face)
        return ret

    # # video_test에만 사용
    # def get(self, img, max_num=0):
    #     # bboxes, kpss = self.det_model.detect(img, threshold=self.det_thresh, max_num=max_num, metric='default')
    #     bboxes, kpss = self.det_model.detect(img, max_num=max_num, metric='default')
    #     if bboxes.shape[0] == 0:
    #         return None
    #     det_score = bboxes[..., 4]

    #     # select the face with the hightest detection score
    #     best_index = np.argmax(det_score)

    #     kps = None
    #     if kpss is not None:
    #         kps = kpss[best_index]
    #     return kps

    def gets(self, img, max_num=0):
        gender_img = self.get_faces(img)
        for gender in gender_img:
            # print(gender['gender'])
            if gender['gender'] == 0:
                bboxes, kpss = self.det_model.detect(img, max_num=max_num, metric='default')
                # print(kpss)
                return kpss

    # def gets(self, img, max_num=0):
    #     bboxes, kpss = self.det_model.detect(img, threshold=self.det_thresh, max_num=max_num, metric='default')
    #     return kpss