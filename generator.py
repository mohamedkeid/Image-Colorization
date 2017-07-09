import torch
import torch.nn as nn
import torch.nn.init as init


class Generator(nn.Module):
    """
    Generative model that learns to colorize an image. It receives a 
    sing-channel "black-and-white" image and outputs a three-channel
    colored image encoded in HSV.
    """

    def __init__(self):
        super(Generator, self).__init__()

        # Conv blocks
        self.conv1 = nn.Conv2d(3, 128, 7, padding=3)
        init.normal(self.conv1.weight, 0., .02)
        self.norm1 = nn.BatchNorm2d(128, momentum=.9)

        self.conv2 = nn.Conv2d(129, 64, 5, padding=2)
        init.normal(self.conv2.weight, 0., .02)
        self.norm2 = nn.BatchNorm2d(64, momentum=.9)

        self.conv3 = nn.Conv2d(65, 64, 5, padding=2)
        init.normal(self.conv3.weight, 0., .02)
        self.norm3 = nn.BatchNorm2d(64, momentum=.9)

        self.conv4 = nn.Conv2d(65, 64, 5, padding=2)
        init.normal(self.conv4.weight, 0., .02)
        self.norm4 = nn.BatchNorm2d(64, momentum=.9)

        self.conv5 = nn.Conv2d(65, 32, 5, padding=2)
        init.normal(self.conv5.weight, 0., .02)
        self.norm5 = nn.BatchNorm2d(32, momentum=.9)

        self.relu = nn.ReLU()

        # Out
        self.conv6 = nn.Conv2d(33, 2, 5, padding=2)
        init.normal(self.conv6.weight, 0., .02)
        self.tanh = nn.Tanh()

    def forward(self, noise, v):
        """
        Given a single-channel "black-and-white" image encoding, runs through all conv
        blocks and outputs a three-channel tensor representing a colorized image in HSV.
        
        Args:
            noise (Tensor)  :   Uniform noise appended to make function non-deterministic.
            v (Tensor)      :   Value channel of image encoding.
        Returns:
            Tensor          :   Three-channel encoding representing image in HSV.
        """

        x = torch.cat([v, noise], 1)

        for i in range(1, 7):
            x = self.conv_block(x, v, i, (i == 6))

        x = self.tanh(x)
        return torch.cat([x, v], 1)

    def conv_block(self, x, v, block, last=False):
        """
        Multi-operation layer comprised of convolution, normalization (except for
        last layer), and activation (relu except for last which is tanh).
        
        Args:
            x (Tensor)  :   Encoding to apply conv -> normalization (possibly) -> activation on.
            v (Tensor)  :   Value channel of image to concatenate onto encoding.
            block (int) :   Block number corresponding to the layer.
            last (bool) :   Whether or not this is the final layer (for normalization).
        Returns:
            Tensor      :   Layer output that has been conved, possibly normalized, and activated.
        """

        x = torch.cat([x, v], 1)
        conv = getattr(self, "conv{}".format(block))
        x = conv(x)

        if not last:
            norm = getattr(self, "norm{}".format(block))
            return self.relu(norm(x))
        else:
            return self.tanh(x)
