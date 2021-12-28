from matplotlib.pyplot import plot
from env import env
from DQN import *
def entry(epochs,steps,batch_print):
  enginee=agent()
  db_env=env()
  setup_seed(123)
  train_loss=[]  
  stage_loss,step_loss,ps_cache,repl_cache,action_cache,reward_cache,types_cache=enginee.train(db_env,epochs,steps,batch_print,greedy=False)
  train_loss+=stage_loss
  plot([i for i in range(len(train_loss))],train_loss)
  # return enginee
  max_idx,ps,replicate,rewards,actions=enginee.inference(db_env,steps,False)
  print(rewards[max_idx],actions[max_idx])
  print(replicate[max_idx])#150,80,10
  display(ps[max_idx])
if __name__=='__main__':
  entry()