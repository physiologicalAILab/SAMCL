import torch
import torch.nn as nn
import numpy as np
import torch.nn.utils.spectral_norm as spectral_norm

relu_slope = 0.01  # Default value 0.01
norm_layer = nn.BatchNorm2d

class DownConv(nn.Module):
    def __init__(self, in_channels, out_channels, apply_spectral_norm=True):
        super(DownConv, self).__init__()
        n_ch1 = in_channels
        n_ch2 = in_channels # in_channels // 2
        n_ch3 = out_channels #out_channels // 3

        if apply_spectral_norm:
            self.conv = nn.Sequential(
                spectral_norm(nn.Conv2d(n_ch1, n_ch2, kernel_size=3, stride=1, padding=1, padding_mode='reflect', bias=False)),
                norm_layer(n_ch2),
                nn.LeakyReLU(negative_slope=relu_slope),
                spectral_norm(nn.Conv2d(n_ch2, n_ch3, kernel_size=3, stride=2, padding=1, padding_mode='reflect', bias=False)),
                norm_layer(n_ch3),
                nn.LeakyReLU(negative_slope=relu_slope),
            )
        else:
            self.conv = nn.Sequential(
                nn.Conv2d(n_ch1, n_ch2, kernel_size=3, stride=1, padding=1, padding_mode='reflect', bias=False),
                norm_layer(n_ch2),
                nn.LeakyReLU(negative_slope=relu_slope),
                nn.Conv2d(n_ch2, n_ch3, kernel_size=3, stride=2, padding=1, padding_mode='reflect', bias=False),
                norm_layer(n_ch3),
                nn.LeakyReLU(negative_slope=relu_slope),
            )

    def forward(self, x):
        x = self.conv(x)
        return x


class ConvFinal(nn.Module):
    def __init__(self, n_ch1, n_ch2, apply_spectral_norm=True):
        super(ConvFinal, self).__init__()

        if apply_spectral_norm:
            self.conv_final = nn.Sequential(
                spectral_norm(nn.Conv2d(n_ch1, n_ch2, kernel_size=1, stride=1, padding=1, padding_mode='reflect', bias=False)),
                norm_layer(n_ch2),
                nn.LeakyReLU(negative_slope=relu_slope),
            )
        else:
            self.conv_final = nn.Sequential(
                nn.Conv2d(n_ch1, n_ch2, kernel_size=1, stride=1, padding=1, padding_mode='reflect', bias=False),
                norm_layer(n_ch2),
                nn.LeakyReLU(relu_slope),
            )

    def forward(self, x):
        x = self.conv_final(x)
        return x


class GCL_Companion(nn.Module):
    def __init__(self, configer):
        super(GCL_Companion, self).__init__()
        self.configer = configer
        self.num_classes = self.configer.get('data', 'num_classes')

        self.bn_type = self.configer.get('network', 'bn_type')
        self.apply_spectral_norm = bool(self.configer.get('gcl', 'apply_spectral_norm'))
        self.n_channels = int(self.configer.get('data', 'num_channels'))
        self.batch_size = int(self.configer.get('train', 'batch_size'))

        self.nf = self.num_classes * self.n_channels
        self.n_filters = np.array([1*self.nf, 2*self.nf, 4*self.nf, 8*self.nf, self.num_classes])
        self.conv_down_1 = DownConv(self.n_filters[0] , self.n_filters[1], apply_spectral_norm=self.apply_spectral_norm, bn_type=self.bn_type)
        self.conv_down_2 = DownConv(self.n_filters[1], self.n_filters[2], apply_spectral_norm=self.apply_spectral_norm, bn_type=self.bn_type)
        self.conv_down_3 = DownConv(self.n_filters[2], self.n_filters[3], apply_spectral_norm=self.apply_spectral_norm, bn_type=self.bn_type)
        self.conv_final = ConvFinal(self.n_filters[3], self.n_filters[4], apply_spectral_norm=self.apply_spectral_norm, bn_type=self.bn_type)

    def forward(self, input_img, seg_map):

        if self.n_channels == 1:
            x0 = input_img * seg_map

        else:
            x0_0 = input_img[:, 0, :, :] * seg_map
            x0_1 = input_img[:, 1, :, :] * seg_map
            x0_2 = input_img[:, 2, :, :] * seg_map
            x0 = torch.cat([x0_0, x0_1, x0_2], dim=1)

        x1 = self.conv_down_1(x0)
        x2 = self.conv_down_2(x1)
        x3 = self.conv_down_3(x2)
        x4 = self.conv_final(x3)
        return [x0, x1, x2, x3, x4]