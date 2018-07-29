"""Implements an RllabAdapter that converts rllab envs in a SoftlearningEnv."""

import gym.spaces

import rllab.spaces
from rllab.core.serializable import Serializable
from rllab.envs.mujoco.swimmer_env import SwimmerEnv
from rllab.envs.mujoco.ant_env import AntEnv
from rllab.envs.mujoco.humanoid_env import HumanoidEnv
from rllab.envs.normalized_env import NormalizedEnv

from softlearning.environments.rllab import (
    MultiDirectionSwimmerEnv,
    MultiDirectionAntEnv,
    MultiDirectionHumanoidEnv,
    CrossMazeAntEnv)

from .softlearning_env import SoftlearningEnv


RLLAB_ENVIRONMENTS = {
    'swimmer': {
        'default': SwimmerEnv,
        'multi-direction': MultiDirectionSwimmerEnv,
    },
    'ant': {
        'default': AntEnv,
        'multi-direction': MultiDirectionAntEnv,
        'cross-maze': CrossMazeAntEnv
    },
    'humanoid': {
        'default': HumanoidEnv,
        'multi-direction': MultiDirectionHumanoidEnv,
    },
}


def convert_rllab_space_to_gym_space(space):
    dtype = space.sample().dtype
    if isinstance(space, rllab.spaces.Box):
        return gym.spaces.Box(low=space.low, high=space.high, dtype=dtype)
    elif isinstance(space, rllab.spaces.Discrete):
        return gym.spaces.Discrete(n=space.n, dtype=dtype)
    elif isinstance(space, rllab.spaces.Product):
        return gym.spaces.Tuple([
            convert_rllab_space_to_gym_space(x)
            for x in space.components
        ])

    raise NotImplementedError(space)


class RllabAdapter(SoftlearningEnv):
    """Adapter to convert Rllab environment into standard."""

    def __init__(self, domain, task, *args, normalize=True, **kwargs):
        Serializable.quick_init(self, locals())
        super(RllabAdapter, self).__init__(domain, task, *args, **kwargs)

        env = RLLAB_ENVIRONMENTS[domain][task](*args, **kwargs)

        if normalize:
            env = NormalizedEnv(env)

        self._env = env

    @property
    def observation_space(self):
        observation_space = convert_rllab_space_to_gym_space(
            self._env.observation_space)
        if len(observation_space.shape) > 1:
            raise NotImplementedError(
                "Observation space ({}) is not flat, make sure to check the"
                " implemenation. ".format(observation_space))
        return observation_space

    @property
    def action_space(self):
        action_space = convert_rllab_space_to_gym_space(
            self._env.action_space)
        if len(action_space.shape) > 1:
            raise NotImplementedError(
                "Action space ({}) is not flat, make sure to check the"
                " implemenation. ".format(action_space))
        return action_space

    def step(self, action, *args, **kwargs):
        # TODO(hartikainen): refactor this to always return OrderedDict,
        # such that the observation for all the envs is consistent. Right now
        # Some of the rllab envs return np.array whereas other return dict.
        #
        # Something like:
        # observation = OrderedDict()
        # observation['observation'] = env.step(action, *args, **kwargs)
        # return observation

        return self._env.step(action, *args, **kwargs)

    def reset(self, *args, **kwargs):
        return self._env.reset(*args, **kwargs)

    def render(self, *args, **kwargs):
        return self._env.render(*args, **kwargs)

    def close(self, *args, **kwargs):
        return self._env.terminate(*args, **kwargs)

    def seed(self, *args, **kwargs):
        pass  # Nothing to seed

    def unwrapped(self, *args, **kwargs):

        pass  # Nothing to unwrap

    def copy(self, *args, **kwargs):
        raise NotImplementedError

    def get_param_values(self, *args, **kwargs):
        raise NotImplementedError

    def set_param_values(self, *args, **kwargs):
        raise NotImplementedError
