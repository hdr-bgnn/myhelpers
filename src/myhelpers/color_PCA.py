import numpy as np
import torch

class Color_PCA():
    def __init__(self, loader, magnitude=0.1, minimum=0.0, maximum=1.0): #loader
        # if torch.cuda.is_available():
        #     samples = samples.cpu()
        samples = None
        for batch in loader:
            images = batch["image"]
            if torch.cuda.is_available():
                images = images.cpu()

            if samples is None:
                samples = images
            else:   
                samples=np.concatenate((images,samples), 0)

        samples = np.transpose(samples, (0, 2, 3, 1))
        samples = samples.reshape((-1, 3))
        # samples -= np.mean(samples, axis=0)
        # samples /= np.std(samples, axis=0)

        self.cov = np.cov(samples, rowvar=False)

        self.lambdas, self.p = np.linalg.eig(self.cov)

        self.minimum = minimum
        self.maximum = maximum
        self.magnitude = magnitude
    
    def perturb_color(self, img):
        alphas = np.random.normal(0, self.magnitude, 3)

        delta = np.dot(self.p, alphas*self.lambdas)
        delta = torch.from_numpy(delta).unsqueeze(0)

        # if torch.cuda.is_available():
        #     delta = delta.cuda()

        # mean = torch.mean(img, axis=0)
        # std = torch.std(img, axis=0)
        delta = delta.view(3, 1,1).expand_as(img)  
        # print('delta',delta)
        # print('img',img)
        pca_augmentation_version_img = img + delta #
        # print('pca_augmentation_version_img',pca_augmentation_version_img)
        # print('maxed',torch.clamp(pca_augmentation_version_img, self.minimum, self.maximum))
        # pca_color_image = pca_augmentation_version_img * std + mean
        # torch.maximum(torch.minimum(pca_color_image, 1), 0)
        return torch.clamp(pca_augmentation_version_img, self.minimum, self.maximum)