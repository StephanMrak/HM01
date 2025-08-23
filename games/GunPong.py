import pygame
import time
import hmsysteme
import os
import platform
import random
import pygame.freetype

class Ball(pygame.sprite.Sprite):
    def __init__(self, ball_images, x, y):
        super().__init__()
        self.ball_images = ball_images
        self.image = ball_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x_speed = 1
        self.y_speed = 0
        self.x_positive = True
        self.y_negate = False
        self.blocked = False
        self.hit = False
        
    def update(self):
        # Move ball
        if self.y_negate:
            self.rect.y += self.y_speed
        else:
            self.rect.y -= self.y_speed
            
        if self.x_positive:
            self.rect.x += self.x_speed
        else:
            self.rect.x -= self.x_speed
            
        # Update image based on blocked state
        if self.blocked:
            self.image = self.ball_images[1]
        else:
            self.image = self.ball_images[0]

class Shot(pygame.sprite.Sprite):
    def __init__(self, shot_image, x, y):
        super().__init__()
        self.image = shot_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.lifetime = 5  # frames to show shot
        
    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

class TextSprite(pygame.sprite.Sprite):
    def __init__(self, text, font, color, x, y, bg_color=None):
        super().__init__()
        self.font = font
        self.color = color
        self.bg_color = bg_color
        self.text = text
        self.render_text()
        self.rect.x = x
        self.rect.y = y
        
    def render_text(self):
        self.image = self.font.render(self.text, True, self.color)
        if self.bg_color:
            # Create background rectangle
            bg_surf = pygame.Surface((self.image.get_width() + 20, self.image.get_height() + 10))
            bg_surf.fill(self.bg_color)
            bg_surf.blit(self.image, (10, 5))
            self.image = bg_surf
        self.rect = self.image.get_rect()
        
    def update_text(self, new_text):
        if self.text != new_text:
            self.text = new_text
            old_center = self.rect.center
            self.render_text()
            self.rect.center = old_center

def main():
    global mausx, mausy, hit_for_screenshot
    global xBall, yBall, offsetBall, xBall_hit, xBall_blocked, xPositiv, xNegativ, xCountRounds, ixBallSpeed, xFault, ixBallSpeedtmp
    global iPlayerPointsLeft, iPlayerPointsRight, listYspeed, iyBallSpeed, xYNegieren
    global xPlayerLeft, xPlayerRight, xNewRound, xNewRoundreal, iCountNextRound, xCountNextRound, iPointsMax, xGameOver, xActivePlayer, iGetAction
    global xGo, Diabolo_Rect
    
    hmsysteme.put_button_names(["ENTER", "RESTART", "x", "x", "x", "x", "x", "x", "x"])
    print(platform.uname())
    pygame.init()

    size = hmsysteme.get_size()
    names = hmsysteme.get_playernames()
    if not names:
        names = ["Stephan", "Marion", "Flori", "Peter Mafai"]

    path = os.path.realpath(__file__)
    if 'Linux' in platform.uname():
        path = path.replace('GunPong.py', '')
    else:
        path = path.replace('GunPong.py', '')

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    pygame.display.set_caption("ePong")

    # Load and convert all resources ONCE
    print("Loading resources...")
    diabolo_img = pygame.image.load(os.path.join(path, "pics/GunPong/Schuss.png")).convert_alpha()
    field_img = pygame.image.load(os.path.join(path, "pics/GunPong/Fieldx.png")).convert()
    ball_images = [
        pygame.image.load(os.path.join(path, "pics/GunPong/Ball.png")).convert_alpha(),
        pygame.image.load(os.path.join(path, "pics/GunPong/Ballx.png")).convert_alpha(),
        pygame.image.load(os.path.join(path, "pics/GunPong/Ballxx.png")).convert_alpha()
    ]

    # Pre-render background surface
    background = pygame.Surface(screen.get_size())
    background.fill((70, 70, 70))  # FIREARMS color
    background.blit(field_img, (0, 0))
    background = background.convert()

    # Initialize fonts
    font_rounds = pygame.font.SysFont("Times", 40)
    font_fault = pygame.font.SysFont("Times", 150)

    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    ball_group = pygame.sprite.Group()
    shot_group = pygame.sprite.Group()
    ui_group = pygame.sprite.Group()

    # Create ball sprite
    ball = Ball(ball_images, 400, 200)
    ball_group.add(ball)
    all_sprites.add(ball)

    # Create UI sprites
    rounds_text = TextSprite("Rally: 0", font_rounds, (0, 0, 0), 610, 40, (255, 255, 255))
    player1_text = TextSprite("Points: 0", font_rounds, (0, 0, 0), 115, 40, (255, 255, 255))
    player2_text = TextSprite("Points: 0", font_rounds, (0, 0, 0), 1100, 40, (255, 255, 255))
    
    ui_group.add(rounds_text, player1_text, player2_text)
    all_sprites.add(rounds_text, player1_text, player2_text)

    # Game variables
    HIMMELBLAU = (120, 210, 255)
    FIREARMS = (70, 70, 70)
    framerate = 30
    mausx = 0
    mausy = 0
    hit_for_screenshot = False
    offsetBall = 0
    xBall_hit = False
    offsetDiabolo = 9
    xBall_blocked = False
    xPositiv = True
    xNegativ = False
    xCountRounds = 0
    ixBallSpeed = 1
    xFault = False
    iPlayerPointsLeft = 0
    iPlayerPointsRight = 0
    xPlayerLeft = False
    xPlayerRight = False
    xNewRound = False
    listYspeed = (0, 1, 2, 3, 4)
    iyBallSpeed = 0
    xYNegieren = False
    xNewRoundreal = False
    iCountNextRound = 91
    xCountNextRound = True
    iPointsMax = 10
    xGameOver = False
    xActivePlayer = True
    iGetAction = 0
    xGo = False
    Diabolo_Rect = (0, 0)
    ixBallSpeedtmp = 0

    # Create masks for collision detection
    mask_diabolo = pygame.mask.from_surface(diabolo_img)
    mask_ball = pygame.mask.from_surface(ball_images[0])

    def reset_parameter():
        global Diabolo_Rect, mausx, mausy
        Diabolo_Rect = [-20, -20]
        mausx = 0
        mausy = 0

    def button_handler():
        global iGetAction, xGo, xGameOver, xCountRounds, ixBallSpeed, xPositiv, iCountNextRound
        global iPlayerPointsLeft, iPlayerPointsRight
        
        iGetAction = hmsysteme.get_action()
        if iGetAction > 0:
            if iGetAction == 1:  # Enter
                xGo = True
            if iGetAction == 2:  # Restart
                reset_game()

    def reset_game():
        global xGameOver, xCountRounds, ixBallSpeed, xPositiv, iCountNextRound
        global iPlayerPointsLeft, iPlayerPointsRight, xPlayerLeft, xPlayerRight, xCountNextRound
        
        xGameOver = False
        ball.rect.x = 400
        ball.rect.y = 200
        ball.x_speed = 1
        ball.x_positive = True
        xCountRounds = 0
        ixBallSpeed = 1
        xPositiv = True
        iCountNextRound = 91
        iPlayerPointsLeft = 0
        iPlayerPointsRight = 0
        xPlayerLeft = False
        xPlayerRight = False
        xCountNextRound = True

    def update_game_logic():
        global xPlayerLeft, xPlayerRight, iPlayerPointsLeft, iPlayerPointsRight, xGameOver
        global xCountNextRound, iCountNextRound, xCountRounds, ixBallSpeed, xActivePlayer
        global xBall_hit, iyBallSpeed, xPositiv, ixBallSpeedtmp, xYNegieren

        # Update ball position from sprite
        global xBall, yBall
        xBall = ball.rect.x
        yBall = ball.rect.y

        # Score handling
        if xPlayerLeft and not xCountNextRound:
            iPlayerPointsLeft += 1
            xCountNextRound = True
        if xPlayerRight and not xCountNextRound:
            iPlayerPointsRight += 1
            xCountNextRound = True
        if iPlayerPointsRight == iPointsMax or iPlayerPointsLeft == iPointsMax:
            xGameOver = True

        # Ball movement and collision logic
        if not xGameOver and not xCountNextRound:
            # Update ball speeds and direction
            ball.x_speed = ixBallSpeed
            ball.x_positive = xPositiv
            ball.y_speed = iyBallSpeed
            ball.y_negate = xYNegieren

            # Ball hit logic
            if xBall_hit and xPositiv:
                xActivePlayer = False
                xCountRounds += 1
                ixBallSpeedtmp += 1
                if ixBallSpeedtmp == 2:
                    ixBallSpeed += 1
                    ixBallSpeedtmp = 0
                xPositiv = False
                xBall_hit = False
            elif xBall_hit and not xPositiv:
                xActivePlayer = True
                ixBallSpeed += 1
                xCountRounds += 1
                xPositiv = True
                xBall_hit = False

            # Ball blocking logic
            ball.blocked = False
            if xBall < 533 and xActivePlayer:
                ball.blocked = True
            if xBall > 683 and not xActivePlayer:
                ball.blocked = True

            # Y direction changes
            if yBall < 93:
                xYNegieren = True
            if yBall > 533:
                xYNegieren = False

            # Scoring boundaries
            if xBall < 113 + ixBallSpeed and not xCountNextRound:
                xPlayerRight = True
                hit_for_screenshot = True
            if xBall > 1102 - ixBallSpeed and not xCountNextRound:
                xPlayerLeft = True
                hit_for_screenshot = True

        # Update UI texts
        rounds_text.update_text(f"Rally: {xCountRounds}")
        player1_text.update_text(f"Points: {iPlayerPointsLeft}")
        player2_text.update_text(f"Points: {iPlayerPointsRight}")

    def draw_countdown():
        if xCountNextRound and not xGameOver:
            if iCountNextRound > 90:
                countdown_text = TextSprite("Press ENTER", font_rounds, (0, 0, 0), 580, 93, (255, 255, 255))
            elif iCountNextRound > 60:
                countdown_text = TextSprite("2", font_fault, (0, 0, 0), 645, 100, (255, 255, 255))
            elif iCountNextRound > 30:
                countdown_text = TextSprite("1", font_fault, (0, 0, 0), 645, 100, (255, 255, 255))
            elif iCountNextRound >= 0:
                countdown_text = TextSprite("GO!", font_fault, (0, 0, 0), 550, 100, (255, 255, 255))
            else:
                return
            
            screen.blit(countdown_text.image, countdown_text.rect)

    def draw_game_over():
        if xGameOver:
            score1_text = TextSprite(str(iPlayerPointsLeft), font_fault, (0, 0, 0), 300, 300)
            score2_text = TextSprite(str(iPlayerPointsRight), font_fault, (0, 0, 0), 1000, 300)
            restart_text = TextSprite("Press RESTART Button for next Round!", font_rounds, (0, 0, 0), 370, 150, (255, 255, 255))
            
            screen.blit(score1_text.image, score1_text.rect)
            screen.blit(score2_text.image, score2_text.rect)
            screen.blit(restart_text.image, restart_text.rect)

    # Main game loop
    while hmsysteme.game_isactive():
        button_handler()
        iGetAction = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.display.quit()
                pygame.quit()
                return
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                hit_for_screenshot = True
                mausx = event.pos[0]
                mausy = event.pos[1]
                
                # Create shot sprite
                shot = Shot(diabolo_img, mausx, mausy)
                shot_group.add(shot)
                all_sprites.add(shot)
                
                # Collision detection
                offsetBall = (int(mausx - (xBall + offsetDiabolo)), int(mausy - (yBall + offsetDiabolo)))
                if mask_ball.overlap(mask_diabolo, offsetBall) and not ball.blocked:
                    xBall_hit = True
                    iyBallSpeed = random.choice(listYspeed)
                    reset_parameter()

        # Handle external hit detection
        if hmsysteme.hit_detected():
            hit_for_screenshot = True
            pos = hmsysteme.get_pos()
            mausx = pos[0]
            mausy = pos[1]
            
            shot = Shot(diabolo_img, mausx, mausy)
            shot_group.add(shot)
            all_sprites.add(shot)
            
            offsetBall = (int(mausx - (xBall + offsetDiabolo)), int(mausy - (yBall + offsetDiabolo)))
            if mask_ball.overlap(mask_diabolo, offsetBall) and not ball.blocked:
                xBall_hit = True
                iyBallSpeed = random.choice(listYspeed)
                reset_parameter()

        # Update game logic
        update_game_logic()

        # Handle countdown
        if xCountNextRound and xGo and not xGameOver:
            iCountNextRound -= 1
            if iCountNextRound <= 0:
                if xPlayerLeft:
                    ball.rect.x = 400
                    ball.x_positive = True
                    xActivePlayer = True
                if xPlayerRight:
                    ball.rect.x = 766
                    ball.x_positive = False
                    xActivePlayer = False
                ixBallSpeed = 1
                iCountNextRound = 91
                xCountRounds = 0
                xGo = False
                xPlayerLeft = False
                xPlayerRight = False
                xCountNextRound = False

        # Update sprites
        if not xCountNextRound and not xGameOver:
            ball_group.update()
        shot_group.update()

        # Draw everything
        screen.blit(background, (0, 0))  # Draw pre-rendered background once
        
        if not xGameOver:
            if xCountNextRound:
                ui_group.draw(screen)
                draw_countdown()
            else:
                ball_group.draw(screen)
                ui_group.draw(screen)
                
        shot_group.draw(screen)
        
        if xGameOver:
            ui_group.draw(screen)
            draw_game_over()

        # Screenshot handling
        if hit_for_screenshot:
            pygame.display.flip()
            hmsysteme.take_screenshot(screen)
            hit_for_screenshot = False
        else:
            pygame.display.flip()

        clock.tick(framerate)

if __name__ == '__main__':
    main()