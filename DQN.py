import math
import random
from collections import namedtuple, deque
from estimator import cost_estimate
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    # torch.cuda.manual_seed_all(run_num)  # if you are using multi-GPU.
    np.random.seed(seed)  # Numpy module.
    random.seed(seed)  # Python random module.
    torch.manual_seed(seed)
    # torch.backends.cudnn.benchmark = False
    # torch.backends.cudnn.deterministic = True

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
Transition = namedtuple('Transition',('state', 'action', 'next_state', 'reward'))
class ReplayMemory(object):

    def __init__(self, capacity):
        self.memory = deque([],maxlen=capacity)

    def push(self, *args):
        """Save a transition"""
        self.memory.append(Transition(*args))
    def push_numpy(self, args):
      # print(args[0].shape,args[1].shape)
      self.push(torch.from_numpy(args[0]),args[1],torch.from_numpy(args[2]),torch.from_numpy(args[3]))

    def sample(self, batch_size):
        # random.seed(0)
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

n_states=67
n_actions=67
import torch.nn.functional as F
# class DQN(nn.Module):
#     def __init__(self):
#         super(DQN, self).__init__()
#         # self.flatten = nn.Flatten()
#         self.linear_relu_stack = nn.Sequential(
#             # nn.Linear(np.array(env.observation_space.shape).prod(), 128, bias=False),
#             nn.Linear(n_states, 128, bias=False),
#             nn.ReLU(),
#             nn.Linear(128, 64),
#             nn.ReLU(),
#             nn.Linear(64, n_actions),
#         )
#         self.head = nn.Linear(n_states, n_actions)

#     def forward(self, x):
#         x = x.float()
#         x = self.linear_relu_stack(x)
#         print('forward output',x.shape)
#         print('reshaped',x.view(x.size(0), -1).shape)
#         if x.size(0)==n_actions:
#           return self.head(x.view(1,-1))
#         else:
#           return self.head(x.view(x.size(0), -1))

class DQN(nn.Module):

  def __init__(self):
    super(DQN, self).__init__()
    self.hidden1 = nn.Linear(n_states, 128)
    self.hidden2 = nn.Linear(128, 64)
    self.output = nn.Linear(64, n_actions)
    # self.head = nn.Linear(n_states, n_actions)

  def forward(self, x):
    x = x.to(device)
    x = x.float()
    # print(x.shape)
    x = F.relu(self.hidden1(x))
    x = F.relu(self.hidden2(x))
    x = self.output(x)
    # print('forward output',x.shape)
    # print('reshaped',x.view(x.size(0), -1).shape)
    # return self.head(x.view(x.size(0), -1))
    return x


def display(scheme):
    ret_dict={}
    for table,values in scheme.items():
        for attr,val in values.items():
            if val==1:
                ret_dict[table]=attr
                break
    print(ret_dict)

BATCH_SIZE = 32
GAMMA = 0.99
EPS_START = 0.9
EPS_END = 0.05
# EPS_DECAY = 0.997
EPS_DECAY = 0.005
TARGET_UPDATE = 10
learning_rate=5e-4
mask_fact_table=[True]*67
mask_fact_table[64]=False # not replicate lineorder
action_mask=torch.from_numpy(np.array(mask_fact_table)).to(device=device) 
class agent():
    def __init__(self) -> None:
        self.policy_net=DQN().float().to(device)
        self.target_net=DQN().float().to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        self.optimizer = optim.Adam(self.policy_net.parameters(),learning_rate)
        self.memory = ReplayMemory(10000)
        self.steps_done=0
    def select_action(self,state):
        # random.seed(0)
        sample = random.random()
        eps_threshold = EPS_END + (EPS_START - EPS_END) * \
            math.exp(-1. * self.steps_done * EPS_DECAY)
        self.steps_done += 1
        if sample > eps_threshold:
            with torch.no_grad():
              output=self.policy_net(torch.FloatTensor(state).unsqueeze(0)) # mask fact table replication
              max_idx=torch.masked_select(output.squeeze(0), action_mask).max(0)[1]
              kept_idx=action_mask.nonzero()
              action= kept_idx[max_idx].view(1,1) 
              return action,'max'               
              # return self.policy_net(torch.FloatTensor(state)).max(1)[1].view(1, 1),'max'
        else:
            # return torch.tensor([[random.randrange(n_actions)]], device=device, dtype=torch.long),'random'
            return torch.tensor([[self.steps_done%67]], device=device, dtype=torch.long),'random'

    def optimize(self):
      BATCH_SIZE=1
      if len(self.memory) < BATCH_SIZE:
        return None      
      # print('optimized!')
      transitions = self.memory.sample(BATCH_SIZE)
      # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
      # detailed explanation). This converts batch-array of Transitions
      # to Transition of batch-arrays.
      transition_batch = Transition(*zip(*transitions))
      # state_batch = torch.stack(transition_batch.state).to(device=device)
      # action_batch = torch.stack(transition_batch.action).to(device=device)
      # reward_batch = torch.stack(transition_batch.reward).to(device=device)
      state_batch = torch.cat(transition_batch.state)
      action_batch = torch.cat(transition_batch.action)
      reward_batch = torch.cat(transition_batch.reward)  

      # print('state_batch',state_batch.shape) 
      # print('action_batch',action_batch.shape)
      # print('reward_batch',reward_batch.shape)   

      # compute Q(s_t, a)
      output=self.policy_net(state_batch)
      # print("output_shape",output.shape)
      state_action_values=output.gather(1, action_batch)
      # state_action_values = self.policy_net(state_batch).gather(1, action_batch)
      next_state_values=self.target_net(state_batch).max(1)[0].detach()
      # next_state_values= self.target_net(state_batch).max(1)[0].detach().view(state_batch.shape[0], 1)
      # print('target_output',next_state_values.shape)

      expected_state_action_values = ((next_state_values * GAMMA) + reward_batch).view(BATCH_SIZE, 1)
      # print('state_action_values',state_action_values.shape)
      # print('expected_state_action_values', expected_state_action_values.shape)
      criterion = nn.SmoothL1Loss()
      loss = criterion(state_action_values, expected_state_action_values.float())
      # Optimize the model
      self.optimizer.zero_grad()
      loss.backward()
      for param in self.policy_net.parameters():
          param.grad.data.clamp_(-1, 1)
      self.optimizer.step()
      return loss

    def train(self,db_env,num_episodes,t_max,Batch_Print,early_stopping=False,greedy=False):
        loss_plot=[]
        prev_loss=0
        loss_rise_cnt=0
        logger_cache=[]
        ps_cache=[]
        repl_cache=[]       
        reward_cache=[]
        action_cache=[]
        types_cache=[]
        for i_episode in range(num_episodes):
            # Initialize the environment and state
            db_env.reset()
            current_state =db_env.get_current_state()
            logger=[]
            # loss_cnt_EPI=0
            # prev_loss_EPI=0
            ps=[]
            repl=[]
            actions=[]
            rwrds=[]
            types=[]
            for t in range(t_max):
                # print('step', t)
                # Select and perform an action
                # TODO reduce actions when generating or stepping
                action,type_action = self.select_action(current_state)
                # action = self.select_action(current_state)
                next_state,msg = db_env.step(action.item())
                reward=cost_estimate(db_env,greedy)
                # reward_cache.append(reward)

                # Store the transition in memory
                self.memory.push_numpy((current_state, action, next_state, reward))

                # # Move to the next state
                current_state = next_state

                # Perform one step of the optimization (on the policy network)
                loss=self.optimize()
                # print(db_env.replicated_table)

                # ps.append(copy.deepcopy(db_env.partition_scheme))
                # repl.append(copy.deepcopy(db_env.replicated_table)) 
                # actions.append([action,type_action,msg])   
                # rwrds.append(reward)
                # types.append(type_action)
                if loss is not None:
                    logger.append(loss)
                    # ps.append(copy.deepcopy(db_env.partition_scheme))
                    # repl.append(copy.deepcopy(db_env.replicated_table)) 
                    # actions.append([action,type_action,msg])   
                    # rwrds.append(reward)
                    # types.append(type_action)
                    
            # # Update the target network, copying all weights and biases in DQN

            # ps_cache.append(ps)
            # repl_cache.append(repl)
            # action_cache.append(actions)
            # reward_cache.append(rwrds)
            # types_cache.append(types)

            if len(logger)>1:
              if num_episodes>1:
                avg_loss=sum(logger)/len(logger)
                loss_plot.append(avg_loss)
              else:
                loss_plot=logger
                # print(len(logger))
            if (i_episode+1) % Batch_Print == 0:
                print('episode batch {} completed'.format(i_episode//Batch_Print))
                self.target_net.load_state_dict(self.policy_net.state_dict())
            # if error:
            #   print(action.item())
            #   break        
            logger_cache.append(logger)   

        print('Complete')  
        # return loss_plot,reward_cache
        return loss_plot,logger_cache,ps_cache,repl_cache,action_cache,reward_cache,types_cache
    def inference(self,db_env,t_max,greedy=True):
        reward_cache=[]
        ps_cache=[]
        replicate_tbl_cache=[]
        db_env.reset()
        current_state =db_env.get_current_state()
        state_set=[]
        action_cache=[]
        for iter in range(t_max):
            # print(len(current_state))
            # output=policy_net(torch.FloatTensor(current_state))
            # action= output.max(1)[1].view(1, 1)
            output=self.policy_net(torch.FloatTensor(current_state).unsqueeze(0)) # mask fact table replication
            max_idx=torch.masked_select(output.squeeze(0), action_mask).max(0)[1]
            kept_idx=action_mask.nonzero()
            action= kept_idx[max_idx].view(1,1)  
            next_state,msg = db_env.step(action.item())
            reward=cost_estimate(db_env,greedy)     
            current_state=next_state
            reward_cache.append(reward)
            ps_cache.append(db_env.partition_scheme)
            replicate_tbl_cache.append(db_env.replicated_table)
            # print(np.where(np.array(current_state)==1))
            state_set.append(current_state)
            action_cache.append([action,msg])
        # print(len(set(state_set)))
        max_idx=np.argmax(np.array(reward_cache))
        # return ps_cache[max_idx],replicate_tbl_cache[max_idx]
        return max_idx,ps_cache,replicate_tbl_cache,reward_cache,action_cache
        