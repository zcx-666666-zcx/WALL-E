"""
DACAN — DACA Channel Attention Network
Face anti-spoofing model architecture (single-modality, type D).

Extracted from RGB2 project. Only the inference path is kept;
training-specific code (FusionNet, Sep_CAM_ResNeXt variants) is omitted.
"""

from collections import OrderedDict
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
BatchNorm2d = nn.BatchNorm2d


class DACA_ChannelAttention(nn.Module):
    """Dual-pooling channel attention with adaptive kernel size."""

    def __init__(self, channels, gamma=2, b=1):
        super().__init__()
        self.channels = channels
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        k_size = int(abs((math.log(self.channels, 2) + b) / gamma))
        k_size = k_size if k_size % 2 else k_size + 1
        self.conv = nn.Conv1d(1, 1, kernel_size=k_size, padding=(k_size - 1) // 2, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg_out = self.avg_pool(x)
        max_out = self.max_pool(x)
        avg_out = self.conv(avg_out.squeeze(-1).transpose(-1, -2))
        avg_out = avg_out.transpose(-1, -2).unsqueeze(-1)
        max_out = self.conv(max_out.squeeze(-1).transpose(-1, -2))
        max_out = max_out.transpose(-1, -2).unsqueeze(-1)
        attention = self.sigmoid(avg_out + max_out)
        return x * attention.expand_as(x)


class DACA_Resblock(nn.Module):
    expansion = 4

    def __init__(self, inplanes, planes, groups, reduction, stride=1,
                 downsample=None, base_width=4, k_size=3):
        super().__init__()
        width = int(math.floor(planes * (base_width / 64)) * groups)

        self.conv1 = nn.Conv2d(inplanes, width, kernel_size=1, stride=1, bias=False)
        self.bn1 = nn.BatchNorm2d(width)
        self.conv2 = nn.Conv2d(width, width, kernel_size=3, stride=stride, padding=1, groups=groups, bias=False)
        self.bn2 = nn.BatchNorm2d(width)
        self.conv3 = nn.Conv2d(width, planes * 4, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * 4)
        self.relu = nn.ReLU(inplace=True)
        self.eca = DACA_ChannelAttention(planes * 4)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        residual = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)
        out = self.conv3(out)
        out = self.bn3(out)
        out = self.eca(out)
        if self.downsample is not None:
            residual = self.downsample(x)
        out += residual
        out = self.relu(out)
        return out


class DACANet(nn.Module):

    def __init__(self, block, layers, groups, reduction, dropout_p=0.2,
                 inplanes=128, input_3x3=True, downsample_kernel_size=3,
                 downsample_padding=1, num_classes=1000):
        super().__init__()
        self.inplanes = inplanes
        if input_3x3:
            layer0_modules = [
                ('conv1', nn.Conv2d(3, 64, 3, stride=2, padding=1, bias=False)),
                ('bn1', nn.BatchNorm2d(64)),
                ('relu1', nn.ReLU(inplace=True)),
                ('conv2', nn.Conv2d(64, 64, 3, stride=1, padding=1, bias=False)),
                ('bn2', nn.BatchNorm2d(64)),
                ('relu2', nn.ReLU(inplace=True)),
                ('conv3', nn.Conv2d(64, inplanes, 3, stride=1, padding=1, bias=False)),
                ('bn3', nn.BatchNorm2d(inplanes)),
                ('relu3', nn.ReLU(inplace=True)),
            ]
        else:
            layer0_modules = [
                ('conv1', nn.Conv2d(3, inplanes, kernel_size=7, stride=2, padding=3, bias=False)),
                ('bn1', nn.BatchNorm2d(inplanes)),
                ('relu1', nn.ReLU(inplace=True)),
            ]
        layer0_modules.append(('pool', nn.MaxPool2d(3, stride=2, ceil_mode=True)))
        self.layer0 = nn.Sequential(OrderedDict(layer0_modules))

        self.layer1 = self._make_layer(block, planes=64, blocks=layers[0],
                                       groups=groups, reduction=reduction,
                                       downsample_kernel_size=1, downsample_padding=0)
        self.layer2 = self._make_layer(block, planes=128, blocks=layers[1], stride=2,
                                       groups=groups, reduction=reduction,
                                       downsample_kernel_size=downsample_kernel_size,
                                       downsample_padding=downsample_padding)
        self.layer3 = self._make_layer(block, planes=256, blocks=layers[2], stride=2,
                                       groups=groups, reduction=reduction,
                                       downsample_kernel_size=downsample_kernel_size,
                                       downsample_padding=downsample_padding)
        self.layer4 = self._make_layer(block, planes=512, blocks=layers[3], stride=2,
                                       groups=groups, reduction=reduction,
                                       downsample_kernel_size=downsample_kernel_size,
                                       downsample_padding=downsample_padding)

        self.avg_pool = nn.AvgPool2d(7, stride=1)
        self.dropout = nn.Dropout(dropout_p) if dropout_p is not None else None
        self.last_linear = nn.Linear(512 * block.expansion, num_classes)

    def _make_layer(self, block, planes, blocks, groups, reduction, stride=1,
                    downsample_kernel_size=1, downsample_padding=0):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion,
                          kernel_size=downsample_kernel_size, stride=stride,
                          padding=downsample_padding, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )
        layers = [block(self.inplanes, planes, groups, reduction, stride, downsample)]
        self.inplanes = planes * block.expansion
        for _ in range(1, blocks):
            layers.append(block(self.inplanes, planes, groups, reduction))
        return nn.Sequential(*layers)

    def features(self, x):
        x = self.layer0(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        return x

    def logits(self, x):
        x = self.avg_pool(x)
        if self.dropout is not None:
            x = self.dropout(x)
        x = x.view(x.size(0), -1)
        x = self.last_linear(x)
        return x

    def forward(self, x):
        x = self.features(x)
        x = self.logits(x)
        return x


def DACAN_D(num_classes=2):
    return DACANet(DACA_Resblock, [3, 4, 4, 3], groups=32, reduction=16,
                   dropout_p=0., inplanes=64, input_3x3=True,
                   downsample_kernel_size=1, downsample_padding=0,
                   num_classes=num_classes)


class Net(nn.Module):
    """Wrapper around DACANet for face anti-spoofing inference."""

    def __init__(self, num_class=2, is_first_bn=False, type="D"):
        super().__init__()
        self.is_first_bn = is_first_bn
        if self.is_first_bn:
            self.first_bn = nn.BatchNorm2d(3)

        if type == 'D':
            self.encoder = DACAN_D()
        else:
            self.encoder = torchvision.models.resnet18(pretrained=False)

        self.conv1 = self.encoder.layer0
        self.conv2 = self.encoder.layer1
        self.conv3 = self.encoder.layer2
        self.conv4 = self.encoder.layer3
        self.conv5 = self.encoder.layer4
        self.fc = nn.Sequential(nn.Linear(2048, num_class))

    def forward(self, x):
        batch_size, C, H, W = x.shape
        if self.is_first_bn:
            x = self.first_bn(x)
        else:
            mean = [0.485, 0.456, 0.406]
            std = [0.229, 0.224, 0.225]
            x = torch.cat([
                (x[:, [0]] - mean[0]) / std[0],
                (x[:, [1]] - mean[1]) / std[1],
                (x[:, [2]] - mean[2]) / std[2],
            ], 1)

        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.conv5(x)
        fea = F.adaptive_avg_pool2d(x, output_size=1).view(batch_size, -1)
        fea = F.dropout(fea, p=0.50, training=self.training)
        logit = self.fc(fea)
        return logit
