import cv2
import mediapipe as mp
import pygame
import sys
import random


mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils


pygame.init()
width, height = 640, 480
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Gesture Controlled Flappy Bird')
clock = pygame.time.Clock()


white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
red = (255, 0, 0)


bird_width, bird_height = 40, 30
bird_x, bird_y = 100, height // 2
bird_speed_y = 0
gravity = 1
jump_speed = -10
fall_speed = 10

bird_image = pygame.image.load("bird.png").convert_alpha()
bird_image = pygame.transform.scale(bird_image, (50, 50))


pipe_width = 60
pipe_height = 300
pipe_gap = 200
pipe_speed = 5
pipe_x = width
pipe_y = random.randint(pipe_gap, height - pipe_gap)


score = 0
highest_score = 0
font = pygame.font.SysFont(None, 35)
pygame.mixer.init()
beep_sound=pygame.mixer.Sound("crash.mp3")
pass_sound=pygame.mixer.Sound("pass.mp3")
wow_sound=pygame.mixer.Sound("wow.mp3")

def show_score(score, highest_score):
    score_text = font.render(f"Score: {score} | Highest Score: {highest_score}", True, black)
    screen.blit(score_text, (10, 10))

def is_thumbs_up(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    return thumb_tip.y < thumb_mcp.y and thumb_tip.y < index_tip.y

def is_thumbs_down(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    return thumb_tip.y > thumb_mcp.y and thumb_tip.y > index_tip.y

def draw_play_button(screen):
    pygame.draw.polygon(screen, red, [(width // 2 - 20, height // 2 - 20), 
                                      (width // 2 - 20, height // 2 + 20), 
                                      (width // 2 + 20, height // 2)])
    text = font.render("Welcome to gesture based Flappy Bird", True, black)
    screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - 100))

def draw_replay_button(screen):
    pygame.draw.rect(screen, red, (width // 2 - 50, height // 2 - 25, 100, 50))
    text = font.render("Replay", True, black)
    screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - 10))

def blur_surface(surface, radius):
    array = pygame.surfarray.array3d(surface)
    array = cv2.blur(array, (radius, radius))
    return pygame.surfarray.make_surface(array)

def load_highest_score():
    try:
        with open("highest_score.txt", "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0

def save_highest_score(score):
    with open("highest_score.txt", "w") as file:
        file.write(str(score))





cap = cv2.VideoCapture(0)
highest_score = load_highest_score()

game_started = False
while not game_started:
    screen.fill(white)
    success, image = cap.read()
    if not success:
        break
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    draw_play_button(screen)
    
    frame_surface = pygame.surfarray.make_surface(image)
    frame_surface = pygame.transform.rotate(frame_surface, -90)
    frame_surface = pygame.transform.flip(frame_surface, True, False)
    blurred_surface = blur_surface(frame_surface, 15)
    screen.blit(blurred_surface, (0, 0))
    draw_play_button(screen)
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            play_button_rect = pygame.Rect(width // 2 - 20, height // 2 - 20, 40, 40)
            if play_button_rect.collidepoint(mouse_pos):
                game_started = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()

    success, image = cap.read()
    if not success:
        break

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    gesture_detected = None
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            if is_thumbs_up(hand_landmarks):
                gesture_detected = 'up'
            elif is_thumbs_down(hand_landmarks):
                gesture_detected = 'down'

    if gesture_detected == 'up':
        bird_speed_y = jump_speed
    elif gesture_detected == 'down':
        bird_speed_y = fall_speed
    else:
        bird_speed_y += gravity

    bird_y += bird_speed_y
    
    screen.blit(bird_image, (bird_x, bird_y))
    bird_rect = pygame.Rect(bird_x, bird_y, bird_width, bird_height)

    pipe_x -= pipe_speed
    if pipe_x < -pipe_width:
        pipe_x = width
        pipe_y = random.randint(pipe_gap, height - pipe_gap)
        score += 1
        if(score==highest_score):
            pygame.mixer.Sound.play(wow_sound)
        else:
            pygame.mixer.Sound.play(pass_sound)
    top_pipe_rect = pygame.Rect(pipe_x, pipe_y - pipe_gap - pipe_height, pipe_width, pipe_height)
    bottom_pipe_rect = pygame.Rect(pipe_x, pipe_y, pipe_width, pipe_height)

    if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect) or \
       bird_y < 0 or bird_y > height - bird_height:
        
        if score > highest_score:
            highest_score = score
            save_highest_score(highest_score)
        score = 0
        bird_y = height // 2
        bird_speed_y = 0
        pipe_x = width
        pipe_y = random.randint(pipe_gap, height - pipe_gap)
        pygame.mixer.Sound.play(beep_sound)

 
        while True:
            screen.fill(white)
            screen.blit(blurred_surface, (0, 0))
            draw_replay_button(screen)
            show_score(score, highest_score)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cap.release()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    replay_button_rect = pygame.Rect(width // 2 - 50, height // 2 - 25, 100, 50)
                    if replay_button_rect.collidepoint(mouse_pos):
                        pipe_x = width
                        pipe_y = random.randint(pipe_gap, height - pipe_gap)
                        bird_y = height // 2
                        break
            else:
                continue
            break

    screen.fill(white)

    screen.blit(bird_image, (bird_x, bird_y))
    pygame.draw.rect(screen, red, top_pipe_rect)
    pygame.draw.rect(screen, red, bottom_pipe_rect)
    show_score(score, highest_score)
    pygame.display.flip()
    clock.tick(30)

    cv2.imshow('Hand Tracking', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
      
