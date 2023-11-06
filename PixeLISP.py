
import pygame
import pygame_textinput
from pygame.locals import *
import re
 

## For Atoms
def identifier(scanner, token): return "I"
scanner = re.Scanner([
    (r"[^\n\s()\"\']+", identifier),
    ])

## For Checking Var Type
def sFloat(scanner, inp): return "SF"
def chrctr(scanner, inp): return "C"
def intgr(scanner, inp): return "I"
scnnr = re.Scanner([
    (r"[0-9]+(\.[0-9]+)", sFloat),
    (r"[0-9]+", intgr),
    (r"[a-zA-Z]\s?", chrctr)
])

## Syntax Checking LISP
lex = [
    ('LPar', '('),
    ('RPar', ')'),
    ('Com', 'write-line', 'setq', 'print', 'defvar'),
    ('Mac', 'defmacro'),
    ('QMark', '"', "'")
]

def tokenize(inp):
    tokens = ''
    parts = inp.split()
    Out = ''
    macName = ''
    qmarkCheck = 0
    macCheck = 0
    currCom = ''
    outCom = ''
    value = ''
    currVarName = ''
    outVarName = ''
    global macros

    for part in parts:
        for mName, mCom, mVar in macros:
            if mName == part:
                tokens = tokens + 'Mac-'
                macName = part
                macCheck = 2


        if part in lex[0]:
            tokens = tokens + 'LPar-'
            if currCom == 'print':
                outCom = 'print'
                currCom = ''
        elif part in lex[1]:
            tokens= tokens + 'RPar-'
        elif part in lex[2]:
            tokens= tokens + 'Com-'
            currCom = part
        elif part in lex[3]:
            tokens = tokens + 'Mac-'
            macCheck += 1
        elif part in lex[4]:
            tokens= tokens + 'QMark-'
            if qmarkCheck%2 == 0:
                tokens = tokens + 'Out-'
            qmarkCheck += 1
            if currCom == 'print' or currCom == 'write-line':
                currVarName = ''
                outCom = currCom
                currCom = ''
        else:
            if qmarkCheck%2 == 1:
                Out = Out + part + ' '
            if macCheck == 1:
                macName = part
                macCheck = 0
            if macCheck == 2:
                macCheck +=1
            elif macCheck == 3:
                outVarName = part
                macCheck = 0
            if currCom == 'setq' or currCom == 'defvar':
                currVarName = part
                outCom = currCom
                currCom = ''
            elif currCom == 'print':
                outVarName = part
                outCom = 'print'
                currCom = ''
                if part == 'type-of':
                    currVarName = 'type-of'
            elif currVarName == 'type-of':
                value = part
                outVarName = currVarName
                currVarName = ''
            elif currVarName != '':
                value = part
                outVarName = currVarName
                currVarName = ''
            
    return tokens[:-1], Out, outCom, outVarName, value, macName

def separate(data):
    sent = ''
    for i in range(0, len(data)):
        if data[i] == '(':
            sent = sent + ' ' + data[i] + ' '
        elif data[i] == ')':
            sent = sent + ' ' + data[i] + ' '
        elif data[i:i+1] == "\"":
            sent = sent + ' ' + "\"" + ' '
        else:
            sent = sent + data[i]
    
    return sent

def checkSyntax(structure):
    parCount = 0
    qCount = 0
    cCount = 0
    mCount = 0

    for i in range(0,len(structure) - 4):
        if structure[i:i+5] == "LPar-":
            parCount += 1
        elif structure[i:i+5] == "-RPar":
            parCount += 1
        elif structure[i:i+5] == "QMark":
            qCount += 1
        elif structure[i:i+5] == "-Com-":
            cCount += 1
        elif structure[i:i+5] == "-Mac-":
            mCount += 1
        
    if parCount > 0 and parCount % 2 == 0 and qCount == 0 and cCount == 0 and mCount == 0:
        return "LIST"
    elif parCount == 0 and qCount > 0 and qCount % 2 == 0 and cCount == 0 and mCount == 0:
        return "STRING"
    elif parCount % 2 == 0 and parCount>0 and qCount >= 0 and qCount % 2 == 0 and mCount == 1:
        return "MACRO"
    elif parCount % 2 == 0 and parCount>0 and qCount >= 0 and qCount % 2 == 0 and mCount == 0:
        return "CORRECT"
    else:
        return "WRONG"

def interpret(otpt, cmd, vrbl, val, mcr):
    global vrbls
    global macros
    global outDialogue
    global vrbls
    global out
    global progress

    for mName, mCom, mVar in macros:
        if mName == mcr:
            if mCom == 'setq' or mCom == 'defvar':
                for name, nVal in vrbls:
                    if name == mVar:
                        val = nVal
                vrbls.append((vrbl, val))
                if progress <13:
                    outDialogue.append('')
                else:
                    afterDia.append('')
                

    #Macros
    if mcr != '':
        if macros != []:
            for mName, mCom, mVar in macros:
                if mName != mcr:
                    macros.append((mcr, cmd, vrbl))
                    if progress <13:
                        outDialogue.append('')
                    else:
                        afterDia.append('')
        else:
            macros.append((mcr, cmd, vrbl))
            vrbls.append((vrbl,val))
            if progress <13:
                outDialogue.append('')
            else:
                afterDia.append('')

    #Commands
    if mcr == '' and cmd != '':
        if cmd == 'setq' or cmd == 'defvar':
            vrbls.append((vrbl, val))
            if progress <13:
                outDialogue.append('')
            else:
                afterDia.append('')
        elif cmd == 'print' and vrbl == '' or cmd == 'write-line' and vrbl == '':
            if progress < 13:
                outDialogue.append(otpt)
            else:
                afterDia.append(otpt)
        elif cmd == 'print' and vrbl != '' and vrbl != 'type-of':
                for name, nVal in vrbls:
                    if name == vrbl:
                        if progress < 13:
                            outDialogue.append(str(nVal))
                        else:
                            afterDia.append(str(nVal))
        elif cmd == 'print' and vrbl == 'type-of':
                for name, nVal in vrbls:
                    if name == val:
                        if nVal == 'nil':
                            if progress <13:
                                outDialogue.append("NULL")
                            else:
                                afterDia.append("NULL")
                        elif scnnr.scan(nVal)[0] == ['SF']:
                            if progress <13:
                                outDialogue.append("SINGLE-FLOAT")
                            else:
                                afterDia.append("SINGLE-FLOAT")
                        elif scnnr.scan(nVal)[0] == ['C']:
                            if progress <13:
                                outDialogue.append("CHARACTER")
                            else:
                                afterDia.append("CHARACTER")
                        elif scnnr.scan(nVal)[0] == ['I']:
                            if progress <13:
                                outDialogue.append("INTEGER")
                            else:
                                afterDia.append("INTEGER")
                        else:
                            if progress <13:
                                outDialogue.append("NaN")
                            else:
                                afterDia.append("NaN")

        



##Game Elements

class Character(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.is_idle = True
        self.is_attacking = False
        self.is_dead = False
        self.idle = []
        self.attack = []
        self.die = []
        self.idle.append(pygame.image.load('assets/characters/MC/idle-00.png'))
        self.idle.append(pygame.image.load('assets/characters/MC/idle-01.png'))
        self.idle.append(pygame.image.load('assets/characters/MC/idle-02.png'))
        self.idle.append(pygame.image.load('assets/characters/MC/idle-03.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/00.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/01.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/02.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/03.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/04.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/05.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/06.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/07.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/08.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/09.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/10.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/11.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/12.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/13.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/14.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/15.png'))
        self.attack.append(pygame.image.load('assets/characters/MC/attack/16.png'))
        self.die.append(pygame.image.load('assets/characters/MC/die/die (1).png'))
        self.die.append(pygame.image.load('assets/characters/MC/die/die (2).png'))
        self.die.append(pygame.image.load('assets/characters/MC/die/die (3).png'))
        self.die.append(pygame.image.load('assets/characters/MC/die/die (4).png'))
        self.die.append(pygame.image.load('assets/characters/MC/die/die (5).png'))
        self.die.append(pygame.image.load('assets/characters/MC/die/die (6).png'))
        self.die.append(pygame.image.load('assets/characters/MC/die/die (7).png'))
        self.current_sprite = 0
        self.image = self.idle[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x,pos_y]
    
    def idling(self):
        if self.is_dead == True:
            self.is_idle == False
        if self.is_attacking == True and self.is_dead == False:
            if self.current_sprite != len(self.attack):
                self.is_idle = False
            else:
                self.is_idle = True
        else:
            self.is_idle = True

    def attacking(self):
        self.is_attacking = True
    
    def dead(self):
        self.is_dead = True
        self.is_idle == False
        self.is_attacking == False

    def update(self, speed):
        if self.is_idle == True and self.is_dead == False:
            self.current_sprite += speed

            if self.current_sprite >= len(self.idle):
                self.current_sprite = 0
                self.is_idle = False
                self.is_attacking = False

            self.image = self.idle[int(self.current_sprite)]
        
        if self.is_attacking == True and self.is_dead == False:
            self.current_sprite += (speed*1.5)

            if self.current_sprite >= len(self.attack):
                self.current_sprite = 0
                self.is_attacking = False
                self.is_idle = True
            
            self.image = self.attack[int(self.current_sprite)]
        
        if self.is_dead == True:
            self.current_sprite += speed/2

            if self.current_sprite >= len(self.die):
                self.current_sprite = len(self.die)-1
                self.is_attacking = False
                self.is_idle = False
                self.is_dead = False
            
            self.image = self.die[int(self.current_sprite)]

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.is_idle = True
        self.is_attacking = False
        self.is_dead = False
        self.idle = []
        self.attack = []
        self.die = []
        self.idle.append(pygame.image.load('assets/characters/Golem/Idle/idle (1).png'))
        self.idle.append(pygame.image.load('assets/characters/Golem/Idle/idle (2).png'))
        self.idle.append(pygame.image.load('assets/characters/Golem/Idle/idle (3).png'))
        self.idle.append(pygame.image.load('assets/characters/Golem/Idle/idle (4).png'))
        self.idle.append(pygame.image.load('assets/characters/Golem/Idle/idle (5).png'))
        self.idle.append(pygame.image.load('assets/characters/Golem/Idle/idle (6).png'))
        self.idle.append(pygame.image.load('assets/characters/Golem/Idle/idle (7).png'))
        self.idle.append(pygame.image.load('assets/characters/Golem/Idle/idle (8).png'))
        self.idle.append(pygame.image.load('assets/characters/Golem/Idle/idle (9).png'))
        self.idle.append(pygame.image.load('assets/characters/Golem/Idle/idle (10).png'))
        self.idle.append(pygame.image.load('assets/characters/Golem/Idle/idle (11).png'))
        self.idle.append(pygame.image.load('assets/characters/Golem/Idle/idle (12).png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/1.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/2.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/3.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/4.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/5.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/6.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/7.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/8.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/9.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/8.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/7.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/6.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/5.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/4.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/3.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/2.png'))
        self.attack.append(pygame.image.load('assets/characters/Golem/Attack/1.png'))
        self.die.append(pygame.image.load('assets/characters/Golem/Death/1.png'))
        self.die.append(pygame.image.load('assets/characters/Golem/Death/2.png'))
        self.die.append(pygame.image.load('assets/characters/Golem/Death/3.png'))
        self.die.append(pygame.image.load('assets/characters/Golem/Death/4.png'))
        self.die.append(pygame.image.load('assets/characters/Golem/Death/5.png'))
        self.die.append(pygame.image.load('assets/characters/Golem/Death/6.png'))
        self.die.append(pygame.image.load('assets/characters/Golem/Death/7.png'))
        self.die.append(pygame.image.load('assets/characters/Golem/Death/8.png'))
        self.die.append(pygame.image.load('assets/characters/Golem/Death/9.png'))
        self.die.append(pygame.image.load('assets/characters/Golem/Death/10.png'))
        self.die.append(pygame.image.load('assets/characters/Golem/Death/11.png'))
        self.die.append(pygame.image.load('assets/characters/Golem/Death/12.png'))
        self.die.append(pygame.image.load('assets/characters/Golem/Death/13.png'))
        self.die.append(pygame.image.load('assets/characters/Golem/Death/14.png'))
        self.current_sprite = 0
        self.image = self.idle[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x,pos_y]
    
    def idling(self):
        if self.is_dead == True:
            self.is_idle == False
        elif self.is_attacking == True and self.is_dead == False:
            if self.current_sprite != len(self.attack):
                self.is_idle = False
            else:
                self.is_idle = True
        else:
            self.is_idle = True

    def attacking(self):
        self.is_attacking = True
    
    def dead(self):
        self.is_dead = True
        self.is_idle == False
        self.is_attacking == False

    def update(self, speed):
        if self.is_idle == True and self.is_dead == False:
            self.current_sprite += speed

            if self.current_sprite >= len(self.idle):
                self.current_sprite = 0
                self.is_idle = False
                self.is_attacking = False

            self.image = self.idle[int(self.current_sprite)]
        
        if self.is_attacking == True and self.is_dead == False:
            self.current_sprite += speed*1.5

            if self.current_sprite >= len(self.attack):
                self.current_sprite = 0
                self.is_attacking = False
                self.is_idle = True
            
            self.image = self.attack[int(self.current_sprite)]
        
        if self.is_dead == True:
            self.current_sprite += speed/1.5

            if self.current_sprite >= len(self.die):
                self.current_sprite = len(self.die)-1
                self.is_attacking = False
                self.is_idle = False
                self.is_dead = False
            
            self.image = self.die[int(self.current_sprite)]

class Portrait(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.is_idle = True
        self.idle = []
        self.idle.append(pygame.image.load('assets/portrait/F (1).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (2).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (3).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (4).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (5).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (6).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (7).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (8).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (9).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (10).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (11).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (12).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (13).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (14).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (15).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (16).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (17).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (18).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (19).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (20).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (21).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (22).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (23).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (24).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (25).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (26).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (27).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (28).gif'))
        self.idle.append(pygame.image.load('assets/portrait/F (29).gif'))
        self.current_sprite = 0
        self.image = self.idle[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.topleft = [pos_x,pos_y]

    def update(self, speed):
        if self.is_idle == True:
            self.current_sprite += speed

            if self.current_sprite >= len(self.idle):
                self.current_sprite = 0

            self.image = self.idle[int(self.current_sprite)]

class Heart:
    def __init__(self, screenheight, screenwidth, imagefile):
        self.shape = pygame.image.load(imagefile)
        self.top = screenheight - self.shape.get_height()-320
        self.left = screenwidth/2 - self.shape.get_width()/2

    def Show(self, surface):
        surface.blit(self.shape, (self.left, self.top))

    def UpdateCoords(self, x, y):
        self.left = x-self.shape.get_width()/2
        self.top = y- self.shape.get_height()-320

class ScrollingBackground:

    def __init__(self, screenwidth, imagefile):
        self.img = pygame.image.load(imagefile)
        self.coord = [0, 0]
        self.coord2 = [-screenwidth, 0]
        self.x_original = self.coord[0]
        self.x2_original = self.coord2[0]

    def Show(self, surface):
        surface.blit(self.img, self.coord)
        surface.blit(self.img, self.coord2)

    
    def UpdateCoords(self, speed_x, time):
        distance_x = speed_x * time
        self.coord[0] += distance_x
        self.coord2[0] += distance_x

        if self.coord2[0] >= 0:
            self.coord[0] = self.x_original
            self.coord2[0] = self.x2_original

class Object:
    def __init__(self, screenheight, screenwidth, imagefile):
        self.shape = pygame.image.load(imagefile)
        self.top = screenheight - self.shape.get_height()-620
        self.left = screenwidth - self.shape.get_width()

    def Show(self, surface):
        surface.blit(self.shape, (self.left, self.top))
    
    def UpdateCoords(self, x, y):
        self.left = x - self.shape.get_width() + 820
        self.top = y - self.shape.get_height() - 620

def render_multi_line(text, x, y, fsize, color):
        lines = text.splitlines()
        for i, l in enumerate(lines):
            screen.blit(font.render(l, 0, (color)), (x, y + fsize*i))

pygame.init()  # initialize pygame
clock = pygame.time.Clock()
screenwidth, screenheight = (1620, 911)
progress = 0 # Determines which part of the game the player is currently at.
after = 0 #For after the game finishes

gameDialogue = [
    "Hi! This is a short tutorial on learning the basics of LISP!\nI'm going to be guiding you althroughout the duration of tutorial.\nLet's have some fun!\n\nLet's start by understanding the basic building blocks of LISP. \nPress enter on the input box. (The gray box)",
    "LISP is made up of three basic building blocks:\n- Atoms\n- Lists\n- Strings\n\nLet's try identifying them. Press enter on the input box.",
    "An ATOM is a number or string of contiguous assets/characters. It includes numbers \nand special assets/characters. Here are some examples:\n\n1. name\t 2. 123008907\t3. *hello*\t4. abc123\n\nTry inputting an atom on the input box and I will check if it is an atom.",
    "This time, let's learn lists. A list is a sequence of atoms and/or other lists\nenclosed in parentheses.Here are some example:\n\n1. ( i am a list) 2. (a ( a b c) d e fgh) 3. ( )\n\nTry inputting a list on the input box and I will check if it is a list.",
    "Now, we will learn about strings. A string is a group of assets/characters enclosed\nin double quotation marks. Here are some examples:\n\n1. \"I am a string\" 2. \"a bc 123 *&$\" 3. \"Hi 123weeoo!\"\n\nTry inputting a string and I will check if it is correct.",
    "You have now familiarized yourself with the basic building blocks of LISP.\nWe will now try practicing with commands. \"write-line\" will allow you to\noutput a string of your choice. Try it out!\n\nExample: (write-line \"Hello World\")",
    "Great! You outputted your first line with LISP! Now, let's try a different\ncommand- \"setq\". Setq sets a variable to a specific value.\n\nExample: (setq x 10) sets the variable 'x' to 10.\n\nTry setting any variable to any value.",
    "Now that you have set a value to your variable, let's try displaying its value!\nThis time, let's use the 'print' command. Follow this example:\n\n(print x) - This will print the value of variable 'x'\n\nTry printing the value of your variable.",
    "Good! Now you know how to display the values of your variables! Then, we will\nlearn a different way to set values to our variables. This is by using the\ncommand 'defvar'. Here is an example:\n\n(defvar test 100) - This sets the value of 'test' to 100. Try using defvar!",
    "You have now set a value for your variable with defvar! For every value, we\nhave a specific data type. There are many different data types.So, let's try\nseeing what data type our value is by using 'print type-of'.Example:\n\n(print type-of test) - this prints the type of the value inside test!\nTry it yourself by following the example.",
    "Amazing! Lastly, we will learn about macros. Macros are commands that\nwe define ourselves. Let's make a macro that sets a variable's value to 50\nby following this example:\n\n(defmacro setTo50(num)(setq num 50)).\nTry it out by typing it onto the input box.",
    "Now that we have defined a macro - 'setTo50', let's try using it!\n\nType in \"(setTo50 z)\" - you may use z or any variable name you want,\nand set its value to 50.",
    "Finally, to check if we truly set the value of that variable to 50 by\nusing our newly-created macro, let's print it!\n\nTo complete our journey, let's 'print' the value of our variable!.",
    "Congratulations! You have officially finished the tutorial!\n\nYou now have knowledge on the basics of LISP! If you wish to learn more,\nyou can go to \"https://www.tutorialspoint.com/lisp/index.htm\"."

]

gameDiaWrong = [
    "Oh no! You may have made a mistake. Try again.\n\nDon't make too many mistakes or you might run out of health(hearts),\nand lose the game!\n\nOnce again, press enter on the input box. (The gray box)",
    "Oh no! You may have made a mistake. Try again.\n\nDon't make too many mistakes or you might run out of health(hearts),\nand lose the game!\n\nOnce again, press enter on the input box. (The gray box)",
    "This is not an atom. Here are some examples:\n\n1. name\t 2. 123008907\t3. *hello*\t4. abc123\n\nTry again and input an atom.",
    "This is not a list. Here are some examples:\n\n1. ( i am a list) 2. (a ( a b c) d e fgh) 3. ( )\n\nTry again and input a list.",
    "This is not a string. Here are some examples:\n\n1. \"I am a string\" 2. \"a bc 123 *&$\" 3. \"Hi 123weeoo!\"\n\nTry again and input a string.",
    "Uh-oh! That's not how you use the write-line command. Try again by following\nthe structure of this example:\n\n(write-line \"Hello World\")",
    "Hmmm... I don't think that's how you set a variable's value. Try again with\n'setq' by following this example:\n\n(setq x 10)",
    "That may not be the name you used for your variable. Try again!\n\nRemember, use the name of your variable. If you set 'x' to 10\nThen, you must '(print x)'",
    "Oh no... That's not how you use defvar. Let's try setting a value to a\nvariable again by following this example:\n\n(defvar test 100).",
    "Hmmm... Maybe you missed a parenthesis, or maybe you made a typo. Try again by\nfollowing this example:\n\n(print type-of test) - This will print the data type of the value inside test.",
    "Uh-oh! That's not how you make a macro. Just a little bit more\nand you will have mastered the basics of LISP! Follow this example:\n\n(defmacro setTo50(num)(setq num 50))",
    "Did you use the right macro name? If you forgot, it was 'setTo50'.\n\nLet's try using it again by following this example:\n\n(setTo50 z)",
    "Hmmm... Did you forget how to print the value of a variable?\n\nDon't worry, you can follow this example: (print x)\n\nLet's try that again and complete our journey!"

]

outDialogue = [
    "",
    "",
    "",
    "Good job! This is an atom!",
    "Good job! This is a list!",
    "Good job! This is a string!",
]

inputAnswers = [
    "",
    "",
    "['I']",
    "LIST",
    "STRING",
    "CORRECT",
    "CORRECT",
    "CORRECT",
    "CORRECT",
    "CORRECT",
    "MACRO",
    "MACRO",
    "CORRECT"

]

afterDia = [
    '',
]


#Sprites
moving_sprites = pygame.sprite.Group()
e_sprites = pygame.sprite.Group()
player =  Character(150, 550)
enemy = Enemy(1010, 460)
portrait = Portrait(50, 45)
moving_sprites.add(player)
moving_sprites.add(portrait)
e_sprites.add(enemy)


#Text Input
textinput = pygame_textinput.TextInputVisualizer()

HHealth = 5
EHealth = 13
HHearts = []
Hcoords = [] 
EHearts = [] 
Ecoords = []
heart = Heart(screenheight, screenwidth, "assets/icons/smallheart.png")

for i in range(0, HHealth):
    HHearts.append(heart)
    Hcoords.append(180+(i*36))

for i in range(0, EHealth):
    EHearts.append(heart)
    Ecoords.append(980+(i*36))

Hcounter = HHealth-1
Ecounter = EHealth-1


bgtime = clock.tick(60)/1000
background = ScrollingBackground(screenwidth, "assets/bg3.png")
screen = pygame.display.set_mode((1366, 768), pygame.RESIZABLE)
font = pygame.font.Font("assets/pixel.ttf", 30)
clock = pygame.time.Clock()

# Box Objects
input_box = pygame.Rect(477, 435, 445, 75)
output_box = pygame.Rect(477,535, 445, 140)
dialog_box = pygame.Rect(335,53, 933, 241)
ibox_bg = Object(screenheight, screenwidth, "assets/textbox.png")
obox_bg = Object(screenheight, screenwidth, "assets/outputbox.png")
dbox_bg = Object(screenheight, 410, "assets/dbbg.png")
color_inactive = pygame.Color('black')
color_active = pygame.Color('white')
color = color_inactive
dead = 0
eDead = 0
active = False
wrong = 0
vrbls = []
macros = []
dialogue = ''
text = ''
out = ''
done = False

def correct():
    global progress
    global player
    global EHealth
    global Ecoords
    global Ecounter
    global HHealth
    global text
    global eDead

    progress += 1
    player.attacking()
    EHealth -= 1
    
    if Ecounter != 0:
        Ecoords[Ecounter] += 800
        Ecounter -= 1
    else:
        eDead = 1
    text = ''

def mistake():
    global text
    global Hcoords
    global Hcounter
    global HHealth
    global dead
    global enemy

    enemy.attacking()
    if Hcounter > 0:
        Hcoords[Hcounter] -= 800
        Hcounter -= 1
        HHealth -= 1
    else:
        Hcoords[Hcounter] -= 800
        Hcounter -= 1
        HHealth -= 1
        dead = 1
    text = ''


while not done:
    
    # pygame.display.update()
    

    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                    active = not active
                else:
                    active = False
                # Change the current color of the input box.
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        if progress == 2:
                            tokens = scanner.scan(text)
                            text = str(tokens[0])
                            if text == inputAnswers[progress]:
                                correct()
                                wrong = 0
                            else:
                                wrong = 1
                                mistake()
                        elif progress >= 3:
                            tokens, otpt, cmd, vrbl, val, mcr = tokenize(separate(text))
                            text = checkSyntax(tokens)
                            if progress >= 5:
                                interpret(otpt, cmd, vrbl, val, mcr)
                                if progress == 5:
                                    if text == inputAnswers[progress] and cmd == 'write-line' and otpt != '':
                                        correct()
                                        wrong = 0
                                    else:
                                        wrong = 1
                                        mistake()
                                elif progress == 6:
                                    if text == inputAnswers[progress] and cmd == 'setq':
                                        correct()
                                        wrong = 0
                                    else:
                                        wrong = 1
                                        mistake()
                                elif progress == 7:
                                    if text == inputAnswers[progress] and cmd == 'print':
                                        correct()
                                        wrong = 0
                                    else:
                                        wrong = 1
                                        mistake()
                                elif progress == 8:
                                    if text == inputAnswers[progress] and cmd == 'defvar':
                                        correct()
                                        wrong = 0
                                    else:
                                        wrong = 1
                                        mistake()
                                elif progress == 9:
                                    if text == inputAnswers[progress] and cmd == 'print':
                                        correct()
                                        wrong = 0
                                    else:
                                        wrong = 1
                                        mistake()
                                elif progress == 10:
                                    if text == inputAnswers[progress]:
                                        correct()
                                        wrong = 0
                                    else:
                                        wrong = 1
                                        mistake()
                                elif progress == 11:
                                    if text == inputAnswers[progress]:
                                        correct()
                                        wrong = 0
                                    else:
                                        wrong = 1
                                        mistake()
                                elif progress == 12:
                                    if text == inputAnswers[progress]:
                                        correct()
                                        wrong = 0
                                    else:
                                        wrong = 1
                                        mistake()
                                elif progress >= 13:
                                    progress += 1
                                    if text == checkSyntax(tokens):
                                        text = ''
                                        after+=1
                                        wrong = 0
                                else:
                                    wrong = 1
                                    mistake()
                            elif text == inputAnswers[progress]:
                                correct()
                                wrong = 0
                            else:
                                wrong = 1
                                mistake()
                        else:
                            if text == inputAnswers[progress]:
                                correct()
                                wrong = 0
                            else:
                                wrong = 1
                                mistake()
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
                        

    screen.fill((30, 30, 30))
    background.Show(screen)
    background.UpdateCoords(7, bgtime)
    ibox_bg.UpdateCoords(135, 1150)
    obox_bg.UpdateCoords(135, 1310)
    dbox_bg.UpdateCoords(500, 910)
    ibox_bg.Show(screen)
    obox_bg.Show(screen)
    dbox_bg.Show(screen)
    moving_sprites.draw(screen)
    e_sprites.draw(screen)
    if dead == 0:
        player.idling()
    else:
        player.dead()
    if eDead == 0:
        enemy.idling()
    else:
        enemy.dead()
    e_sprites.update(0.25)
    moving_sprites.update(0.25)
    
    if progress < 13:
        if wrong == 1:
            if dead == 1:
                dialogue = "You have died. Please try again from the beginning."
            else:
                dialogue = gameDiaWrong[progress]
        else:
            dialogue = gameDialogue[progress]
    else:
        dialogue = gameDialogue[13]

    if progress <= 13:
        out = outDialogue[progress]
    else:
        out = afterDia[after]

    ##Player Health Display
    for i in range(0, HHealth):
        HHearts[i].UpdateCoords(Hcoords[i], 831)
        HHearts[i].Show(screen)
   
    #Enemy Health Display:
    for i in range(0, EHealth):
        if i < 6:
            EHearts[i].UpdateCoords(Ecoords[i]+90, 811)
            EHearts[i].Show(screen)
        else:
            EHearts[i].UpdateCoords(Ecoords[i]-147, 771)
            EHearts[i].Show(screen)


        # Render the current text.
    txt_surface = font.render(text, True, color)
    out_text = render_multi_line(out, output_box.x + 5, output_box.y, 30, 'black')
    dialog_text = render_multi_line(dialogue, dialog_box.x + 20, dialog_box.y + 10, 30, 'white')
    width = max(445, input_box.width)
        # Blit the text.
    screen.blit(txt_surface, (input_box.x+5, input_box.y))
        # Blit the input_box rect.
    pygame.draw.rect(screen, color, input_box, 1)
    pygame.display.flip()
    
    clock.tick(30)









