import pyo
import pygame
s = pyo.Server().boot().start()
wrong_button = pyo.SfPlayer("Sounds/wrong_hit.wav")
pygame.init()
for event in pygame.event.get():
    if pygame.joystick.get_count != 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    if event.type == pygame.JOYBUTTONDOWN:
        wrong_button.out()
