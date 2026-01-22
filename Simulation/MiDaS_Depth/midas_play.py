'''
Testing MiDaS pretrained model on sample images: Given an image, which part looks closer to a human observer?-- doesnot measure the actualk distance, it is like guessing pixels are closer or far relatively
'''

import sys
print("PYTHON EXECUTABLE:", sys.executable)
import os
import torch
import cv2
import numpy as np
import matplotlib.pyplot as plt

input_folder="."
output_folder="sampleDEPTH/"
os.makedirs(output_folder, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

midas = torch.hub.load("intel-isl/MiDas","MiDaS_small") #pythorch goes to guithub and downloads the MiDaS model--pretrained NN
'''
MiDaS -- {convolution layers + Feature extraction + encoder-decoder network}
This model was trained on millions of images with depth cues, so it can predict relative depth from a single image.
'''
midas.to(device) #moves the model to GPU if available
midas.eval() #sets the model to evaluation mode (not training mode) --no randomness, no dropout

transforms = torch.hub.load("intel-isl/MiDas","transforms") #download the transformation functions for MiDaS - this will resize, normalize, and convert the image to tensor
transform = transforms.small_transform #select the transformation for MiDaS_small model -- this smalltransform resizes to 256x256

for i in range(1,3):
    img_file = f"test{i}.jpg"
    img_path = os.path.join(input_folder, img_file)
    img_path = os.path.abspath(os.path.join(".", img_file))  # full absolute path
    if not os.path.exists(img_path):
        print(f"Image {img_path} not found, skipping.")
        continue

    img = cv2.imread(img_path) #reads the image using OpenCV -- in BGR format
    if img is None:
        print(f"Cannot read image: {img_file}")
        continue
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #convert BGR to RGB since OpenCV uses BGR by default and MiDaS expects RGB
    input_batch = transform(img_rgb).to(device) #resize the mage, scale pixel values, convert to tensor, and move to GPU if available - shape [1, 3, H, W] meaning batch size 1, 3 color channels, height, width

    with torch.no_grad(): #this is where inferencing is happening -- no gradients are computed, saving memory and computation
        depth = midas(input_batch) #forward pass through the model to get depth prediction - shape [1, 1, H', W'] where H' and W' are the output dimensions
        ''' looks at the edges, perspective, texture size, object shapes, combines all this and produces a depth map -- relative depth -- closer parts are lighter, farther parts are darker
        NOTE: these scores that we get per pixel are not in meters, they are relative depth scores -- useful for understanding scene geometry but not for measuring actual distances
        '''

    depth = torch.nn.functional.interpolate(
        depth.unsqueeze(1),
        size=img_rgb.shape[:2],
        mode="bicubic",
        align_corners=False,
    ).squeeze() #depth.unsqueeze(1) adds a channel dimension to depth to make it [1, 1, H', W'], then we resize it to the original image size using bicubic interpolation, and finally squeeze() removes the extra dimensions to get [H, W]
    #bicubic interpolation is a method of resizing images that considers the closest 16 pixels to estimate a new pixel value, resulting in smoother images compared to nearest-neighbor or bilinear interpolation.

    depth = depth.cpu().numpy() #convert the depth tensor to a numpy array on the CPU for further processing
    print(f"Full depth is {depth}") #lareg num -- very close. small num -- far
    print(f"Depth stats - min: {np.min(depth)}, max: {np.max(depth)}, mean: {np.mean(depth)}")

    depth_vis = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    print(f"after norm depth matrix is {depth_vis}")
    print(f"Visual depth stats - min: {np.min(depth_vis)}, max: {np.max(depth_vis)}, mean: {np.mean(depth_vis)}")
    plt.figure(figsize=(12,5))

    plt.subplot(1,2,1)
    plt.title("RGB Image")
    plt.imshow(img_rgb)
    plt.axis("off")

    plt.subplot(1,2,2)
    plt.title("MiDas Depth (Near = Bright, Far = Dark)")
    plt.imshow(depth_vis, cmap="gray")
    plt.axis("off")
    plt.show()

    depth_out_path = os.path.join(output_folder, f"{os.path.splitext(img_file)[0]}_depth.png")
    cv2.imwrite(depth_out_path, depth_vis)
    print(f"Depth map saved to {depth_out_path}") #we use change in depth values to infer relative distances-- obstacle -- sudden change in the gradient of depth; floor -- smooth depth changes
    #obstacke detection can be modeled from how this depth values change -- not how bright each pixel is!
print("Processing complete.")