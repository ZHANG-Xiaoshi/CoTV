"""FlowCAV under Dublin scenario (sumo template)"""
import os

from ray.rllib.agents.ppo.ppo_policy import PPOTFPolicy
from ray.tune.registry import register_env
from flow.utils.registry import make_create_env
from flow.envs.multiagent import FlowCAVCustomEnv

from flow.core.params import VehicleParams
from flow.core.params import NetParams
from flow.core.params import EnvParams
from flow.core.params import SumoParams
from flow.core.params import TrafficLightParams

from flow.networks import SumoNetwork

# Experiment parameters
N_ROLLOUTS = 18  # number of rollouts per training iteration
N_CPUS = 18  # number of parallel workers
HORIZON = 720  # time horizon of a single rollout

SPEED_LIMIT = 15
MAX_ACCEL = 3  # maximum acceleration for autonomous vehicles, in m/s^2
MAX_DECEL = 3  # maximum deceleration for autonomous vehicles, in m/s^2

ABS_DIR = os.path.abspath(os.path.dirname(__file__)).split('flow')[0]

vehicles = VehicleParams()

# if traffic is in osm, activate this
tl_logic = TrafficLightParams(baseline=False)

flow_params = dict(
    exp_tag='FlowCAV_Dublin',

    env_name=FlowCAVCustomEnv,

    network=SumoNetwork,

    simulator='traci',

    sim=SumoParams(
        render=False,
        sim_step=1,
        restart_instance=True,
        emission_path="{}output/FlowCAV_Dublin".format(ABS_DIR)
    ),

    env=EnvParams(
        horizon=HORIZON,
        additional_params={
            "target_velocity": SPEED_LIMIT,
            'max_accel': MAX_ACCEL,
            'max_decel': MAX_ACCEL,
            "safety_device": True,  # 'True' needs emission path to save output file
        },
    ),

    net=NetParams(
        template={
            "net": "{}/scenarios/CoTV/Dublin/dublin.net.xml".format(ABS_DIR),
            "rou": "{}/scenarios/CoTV/Dublin/dublin_clip_rl.rou.xml".format(ABS_DIR),
            "vtype": "{}/scenarios/CoTV/Dublin/rl_vtypes.add.xml".format(ABS_DIR)}
    ),

    veh=vehicles,

    tls=tl_logic
)

create_env, env_name = make_create_env(params=flow_params, version=0)

# Register as rllib env
register_env(env_name, create_env)

test_env = create_env()
obs_space = test_env.observation_space
act_space = test_env.action_space


def gen_policy():
    """Generate a policy in RLlib."""
    return PPOTFPolicy, obs_space, act_space, {}


# Setup PG with a single policy graph for all agents
POLICY_GRAPHS = {'cav': gen_policy()}


def policy_mapping_fn(_):
    """Map a policy in RLlib."""
    return 'cav'


policies_to_train = ['cav']
