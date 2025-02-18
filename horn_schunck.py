# -*- coding: utf-8 -*-
"""Horn-Schunck.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17-TrMmqiiQo0q_UHyNC0S0lctNX395cU
"""

import numpy as np
from natsort import natsorted, ns
from  scipy.ndimage.filters import convolve
import matplotlib.pyplot as plt
import os
import imageio
import glob

from google.colab import drive
drive.mount('/content/gdrive')

def opticalFlowDerevatives(img_1, img_2):
  mask_x = np.array([[-1, 1], [-1, 1]]) * 0.25
  mask_y = np.array([[-1, -1], [1, 1]]) * 0.25
  mask_t = -np.ones((2, 2)) * 0.25
    
  fx = convolve(img_1, mask_x) + convolve(img_2, mask_x)
  fy = convolve(img_1, mask_y) + convolve(img_2, mask_y)
  ft = convolve(img_1, mask_t) + convolve(img_2, -mask_t)

  return fx, fy, ft

def HornSchunck(img_1, img_2, smooth_param, num_iterations, plotD = False):
  mask_average = np.array([[1/12, 1/6, 1/12], [1/6, 0, 1/6], [1/12, 1/6, 1/12]], float)
  
  img_1, img_2 = img_1.astype(np.float32), img_2.astype(np.float32)
  
  U, V = np.zeros([img_1.shape[0], img_1.shape[1]]), np.zeros([img_1.shape[0], img_1.shape[1]]) # We may initilize U and V differently, hence creating initiail_U and initial_V
    
  fx, fy, ft = opticalFlowDerevatives(img_1, img_2)
  
  if plotD:
    plotDerevatives(fx, fy, ft) 
  
  for iteration in range(num_iterations):
    average_U, average_V = convolve(U, mask_average), convolve(V, mask_average)
    P = (fx * average_U) + (fy * average_V) + ft
    D = smooth_param**2 + fx**2 + fy**2
    
    U = average_U - (fx * (P/D))
    V = average_V - (fy * (P/D))
    
  return U, V
    
def plotDerevatives(fx, fy, ft):
    fg = plt.figure(figsize=(18, 5))
    ax = fg.subplots(1, 3)

    for f, a, t in zip((fx, fy, ft), ax, ('$fx$', '$fy$', '$ft$')):
        h = a.imshow(f, cmap='bwr')
        a.set_title(t)
        fg.colorbar(h, ax=a)

def plotArrows(U, V, image, path, scale=3, step=5):

    fig = plt.figure(figsize=(12, 12)).gca()
    fig.imshow(image, cmap='gray')
    
    for i in range(0, U.shape[0], step):
        for j in range(0, V.shape[1], step): # Obviosly the shape of both U and V is the same, the difference in these lines in just to enhance that j in associated with V
            fig.arrow(j, i, V[i, j]*scale, U[i, j]*scale, color='red', head_width=1, head_length=1)

    fig.set_title(path.rpartition('/')[-1])
    plt.draw()
    
        
def Runner(Path, useCase, imageList, smooth_param, num_iterations):
  for i in range(len(imageList) - 1):
    img_1 = imageio.imread(Path + useCase + imageList[i], as_gray=True)
    img_2 = imageio.imread(Path + useCase + imageList[i + 1], as_gray=True)
    
    U, V = HornSchunck(img_1, img_2, smooth_param, num_iterations, plotD = True) # Change plotD to TRUE if the derevatives plot is wanted
    pathArrows = Path + useCase + imageList[i + 1]
    plotArrows(U, V, img_2, pathArrows)
    plt.savefig('image_{:04d}.png'.format(i))

  
  return U, V

Path = '/content/gdrive/My Drive/Colab Notebooks/Horn-Schunck/Optical Flow/'
useCase = 'Aperture/'
imageList = os.listdir(Path + useCase)
imageList = natsorted(imageList, alg=ns.IGNORECASE) # Natural sorting ("Human sorting")

smooth_param, num_iterations = 10, 1000
U, V = Runner(Path, useCase, imageList, smooth_param, num_iterations)
plt.show()

anim_file = useCase[:-1] + '_smooth=' + str(smooth_param) + '_gif.gif'

with imageio.get_writer(anim_file, mode='I') as writer:
  filenames = glob.glob('image*.png')
  filenames = sorted(filenames)
  last = -1
  for i,filename in enumerate(filenames):
    frame = 2*(i**0.5)
    if round(frame) > round(last):
      last = frame
    else:
      continue
    image = imageio.imread(filename)
    writer.append_data(image)
  image = imageio.imread(filename)
  writer.append_data(image)

import IPython
if IPython.version_info > (6,2,0,''):
  display.Image(filename=anim_file)

try:
  from google.colab import files
except ImportError:
  pass
else:
  files.download(anim_file)

