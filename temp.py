'''
import numpy as np
import os
import cv2
import copy

# pth = r"~/dev/data/thermal/Thermal_FaceDB/Processed/val/label/"
pth = r"~/dev/data/thermal/Thermal_FaceDB/Processed/train/label/"

flist = os.listdir(pth)

src_extension = '.npy'
target_extension = '.png'

for fn in flist:
    img_extension = fn.split('.')[-1]
    if img_extension in src_extension:
        src_path = os.path.join(pth, fn)
        img = np.load(src_path).astype(np.uint8)
        target_fn = fn.replace(src_extension, target_extension)
        dst_path = os.path.join(pth, target_fn)
        print("Saving...", target_fn)
        cv2.imwrite(dst_path, img)

'''

'''
import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt

pth = r"~/dev/data/thermal/Thermal_FaceDB/Processed/train/label/"
flist = os.listdir(pth)
remap_classes = [0, 1, 2, 3, 3, 4, 4, 5]

for fn in flist:
    labelmap = cv2.imread(os.path.join(pth, fn), 0)

    max_cls_val = np.max(labelmap)
    remapped_labelmap = copy.deepcopy(labelmap)
    for cls_val in range(max_cls_val+1):
        remapped_labelmap[labelmap == cls_val] = remap_classes[cls_val]

    plt.imshow(remapped_labelmap)
    plt.show()
    break
'''

from logging import root
import matplotlib.pyplot as plt
import os
import cv2
import numpy as np

# root_pth = r"~/dev/data/ThermalFaceDB"
# root_pth = r"~/dev/data/ThermalFaceDBx256"
root_pth = r"~/dev/data/ThermalFaceDBx340"

# pth_label = os.path.join(
#     root_pth, "seg_results", "thermalFaceDBdeeplab_v3_contrast_deepbase_resnet101_dilated8_"+ "chk_cl_4gpu" + "_val", "label")
# pth_vis = os.path.join(
#     root_pth, "seg_results", "thermalFaceDBdeeplab_v3_contrast_deepbase_resnet101_dilated8_"+ "chk_cl_4gpu" + "_val" , "vis")

# pth_label = os.path.join(
#     root_pth, "seg_results", "thermalFaceDBdeeplab_v3_contrast_deepbase_resnet101_dilated8_" + "cl_no_occ" + "_val", "label")
# pth_vis = os.path.join(
#     root_pth, "seg_results", "thermalFaceDBdeeplab_v3_contrast_deepbase_resnet101_dilated8_" + "cl_no_occ" + "_val", "vis")

# pth_label = os.path.join(
#     root_pth, "seg_results", "thermalFaceDBdeeplab_v3_contrast_deepbase_resnet101_dilated8_" + "cl_occ" + "_val", "label")
# pth_vis = os.path.join(
#     root_pth, "seg_results", "thermalFaceDBdeeplab_v3_contrast_deepbase_resnet101_dilated8_" + "cl_occ" + "_val", "vis")

# pth_label = os.path.join(
#     root_pth, "seg_results", "thermalFaceDB" + "hrnet_w48_mem" + "_" + "deepbase_resnet101_dilated8_" + "cl_hrnet_mem_rmi_no_occ" + "_val", "label")
# pth_vis = os.path.join(
#     root_pth, "seg_results", "thermalFaceDB" + "hrnet_w48_mem" + "_" + "deepbase_resnet101_dilated8_" + "cl_hrnet_mem_rmi_no_occ" + "_val", "vis")

mode = 'test'  # 'val'

pth_label = os.path.join(
    root_pth, "seg_results", "thermalFaceDB" + "hrnet_w48" + "_" + "deepbase_resnet101_dilated8_" + \
    "hrnet_gcl_rmi_occ_wide_critic" + "_test_ss", "label")

if mode == 'val':
    pth_gt_label = os.path.join(root_pth, "Processed", "val", "label")
    pth_image = os.path.join(root_pth, "Processed", "val", "image")
else:
    pth_image = os.path.join(root_pth, "Processed", "test")

print("Path exists:", pth_label, os.path.exists(pth_label))

lsdir = os.listdir(pth_label)

for i in range(len(lsdir)):
    img = np.load(os.path.join(pth_image, lsdir[i].replace(".png", ".npy")))
    pred_mask = cv2.imread(os.path.join(pth_label, lsdir[i]), 0)

    fig, ax = plt.subplots(1, 2)
    if mode == 'val':
        gt_mask = cv2.imread(os.path.join(pth_gt_label, lsdir[i]), 0)

        ax[0].imshow(img, cmap='gray')
        ax[0].imshow(pred_mask, cmap='seismic', alpha=0.65)

        ax[1].imshow(img, cmap='gray')
        ax[1].imshow(gt_mask, cmap='seismic', alpha=0.65)

    else:
        ax[0].imshow(img, cmap='gray')

        ax[1].imshow(img, cmap='gray')
        ax[1].imshow(pred_mask, cmap='seismic', alpha=0.65)

    plt.show()
