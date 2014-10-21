"""
Space Invaders-style game for auditory category learning task
Designed by Josh Oberman at Howard Nusbaum Lab, University of Chicago, February-March 2014
"""
from os import listdir, mkdir, path
import pygame
import random
from psychopy import core
import xlsxwriter
import pyo
from itertools import izip_longest
import egi.threaded as egi

#--- Global constants ---
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
BLUE     = (    0,  100,  255)
YELLOW   = (  255, 255,  0)
BROWN = (103, 50, 0)
GREY = (160,160, 160)

 
SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 750

"""ns = egi.NetStation()
address = '10.10.10.2'
port = 55513"""

"""get the subject number, check if data already exists and prompt experimenter"""
SUBJECT = raw_input("Subject Number: ")
def checkData(SUBJECT):
    if path.exists("Subject %s"%SUBJECT):
        answer = raw_input("Data already exists for Subject %s, would you like to erase the data and continue? Y/N: "%SUBJECT)
        if answer == "N":
            SUBJECT = raw_input ("Subject Number:")
            checkData(SUBJECT)
        elif answer == "Y":
            pass
        else:
            checkData(SUBJECT)
checkData(SUBJECT)

# --- Classes ---
 
class Enemy(pygame.sprite.Sprite):
    """ This class represents the enemies """
    f_notes = listdir("Notes/F#")
    f_notes = ["Notes/F#/{0}".format(i) for i in f_notes if not i.startswith('.')]#format so they can be read in to pyo sound tables, don't read hidden proprietary files
    a_notes = listdir("Notes/A")
    a_notes = ["Notes/A/{0}".format(i) for i in a_notes if not i.startswith('.')]
    c_notes = listdir("Notes/C")
    c_notes = ["Notes/C/{0}".format(i) for i in c_notes if not i.startswith('.')]
    d_notes = listdir("Notes/D#")
    d_notes = ["Notes/D#/{0}".format(i) for i in d_notes if not i.startswith('.')]
    enemies = listdir("Images/Enemies")
    enemies = ["Images/Enemies/{0}".format(i) for i in enemies if not i.startswith('.')]
    x_speed = 1
    y_speed = 1
    #prob = 0.6
    offscreen_min = 4 #min of generation of enemy/sound stimulus onset offscreen in seconds
    offscreen_max = 6 #max of generation of enemy/sound stimulus onset offscreen in seconds
    enemyA_sight_time = []
    enemyB_sight_time = []
    enemyC_sight_time = []
    enemyD_sight_time = []
    enemyA_generate_time = []
    enemyB_generate_time = []
    enemyC_generate_time = []
    enemyD_generate_time = []
    lag = 0.5
    def get_range(pos):
        return range(pos, pos+32, 1)
    a_pos = 10        
    a_range = get_range(a_pos)
    b_pos = SCREEN_WIDTH//3
    b_range = get_range(b_pos)
    c_pos = 2*(SCREEN_WIDTH//3)
    c_range = get_range(c_pos)
    d_pos = SCREEN_WIDTH - 42
    d_range = get_range(d_pos)
    #sound = pygame.mixer.Sound("Users/joshuaoberman/documents/speaker.wav")
    def __init__(self, enemy_type):
        """ Constructor, create the image of the enemy/sound for enemy. Selected from three enemy types """
        pygame.sprite.Sprite.__init__(self)
        self.enemy_type = enemy_type
        #self.env = pyo.Fader(fadein=.01,fadeout=.2, dur=0) #amplitude envelope to get rid of pops
        self.pop = pyo.SfPlayer("Sounds/kill.wav")#for when enemy dies
        if self.enemy_type == 'A':
            self.c_notes = [pyo.SndTable(c) for c in self.c_notes]
            snd = random.choice(self.c_notes)
            freq = snd.getRate()
            self.sound = pyo.TableRead(snd, freq=freq, loop=True, mul=1)
            #the following function lets us switch between .wav files each time through the loop
            def switch():
                snd = random.choice(self.c_notes)
                freq = snd.getRate()
                self.sound.setTable(snd)
                self.sound.setFreq(freq)
            self.trig = pyo.TrigFunc(self.sound['trig'],switch)
            self.image = pygame.image.load(self.enemies[0])
        elif self.enemy_type == 'B':
            self.f_notes = [pyo.SndTable(f) for f in self.f_notes]
            snd = random.choice(self.f_notes)
            freq = snd.getRate()
            self.sound = pyo.TableRead(snd, freq=freq, loop=True, mul=1)
            def switch():
                snd = random.choice(self.f_notes)
                freq = snd.getRate()
                self.sound.setTable(snd)
                self.sound.setFreq(freq)
            self.trig = pyo.TrigFunc(self.sound['trig'],switch)     
            self.image = pygame.image.load(self.enemies[1])
        elif self.enemy_type == 'C':
            self.a_notes = [pyo.SndTable(a) for a in self.a_notes]
            snd = random.choice(self.a_notes)
            freq = snd.getRate()
            self.sound = pyo.TableRead(snd, freq=freq, loop=True, mul=1)
            def switch():
                snd = random.choice(self.a_notes)
                freq = snd.getRate()
                self.sound.setTable(snd)
                self.sound.setFreq(freq)
            self.trig = pyo.TrigFunc(self.sound['trig'],switch)
            self.image = pygame.image.load(self.enemies[2])
        elif self.enemy_type == 'D':
            self.d_notes = [pyo.SndTable(d) for d in self.d_notes]
            snd = random.choice(self.d_notes)
            freq = snd.getRate()
            self.sound = pyo.TableRead(snd, freq=freq, loop=True, mul=1)
            def switch():
                snd = random.choice(self.d_notes)
                freq = snd.getRate()
                self.sound.setTable(snd)
                self.sound.setFreq(freq)
            self.trig = pyo.TrigFunc(self.sound['trig'],switch)
            self.image = pygame.image.load(self.enemies[3])
            
        self.image = pygame.transform.scale(self.image, (32,32))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
    def generate(self):
        """ generate the enemy off screen """
        #distance for offset = desired time * velocity
        #ns.sync()
        self.offset_time = 60*random.randrange(self.offscreen_min, self.offscreen_max) #multiply by 60 for fps-->s
        self.offset_distance = -(self.offset_time * self.y_speed)
        self.rect.y = self.offset_distance
        if self.enemy_type == 'A':
            self.sound.out()
            #ns.send_event('SndA', timestamp = egi.ms_localtime())
            self.rect.x = self.a_pos
            time = core.getTime()
            self.enemyA_generate_time.append(time)
        elif self.enemy_type == 'B':
            self.sound.out()
            #ns.send_event('SndB', timestamp = egi.ms_localtime())
            self.rect.x = self.b_pos
            time = core.getTime()
            self.enemyB_generate_time.append(time)
        elif self.enemy_type == 'C':
            self.sound.out()
            #ns.send_event('SndC', timestamp = egi.ms_localtime())
            self.rect.x = self.c_pos
            time = core.getTime()
            self.enemyC_generate_time.append(time)
        elif self.enemy_type == 'D':
            self.sound.out()
            #ns.send_event('SndC', timestamp = egi.ms_localtime())
            self.rect.x = self.d_pos
            time = core.getTime()
            self.enemyD_generate_time.append(time)
    
    def wrong_hit(self):
        """play a sound, decrease score when wrong bullet hits enemy"""
        self.miss = pyo.SfPlayer("Sounds/beep.wav", loop=False).mix(2)
        self.miss.out()
    
    def update(self):
        """ Automatically called when we need to move the enemy. """
        self.rect.y += self.y_speed
        #self.rect.x += self.x_speed
        #bounce off edges
        #if self.rect.x > SCREEN_WIDTH - self.rect.width or self.rect.x <= 0:
        #    self.x_speed = -self.x_speed
        #change x direction based on probability function
        #self.random = random.random
        #if self.random < self.prob:
        #    self.x_speed = -self.x_speed
        """ Record time right when enemy fully enters screen """
        if -1<= self.rect.y <= 0:
            t_sight = core.getTime()
            #ns.send_event('Site', timestamp = egi.ms_localtime())
            if self.enemy_type=='A':
                #ns.send_event('Site', timestamp = egi.ms_localtime())
                t_sight = core.getTime()
                self.enemyA_sight_time.append(t_sight)
            if self.enemy_type =='B':
                #ns.send_event('Site', timestamp = egi.ms_localtime())
                t_sight = core.getTime()
                self.enemyB_sight_time.append(t_sight)
            if self.enemy_type=='C':
                #ns.send_event('Site', timestamp = egi.ms_localtime())
                t_sight = core.getTime()
                self.enemyC_sight_time.append(t_sight)
            if self.enemy_type=='D':
                #ns.send_event('Site', timestamp = egi.ms_localtime())
                t_sight = core.getTime()
                self.enemyD_sight_time.append(t_sight)
                
 
class Player(pygame.sprite.Sprite):
    """ This class represents the player. """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.Surface([35, 5])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH/2 #put in middle of screen
        self.rect.y = SCREEN_HEIGHT - self.rect.height - 2
        #measurement of firing locus of bullet from player, can be used to determine when player position is in succesful firing range
 
    def update(self):
        """ Update the player location. """
        return self.rect.x

class Bullet(pygame.sprite.Sprite):
    """ Bullets, three kinds of colors defined in game logic """
    bullet_speed = 10
    def __init__(self, color):
        pygame.sprite.Sprite.__init__(self)                  
        self.image = pygame.Surface([5, 15])
        self.image.fill(color)
        self.rect = self.image.get_rect()
    def update(self):
        self.rect.y -= self.bullet_speed
        
class Target(pygame.sprite.Sprite):
    def __init__(self, color, size, x_pos):
            """show target for enemies B and C"""
            pygame.sprite.Sprite.__init__(self)
            font = pygame.font.Font(None, size)
            self.image = font.render("+", True, color)
            self.rect = ([x_pos, SCREEN_HEIGHT-80])

class Level(object):
    currentLevel = 1
    level_success = None
    ammo = None
    def __init__(self):
        self.live_list = []
        self.kill_list = []
        self.enemies_list = ['A','A','A','A','B','B','B','B','C','C','C','C','D','D','D','D']
        random.shuffle(self.enemies_list)
        if self.currentLevel==1 or self.currentLevel==2:
            self.ammo = 60
        elif self.currentLevel==3 or self.currentLevel==4:
            self.ammo = 50
        elif self.currentLevel==5:
            self.ammo = 40
        elif self.currentLevel==6:
            self.ammo = 35
            Enemy.y_speed = 4
            Game.stick_sensitvity = 6
        elif self.currentLevel==7 or self.currentLevel==8 or self.currentLevel==9:
            self.ammo = 30
        elif self.currentLevel==9 or self.currentLevel==10 or self.currentLevel==11 or self.currentLevel==12:
            self.ammo = 22
        
    def check_success(self):
        if len(self.kill_list)<=10:
            self.level_success = False #failed the level
        else:
            self.level_success = True
            self.increase_level()
    
    def increase_level(self):
        self.currentLevel+=1
        Enemy.y_speed += 1.8
        Bullet.bullet_speed += 1.5
        Game.stick_sensitivity += 1
        Enemy.lag-=.05
        
    
    def load_level(self):
        self.__init__()
        
class Stars(pygame.sprite.Sprite):
    def __init__(self, size):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(None, size)
        self.image = self.font.render("*", True, WHITE)
        self.rect = self.image.get_rect()
    def update(self, speed):
        self.rect.y+=speed
        if self.rect.y>SCREEN_HEIGHT:
            self.rect.y = -5
            self.rect.x = random.randrange(SCREEN_WIDTH)

class Game(object):
    """ This class represents an instance of the game. If we need to
        reset the game we'd just need to create a new instance of this
        class. """
 
    # --- Class attributes. 
     
    # Sprite lists
    enemyA_list = None
    enemyB_list = None
    enemyC_list = None
    enemyD_list = None
    A_bullet_list = None
    B_bullet_list = None
    C_bullet_list = None
    D_bullet_list = None
    all_sprites_list = None
    player = None
    dead_enemies = None
    small_star_list = None
    large_star_list = None
    #Time measurements
    Ashot_time = []
    Bshot_time = []
    Cshot_time = []
    Dshot_time = []
    enemyA_kill_time = []
    enemyB_kill_time = []
    enemyC_kill_time = []
    enemyD_kill_time = []
    # Other data
    levels = []
    score = 0
    maxTrials = 12 #maximum number of levels to play through
    enemy_live = False #bool to tell us if there is a live enemy
    elapsedTime = 0.0 #keep track of elapsed time via frame rate changes
    enemySpawnTime= 120.0 # of frames between enemy death and next enemy spawn
    stick_sensitivity = 6 #sensitivity of joystick for player motion, represents max number of
    #pixels per frame the player moves when stick is moved all the way to left or right
    trajectory = []
    trial = 0
    #bools for adding/removing target
    is_b_target = False
    is_c_target = False
     
    # --- Class methods
    # Set up the game
    def __init__(self):
        self.score = 0
        self.game_over = False
        self.game_start = True
        self.level_over = False
         
        # Create sprite lists
        self.enemyA_list = pygame.sprite.Group()
        self.enemyB_list = pygame.sprite.Group()
        self.enemyC_list = pygame.sprite.Group()
        self.enemyD_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()
        self.A_bullet_list = pygame.sprite.Group()
        self.B_bullet_list = pygame.sprite.Group()
        self.C_bullet_list = pygame.sprite.Group()
        self.D_bullet_list = pygame.sprite.Group()
        self.dead_enemies = pygame.sprite.Group()
        self.small_star_list = pygame.sprite.Group()
        self.large_star_list = pygame.sprite.Group()
         
         
        # Create the player
        self.player = Player()
        self.all_sprites_list.add(self.player)
        self.x_speed = 0
        self.level = Level()
        #shot sound
        self.shot_sound = pyo.SfPlayer("Sounds/laser_shot.aif", mul=0.4)
        #wrong button sound
        self.wrong_button = pyo.SfPlayer("Sounds/wrong_hit.wav")
        self.controller = True #Is controller plugged in-->defaults to yes
        try:
            pygame.joystick.Joystick(0)
        except:
            print "NO CONTROLLER PLUGGED IN"
            self.controller = False
        """set stars in motion"""
        for i in range(50):
            star = Stars(25)
            star.rect.x = random.randrange(SCREEN_WIDTH-star.rect.x)
            star.rect.y = random.randrange(SCREEN_HEIGHT-10)
            self.small_star_list.add(star)
        for i in range (25):
            star = Stars(40)
            star.rect.x = random.randrange(SCREEN_WIDTH-star.rect.x)
            star.rect.y = random.randrange(SCREEN_HEIGHT-10)
            self.large_star_list.add(star)
 
    def process_events(self):
        """ Process all of the events. Return a "True" if we need
            to close the window. """
        #define middle of player
        self.player.middle = self.player.rect.x + (self.player.rect.width//2)  
        def shoot(bullet_type, color):
            self.bullet = Bullet(color)
            self.bullet.color = str(color)
            # Set the bullet so it shoots from middle of player
            self.bullet.rect.x = self.player.middle
            self.bullet.rect.y = self.player.rect.y
            #play bullet sound
            self.shot_sound.out()
            #decrease ammo supply by 1
            self.level.ammo-=1
            # Add the bullet to the lists
            self.all_sprites_list.add(self.bullet)
            if color == GREEN:
                shot = core.getTime()
                self.Ashot_time.append(shot)
                self.A_bullet_list.add(self.bullet)
            elif color == RED:
                shot = core.getTime()
                self.Bshot_time.append(shot)
                self.B_bullet_list.add(self.bullet)
            elif color == YELLOW:
                shot = core.getTime()
                self.Cshot_time.append(shot)
                self.C_bullet_list.add(self.bullet)
            elif color == BROWN:
                shot = core.getTime()
                self.Dshot_time.append(shot)
                self.D_bullet_list.add(self.bullet)
         
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                return True
            if self.controller:
                joystick = pygame.joystick.Joystick(0)
                joystick.init()
                horiz_pos = joystick.get_axis(0)
                if -0.1<horiz_pos<0.1:
                    horiz_pos = 0
                self.x_speed = horiz_pos * self.stick_sensitivity
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.level.ammo>0:
                        if (self.level.currentLevel==1 or self.level.currentLevel==2 or self.level.currentLevel==3 or self.level.currentLevel==4 or self.level.currentLevel==5):
                            if event.button==0:
                                shoot('A', GREEN)
                            elif event.button == 1:
                                shoot('B', RED)
                            elif event.button == 2:
                                shoot('C', YELLOW)
                            elif event.button == 3:
                                shoot('D', BROWN)
                        elif (self.level.currentLevel==6 or self.level.currentLevel==7 or self.level.currentLevel==8 or
                              self.level.currentLevel==9 or self.level.currentLevel==10 or self.level.currentLevel==11 or self.level.currentLevel==12):
                            if event.button == 0:
                                if joystick.get_button(4)==1 and joystick.get_button(5) == 0 and joystick.get_button(6)==0: #set up mod and exclude others to prevent cheating
                                    shoot('A', GREEN)
                                else:
                                    #play wrong button sound
                                    self.wrong_button.out()
                            elif event.button == 1:
                                if joystick.get_button(5)==1 and joystick.get_button(4) == 0 and joystick.get_button(6)==0 and joystick.get_button(7)==0:
                                    shoot('B',RED)
                                else:
                                    self.wrong_button.out()
                            elif event.button == 2:
                                if joystick.get_button(6)==1 and joystick.get_button(5) == 0 and joystick.get_button(7)==0 and joystick.get_button(4)==0:
                                    shoot('C', YELLOW)
                                else:
                                    self.wrong_button.out()
                            elif event.button == 3:
                                if joystick.get_button(7) ==1 and joystick.get_button(5) ==0 and joystick.get_button(4) == 0 and joystick.get_button(6)==0:
                                    shoot('D', BROWN)
                                else:
                                    self.wrong_button.out()
                    if event.button == 8 or event.button == 9:
                        if self.game_start:
                            self.game_start = False
                        if self.level_over:
                            self.level.load_level()
                            self.level_over = False
        return False #for exiting game
 
    def run_logic(self):
        """
        This method is run each time through the frame. It
        updates positions and checks for collisions.
        """
        """define timestamping for when character enters enemy range"""
        def record_player():
            time = core.getTime()
            self.trajectory.append("%d, %f, %s"%(self.player.middle, time, self.enemy.enemy_type))
        def write_trajectory(trial, level):
            """write trial trajectory to text file in level directory, make directory if necessary"""
            directory = "Subject %s/Level %d" % (SUBJECT, level)
            if not path.exists(directory):
                mkdir(directory)
            trajectories = open(directory+"/"+str(trial)+".txt", 'w')
            for item in self.trajectory:
                trajectories.write(str(item)+'\n')
            del self.trajectory[:]
            trajectories.close()

        if not self.level_over and not self.game_start and not self.game_over:
        # Create the enemy sprites
            if not self.enemy_live and self.elapsedTime==self.enemySpawnTime:
                self.enemy_type = self.level.enemies_list.pop()
                self.enemy = Enemy(self.enemy_type)
                self.enemy.generate()
                self.trial+=1
                self.enemy_live = True
                self.all_sprites_list.add(self.enemy)
                if self.enemy_type=='A':
                    self.enemyA_list.add(self.enemy)
                elif self.enemy_type =='B':
                    self.enemyB_list.add(self.enemy)
                elif self.enemy_type=='C':
                    self.enemyC_list.add(self.enemy)
                elif self.enemy_type=='D':
                    self.enemyD_list.add(self.enemy)
                
            if self.enemy_live:
                record_player()
                #when enemy enters screen, decrease score    
                if self.enemy.rect.y>0:
                    self.score -= 1/float(60) # decrease score by 1 for every second that enemy is alive
                #kill enemy if it goes off screen
                if self.enemy.rect.y > SCREEN_HEIGHT + self.enemy.rect.height:
                    self.enemy.sound.stop()
                    self.all_sprites_list.remove(self.enemy)
                    if self.enemy.enemy_type == 'A':
                        self.enemyA_list.remove(self.enemy)
                    if self.enemy.enemy_type == 'B':
                        self.enemyB_list.remove(self.enemy)
                    if self.enemy.enemy_type == 'C':
                        self.enemyC_list.remove(self.enemy)
                    if self.enemy.enemy_type == 'D':
                        self.enemyD_list.remove(self.enemy)
                    self.dead_enemies.add(self.enemy)
                    self.level.live_list.append(self.enemy.enemy_type)
                    self.elapsedTime = 0
                    self.score -= 20
                    self.enemy_live = False
            def kill_enemy(bullet_color, enemy_type):
                time = core.getTime()
                if enemy_type=='A':
                    self.enemyA_kill_time.append(('Level-'+str(self.level.currentLevel) + ', time-' +str(time)))
                if enemy_type=='B':
                    self.enemyB_kill_time.append(('Level-'+str(self.level.currentLevel) + ', time-' +str(time)))
                if enemy_type=='C':
                    self.enemyC_kill_time.append(('Level-'+str(self.level.currentLevel) + ', time-' +str(time)))
                if enemy_type=='D':
                    self.enemyD_kill_time.append(('Level-'+str(self.level.currentLevel) + ', time-' +str(time)))
                self.enemy.sound.stop()
                self.enemy.pop.out()
                self.score += 10
                self.elapsedTime = 0
                self.level.kill_list.append('Kill')
                self.dead_enemies.add(enemy)
                self.enemy_live = False
                write_trajectory(self.trial, self.level.currentLevel)
                self.all_sprites_list.remove(bullet)
                if bullet_color == 'green':
                    self.A_bullet_list.remove(bullet)
                elif bullet_color == 'red':
                    self.B_bullet_list.remove(bullet)
                elif bullet_color == 'yellow':
                    self.C_bullet_list.remove(bullet)
                elif bullet_color == 'brown':
                    self.D_bullet_list.remove(bullet)
            
            self.player.rect.x += self.x_speed #update speed based on joystick 
            #keep player in boundaries
                
            if self.player.rect.x <= 0:
                self.x_speed = 0
                self.player.rect.x = 0
            elif self.player.rect.x >= SCREEN_WIDTH - self.player.rect.width:
                self.x_speed = 0
                self.player.rect.x = SCREEN_WIDTH-self.player.rect.width
                    
                
            #update stars
            self.small_star_list.update(3)
            self.large_star_list.update(2)
            
            # Move all the sprites
            self.all_sprites_list.update()
            
            #increase time for enemy spawn    
            self.elapsedTime +=1
            
                # Calculate mechanics for each bullet
            for bullet in self.A_bullet_list:
                self.enemy_hit_list = pygame.sprite.spritecollide(bullet, self.enemyA_list, True) #only kill enemy type A
                for enemy in self.enemy_hit_list:
                    kill_enemy('green', 'A')
                if bullet.rect.y < -10:
                    self.A_bullet_list.remove(bullet)
                    self.all_sprites_list.remove(bullet)
                """give audio feedback if wrong sprite shot"""
                if pygame.sprite.spritecollide(bullet, self.enemyB_list, False) or pygame.sprite.spritecollide(bullet, self.enemyC_list, False) or pygame.sprite.spritecollide(bullet,self.enemyD_list, False):
                    self.enemy.wrong_hit()
                    self.score -= float(5)/4
            for bullet in self.B_bullet_list:
                self.enemy_hit_list = pygame.sprite.spritecollide(bullet, self.enemyB_list, True) #only kill enemy type B
                for enemy in self.enemy_hit_list:
                    kill_enemy('red', 'B')
                if bullet.rect.y < -10:
                    self.B_bullet_list.remove(bullet)
                    self.all_sprites_list.remove(bullet)
                """give audio feedback if wrong sprite shot"""
                if pygame.sprite.spritecollide(bullet, self.enemyA_list, False) or pygame.sprite.spritecollide(bullet, self.enemyC_list, False)or pygame.sprite.spritecollide(bullet,self.enemyD_list, False):
                    self.enemy.wrong_hit()
                    self.score -= float(5)/4
            for bullet in self.C_bullet_list:
                self.enemy_hit_list = pygame.sprite.spritecollide(bullet, self.enemyC_list, True) #only kill enemy type C
                for enemy in self.enemy_hit_list:
                    kill_enemy('yellow', 'C')
                if bullet.rect.y < -10:
                    self.C_bullet_list.remove(bullet)
                    self.all_sprites_list.remove(bullet)
                """give audio feedback if wrong sprite shot"""
                if pygame.sprite.spritecollide(bullet, self.enemyA_list, False) or pygame.sprite.spritecollide(bullet, self.enemyB_list, False) or pygame.sprite.spritecollide(bullet,self.enemyD_list, False):
                    self.enemy.wrong_hit()
                    self.score -= float(5)/4
            for bullet in self.D_bullet_list:
                self.enemy_hit_list = pygame.sprite.spritecollide(bullet, self.enemyD_list, True) #only kill enemy type D
                for enemy in self.enemy_hit_list:
                    kill_enemy('brown', 'D')
                if bullet.rect.y < -10:
                    self.D_bullet_list.remove(bullet)
                    self.all_sprites_list.remove(bullet)
                """give audio feedback if wrong sprite shot"""
                if pygame.sprite.spritecollide(bullet, self.enemyA_list, False) or pygame.sprite.spritecollide(bullet, self.enemyB_list, False) or pygame.sprite.spritecollide(bullet,self.enemyC_list,False):
                    self.enemy.wrong_hit()
                    self.score -= float(5)/4   

            """define end of level"""
            if len(self.level.enemies_list)==0 and not self.enemy_live:
                self.levels.append(self.level.currentLevel)
                #check to see if we've completed the max number of trials
                if len(self.levels) == self.maxTrials:
                    self.game_over = True
                else:
                    self.level_over = True
                    self.level.check_success()
                 
    def display_frame(self, screen):
        """ Display everything to the screen for the game. """
         
        def center_text(text):
            center_x = (SCREEN_WIDTH // 2) - (text.get_width() // 2)
            center_y = (SCREEN_HEIGHT // 2) - (text.get_height() // 2)
            screen.blit(text, [center_x, center_y])
        def next_line(text, spacing):
            center_x = (SCREEN_WIDTH // 2) - (text.get_width() // 2)
            center_y = (SCREEN_HEIGHT // 2) - (text.get_height() // 2) + spacing
            screen.blit(text, [center_x,center_y])
        def display_enemies():
            A = pygame.image.load(Enemy.enemies[0])
            A = pygame.transform.scale(A, [32,32])
            A.set_colorkey(WHITE)
            screen.blit(A, [275,440])
            B = pygame.image.load(Enemy.enemies[1])
            B = pygame.transform.scale(B, [32,32])
            B.set_colorkey(WHITE)
            screen.blit(B, [415,440])
            C = pygame.image.load(Enemy.enemies[2])
            C = pygame.transform.scale(C, [32,32])
            C.set_colorkey(WHITE)
            screen.blit(C, [550,440])
            D = pygame.image.load(Enemy.enemies[3])
            D = pygame.transform.scale(D, [32,32])
            D.set_colorkey(WHITE)
            screen.blit(D, [700,440])

        if self.game_over:  
            font = pygame.font.Font(None, 25)
            text = font.render("Game Over, you successfully completed "+ str(self.level.currentLevel) +
                               " levels", True, GREEN)
            center_text(text)
            text2 = font.render("You successfully killed "+ str(len(self.dead_enemies)) +
                                " out of " + str(len(self.dead_enemies)) + " enemies, for a score of {:.0f}".format(self.score),
                                True, GREEN)
            center_x = (SCREEN_WIDTH // 2) - (text2.get_width() // 2)
            center_y = (SCREEN_HEIGHT // 2) + (text2.get_height() // 2) + 2
            screen.blit(text2, [center_x, center_y])

            
        if self.game_start:
            font = pygame.font.Font(None, 25)
            text = font.render("Hello, thank you for participating in this experiment! You will be using the following buttons for the first level:",
                               True, WHITE)
            text2 = font.render("Button 1:            Button 2:            Button 3:            Button 4:", True, WHITE)
            center_text(text)
            next_line(text2, 40)
            display_enemies()
            
        if self.level_over:
            trial = 0
            if not self.level.level_success:
                font = pygame.font.Font(None, 25)
                text = font.render("Level Over, you killed "+ str(len(self.level.kill_list)) +
                                   " out of 16 enemies, you must repeat this level.", True, RED)
                center_text(text)
            if self.level.level_success:
                font = pygame.font.Font(None, 25)
                text = font.render("Level Over, you killed " + str(len(self.level.kill_list)) +
                                   " out of 16 enemies, you will move on to the next level."
                                   , True, GREEN)
                center_text(text)
            if self.level.currentLevel == 5:
                font = pygame.font.Font(None, 25)
                text = font.render("For the next two levels, you must use the following keys for each enemy:", True, GREEN)
                center_x = (SCREEN_WIDTH // 2) - (text.get_width() // 2)
                center_y = (SCREEN_HEIGHT // 2) + (text.get_height() // 2) + 5
                screen.blit(text, [center_x, center_y])
                text2 = font.render("L1 + 1 for:             R1 + 2 for:            L2 + 3 for:         R2 + 4 for:", True, GREEN)
                next_line(text2,40)
                display_enemies()
         
        if not self.game_over and not self.game_start and not self.level_over:
            """draw sprites, print score"""
            self.all_sprites_list.draw(screen)
            self.small_star_list.draw(screen)
            self.large_star_list.draw(screen)
            font = pygame.font.Font(None, 15)
            score = font.render('Score: %s'%"{:,.0f}".format(self.score), True, RED)
            level = font.render('Level: %d'%self.level.currentLevel, True, GREEN)
            ammo = font.render('Ammo: %d'%self.level.ammo, True, YELLOW)
            x_pos = 6
            screen.blit(level, [x_pos, level.get_height()])
            screen.blit(score, [x_pos, level.get_height()+score.get_height()])
            screen.blit(ammo, [x_pos, level.get_height()+score.get_height()+ammo.get_height()])

                
             
        pygame.display.flip()
     
         
def main():
    """make directory for subject if it doesn't already exist"""
    if not path.exists("Subject %s"%SUBJECT):
        mkdir("Subject %s"%SUBJECT)

    """ Main program function. """
    # Initialize Pygame and set up the window
    pygame.init()
    #start pyo sound
    s = pyo.Server(duplex=0)
    s.setOutputDevice(2)
    s.boot()
    s.start()
    
    #start NetStation
    """ms_localtime = egi.ms_localtime

    ns.initialize(address, port)
    ns.BeginSession()
    ns.sync()
    ns.StartRecording()"""
    
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    """bgimage = pygame.image.load("Images/planet.bmp")
    bgimage = pygame.transform.scale(bgimage, (SCREEN_WIDTH, SCREEN_HEIGHT))"""

    """set targets for reference points for aliens"""
    def bgtarget(xcoord):
        pygame.draw.ellipse(screen, GREY, [xcoord, SCREEN_HEIGHT-26, 32, 26])
        #black dot in center for fun
        pygame.draw.ellipse(screen, BLACK, [xcoord+11, SCREEN_HEIGHT-18, 10, 10])
    pygame.display.set_caption("Josh's Game")
    pygame.mouse.set_visible(False)
    elapsedTime = 0 #starts at 0, increases by one per frame change
    timeBetweenSpawns = 500 #number of frames between spawns
     
    # Create our objects and set the data
    done = False
    clock = pygame.time.Clock()
     
    # Create an instance of the Game class
    game = Game()
    # Main game loop
    while not done:
        screen.fill(BLACK)
        # Process events (keystrokes, mouse clicks, etc)
        done = game.process_events()
        #draw bg image
        """screen.blit(bgimage, [0,0])"""
        #draw targets
        """screen.blit(bgtarget, [Enemy.a_pos, SCREEN_HEIGHT-20])
        screen.blit(bgtarget, [Enemy.b_pos, SCREEN_HEIGHT-20])
        screen.blit(bgtarget, [Enemy.c_pos, SCREEN_HEIGHT-20])
        screen.blit(bgtarget, [Enemy.d_pos, SCREEN_HEIGHT-20])"""
        bgtarget(Enemy.a_pos)
        bgtarget(Enemy.b_pos)
        bgtarget(Enemy.c_pos)
        bgtarget(Enemy.d_pos)

        # Update object positions, check for collisions
        game.run_logic()
         
        # Draw the current frame
        game.display_frame(screen)
         
        # Pause for the next frame, 60 fps
        clock.tick(60)
    # write data to xlsx file
    workbook = xlsxwriter.Workbook('Response_Times.xlsx')
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    worksheet.write(0, 1, 'Shot Fired (s)', bold)
    worksheet.write(0, 2, 'Enemy generation (s)', bold)
    worksheet.write(0, 3, 'Enemy sight (s)', bold)
    worksheet.write(0, 4, 'Enemy killed (s)', bold)
    row = 1
    column = 1
    """format worksheet"""
    for column in range(5):
        worksheet.set_column(0, column, 20)
        column += 1
    column = 1 #reset to 0th column for writing data
    """write data"""
    sight_times = open("Subject %s/sight_times.txt"%SUBJECT, "w")
    for A_sight in Enemy.enemyA_sight_time:
        item = str((Enemy.a_pos, A_sight)) + '\n'
        sight_times.write(item)
        
    for B_sight in Enemy.enemyB_sight_time:
        item = str((Enemy.b_pos, B_sight))+ '\n'
        sight_times.write(item)
    
    for C_sight in Enemy.enemyC_sight_time:
        item = str((Enemy.c_pos, C_sight))+ '\n'
        sight_times.write(item)
        
    for D_sight in Enemy.enemyD_sight_time:
        item = str((Enemy.d_pos, D_sight))+ '\n'
        sight_times.write(item)
    sight_times.close()
    """xcel sheet"""
    """worksheet.write(row, 0 , 'TypeA', bold)
    for A_shot, A_enemy, A_sight, A_death in izip_longest(Game.Ashot_time, Enemy.enemyA_generate_time, Enemy.enemyA_sight_time, Game.enemyA_kill_time, fillvalue = '-'):
        worksheet.write(row, column, A_shot)
        worksheet.write(row, column+1, A_enemy)
        worksheet.write(row, column+2, A_sight)
        worksheet.write(row, column+3, A_death)
        row += 1
    worksheet.write(row, 0, 'TypeB', bold)
    for B_shot,B_enemy,B_sight,B_death in izip_longest(Game.Bshot_time, Enemy.enemyB_generate_time, Enemy.enemyB_sight_time, Game.enemyB_kill_time, fillvalue = '-'):
        worksheet.write(row, column, B_shot)
        worksheet.write(row, column+1, B_enemy)
        worksheet.write(row, column+2, B_sight)
        worksheet.write(row, column+3, B_death)
        row+=1
    worksheet.write(row, 0 , 'TypeC', bold)
    for C_shot,C_enemy,C_sight,C_death in izip_longest(Game.Cshot_time, Enemy.enemyC_generate_time, Enemy.enemyC_sight_time, Game.enemyC_kill_time, fillvalue = '-'):
        worksheet.write(row, column, C_shot)
        worksheet.write(row, column+1, C_enemy)
        worksheet.write(row, column+2, C_sight)
        worksheet.write(row, column+3, C_death)
        row+=1
    worksheet.write(row, 0 , 'TypeD', bold)
    for D_shot,D_enemy,D_sight,D_death in izip_longest(Game.Dshot_time, Enemy.enemyD_generate_time, Enemy.enemyD_sight_time, Game.enemyD_kill_time, fillvalue = '-'):
        worksheet.write(row, column, D_shot)
        worksheet.write(row, column+1, D_enemy)
        worksheet.write(row, column+2, D_sight)
        worksheet.write(row, column+3, D_death)
        row+=1
    workbook.close()"""
    #shut down pyo server
    s.stop()
    #Stop NetStation Recording
    """ns.StopRecording()
    ns.EndSession()
    ns.finalize()"""
    # Close window and exit
    pygame.quit()

 
# Call the main function, start up the game
if __name__ == "__main__":
    main()