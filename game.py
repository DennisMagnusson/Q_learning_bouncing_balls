from __future__ import print_function

import pygame
from pygame.locals import *
from random import random

import Box2D
import Box2D.b2 as b2d

#Deifnin' some sweet constants
PPM = 100.0 #Pixels per meter.
TARGET_FPS = 60
TIME_STEP = 1.0 / TARGET_FPS
WIDTH, HEIGHT = 640, 480
GRAVITY = 9.81

VELOCITY = 1500 / PPM

BALL_RADIUS = 0.15
PAD_RADIUS = 5

NUMBER_OF_BALLS = 2

frames = 0

pygame.init()
font = pygame.font.SysFont("monospace", 15)

screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)#I have no idea what this does
pygame.display.set_caption("SuperKoolt spel")
clock = pygame.time.Clock()

world = b2d.world(gravity=(0, -GRAVITY), doSleep=True)

world.CreateStaticBody(position=(0, 0), shapes=b2d.polygonShape(box=(0.01, 100)))#Left wall
world.CreateStaticBody(position=(float(WIDTH/PPM), 0), shapes=b2d.polygonShape(box=(0.01, 100))) #Right wall
world.CreateStaticBody(position=(0, float(HEIGHT/PPM)), shapes=b2d.polygonShape(box=(100, 0.01)))#Roof

pad_body = world.CreateKinematicBody(position=(WIDTH/(PPM*2), 0.3 - PAD_RADIUS), 
                                     shapes=b2d.circleShape(radius=PAD_RADIUS))
pad_body.mass = 10000
pad_body.fixedRotation = True

pygame.key.set_repeat(1000/TARGET_FPS, 1000/TARGET_FPS)

balls = []
for i in range(NUMBER_OF_BALLS):
  balls.append(world.CreateDynamicBody(position=(WIDTH/(PPM*2) - 1 + 2*random(), HEIGHT/(PPM*1.1))))
  balls[i].CreateCircleFixture(radius=BALL_RADIUS, restitution=0.9)

def draw():
  for ball in balls:
    draw_circle(ball, BALL_RADIUS)
  draw_circle(pad_body, PAD_RADIUS)

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
  pad_body.linearVelocity = (-VELOCITY, 0)

def move_right():
  pad_body.linearVelocity = (VELOCITY, 0)

def do_nothing():
  pad_body.linearVelocity = (0, 0)

def tick(render=True, learn=False):
  global frames
  for ball in balls:
    if ball.position[1] < -BALL_RADIUS:
      return False

    frames += 1

    if render:
      screen.fill((0, 0, 0, 255))
      draw()
      screen.blit(font.render(str(frames/60), 1, (255, 255, 255)), (0, 0))
      pygame.display.flip()

    world.Step(TIME_STEP, 10, 10)

    clock.tick(TARGET_FPS)

    return True

def human_play(render=True, inp=True):
  while tick(render=True):#Totally makes sense
    get_input()

  pygame.quit()
  print("SCORE: ", frames/60)

def get_input():
  pad_body.linearVelocity = (0, 0)
  for event in pygame.event.get():
    if event.type == KEYDOWN:
      if event.key == K_a:
        pad_body.linearVelocity = (-VELOCITY, 0)
      elif event.key == K_d:
        pad_body.linearVelocity = (VELOCITY, 0)


if __name__ == "__main__":
  human_play()
