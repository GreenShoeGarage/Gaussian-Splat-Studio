from PIL import Image
import numpy as np
from plyfile import PlyData, PlyElement


class GaussianCloud:

    def __init__(self, data):
        self.data=data

    def write(self,path):

        PlyData(
            [PlyElement.describe(self.data,"vertex")]
        ).write(path)


def initialize_gaussians(path):

    img=np.array(
        Image.open(path).convert("RGB")
    )

    h,w,_=img.shape

    yy,xx=np.mgrid[:h,:w]

    n=h*w

    data=np.zeros(
        n,
        dtype=[
        ("x","f4"),
        ("y","f4"),
        ("z","f4"),
        ("red","u1"),
        ("green","u1"),
        ("blue","u1"),
        ("opacity","f4"),
        ("scale_0","f4"),
        ("scale_1","f4"),
        ("scale_2","f4")
        ])

    data["x"]=xx.flatten()/w
    data["y"]=yy.flatten()/h
    data["z"]=1

    colors=img.reshape(-1,3)

    data["red"]=colors[:,0]
    data["green"]=colors[:,1]
    data["blue"]=colors[:,2]

    data["opacity"]=1
    data["scale_0"]=0.01
    data["scale_1"]=0.01
    data["scale_2"]=0.01

    return GaussianCloud(data)