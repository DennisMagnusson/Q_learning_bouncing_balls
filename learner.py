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
discount = 0.5
exploitation_rate = 0.8
batch_size = 50

memories = []
losses = []
scores = []

actions = [game.move_left, game.move_right, game.do_nothing]

def train(model, eps=1000, speed=1):
  global exploitation_rate, losses

  for e in range(eps):
    frames = 0
    exploitation_rate = 1.0 - 0.2*(1.25**-(e/10))

    game.restart()
    prev_state, reward, score = game.tick(render=True, learn=True)
    prev_state = normalize(prev_state)
    state = prev_state

    while True:
      render = frames % speed == 0
      action = get_action(state)
      actions[action]()
      state, reward, score = game.tick(render=render, learn=True)
      state = normalize(state)

      memories.append([state, prev_state, action, reward])#Remember
      reinforce()
      
      prev_state = state
      frames += 1

      if score != -1:
        if reward > 0:
          print("Game solved after", e, "epochs")
        scores.append(score)
        break

    avg_loss = sum(losses) / len(losses)
    avg_score = sum(scores) / len(scores)
    print("Ep:{:4}, Score:{:2}, loss: {:.5f}, avg score: {:.2f}".format(e, scores[len(scores)-1], avg_loss, avg_score))
    #losses = []

#I think this is the correct way of doing it
#def reinforce(state, prev_state, action, reward):
def reinforce():
  bs = batch_size if batch_size < len(memories) else len(memories)
  s = sample(range(len(memories)), bs)
  x = []
  y = []
  for i in s:
    x.append(memories[i][0])
    reward = model.predict(np.array([memories[i][0]]))[0]
    reward[memories[i][2]] = memories[i][3] + discount * np.max(reward)
    y.append(reward)

  x = np.array([x[0]])
  y = np.array([y[0]])
  loss = np.average(np.array(model.fit(x, y, epochs=1, verbose=0).history['loss']))
  losses.append(loss)
  
def get_action(state):
  if random() > exploitation_rate:
    return randint(0, 2)

  expected_reward = model.predict(np.array([state]))
  return np.argmax(expected_reward)

def normalize(state):
  #Shitty code incoming
  l = []
  pad_x = state.pop()
  l.append(pad_x / game.WIDTH)

  for i in range(0, len(state), 4):
    l.append(state.pop() / 20 + 0.5)
    l.append(state.pop() / 20 + 0.5)
    l.append(state.pop() / game.HEIGHT)
    l.append(state.pop() / game.WIDTH)

  return l


#The model is trained with the expected rewards and the actual reward of the action + the next (current) reward times the discount. so expected_reward = model.predict(state)
#expected_reward[action] += reward * discount , I think
def create_model(input_size):
  model = Sequential()
  model.add(Dense(40, input_dim=input_size))
  model.add(Activation("relu"))
  model.add(Dense(len(actions)))
  model.add(Activation("linear"))
  
  model.compile(loss='mse', optimizer=keras.optimizers.adam(lr=lr))

  return model

if __name__ == "__main__":
  if len(sys.argv) == 1:
    print("Please specify number of balls")
    sys.exit()
  game.init_game(int(sys.argv[1]))
  model = create_model(1+4*int(sys.argv[1]))
  train(model, eps=10000, speed=int(sys.argv[2]))
