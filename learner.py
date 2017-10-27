from __future__ import print_function
import sys, math
import game

import numpy as np

###Constants
X_POS_BUCKETS = 6
Y_POS_BUCKETS = 4
X_VEL_BUCKETS = 4
Y_VEL_BUCKETS = 4#Change this to 2? Or maybe 3. Negative, positive and near-zero?
PAD_POS_BUCKETS = 6

NUM_ACTIONS = 3#Left right nothing

lr = 0.2
discount = 0.3

q_table = ()

actions = [game.move_left, game.move_right, game.do_nothing]

def to_buckets(state):
  buckets = []
  buckets.append(int(state.pop() / (game.WIDTH * PAD_POS_BUCKETS)))
  #TODO Order after y-position or something in order to reduce possible dimensions.
  for i in range(0, len(state), 4):
    buckets.append(int(state.pop() / (game.WIDTH  * X_POS_BUCKETS)))
    buckets.append(int(state.pop() / (game.HEIGHT * Y_POS_BUCKETS)))
    buckets.append(int(state.pop() / (game.WIDTH  * X_VEL_BUCKETS)))
    buckets.append(int(state.pop() / (game.HEIGHT * Y_VEL_BUCKETS)))
  
  print(buckets)
  return buckets
  

def train(eps):
  for e in range(eps):
    state, reward = game.tick(render=True, learn=True)
    while True:
      state = to_buckets(state)
      #print(state.shape())
      print(q_table.shape())
      print(q_table[state].shape())
      #TODO Convert state to tuple
      action = np.argmax(q_table[state])
      actions[actions]()
      state, reward = game.tick(render=True, learn=True)
      #q_table[state, action] = #The equation

      #if reward == -1:
        ##TODO Do some shit and modify weights or whatever
        #break
    #TODO Action

def get_max_q(state):
 options = q_table[to_tuple(state)]#Don't know how to do to tuple, but I'll fix it later.
 print(max(options))
 return np.argmax(options)

def init_ai():
  global q_table
  NUM_BUCKETS = [PAD_POS_BUCKETS, game.n_balls*[X_POS_BUCKETS, Y_POS_BUCKETS, X_VEL_BUCKETS, Y_VEL_BUCKETS]]
  #Very shitty hack
  q_table = np.random.normal(np.zeros(NUM_BUCKETS.append(NUM_ACTIONS)))-0.5#Center at 0


if __name__ == "__main__":
  if len(sys.argv) == 1:
    print("Please specify number of balls")
    sys.exit()
  game.init_game(int(sys.argv[1]))
  init_ai()
  train(10)
