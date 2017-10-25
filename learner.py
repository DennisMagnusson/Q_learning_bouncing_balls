import sys
import game

import numpy as np

###Constants
X_POS_BUCKETS = 6
Y_POS_BUCKETS = 4
X_VEL_BUCKETS = 4
Y_VEL_BUCKETS = 4#Change this to 2? Or maybe 3. Negative, positive and near-zero?
PAD_POS_BUCKETS = 6

NUM_ACTIONS = 3#Left right nothing

q_table = ()

def to_buckets(state):
  buckets = []
  buckets.append(state.pop() / (WIDTH * PAD_POS_BUCKETS))
  #TODO Order after y-position or something in order to reduce possible dimensions.
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

def init_ai():
  global q_table
  NUM_BUCKETS = (PAD_POS_BUCKETS) + n_balls*(X_POS_BUCKETS, Y_POS_BUCKETS, X_VEL_BUCKETS, Y_VEL_BUCKETS)
  q_table = np.zeros(NUM_BUCKETS + (NUM_ACTIONS,))


if __name__ == "__main__":
  if len(sys.argv) == 1:
    print("Please specify number of balls")
    sys.exit()
  init_game(int(sys.argv[1]))
  init_ai()
  train()
