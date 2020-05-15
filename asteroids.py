# implementation of Spaceship - program template for RiceRocks
# pvillaflores 2012-12-12
# original codeskulptor link:

import simplegui
import math
import random

# globals for user interface
width = 800
height = 600
score = 0
lives = 3
time = 0
started = False
rock_group = set()
missile_group = set()
explosion_group = set()
state_group = set()

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
# .ogg versions of sounds are also available, just replace .mp3 by .ogg
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    a = []
    a.append( math.sqrt((p[0]-q[0])**2+(p[1]-q[1])**2) )
    # expanding dist to take into account screen wrap-around
    a.append( math.sqrt((p[0]+width-q[0])**2+(p[1]-q[1])**2) )
    a.append( math.sqrt((p[0]-width-q[0])**2+(p[1]-q[1])**2) )
    a.append( math.sqrt((p[0]-q[0])**2+(p[1]+height-q[1])**2) )
    a.append( math.sqrt((p[0]-q[0])**2+(p[1]-height-q[1])**2) )
    a.append( math.sqrt((p[0]+width-q[0])**2+(p[1]+height-q[1])**2) )
    a.append( math.sqrt((p[0]+width-q[0])**2+(p[1]-height-q[1])**2) )
    a.append( math.sqrt((p[0]-width-q[0])**2+(p[1]+height-q[1])**2) )
    a.append( math.sqrt((p[0]-width-q[0])**2+(p[1]-height-q[1])**2) )
    return min(a)

# Ship class
class Ship:

    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0], self.image_center[1]] , self.image_size,
                              self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % width
        self.pos[1] = (self.pos[1] + self.vel[1]) % height

        # update velocity
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * .1
            self.vel[1] += acc[1] * .1
            
        self.vel[0] *= .99
        self.vel[1] *= .99

    def set_thrust(self, on):
        self.thrust = on
        ship_thrust_sound.rewind()
        if on:
            ship_thrust_sound.play()
       
    def increment_angle_vel(self):
        self.angle_vel += .05
        
    def decrement_angle_vel(self):
        self.angle_vel -= .05
        
    def shoot(self):
        forward = angle_to_vector(self.angle)
        missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
        missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
        a_missile = Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)       
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.set_volume(1)
            sound.play()
   
    def draw(self, canvas, scale):
        i = 0
        if self.animated:
            i = self.age
        canvas.draw_image(self.image, [self.image_center[0]+i*self.image_size[0], self.image_center[1]], self.image_size,
                          self.pos, [self.image_size[0]*scale, self.image_size[1]*scale], self.angle)

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % width
        self.pos[1] = (self.pos[1] + self.vel[1]) % height

        self.age += 1
        return self.age > self.lifespan

    def collide(self, other_object):
        return dist(self.pos, other_object.pos) < self.radius + other_object.radius
            
# key handlers to control ship   
def keydown(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(True)
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot()
        
def keyup(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(False)

def init_state_group():
    global state_group
    state_group = set()
    state_group.add(Sprite([145,110], [0,0], 1.5*math.pi, 0, ship_image, ship_info))
    state_group.add(Sprite([100,110], [0,0], 1.5*math.pi, 0, ship_image, ship_info))
    state_group.add(Sprite([55,110], [0,0], 1.5*math.pi, 0, ship_image, ship_info))

# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, lives, score, my_ship
    center = [width / 2, height / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        lives = 3
        score = 0
        my_ship = Ship([width / 2, height / 2], [0, 0], 0, ship_image, ship_info)
        init_state_group()

def group_collide(group, other_object):
    count = 0
    for a in list(group):
        if a.collide(other_object):
            count += 1
            x = Sprite(a.pos, [0,0], 0, 0, explosion_image, explosion_info, explosion_sound)
            explosion_group.add(x)
            group.remove(a)
    return count

def group_group_collide(group, other_group):
    count = 0
    for a in list(group):
        b = group_collide(other_group, a)
        if b > 0:
            count += b
            group.remove(a)
    return count

def process_sprite_group(canvas, sprite_group, scale):
    for a in list(sprite_group):
        a.draw(canvas, scale)
        if a.update():
            sprite_group.remove(a)

def draw(canvas):
    global time, started, lives, score, rock_group
    
    # animiate background
    time += 1
    center = debris_info.get_center()
    size = debris_info.get_size()
    wtime = (time / 8) % center[0]
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [width/2, height/2], [width, height])
    canvas.draw_image(debris_image, [center[0]-wtime, center[1]], [size[0]-2*wtime, size[1]], 
                                [width/2+1.25*wtime, height/2], [width-2.5*wtime, height])
    canvas.draw_image(debris_image, [size[0]-wtime, center[1]], [2*wtime, size[1]], 
                                [1.25*wtime, height/2], [2.5*wtime, height])

    # draw UI
    canvas.draw_text("Lives", [50, 50], 22, "White")
    canvas.draw_text("Score", [680, 50], 22, "White")
    canvas.draw_text(str(lives), [50, 80], 22, "White")
    canvas.draw_text(str(score), [680, 80], 22, "White")

    # draw ship and sprites
    my_ship.draw(canvas)
    process_sprite_group(canvas, rock_group, 1)
    process_sprite_group(canvas, missile_group, 1)
    process_sprite_group(canvas, explosion_group, 1)
    process_sprite_group(canvas, state_group, .5)
    
    # update ship
    my_ship.update()
    score += group_group_collide(rock_group, missile_group)
    if group_collide(rock_group, my_ship) > 0:
        lives -= 1
        x = Sprite(my_ship.pos, [0,0], 0, 0, explosion_image, explosion_info, explosion_sound)
        explosion_group.add(x)
        for i in list(state_group):
            if i.image == ship_image:
                state_group.remove(i)
                x = Sprite(i.pos, [0,0], 0, 0, explosion_image, explosion_info, explosion_sound)
                state_group.add(x)
                break
        rock_group = set()
        
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [width/2, height/2], 
                          splash_info.get_size())

    if lives < 1:
        started = False
        rock_group = set()

# timer handler that spawns a rock    
def rock_spawner():
    bad_rock = True
    if len(rock_group) > 11 or not started:
        return
    rock_vel = [random.random() * .6 - .3, random.random() * .6 - .3]
    rock_avel = random.random() * .2 - .1
    while bad_rock:
        rock_pos = [random.randrange(0, width), random.randrange(0, height)]
        if dist(rock_pos, my_ship.pos) > 150:
            bad_rock = False
    rock_vel[0] *= (score // 10) + 1
    rock_vel[1] *= (score // 10) + 1
    a_rock = Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image, asteroid_info)
    rock_group.add(a_rock)
    
# initialize stuff
frame = simplegui.create_frame("Asteroids", width, height)

# initialize ship and two sprites
my_ship = Ship([width / 2, height / 2], [0, 0], 0, ship_image, ship_info)
ship_thrust_sound.set_volume(1)
explosion_sound.set_volume(1)
init_state_group()

# register handlers
frame.set_keyup_handler(keyup)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(click)
frame.set_draw_handler(draw)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
