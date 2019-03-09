import pygame
import random

def main():
    pygame.init()

    # Setting the main variables of the game
    screen=pygame.display.set_mode((400,600)) 
    background=pygame.image.load("wallpaper.jpg").convert_alpha()
    bat=pygame.image.load("bat.png").convert_alpha()
    pygame.display.set_caption("Defeat the bat - Manuel")
    time=pygame.time.Clock()

    # Setting colors
    white=(255,255,255) # the color of the movement of the cursor
    red=(200,0,0)
    blue=(0,0,250)

    # Setting random movements for the bat
    spritebat=pygame.sprite.Sprite()
    spritebat.image=bat
    spritebat.rect=bat.get_rect()
    spritebat.rect.top=random.randrange(100,400)
    spritebat.rect.left=random.randrange(100,300)

    # variables for collisions
    vx,vy=0,0
    leftcrash=True
    rightcrash=False
    upcrash=True
    downcrash=False

    # Setting start position of the bar
    botontouch1=pygame.Rect(20,100,180,470)
    botontouch2=pygame.Rect(210,100,180,470)

    xp=50
    player=pygame.Rect(xp,30,100,25)
    cursor=pygame.Rect(0,0,10,10)
    velx=0
    exit=False
    endGame=False

    while exit!= True and endGame!=True:
        
        for event in pygame.event.get():
            if event.type== pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit =True
            if event.type == pygame.QUIT:
                exit=True

        # To allow the bar movement
        if cursor.colliderect(botontouch1):
            velx=-5
        elif cursor.colliderect(botontouch2):
            velx=5
        else:
            velx=0

        # To allow the bar movement
        if player.left+velx > 0 and player.left+velx<300:
            player.left+=velx

        # If the bat goes out of the window
        if spritebat.rect.top>570:
            upcrash=False
            downcrash=True

        if spritebat.rect.left<0:
            leftcrash=True
            rightcrash=False

        if spritebat.rect.top>370:
            leftcrash=False
            rightcrash=True

        if spritebat.rect.left>370:
            leftcrash=False
            rightcrash=True

        # The bat can't pass over the bar
        if spritebat.rect.colliderect(player):
            upcrash=True
            downcrash=False

        # If the bat goes out up of the window
        if spritebat.rect.top<0:
            endGame=True

        if leftcrash:
            vx=1
        elif rightcrash:
            vx=-1
        if downcrash:
            vy=-1
        elif upcrash:
            vy=1
        
        # To allow the movement of the bat
        spritebat.rect.move_ip(vx,vy)
        # To control the velocity of the bat (200fps=frames per second)
        time.tick(200)
        # To allow the movement of the cursor
        (cursor.left,cursor.top)=pygame.mouse.get_pos()
        cursor.left-=cursor.width/2
        cursor.top-=cursor.height/2

        # Set the background color
        screen.blit(background,(0,0))
        pygame.draw.rect(screen,white,cursor)
        #pygame.draw.rect(screen,red,botontouch1)
        #pygame.draw.rect(screen,blue,botontouch2)
        screen.blit(spritebat.image,spritebat.rect)
        pygame.draw.rect(screen,white,player)
        pygame.display.update()

    pygame.quit()

main()
