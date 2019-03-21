from pysc2.lib import actions as sc2_actions
import numpy as np
from visdom import Visdom

FUNCTION_TYPES = sc2_actions.FUNCTION_TYPES
FunctionCount = len(FUNCTION_TYPES)

FUNCTIONS = sc2_actions.FUNCTIONS

Hyperparam = {
    "Episodes": 100000,
    "Steps": 40,
    "Discount": 0.99,
    "Entropy": 0.001,
    "GameSteps": 8, # 180 APM
    "LR": 0.0001,
    "FeatureSize": 64
}

screen_ind = [1, 5, 8, 9, 14, 15]
minimap_ind = [1, 4, 5]
FeatureScrCount = len(screen_ind)
FeatureMinimapCount = len(minimap_ind)

class VisdomWrap():

    def __init__(self):
        self.vis = Visdom()

        self.reward_layout = dict(title="Episode rewards", xaxis={'title': 'episode'}, yaxis={'title': 'reward'})
        self.policy_layout = dict(title="Policy loss", xaxis={'title': 'n-step iter'}, yaxis={'title': 'loss'})
        self.value_layout = dict(title="Value loss", xaxis={'title': 'n-step iter'}, yaxis={'title': 'loss'})
        self.entropy_layout = dict(title="Entropies", xaxis={'title': 'n-step iter'}, yaxis={'title': 'entropy'})
        self.spatial_entropy_layout = dict(title="Spatial entropies", xaxis={'title': 'n-step iter'},
                                      yaxis={'title': ' spatial entropy'})

        self.NSTEPITER = []
        self.VALUELOSS = []
        self.VALUELOSS_MEAN = []
        self.valueloss_sample = []
        self.POLICYLOSS = []
        self.POLICYLOSS_MEAN = []
        self.policyloss_sample = []
        self.ENTROPY = []
        self.ENTROPY_MEAN = []
        self.entropy_sample = []
        self.SPATIALENTROPY = []
        self.SPATIALENTROPY_MEAN = []
        self.spatial_entropy_sample = []

        self.EPISODES = []
        self.REWARDS = []
        self.REWARDS_MEAN = []
        self.reward_sample = []


    def SendData(self, is_nstep, value_loss, policy_loss, entropy, spatial_entropy, reward):

        if is_nstep:

            self.valueloss_sample.append(value_loss)
            self.policyloss_sample.append(policy_loss)
            self.entropy_sample.append(float(entropy))
            self.spatial_entropy_sample.append(float(spatial_entropy))

            if len(self.valueloss_sample) == 25:
                self.NSTEPITER.append(len(self.NSTEPITER) + 1)
                self.VALUELOSS.append(np.mean(self.valueloss_sample))
                self.POLICYLOSS.append(np.mean(self.policyloss_sample))
                self.ENTROPY.append(np.mean(self.entropy_sample))
                self.SPATIALENTROPY.append(np.mean(self.spatial_entropy_sample))

                self.valueloss_sample = []
                self.policyloss_sample = []
                self.entropy_sample = []
                self.spatial_entropy_sample = []

                if len(self.NSTEPITER) % 10 == 0:
                    self.VALUELOSS_MEAN.append(np.mean(self.VALUELOSS[len(self.VALUELOSS) - 10:]))
                    self.POLICYLOSS_MEAN.append(np.mean(self.POLICYLOSS[len(self.POLICYLOSS) - 10:]))
                    self.ENTROPY_MEAN.append(np.mean(self.ENTROPY[len(self.ENTROPY) - 10:]))
                    self.SPATIALENTROPY_MEAN.append(np.mean(self.SPATIALENTROPY[len(self.SPATIALENTROPY) - 10:]))

                trace_value = dict(x=self.NSTEPITER, y=self.VALUELOSS, type='custom', mode="lines", name='loss')
                trace_policy = dict(x=self.NSTEPITER, y=self.POLICYLOSS, type='custom', mode="lines", name='loss')
                trace_entropy = dict(x=self.NSTEPITER, y=self.ENTROPY, type='custom', mode="lines", name='entropy')
                trace_spatial_entropy = dict(x=self.NSTEPITER, y=self.SPATIALENTROPY, type='custom', mode="lines",
                                             name='spatial entropy')

                trace_value_mean = dict(x=self.NSTEPITER[::10], y=self.VALUELOSS_MEAN,
                                    line={'color': 'red', 'width': 3}, type='custom', mode="lines", name='mean loss')
                trace_policy_mean = dict(x=self.NSTEPITER[::10], y=self.POLICYLOSS_MEAN,
                                     line={'color': 'red', 'width': 3}, type='custom', mode="lines", name='mean loss')
                trace_entropy_mean = dict(x=self.NSTEPITER[::10], y=self.ENTROPY_MEAN,
                                    line={'color': 'red', 'width': 3}, type='custom', mode="lines", name='mean entropy')
                trace_spatial_entropy_mean = dict(x=self.NSTEPITER[::10], y=self.SPATIALENTROPY_MEAN,
                                          line={'color': 'red', 'width': 3}, type='custom', mode="lines",
                                          name='mean spatial entropy')

                self.vis._send(
                    {'data': [trace_value, trace_value_mean], 'layout': self.value_layout, 'win': 'valuewin'})
                self.vis._send(
                    {'data': [trace_policy, trace_policy_mean], 'layout': self.policy_layout, 'win': 'policywin'})
                self.vis._send(
                    {'data': [trace_entropy, trace_entropy_mean], 'layout': self.entropy_layout, 'win': 'entropywin'})
                self.vis._send(
                    {'data': [trace_spatial_entropy, trace_spatial_entropy_mean], 'layout': self.spatial_entropy_layout,
                     'win': 'spatial_entropywin'})

        else:

            self.reward_sample.append(reward)
            if(len(self.reward_sample) == 5):
                self.EPISODES.append(len(self.EPISODES) + 1)
                self.REWARDS.append(np.mean(self.reward_sample))
                self.reward_sample = []

                if len(self.EPISODES) % 10 == 0:
                    self.REWARDS_MEAN.append(np.mean(self.REWARDS[len(self.REWARDS) - 10:]))

                trace_reward = dict(x=self.EPISODES, y=self.REWARDS, type='custom', mode="lines", name='reward')
                trace_reward_mean = dict(x=self.EPISODES[::10], y=self.REWARDS_MEAN,
                                    line={'color': 'red', 'width': 4}, type='custom', mode="lines", name='mean reward')

                self.vis._send(
                    {'data': [trace_reward, trace_reward_mean], 'layout': self.reward_layout, 'win': 'rewardwin'})