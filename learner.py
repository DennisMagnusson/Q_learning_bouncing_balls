from __future__ import print_function, division
import sys, math
import game
from keras.models import Sequential
from keras.layers import Dense, Activation
import keras.optimizers

import numpy as np

###Constants
X_POS_BUCKETS = 4
Y_POS_BUCKETS = 1
X_VEL_BUCKETS = 1
Y_VEL_BUCKETS = 3
PAD_POS_BUCKETS = 1

NUM_ACTIONS = 3#Left right nothing

lr = 0.01
discount = 0.08

q_table = ()

actions = [game.move_left, game.move_right, game.do_nothing]

def train(model, eps=1000, speed=1):
  #TODO Input needs to be normalized FIXME XXX
  #TODO How to normalize the velocity?

  for e in range(eps):
    game.restart()
    prev_state, reward = game.tick(render=True, learn=True, speed=speed)
    action = 2#Do nothing on the first move.
    while True:
      state, reward = game.tick(render=True, learn=True, speed=speed)
      state = normalize(state)
      #if action == 2:#TODO Update this in some way
        #reward -= 0.91
      #else:
      #reward -= 0.75

      action = reinforce(state, prev_state, action, reward)

      if reward <= -1:#Game over, man
        break

      #action = np.argmax(q_table[tuple(state)])
      actions[action]()
      prev_state = state

#TODO Use the X pos in relation to the pad
#TODO Maybe try to keep values between -1 and 1 FIXME XXX
def normalize(state):
  #Shitty code incoming
  l = []
  pad_x = state.pop()
  l.append(pad_x / 640)

  for i in range(0, len(state), 4):
    l.append(state.pop() / 10)
    l.append(state.pop() / 10)
    l.append(state.pop() / 480)
    l.append((state.pop() - pad_x) / 640)

  return l

#Update Q table
#Q(state_t, action_t) += lr*(reward + discount*maxQ_a(state_t+1, a) - Q(state_t, action_t)
#Where t is when the simulation was done and t+1 is after the simulation
def update_q(state, prev_state, action, reward):
  global q_table
  prev_q_index = tuple(prev_state) + tuple([action])
  best_q_index = tuple(state) + tuple([np.argmax(q_table[tuple(state)])])
  q_table[prev_q_index] += lr*(reward + discount*q_table[best_q_index] - q_table[prev_q_index])


#I think this is the correct way of doing it
def reinforce(state, prev_state, action, reward):
  expected_reward = model.predict(np.array([prev_state]))
  print(np.argmax([expected_reward]))
  print(expected_reward[0])#TODO Check this
  #action -= 1
  expected_reward[0][action] = reward + discount * np.argmax(model.predict(np.array([state])))
  print(expected_reward[0])
  
  model.fit(np.array([state]), expected_reward, epochs=1, verbose=0)
  return np.argmax(expected_reward)

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


#TODO Change to Tensorflow?
#TODO The model is trained with the expected rewards and the actual reward of the action + the next (current) reward times the discount. so expected_reward = model.predict(state)

#expected_reward[action] += reward * discount , I think
#TODO The action is the argmax of the output.

def create_model(input_size):
  model = Sequential()
  model.add(Dense(30, input_dim=input_size))
  model.add(Activation("relu"))
  model.add(Dense(20))
  model.add(Activation("relu"))
  model.add(Dense(len(actions)))
  model.add(Activation("linear"))
  
  #TODO set the learning rate
  model.compile(loss='mse', optimizer=keras.optimizers.rmsprop(lr=lr))#TODO Change to logloss?

  return model

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
  model = create_model(1+4*int(sys.argv[1]))
  train(model, eps=1000, speed=int(sys.argv[2]))
