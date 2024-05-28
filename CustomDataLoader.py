import glob
import random
from PIL import Image
import polars as pl
from torch.utils.data import Dataset
from torchvision import transforms
import matplotlib.pyplot as plt

class MyDatasets(Dataset):
    def __init__(self, path, train = True, transform = None):
        self.path = path
        
        if train:
            self.data_real = glob.glob(self.path + '/train/real/*.jpg')
            self.data_real = random.sample(self.data_real, 1000)
            self.data_generated = glob.glob(self.path + '/train/generated/*.*')
            self.data = self.data_real + self.data_generated
            self.class_list = ["real"] * len(self.data_real) + ["generated"] * len(self.data_generated)
        else:
            self.data = glob.glob(self.path + '/test/*.jpg')
            class_list = pl.read_csv("./datasets/test/test_labels.csv", separator = ';')
            self.class_list = class_list.select(pl.col('label')).to_numpy().flatten()
        
        self.transform = transform
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        img_path = self.data[idx]
        img = Image.open(img_path)
        label = self.class_list[idx]
        if self.transform:
            img = self.transform(img)
            
        return img, label


class DataProcesser():
    def __init__(self, size = 224):
        self.trans = transforms.Compose([transforms.Resize((size, size)),
                                    transforms.ToTensor(),
                                    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        
        self.rev_trans = transforms.Compose([transforms.Normalize((-1, -1, -1), (2, 2, 2)),
                                            transforms.ToPILImage()])
    
    def show_tensor_image(self, img): 
        if len(img.shape) == 4:
            for idx in range(img.shape[0]):
                img = img[idx, :, : ,:]
                img = self.rev_trans(img)
                plt.subplot(1, img.shape[0], idx)
                plt.imshow(img)
            
        else:
            img = self.rev_trans(img)
            plt.imshow(img)
            
        plt.show()

    def get_datasets(self, path):
        return MyDatasets(path = path, transform = self.trans)