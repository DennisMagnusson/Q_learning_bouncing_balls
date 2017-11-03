from __future__ import print_function
import sys, math
import game

import numpy as np

###Constants
X_POS_BUCKETS = 4
Y_POS_BUCKETS = 1
X_VEL_BUCKETS = 1
Y_VEL_BUCKETS = 3
PAD_POS_BUCKETS = 1

NUM_ACTIONS = 3#Left right nothing

lr = 0.1
discount = 0.8

q_table = ()

actions = [game.move_left, game.move_right, game.do_nothing]

def train(eps, speed=1):
  for e in range(eps):
    game.restart()
    state, reward = game.tick(render=True, learn=True, speed=speed)
    action = 2#Do nothing on the first move.
    prev_state = to_buckets(state)
    while True:
      state, reward = game.tick(render=True, learn=True, speed=speed)
      state = to_buckets(state)
      update_q(state, prev_state, action, reward)

      if reward <= -1:#Game over, man
        break

      action = np.argmax(q_table[tuple(state)])
      actions[action]()
      prev_state = state


#Update Q table
#Q(state_t, action_t) += lr*(reward + discount*maxQ_a(state_t+1, a) - Q(state_t, action_t)
#Where t is when the simulation was done and t+1 is after the simulation
def update_q(state, prev_state, action, reward):
  global q_table
  prev_q_index = tuple(prev_state) + tuple([action])
  best_q_index = tuple(state) + tuple([np.argmax(q_table[tuple(state)])])
  q_table[prev_q_index] += lr*(reward + discount*q_table[best_q_index] - q_table[prev_q_index])

def to_buckets(state):
  buckets = []
  pad_x = state.pop()
  #Fix some errors
  if pad_x > game.WIDTH:
    pad_x = game.WIDTH - 1
  if pad_x < 0:
    pad_x = 1

  buckets.append(int(pad_x * PAD_POS_BUCKETS / game.WIDTH))
  for i in range(0, len(state), 4):
    y_vel = state.pop()
    if abs(y_vel) < 0.2:
      buckets.append(0)
    elif y_vel < 0:
      buckets.append(1)
    else:
      buckets.append(2)
    #X velocity (ignored)
    state.pop()
    buckets.append(0)

    buckets.append(int(state.pop() * Y_POS_BUCKETS / game.HEIGHT))

    ball_x = state.pop()
    if abs(ball_x - pad_x) < 170:#If ball is above pad
      if ball_x < pad_x:
        buckets.append(0)
      else:
        buckets.append(3)
    elif ball_x < pad_x:
      buckets.append(1)
    else:
      buckets.append(2)

  
  return buckets


def init_ai():
  global q_table

  n_buckets = [PAD_POS_BUCKETS]
  for i in range(game.n_balls):
    n_buckets.append(Y_VEL_BUCKETS)
    n_buckets.append(X_VEL_BUCKETS)
    n_buckets.append(Y_POS_BUCKETS)
    n_buckets.append(X_POS_BUCKETS)
  q_table = np.random.random_sample(n_buckets + [NUM_ACTIONS])-0.5#Center at 0


if __name__ == "__main__":
  if len(sys.argv) == 1:
    print("Please specify number of balls")
    sys.exit()
  game.init_game(int(sys.argv[1]))
  init_ai()
  train(1000, speed=int(sys.argv[2]))
