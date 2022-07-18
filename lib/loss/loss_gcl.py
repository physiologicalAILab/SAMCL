# coding=utf-8

"""
The implementation of the paper:
Region Mutual Information Loss for Semantic Segmentation.
"""

# python 2.X, 3.X compatibility
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

from abc import ABC

import torch.nn as nn
import torch.nn.functional as F
from lib.loss.loss_helper import FSAuxCELoss, FSAuxRMILoss, FSDiceLoss
from lib.loss.rmi_loss import RMILoss
from lib.utils.tools.logger import Logger as Log
from lib.loss.pytorch_ssim import SSIM

class GCL_Loss(nn.Module, ABC):
    def __init__(self, configer=None):
        super(GCL_Loss, self).__init__()

        self.configer = configer
        default_loss = False

        if self.configer.exists('gcl', 'gcl_loss'):
            if "ssim" in self.configer.get('gcl', 'gcl_loss').lower():
                self.feature_loss_fn_direction = 1.0
                self.lossObj0 = SSIM(window_size=11)
                self.lossObj1 = SSIM(window_size=9)
                self.lossObj2 = SSIM(window_size=7)
                self.lossObj3 = SSIM(window_size=5)
                self.lossObj4 = SSIM(window_size=3)
            else:
                default_loss = True
        else:
            default_loss = True
        
        if default_loss:
            self.gcl_loss_type = "L1"
            self.feature_loss_fn_direction = -1.0
            self.lossObj0 = nn.SmoothL1Loss()
            self.lossObj1 = nn.SmoothL1Loss()
            self.lossObj2 = nn.SmoothL1Loss()
            self.lossObj3 = nn.SmoothL1Loss()
            self.lossObj4 = nn.SmoothL1Loss()

    def forward(self, gcl_real_seg, gcl_fake_seg, gcl_pred_seg, with_pred_seg=False):

        real_seg_x0, real_seg_x1, real_seg_x2, real_seg_x3, real_seg_x4 = gcl_real_seg
        fake_seg_x0, fake_seg_x1, fake_seg_x2, fake_seg_x3, fake_seg_x4 = gcl_fake_seg

        loss = 0.33 * (self.feature_loss_fn_direction) * (
            0.25 * self.lossObj0(real_seg_x0, fake_seg_x0) +
            0.50 * self.lossObj1(real_seg_x1, fake_seg_x1) +
            0.50 * self.lossObj2(real_seg_x2, fake_seg_x2) +
            0.50 * self.lossObj3(real_seg_x3, fake_seg_x3) +
            1.00 * self.lossObj4(real_seg_x4, fake_seg_x4))

        if with_pred_seg:
            pred_seg_x0, pred_seg_x1, pred_seg_x2, pred_seg_x3, pred_seg_x4 = gcl_pred_seg

            loss = loss + 0.5 * (
                0.25 * self.lossObj0(pred_seg_x0, fake_seg_x0) +
                0.50 * self.lossObj1(pred_seg_x1, fake_seg_x1) +
                0.50 * self.lossObj2(pred_seg_x2, fake_seg_x2) +
                0.50 * self.lossObj3(pred_seg_x3, fake_seg_x3) +
                1.00 * self.lossObj4(pred_seg_x4, fake_seg_x4) -
                0.25 * self.lossObj0(pred_seg_x0, real_seg_x0) -
                0.50 * self.lossObj1(pred_seg_x1, real_seg_x1) -
                0.50 * self.lossObj2(pred_seg_x2, real_seg_x2) -
                0.50 * self.lossObj3(pred_seg_x3, real_seg_x3) -
                1.00 * self.lossObj4(pred_seg_x4, real_seg_x4))

        return loss


# GCL_RMI_Loss
class GCL_RMI_Loss(nn.Module, ABC):
    def __init__(self, configer=None):
        super(GCL_RMI_Loss, self).__init__()

        self.configer = configer

        self.loss_weight = self.configer.get('gcl', 'loss_weight')
        self.use_rmi = self.configer.get('gcl', 'use_rmi')

        if self.use_rmi:
            self.seg_criterion = RMILoss(configer=configer)
        else:
            self.seg_criterion = FSDiceLoss(configer=configer)

        self.gcl_criterion = GCL_Loss(configer=configer)

    def forward(self, preds, target, with_pred_seg=False):
        h, w = target.size(1), target.size(2)

        assert "pred_seg" in preds
        assert "gcl_real_seg" in preds
        assert "gcl_fake_seg" in preds
        assert "gcl_pred_seg" in preds

        pred_seg = preds['pred_seg']

        pred_seg = F.interpolate(input=pred_seg, size=(h, w), mode='bilinear', align_corners=True)
        loss = self.seg_criterion(pred_seg, target)

        if with_pred_seg:
            gcl_real_seg = preds['gcl_real_seg']
            gcl_fake_seg = preds['gcl_fake_seg']
            gcl_pred_seg = preds['gcl_pred_seg']
            loss_gcl = self.gcl_criterion(gcl_real_seg, gcl_fake_seg, gcl_pred_seg, with_pred_seg)
            return loss + self.loss_weight * loss_gcl

        else:
            return loss + 0 * loss_gcl  # just a trick to avoid errors in distributed training