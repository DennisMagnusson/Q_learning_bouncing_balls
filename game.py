from __future__ import print_function

import pygame
from pygame.locals import *
from random import random
import sys, math

import Box2D
import Box2D.b2 as b2d

###Constants
PPM = 100.0 #Pixels per meter.
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS
WIDTH, HEIGHT = 640, 480
GRAVITY = 9.81

VELOCITY = 750 / PPM

BALL_RADIUS = 0.15
PAD_RADIUS = 5

n_balls = -1
frames = 0

pygame.init()
font = pygame.font.SysFont("monospace", 15)

screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption("SuperKoolt spel")
clock = pygame.time.Clock()

world = b2d.world(gravity=(0, -GRAVITY), doSleep=True)

world.CreateStaticBody(position=(0, 0), shapes=b2d.polygonShape(box=(0.01, 100)))#Left wall
world.CreateStaticBody(position=(float(WIDTH/PPM), 0), shapes=b2d.polygonShape(box=(0.01, 100))) #Right wall
world.CreateStaticBody(position=(0, float(HEIGHT/PPM)), shapes=b2d.polygonShape(box=(100, 0.01)))#Ceiling

pad_body = world.CreateKinematicBody(position=(WIDTH/(PPM*2), 0.3 - PAD_RADIUS), 
                                     shapes=b2d.circleShape(radius=PAD_RADIUS))
pad_body.mass = 10000
pad_body.fixedRotation = True

pygame.key.set_repeat(10, 10)

balls = []

def draw():
  screen.fill((0, 0, 0, 255))#Clear screen
  for ball in balls:
    draw_circle(ball, BALL_RADIUS)
  draw_circle(pad_body, PAD_RADIUS)

  screen.blit(font.render(str(frames/TARGET_FPS), 1, (255, 255, 255)), (0, 0))
  pygame.display.flip()

def draw_circle(body, radius):
  pos = body.transform*body.position*PPM/2.0 #I have no fucking idea why everything needs to be divided by two
  pos[1] = HEIGHT - pos[1]#Count from the top
  pygame.draw.circle(screen, (255, 0, 0, 255), [int(pos[0]), int(pos[1])], int(radius*PPM))

def draw_ground():
  for fixture in ground_body.fixtures:
    shape = fixture.shape
    vertices = [(ground_body.transform * v) * PPM for v in shape.vertices]
    vertices = [(v[0], HEIGHT - v[1]) for v in vertices]
    pygame.draw.polygon(screen, (0, 0, 255, 255), vertices)

def move_left():
  if pad_body.position[0] > 0:
    pad_body.linearVelocity = (-VELOCITY, 0)
  else:
    do_nothing()
    return -1

def move_right():
  if pad_body.position[0] < WIDTH/PPM:
    pad_body.linearVelocity = (VELOCITY, 0)
  else:
    do_nothing()
    return -1

def do_nothing():
  pad_body.linearVelocity = (0, 0)

def get_input():
  pad_body.linearVelocity = (0, 0)
  for event in pygame.event.get():
    if event.type == KEYDOWN:
      if event.key == K_a:
        move_left()
      elif event.key == K_d:
        move_right()

def get_state():
  a = []
  for ball in balls:
    a.append(ball.position[0]*PPM)
    a.append(ball.position[1]*PPM)
    a.append(ball.linearVelocity[0])
    a.append(ball.linearVelocity[1])
 
  a.append(pad_body.position[0]*PPM)
  
  #Bubble sort balls after y position
  for i in range(len(balls)):
    for j in range(i+1, len(balls)):
      if balls[i].position[1] > balls[j].position[1]:
        for k in range(4):
          tmp = a[i*4 + k]
          a[i*4 + k] = a[j*4 + k]
          a[j*4 + k] = tmp

  #I could reverse this, but I'm afraid things might break
  return a

def human_play():
  while tick(render=True):#Totally makes sense
    get_input()

  restart()
  human_play()

def init_game(number_of_balls=2):
  global n_balls
  n_balls = number_of_balls
  for i in range(n_balls):
    balls.append(world.CreateDynamicBody(position=(WIDTH/(PPM*2) - 1 + 2*random(), HEIGHT/(PPM*1.1))))
    balls[i].CreateCircleFixture(radius=BALL_RADIUS, restitution=0.9)
    balls[i].linearVelocity = (-1 + 2*random(), -1 + 2*random())
 
def restart():
  global frames, balls, pad_body
  frames = 0
  for ball in balls:
    ball.position = (WIDTH/(PPM*2) - 1 + 2*random(), HEIGHT/(PPM*1.1))
    ball.linearVelocity = (-1 + 2*random(), -1 + 2*random())
  
  #Move the pad to the middle
  #No idea why I have to divide by 2
  #Also this is the shittiest hack ever
  pad_body.linearVelocity[0] = ((WIDTH / (2*PPM)) - pad_body.position[0]) * TARGET_FPS/2.0
  world.Step(TIME_STEP, 10, 10)
  pad_body.linearVelocity[0] = 0

def tick(render=True, learn=False):
  global frames

  reward = -0.1
  score = frames/TARGET_FPS
  if score > 60:#Win
    print("Winner Winner Chicken Dinner")
    return False if not learn else [get_state(), 1, 60]

  for ball in balls:
    dx = ball.position[0] - pad_body.position[0]
    dy = ball.position[1] - pad_body.position[1]

    if ball.position[1] < -BALL_RADIUS:#Game over
      #print("SCORE: ", frames/TARGET_FPS)
      return False if not learn else [get_state(), -1, frames/TARGET_FPS]

    elif math.sqrt((dx**2 + dy**2)) < PAD_RADIUS + 2*BALL_RADIUS:
      reward += 1#Increase reward if almost touching

  frames += 1

  if render:
    draw()
    clock.tick(TARGET_FPS)

  world.Step(TIME_STEP, 10, 10)

  return [get_state(), reward, -1] if learn else True

if __name__ == "__main__":
  init_game(number_of_balls=int(sys.argv[1]))
  human_play()
