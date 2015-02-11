"""
Space Invaders-style game for auditory category learning task
Designed by Josh Oberman at Howard Nusbaum Lab, University of Chicago, February-March 2014
"""
from os import listdir, mkdir, path
import pygame
import random
from psychopy import core
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
            return checkData(SUBJECT)
        elif answer == "Y":
            pass
        else:
            return checkData(SUBJECT)
checkData(SUBJECT)

CONDITION = raw_input("Condition 1 (variable) or 2 (static)? ")
def checkCond(CONDITION):
    CONDITION = int(CONDITION)
    if CONDITION != 1 and CONDITION != 2:
        CONDITION = raw_input("Not a valid entry. Condition 1 (variable) or 2 (static)? ")
        return checkCond(CONDITION)
    return CONDITION

CONDITION = checkCond(CONDITION)
print CONDITION

# --- Classes ---
 
class Enemy(pygame.sprite.Sprite):
    """ This class represents the enemies """
    centsRangeDesc = range(25,0,-5) #for pos values
    centsRangeAsc = range(5,30,5) #for neg values
    cSharp_notes = ["C#+%d.wav"%num for num in centsRangeDesc] + ["C#.wav"] + ["C#-%d.wav"%num for num in centsRangeAsc]
    cSharp_notes = ["Notes/C#/{0}".format(i) for i in cSharp_notes if not i.startswith('.')]#format so they can be read in to pyo sound tables, don't read hidden proprietary files
    del cSharp_notes[6]
    print cSharp_notes
    d_notes = ["D+%d.wav"%num for num in centsRangeDesc] + ["D.wav"] + ["D-%d.wav"%num for num in centsRangeAsc]
    d_notes = ["Notes/D/{0}".format(i) for i in d_notes if not i.startswith('.')]
    dSharp_notes = ["D#+%d.wav"%num for num in centsRangeDesc] + ["D#.wav"] + ["D#-%d.wav"%num for num in centsRangeAsc]
    dSharp_notes = ["Notes/D#/{0}".format(i) for i in dSharp_notes if not i.startswith('.')]
    e_notes = ["E+%d.wav"%num for num in centsRangeDesc] + ["E.wav"] + ["E-%d.wav"%num for num in centsRangeAsc]
    e_notes = ["Notes/E/{0}".format(i) for i in e_notes if not i.startswith('.')]
    """cSharp_10cents = listdir("Notes/C#-10cent")
    cSharp_10cents = ["Notes/C#-10cent/{0}".format(i) for i in cSharp_10cents if not i.startswith('.')]#format so they can be read in to pyo sound tables, don't read hidden proprietary files
    d_10cents = listdir("Notes/D-10cent")
    d_10cents = ["Notes/D-10cent/{0}".format(i) for i in d_10cents if not i.startswith('.')]
    dSharp_10cents = listdir("Notes/D#-10cent")
    dSharp_10cents = ["Notes/D#-10cent/{0}".format(i) for i in dSharp_10cents if not i.startswith('.')]
    e_10cents = listdir("Notes/E-10cent")
    e_10cents = ["Notes/E-10cent/{0}".format(i) for i in e_10cents if not i.startswith('.')]"""
    enemies = listdir("Images/Enemies")
    enemies = ["Images/Enemies/{0}".format(i) for i in enemies if not i.startswith('.')]
    x_speed = 1
    y_speed = 1
    #prob = 0.6
    offscreen_min = 6 #min of generation of enemy/sound stimulus onset offscreen in seconds
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
    """probability weights, these are based on how listdir() will naturally order the  files. Verify that they are indeed being read in in this order
    on whatever machine you're using before you run this game: [+10, +15, +20, +25, +5, -10, -15, -20, -25, -5, 0] """
    probs = [6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 6.25, 50]
    def __init__(self, enemy_type):
        """ Constructor, create the image of the enemy/sound for enemy. Selected from three enemy types """
        pygame.sprite.Sprite.__init__(self)
        self.enemy_type = enemy_type
        #self.env = pyo.Fader(fadein=.01,fadeout=.2, dur=0) #amplitude envelope to get rid of pops
        self.pop = pyo.SfPlayer("Sounds/kill.wav", mul=0.4)#for when enemy dies

        #this function will return an index 
        def random_walk(currInd):
            coinFlip = random.randrange(3) #three outcome 'coin flip' to determine whether to move up, down, or stay the same
            if coinFlip == 0:
                if currInd != 0 and currInd != 10:
                    currInd -= 1
                elif currInd == 0:
                    currInd += 1
                elif currInd == 10:
                    currInd -= 1
            elif coinFlip == 1:
                if currInd != 0 and currInd != 10:
                    currInd += 1
                elif currInd == 0:
                    currInd += 1
                elif currInd == 10:
                    currInd -= 1
            elif coinFlip == 2:
                pass
            return currInd

        self.cSharp_notes = [pyo.SndTable(note) for note in self.cSharp_notes]
        self.d_notes = [pyo.SndTable(note) for note in self.d_notes]
        self.dSharp_notes = [pyo.SndTable(note) for note in self.dSharp_notes]
        self.e_notes = [pyo.SndTable(note) for note in self.e_notes]
        
        #This is experimental condition
        if CONDITION == 1:
            if self.enemy_type == 'A':
                self.ind = random.randrange(0,11,1)
                snd = self.e_notes[self.ind]
                freq = snd.getRate()
                self.sound = pyo.TableRead(snd, freq=freq, loop=True, mul=1)
                def switch():
                    self.ind = random_walk(self.ind)
                    snd = self.e_notes[self.ind]
                    freq = snd.getRate()
                    self.sound.setTable(snd)
                    self.sound.setFreq(freq)
                self.trig = pyo.TrigFunc(self.sound['trig'],switch)
                self.image = pygame.image.load(self.enemies[0])
            elif self.enemy_type == 'B':
                self.ind = random.randrange(0,11,1)
                snd = self.cSharp_notes[self.ind]
                freq = snd.getRate()
                self.sound = pyo.TableRead(snd, freq=freq, loop=True, mul=1)
                def switch():
                    self.ind = random_walk(self.ind)
                    snd = self.cSharp_notes[self.ind]
                    freq = snd.getRate()
                    self.sound.setTable(snd)
                    self.sound.setFreq(freq)
                self.trig = pyo.TrigFunc(self.sound['trig'],switch) 
                self.image = pygame.image.load(self.enemies[1])
            elif self.enemy_type == 'C':
                self.ind = random.randrange(0,11,1)
                snd = self.d_notes[self.ind]
                freq = snd.getRate()
                self.sound = pyo.TableRead(snd, freq=freq, loop=True, mul=1)
                def switch():
                    self.ind = random_walk(self.ind)
                    snd = self.d_notes[self.ind]
                    freq = snd.getRate()
                    self.sound.setTable(snd)
                    self.sound.setFreq(freq)
                self.trig = pyo.TrigFunc(self.sound['trig'],switch)
                self.image = pygame.image.load(self.enemies[2])
            elif self.enemy_type == 'D':
                self.ind = random.randrange(0,11,1)
                snd = self.dSharp_notes[self.ind]
                freq = snd.getRate()
                self.sound = pyo.TableRead(snd, freq=freq, loop=True, mul=1)
                def switch():
                    self.ind = random_walk(self.ind)
                    snd = self.dSharp_notes[self.ind]
                    freq = snd.getRate()
                    self.sound.setTable(snd)
                    self.sound.setFreq(freq)
                self.trig = pyo.TrigFunc(self.sound['trig'],switch)
                self.image = pygame.image.load(self.enemies[3])

        #control condition
        elif CONDITION==2:
            if self.enemy_type == 'A':
                note = self.e_notes[5]
                snddur = note.getDur()
                self.sound = pyo.Looper(note, dur = snddur + self.lag, mul=1)
                self.image = pygame.image.load(self.enemies[0])   
            elif self.enemy_type == 'B':
                note = self.cSharp_notes[5]
                snddur = note.getDur()
                self.sound = pyo.Looper(note, dur = snddur + self.lag, mul=1)
                self.image = pygame.image.load(self.enemies[1])   
            elif self.enemy_type == 'C':
                note = self.d_notes[5]
                snddur = note.getDur()
                self.sound = pyo.Looper(note, dur = snddur + self.lag, mul=1)
                self.image = pygame.image.load(self.enemies[2])   
            elif self.enemy_type == 'D':
                note = self.dSharp_notes[5]
                snddur = note.getDur()
                self.sound = pyo.Looper(note, dur = snddur + self.lag, mul=1)
                self.image = pygame.image.load(self.enemies[3])                
            
        self.image = pygame.transform.scale(self.image, (32,32))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
    def generate(self):
        """ generate the enemy off screen """
        #distance for offset = desired time * velocity
        #ns.sync()
        self.offset_time = 60 * self.offscreen_max #multiply by 60 for fps-->s
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

class Level(object):
    #this is used to define levels and the ammo and speed attributes as they increase
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
            self.ammo = 45
            Enemy.y_speed = 1
            Game.stick_sensitvity = 5
        elif self.currentLevel==7 or self.currentLevel==8 or self.currentLevel==9:
            self.ammo = 35
        elif self.currentLevel==9 or self.currentLevel==10 or self.currentLevel==11 or self.currentLevel==12:
            self.ammo = 30
        
    def check_success(self):
        if len(self.kill_list)<=10:
            self.level_success = False #failed the level
        else:
            self.level_success = True
            self.increase_level()
    
    def increase_level(self):
        self.currentLevel+=1
        Enemy.y_speed += 1
        Bullet.bullet_speed += 1
        Game.stick_sensitivity += 0.1
        
    
    def load_level(self):
        self.__init__()

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
    #Time measurements
    Ashot_time = []
    Bshot_time = []
    Cshot_time = []
    Dshot_time = []
    enemyA_kill_time = []
    enemyB_kill_time = []
    enemyC_kill_time = []
    enemyD_kill_time = []
    enemyA_hitBase_time = []
    enemyB_hitBase_time = []
    enemyC_hitBase_time = []
    enemyD_hitBase_time = []

    # Other data
    levels = []
    score = 0
    maxTrials = 12 #maximum number of levels to play through
    enemy_live = False #bool to tell us if there is a live enemy
    elapsedTime = 0.0 #keep track of elapsed time via frame rate changes
    enemySpawnTime= 180.0 # of frames between enemy death and next enemy spawn
    stick_sensitivity = 4 #sensitivity of joystick for player motion, represents max number of
    #pixels per frame the player moves when stick is moved all the way to left or right
    trajectory = []
    trial = 0
    #bools for adding/removing target
    is_b_target = False
    is_c_target = False
    #for the noise mask
    playNoise = False
     
    # --- Class methods
    # Set up the game
    def __init__(self):
        self.score = 0
        self.game_over = False
        self.game_start = True
        self.first_trial = True
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
         
         
        # Create the player
        self.player = Player()
        self.all_sprites_list.add(self.player)
        self.x_speed = 0
        self.level = Level()
        #shot sound
        self.shot_sound = pyo.SfPlayer("Sounds/laser_shot.aif", mul=0.2)
        #wrong button sound
        self.wrong_button = pyo.SfPlayer("Sounds/wrong_hit.wav", mul=0.4)
        self.controller = True #Is controller plugged in-->defaults to yes
        try:
            pygame.joystick.Joystick(0)
        except:
            print "NO CONTROLLER PLUGGED IN"
            self.controller = False

        t = pyo.CosTable([(0,0),(50,1), (500,0.3), (8191,0)])
        met = pyo.Metro(time=.2).play()
        amp = pyo.TrigEnv(met, table=t, dur=0.18, mul=.35)
        freq = pyo.TrigRand(met, min=400.0, max=1000.0)
        self.a = pyo.Sine(freq=[freq,freq], mul=amp)
        self.n = pyo.Noise(mul=.035).mix(2)
 
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
         
        #event handling from joystick controller
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
                        if event.button==0:
                            shoot('A', GREEN)
                        elif event.button == 1:
                            shoot('B', RED)
                        elif event.button == 2:
                            shoot('C', YELLOW)
                        elif event.button == 3:
                            shoot('D', BROWN)
                    else:
                        self.wrong_button.out()

                    if event.button == 8 or event.button == 9:
                        if self.game_start:
                            self.game_start = False
                        if self.level_over:
                            self.level.load_level()
                            self.first_trial = True
                            self.level_over = False
        return False #for exiting game
 
    def run_logic(self):
        """
        This method is run each time through the frame. It
        updates positions and checks for collisions.
        """

        """setup variable that we switch on if there's a wrong hit"""
        self.wrongHit = False
        if self.wrongHit:
            self.score-=5
            self.wrongHit = False

        """define timestamping for when character enters enemy range"""
        def record_player():
            time = core.getTime()
            self.trajectory.append("%d,%f,%s"%(self.player.middle,time,self.enemy.enemy_type))
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
            if not self.enemy_live and 20.0<self.elapsedTime<self.enemySpawnTime and not self.first_trial:
                #time to play masking noise
                self.n.out()
                self.a.out()
            if not self.enemy_live and self.elapsedTime==self.enemySpawnTime:
                self.a.stop()
                self.n.stop()
                if self.first_trial:
                    self.first_trial = False
                # spawn enemy
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
                    #remove enemy, lose 20 points if it reaches a base
                    time = core.getTime()
                    self.enemy.sound.stop()
                    self.all_sprites_list.remove(self.enemy)
                    if self.enemy.enemy_type == 'A':
                        self.enemyA_hitBase_time.append(time)
                        self.enemyA_list.remove(self.enemy)
                    if self.enemy.enemy_type == 'B':
                        self.enemyB_hitBase_time.append(time)
                        self.enemyB_list.remove(self.enemy)
                    if self.enemy.enemy_type == 'C':
                        self.enemyC_hitBase_time.append(time)
                        self.enemyC_list.remove(self.enemy)
                    if self.enemy.enemy_type == 'D':
                        self.enemyD_hitBase_time.append(time)
                        self.enemyD_list.remove(self.enemy)
                    self.dead_enemies.add(self.enemy)
                    self.level.live_list.append(self.enemy.enemy_type)
                    self.elapsedTime = 0
                    self.score -= 20
                    write_trajectory(self.trial, self.level.currentLevel)
                    self.enemy_live = False
            def kill_enemy(bullet_color, enemy_type):
                # do all the stuff
                time = core.getTime()
                if enemy_type=='A':
                    self.enemyA_kill_time.extend((self.level.currentLevel,time))
                if enemy_type=='B':
                    self.enemyB_kill_time.extend((self.level.currentLevel,time))
                if enemy_type=='C':
                    self.enemyC_kill_time.extend((self.level.currentLevel,time))
                if enemy_type=='D':
                    self.enemyD_kill_time.extend((self.level.currentLevel,time))
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
                    self.wrongHit = True
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
                    self.wrongHit = True
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
                    self.wrongHit = True
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
                    self.wrongHit = True   

            """define end of level"""
            if len(self.level.enemies_list)==0 and not self.enemy_live:
                self.levels.append(self.level.currentLevel)
                scores = open("Subject %s/scores.txt"%SUBJECT, "w")
                scores.write(str(self.score)+'\n')
                scores.close()
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
            text2 = font.render("You scored %d out of 1920 possible points"%self.score,
                                True, GREEN)
            center_x = (SCREEN_WIDTH // 2) - (text2.get_width() // 2)
            center_y = (SCREEN_HEIGHT // 2) + (text2.get_height() // 2) + 2
            screen.blit(text2, [center_x, center_y])

            
        if self.game_start:
            font = pygame.font.Font(None, 25)
            text = font.render("Hello, thank you for participating in this experiment! You will be using the following buttons for this game:",
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
         
        if not self.game_over:
            """draw sprites, print score"""
            self.all_sprites_list.draw(screen)
            font = pygame.font.Font(None, 15)
            score = font.render('Score: %s'%"{:,.0f}".format(self.score), True, RED)
            level = font.render('Level: %d'%self.level.currentLevel, True, GREEN)
            ammo = font.render('Ammo: %d'%self.level.ammo, True, YELLOW)
            x_pos = SCREEN_WIDTH//2-level.get_width()//2
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
    #start pyo sound, use lowest latency output
    s = pyo.Server(duplex=0, audio="jack")
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
    bgimage = pygame.image.load("Images/planet.bmp")
    bgimage = pygame.transform.scale(bgimage, (SCREEN_WIDTH, SCREEN_HEIGHT))
    """set targets for reference points for aliens"""
    def bgtarget(xcoord):
        pygame.draw.ellipse(screen, GREY, [xcoord, SCREEN_HEIGHT-26, 32, 26])
        #black dot in center for fun
        pygame.draw.ellipse(screen, BLACK, [xcoord+11, SCREEN_HEIGHT-18, 10, 10])
    pygame.display.set_caption("AP Game")
    pygame.mouse.set_visible(False)
    elapsedTime = 0 #starts at 0, increases by one per frame change
     
    # Create our objects and set the data
    done = False
    clock = pygame.time.Clock()
     
    # Create an instance of the Game class
    game = Game()
    # Main game loop
    while not done:
        # Process events (keystrokes, mouse clicks, etc)
        done = game.process_events()
        #draw bg image
        screen.blit(bgimage, [0,0])
        #draw targets
        bgtarget(Enemy.a_pos)
        bgtarget(Enemy.b_pos)
        bgtarget(Enemy.c_pos)
        bgtarget(Enemy.d_pos)
        # Update object positions, check for collisions
        game.run_logic()
         
        # Draw the current frame
        game.display_frame(screen)
         
        # Pause for the next frame
        clock.tick(60)
    """write data"""
    condition = open("Subject %s/condition.txt"%SUBJECT,"w")
    condition.write(str(CONDITION))
    condition.close()

    sight_times = open("Subject %s/sight_times.txt"%SUBJECT, "w")
    for A_sight in Enemy.enemyA_sight_time:
        item = "A"+str(A_sight) + '\n'
        sight_times.write(item)
        
    for B_sight in Enemy.enemyB_sight_time:
        item = 'B'+str(B_sight)+ '\n'
        sight_times.write(item)
    
    for C_sight in Enemy.enemyC_sight_time:
        item = 'C'+str(C_sight)+'\n'
        sight_times.write(item)
        
    for D_sight in Enemy.enemyD_sight_time:
        item = 'D'+str(D_sight)+ '\n'
        sight_times.write(item)
    sight_times.close()
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
