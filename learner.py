from __future__ import print_function, division
import sys, math
from random import random, randint, sample
import game
from keras.models import Sequential
from keras.layers import Dense, Activation
import keras.optimizers

import numpy as np

NUM_ACTIONS = 3#Left right nothing

lr = 0.001
discount = 0.03#Lower is usually better
exploitation_rate = 0.8
batch_size = 100
experiences = []
experiences_y = []

q_table = ()

actions = [game.move_left, game.move_right, game.do_nothing]

def train(model, eps=1000, speed=1):
  global exploitation_rate

  for e in range(eps):
    frames = 0
    exploitation_rate *= 1.01
    game.restart()
    prev_state, reward = game.tick(render=True, learn=True)
    prev_state = normalize(prev_state)
    action = 2#Do nothing on the first move.
    while True:
      render = frames % speed == 0
      state, reward = game.tick(render=render, learn=True)
      state = normalize(state)
      action = reinforce(state, prev_state, action, reward)

      if reward <= -10 or reward == 100:#Game over, man
        break

      #action = np.argmax(q_table[tuple(state)])
      if actions[action]() == -1:
        reinforce(state, prev_state, action, -1)
      
      prev_state = state
      frames += 1

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
    l.append(state.pop() / 640)

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
  #experiences.append([state, prev_state, action, reward])#Save
  experiences.append([state])
  expected_reward = model.predict(np.array([prev_state]))
  #print(np.argmax([expected_reward]))
  #print(expected_reward[0])
  expected_reward[0][action] = reward + discount * np.max(model.predict(np.array([state])))
  #print(expected_reward[0])

  experiences_y.append(expected_reward)

  bs = batch_size if batch_size < len(experiences) else len(experiences)
  s = sample(range(len(experiences)), bs)
  #x = np.array([np.array(experiences[i]) for i in s])[0].T
  x = []
  y = []
  for i in s:
    x.append(experiences[i])
    y.append(experiences_y[i])

  x = np.array(x[0])
  y = np.array(y[0])
  #x = np.array([np.array([e for e in experiences[i]]) for i in s])
  #y = np.array([np.array(experiences_y[i]) for i in s])[0]
  model.fit(x, y, epochs=1, verbose=0)#TODO Change verbosity to 0
  #model.fit(np.array([state]), expected_reward, epochs=1, verbose=0)

  #Return the next action
  if random() > exploitation_rate:
    return randint(0, 2)
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
  model.add(Dense(20, input_dim=input_size))
  model.add(Activation("sigmoid"))
  #model.add(Dense(20))
  #model.add(Activation("relu"))
  model.add(Dense(len(actions)))
  model.add(Activation("linear"))
  
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
