import pygame

import math

# colors used in the display
red = pygame.Color(158, 27, 50)
white = pygame.Color(255, 255, 255)
gray = pygame.Color(130, 138, 143)
black = pygame.Color(10, 0, 2)

# text and fonts used in the display
futura50 = pygame.font.Font("futura medium condensed bt.ttf", 50)
futura30 = pygame.font.Font("futura medium condensed bt.ttf", 30)

# images used in the display
speedometer = pygame.image.load('Speedometer.png').convert_alpha()
speedometer = pygame.transform.scale(speedometer, (350, 350))
tachometer = pygame.image.load('Tachometer.png').convert_alpha()
tachometer = pygame.transform.scale(tachometer, (350, 350))
needle = pygame.image.load('Needle.png').convert_alpha()
needle = pygame.transform.scale(needle, (181, 28))

# initialize pygame
pygame.init()

# dimensions of onscreen display
(width, height) = (1024, 600)

# sets up the display
screen = pygame.display.set_mode((width, height))
pygame.display.flip()

def draw_meter(x, y, theta, value):
    # variables
    l = 350  # x length of image
    h = 350  # y length of image
    cx = x + 176  # x coordinate of center of speedometer
    cy = y + 191  # y coordinate of center of speedometer

    # draw speedometer to the screen
    pygame.draw.ellipse(screen, (0, 0, 0), (x, y, l, h))
    screen.blit(speedometer, (x, y))

    draw_needle(cx, cy, theta)
    label = futura50.render(value, 1, gray)

    if value < 10:
        screen.blit(label, (108 + 154, 390))
    else:
        screen.blit(label, (108 + 143, 390))


def draw_needle(x, y, theta):
    """Draws a needle at a particular x, y coordinate and angle
    Angle is measured in degrees, and 0 deg is pointing right
    needle image dimensions: 181 x 28
    center of needle (pivot point): 152, 14"""

    theta += 180
    theta = theta % 360
    
    rotated_needle = pygame.transform.rotate(needle, theta)
    
    theta = theta * math.pi/180

    l = 181  # x length of image
    h = 28  # y length of image
    x0 = 152  # x distance to pivot point
    y0 = 14  # y distance to pivot point

    # adjusts the position of the needle to be correct after the rotation
    dx = 0
    dy = 0

    if 1.5*math.pi <= theta <= 2*math.pi:
        dx = -y0 * math.sin(theta) + x0 * math.cos(theta)
        dy = -x0 * math.sin(theta) + y0 * math.cos(theta)
    elif 0 <= theta <= 0.5*math.pi:
        dx = y0 * math.sin(theta) + x0 * math.cos(theta)
        dy = (l - x0) * math.sin(theta) + y0 * math.cos(theta)
    elif 0.5*math.pi <= theta <= math.pi:
        dx = y0 * math.sin(theta) - (l - x0) * math.cos(theta)
        dy = (l - x0) * math.sin(theta) - y0 * math.cos(theta)
    elif math.pi <= theta <= 1.5*math.pi:
        dx = -y0 * math.sin(theta) - (l - x0) * math.cos(theta)
        dy = -x0 * math.sin(theta) - y0 * math.cos(theta)

    x = x - dx
    y = y - dy

    # draws the needle to the screen
    screen.blit(rotated_needle, (x, y))