from __future__ import print_function, division
import sys, math
from random import random, randint, sample
import game
from keras.models import Sequential
from keras.layers import Dense, Activation
import keras.optimizers

import numpy as np

NUM_ACTIONS = 3#Left right nothing

#Hyperparams
lr = 0.001
discount = 0.99
exploitation_rate = 0.7
batch_size = 100

experiences = []
experiences_y = []

actions = [game.move_left, game.move_right, game.do_nothing]

def train(model, eps=1000, speed=1):
  global exploitation_rate

  for e in range(eps):
    frames = 0
    exploitation_rate = 1.0 - 0.3*(1.1**-(e/10))
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

      if actions[action]() == -1:#Punish pushing against wall
        reinforce(state, prev_state, action, -1)
      
      prev_state = state
      frames += 1

def normalize(state):
  #Shitty code incoming
  l = []
  pad_x = state.pop()
  l.append(pad_x / 640)

  for i in range(0, len(state), 4):
    l.append(state.pop() / 10)
    l.append(state.pop() / 10)
    l.append(state.pop() / game.HEIGHT)
    l.append(state.pop() / game.WIDTH)

  return l

#I think this is the correct way of doing it
def reinforce(state, prev_state, action, reward):
  experiences.append([state])
  expected_reward = model.predict(np.array([prev_state]))
  print(expected_reward[0])
  expected_reward[0][action] = reward + discount * np.max(model.predict(np.array([state])))
  print(expected_reward[0])

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
  loss = np.average(np.array(model.fit(x, y, epochs=1, verbose=0).history['loss']))
  print(loss)

  #Return the next action
  if random() > exploitation_rate:
    return randint(0, 2)
  return np.argmax(expected_reward)

#The model is trained with the expected rewards and the actual reward of the action + the next (current) reward times the discount. so expected_reward = model.predict(state)
#expected_reward[action] += reward * discount , I think
def create_model(input_size):
  model = Sequential()
  model.add(Dense(40, input_dim=input_size))
  model.add(Activation("sigmoid"))
  model.add(Dense(20))
  model.add(Activation("sigmoid"))
  model.add(Dense(len(actions)))
  model.add(Activation("linear"))
  
  model.compile(loss='mse', optimizer=keras.optimizers.rmsprop(lr=lr))

  return model

if __name__ == "__main__":
  if len(sys.argv) == 1:
    print("Please specify number of balls")
    sys.exit()
  game.init_game(int(sys.argv[1]))
  model = create_model(1+4*int(sys.argv[1]))
  train(model, eps=10000, speed=int(sys.argv[2]))
