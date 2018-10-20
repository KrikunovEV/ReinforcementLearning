import torch
import numpy as np

class Flatten(torch.nn.Module):
    def forward(self, input):
        return input.view(input.size(0), -1)

class ActorCriticModel(torch.nn.Module):

    def __init__(self, scope):
        super(ActorCriticModel, self).__init__()

        self.scope = scope

        self.ActorCritic = torch.nn.Sequential(
            torch.nn.Conv2d(1, 16, 8, stride=4),
            torch.nn.ELU(),
            torch.nn.Conv2d(16, 32, 4, stride=2),
            torch.nn.ELU(),
            torch.nn.Conv2d(32, 32, 3, stride=1),
            torch.nn.ELU(),
            Flatten(),
            torch.nn.Linear(9 * 6 * 32, 256),
            torch.nn.ELU()
        ).cuda()

        self.Policy = torch.nn.Sequential(
            torch.nn.Linear(256, 6, bias=False),
            torch.nn.Softmax()
        ).cuda()
        constants = np.random.randn(self.Policy.weight.shape)
        constants *= 0.01 / np.sqrt(np.square(constants).sum(axis=0, keepdims=True))
        torch.nn.init.constant_(self.Policy.weight, constants)

        self.Value = torch.nn.Sequential(
            torch.nn.Linear(256, 1, bias=False)
        ).cuda()
        constants = np.random.randn(self.Policy.weight.shape)
        constants *= 1 / np.sqrt(np.square(constants).sum(axis=0, keepdims=True))
        torch.nn.init.constant_(self.Policy.weight, constants)


    def forward(self, input):
        return input


    def noGradForward(self, input):
        with torch.no_grad():
            pass
        return input