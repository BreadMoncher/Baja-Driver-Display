# Aidan Cantu
# Baja Display
# Main.py
# This program creates a dashboard with a speedometer and tachometer

import pygame
import math
import datetime
from datetime import timedelta
import time
import RPi.GPIO as GPIO

# initialize GPIO
GPIO.setmode(GPIO.BOARD)

# Yellow Wire
GPIO.setup(7, GPIO.OUT)

# Blue Wire
SPEED_SENSOR = 13
GPIO.setup(SPEED_SENSOR, GPIO.IN)

# initialize pygame
pygame.init()

# dimensions of onscreen display
(width, height) = (1024, 600)

# sets up the display
screen = pygame.display.set_mode((width, height))
pygame.display.flip()

# settings for system
SIUnits = False
darkMode = False

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



# variables
speedMPH = 0  # speed in Miles per Hour
RPM = 0  # Rotations per Minute for the engine
date_and_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Current date and time
start_time = time.time()  # Time that stopwatch began
watch_running = False
time_lapsed = 0  # Time elapsed on the stopwatch

# lists a time (in seconds) and the sensor input
speed_data_points = [(time.time(),0) for x in range(2000)]
speed_moving_average = [(time.time(),0) for x in range(2000)]
speed_time_list = []

speed_data_file_name = date_and_time + '_speed_data' #name of file containing speed data
rpm_data_file_name = date_and_time + '_rpm_data' #name of file containing rpm data


# method for drawing the speedometer
# speedometer image dimensions are 350 x 350
# speedometer is centered at 458, 475
def draw_speedometer(x, y):
    """Draws a speedometer with a needle at a particular x, y coordinate
    speedometer image dimensions: 350, 350
    center of speedometer (where the needle goes): 176, 191
    speedometer location: 108, 125"""

    # variables
    l = 350  # x length of image
    h = 350  # y length of image
    cx = x + 176  # x coordinate of center of speedometer
    cy = y + 191  # y coordinate of center of speedometer

    # draw speedometer to the screen
    pygame.draw.ellipse(screen, (0, 0, 0), (x, y, l, h))
    screen.blit(speedometer, (x, y))

    # calculate angle for needle, and draw to screen
    theta = 216 - (speedMPH * 18) // 5
    draw_needle(cx, cy, theta)

    # draw speed in MPH to bottom of speedometer
    text = f"{speedMPH:.1f}"
    label = futura50.render(text, 1, gray)
    if speedMPH < 10:
        screen.blit(label, (108 + 154, 390))
    else:
        screen.blit(label, (108 + 143, 390))


def draw_tachometer(x, y):
    """Draws a tachometer with a needle at a particular x, y coordinate
    tachometer image dimensions: 350, 350
    center of tachometer (where the needle goes): 176, 191
    tachometer location: 568, 125"""

    # variables
    l = 350  # x length of image
    h = 350  # y length of image
    cx = x + 176  # x coordinate of center of speedometer
    cy = y + 191  # y coordinate of center of speedometer

    # draw speedometer to the screen
    pygame.draw.ellipse(screen, ((0 * 7) / 500, 0, 0), (x, y, l, h))
    screen.blit(tachometer, (x, y))

    # calculate angle for needle, and draw to screen
    theta = 216 - (RPM * 63) // 1250
    draw_needle(cx, cy, theta)

    # draw speed in MPH to bottom of speedometer
    text = f"{RPM:04d}"
    label = futura50.render(text, 1, gray)
    screen.blit(label, (568 + 138, 390))


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

def update_speed_data():
    '''updates the list of speed data points
    each data point is a tuple with a timestamp and a 0/1 value
    
    the hall effect sensor sends a square wave digital input
    1 meaning that the sensor is aligned with the magnet, 0 otherwise
    
    the first entry in the speed_data_point list is the most recent
    the last one is deleted'''
    global speed_data_points, speed_moving_average, speed_time_list
    
    speed_data_points.pop()
    
    n = (time.time(),not GPIO.input(SPEED_SENSOR))
    speed_data_points.insert(0, n)
    
    '''we take an average of the k most recent speed data points
    by integrating w/ trapezoids, and then dividing by change in time
    we call this the moving average'''
    area = 0
    total_time = 0
    k = 2
    for i in range(0,k-1):
        n = speed_data_points[i][1] + speed_data_points[i+1][1]
        t = speed_data_points[i+1][0] - speed_data_points[i][0]
        area += 0.5*n*t
        total_time += t
     
    '''this moving average is made into another data point and
    added to the front of the list speed_moving_average'''
    speed_moving_average.pop()
    n = (speed_data_points[k][0], area/total_time)
    speed_moving_average = [n] + speed_moving_average
    
    '''now we determine if the moving average increased
    above the threshold value. If it did, it indicates
    that there is likely a rising edge signal from the
    sensor. This point in time is added to timelist'''
    
    sample = 10
    threshold = 0.7
    if speed_moving_average[0][1] > threshold:
        if speed_moving_average[1][1] <= threshold:
            speed_time_list.insert(0, speed_moving_average[0][0])
    while len(speed_time_list) > sample:
        speed_time_list.pop()
    for i in range(len(speed_time_list)):
        if time.time() - speed_time_list[i]> 3:
            speed_time_list = speed_time_list[:i]
            break
        

def get_speed():
    '''uses the speed_time_list to calculate the current speed
    of the vehicle.
    
    these times correspond to the most likely places where the axel
    completed 1 rotation'''
    
    distance_per_turn = 1
    rps = 0
    
    '''we then find the difference between these times, and take
    their average, to get the average time it takes to complete
    1 axel rotation'''
    
    
    '''If there are less than two datapoints in the sample range
    then we assume that the car is not moving'''
    if len(speed_time_list)<=2:
        rps = 0
    elif time.time()-speed_time_list[0] > 2:
        rps = 0
    else:
        average_time = 0
        for i in range(len(speed_time_list)-1):
            average_time += speed_time_list[i]-speed_time_list[i+1]
            
        average_time = average_time / (len(speed_time_list)-1)
        rps = 1/average_time
    speed = rps*10
    
    save_to_file(speed_data_file_name, speed_time_list[0])
    
    return speed

def save_to_file(file_name, time, data_point):
    df = pd.DataFrame(columns = ['time','data'])
    a = {'time': time, 'data': data_point}
    df = df.append(a, ignore_index = True)
    df.to_csv(file_name, mode = 'a')
    

def get_rpm():
    return 2190


def get_stopwatch_format():
    global watch_running, time_lapsed, start_time
    if watch_running:
        time_lapsed = time.time() - start_time
    text = str(timedelta(seconds=time_lapsed))
    text = text[:-4]
    return text


def start_stopwatch():
    global watch_running, start_time
    watch_running = True
    start_time = time.time()


def stop_stopwatch():
    global watch_running
    watch_running = False

def render():
    """renders the display at 20fps"""
    
    # draw the screen background
    
    if darkMode:
        screen.fill(black)
    else:
        screen.fill(white)
        
    # draw speedometer and tachometer (dimensions = 350x350)
    draw_speedometer(108, 125)
    draw_tachometer(568, 125)
    
    # draw clock
    label = futura50.render(date_and_time, 1, gray)
    screen.blit(label, (15, 10))

    # draw stopwatch
    label = futura50.render(get_stopwatch_format(), 1, gray)
    screen.blit(label, (830, 10))
    
    # update display
    pygame.display.update()

# loop (when this loop stops, the program closes)
running = True
start_stopwatch()
current_time = 0
time_at_frame = time.time()
seconds_per_frame = 1/20

t = 0

while running:
    
    
    t += 1
    if t%100==0:
        print(t)
    
    
    # update variables
    speedMPH = get_speed()
    RPM = get_rpm()
    date_and_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # update data
    update_speed_data()
    #fast_update_speed_data()
    
    # determine if frame needs to be rendered
    current_time = time.time()
    if current_time - time_at_frame >= seconds_per_frame:
        render()
        time_at_frame = time.time()

    # handler for pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            GPIO.cleanup()
    
