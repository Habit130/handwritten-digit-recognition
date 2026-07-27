from collections import OrderedDict

import torch
from torch import Tensor, nn
from torch.nn import functional as F


class DigitCNN(nn.Module):
    """The one canonical CNN used by training, inference, and visualization."""

    def __init__(self) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(1, 8, kernel_size=5)
        self.conv2 = nn.Conv2d(8, 16, kernel_size=5)
        self.fc1 = nn.Linear(16 * 4 * 4, 64)
        self.fc2 = nn.Linear(64, 10)

    def forward(self, inputs: Tensor) -> Tensor:
        logits, _ = self.forward_with_activations(inputs)
        return logits

    def forward_with_activations(
        self, inputs: Tensor
    ) -> tuple[Tensor, OrderedDict[str, Tensor]]:
        activations: OrderedDict[str, Tensor] = OrderedDict()

        # layer:input
        activations["input"] = inputs
        # layer:conv1
        conv1 = self.conv1(inputs)
        activations["conv1"] = conv1
        # layer:relu1
        relu1 = F.relu(conv1)
        activations["relu1"] = relu1
        # layer:pool1
        pool1 = F.max_pool2d(relu1, 2)
        activations["pool1"] = pool1
        # layer:conv2
        conv2 = self.conv2(pool1)
        activations["conv2"] = conv2
        # layer:relu2
        relu2 = F.relu(conv2)
        activations["relu2"] = relu2
        # layer:pool2
        pool2 = F.max_pool2d(relu2, 2)
        activations["pool2"] = pool2
        # layer:flatten
        flattened = torch.flatten(pool2, 1)
        activations["flatten"] = flattened
        # layer:fc1
        fc1 = self.fc1(flattened)
        activations["fc1"] = fc1
        # layer:relu3
        relu3 = F.relu(fc1)
        activations["relu3"] = relu3
        # layer:logits
        logits = self.fc2(relu3)
        activations["logits"] = logits
        # layer:probabilities
        activations["probabilities"] = F.softmax(logits, dim=1)
        return logits, activations
