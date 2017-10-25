import numpy as np

import game

###Constants
X_POS_BUCKETS = 6
Y_POS_BUCKETS = 4
X_VEL_BUCKETS = 4
Y_VEL_BUCKETS = 4
PAD_POS_BUCKETS = 6

NUM_ACTIONS = 3#Left right nothing

def to_buckets(state):
  buckets = []
  buckets.append(state.pop() / (WIDTH * PAD_POS_BUCKETS))
  for i in range(0, len(state), 4):
    buckets.append(state.pop() / (WIDTH  * X_POS_BUCKETS))
    buckets.append(state.pop() / (HEIGHT * Y_POS_BUCKETS))
    buckets.append(state.pop() / (WIDTH  * X_VEL_BUCKETS))
    buckets.append(state.pop() / (HEIGHT * Y_VEL_BUCKETS))
  
  return buckets
  

def train(eps):
  for e in range(eps):
    while True:
      state, reward = tick(render=False, learn=True)
      if reward == -1:
        #TODO Do some shit and modify weights or whatever
        break
    #TODO Action


if __name__ == "__main__":
  train()
