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

import torch
import torch.nn as nn

class GCL_Loss(nn.Module, ABC):
    def __init__(self, configer=None):
        super(GCL_Loss, self).__init__()

        self.configer = configer

        self.lossObj_x1 = nn.SmoothL1Loss()
        self.lossObj_x2 = nn.SmoothL1Loss()
        self.lossObj_x3 = nn.SmoothL1Loss()
        self.lossObj_x4 = nn.BCEWithLogitsLoss()

    def forward(self, critic_outputs_real, critic_outputs_fake, critic_outputs_pred, with_pred_seg=False):

        real_seg_x1, real_seg_x2, real_seg_x3, real_seg_x4 = critic_outputs_real
        fake_seg_x1, fake_seg_x2, fake_seg_x3, fake_seg_x4 = critic_outputs_fake

        loss = (
            (-0.50) * self.lossObj_x1(real_seg_x1, fake_seg_x1) +
            (-0.50) * self.lossObj_x2(real_seg_x2, fake_seg_x2) +
            (-0.50) * self.lossObj_x3(real_seg_x3, fake_seg_x3)
        ) + (
            (1.00) * self.lossObj_x4(real_seg_x4, torch.ones_like(real_seg_x4)) +
            (1.00) * self.lossObj_x4(fake_seg_x4, torch.zeros_like(fake_seg_x4))
        )

        if with_pred_seg:
            pred_seg_x1, pred_seg_x2, pred_seg_x3, pred_seg_x4 = critic_outputs_pred

            loss = loss + (
                (-0.50) * self.lossObj_x1(pred_seg_x1, fake_seg_x1) +
                (-0.50) * self.lossObj_x2(pred_seg_x2, fake_seg_x2) +
                (-0.50) * self.lossObj_x3(pred_seg_x3, fake_seg_x3) +
                (1.00) * self.lossObj_x1(pred_seg_x1, real_seg_x1) +
                (1.00) * self.lossObj_x2(pred_seg_x2, real_seg_x2) +
                (1.00) * self.lossObj_x3(pred_seg_x3, real_seg_x3)
            ) + (
                (1.00) * self.lossObj_x4(pred_seg_x4, torch.ones_like(pred_seg_x4))
            )

        return loss


