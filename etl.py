import numpy as np
import torch
import torchvision.datasets as dset
import torchvision.transforms as transforms
from multiprocessing import Pool
from torch.autograd import Variable
from torch.utils.data import DataLoader


class ETL:
    def __init__(self, batch_size, image_size):
        # Keep params
        self.batch_size = batch_size
        self.image_size = image_size

        transform = transforms.Compose([
            transforms.RandomHorizontalFlip(),
            transforms.Scale(self.image_size),
            transforms.CenterCrop(self.image_size),
       ])
        cap = dset.ImageFolder('data/training', transform=transform)

        self.loader = iter(DataLoader(cap, self.batch_size))
        self.n_examples = len(cap)
        self.pool = Pool()

    def next_batch(self):
        images = next(self.loader)
        images = self.pool.map(self.rgb2yuv, images)
        images = torch.Tensor(images)
        y = images[:, :, :, 0].unsqueeze(-1)
        return y, images

    def rgb2yuv(self, image):
        cvt_matrix = np.array([[0.299, -0.169, 0.5],
                               [0.587, -0.331, -0.419],
                               [0.114, 0.5, -0.081]], dtype=np.float32)
        image = image.dot(cvt_matrix) + [0, 127.5, 127.5]
        return image / 127.5 - 1.

    def yuv2rgb(self, image):
        cvt_matrix = np.array([[1, 1, 1],
                               [-0.00093, -0.3437, 1.77216],
                               [1.401687, -0.71417, 0.00099]], dtype=np.float32)
        image -= [0, 127.5, 127.5]
        return image.dot(cvt_matrix).clip(min=0, max=255)