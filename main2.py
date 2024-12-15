import pygame
import pytmx

pygame.init()

pygame.mixer.init()

pygame.mixer.music.load("assets/sounds/overworld.mp3")  
pygame.mixer.music.set_volume(0.5)  
pygame.mixer.music.play(loops=-1, start=0.0)  

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
background = pygame.image.load("assets/mario-moves/level_background.png")
bg_width, bg_height = background.get_size()

scaled_bg_height = HEIGHT
scaled_bg_width = 8000  

background_scaled = pygame.transform.scale(background, (scaled_bg_width, scaled_bg_height))

mario_sprites = {
    "small": {
        "idle_right": pygame.image.load("assets/mario-moves/small_idle_right.png"),
        "idle_left": pygame.image.load("assets/mario-moves/small_idle_left.png"),
        "walk_right": [
            pygame.image.load("assets/mario-moves/small_walk1_right.png"),
            pygame.image.load("assets/mario-moves/small_walk2_right.png"),
            pygame.image.load("assets/mario-moves/small_walk3_right.png")
        ],
        "walk_left": [
            pygame.image.load("assets/mario-moves/small_walk1_left.png"),
            pygame.image.load("assets/mario-moves/small_walk2_left.png"),
            pygame.image.load("assets/mario-moves/small_walk3_left.png")
        ],
        "turn_left_to_right": pygame.image.load("assets/mario-moves/small_turn_left_to_right.png"),
        "turn_right_to_left": pygame.image.load("assets/mario-moves/small_turn_right_to_left.png"),
        "jump_right": pygame.image.load("assets/mario-moves/small_jump_right.png"),
        "jump_left": pygame.image.load("assets/mario-moves/small_jump_left.png")
    },
    "big": {
        "idle_right": pygame.image.load("assets/mario-moves/big_idle_right.png"),
        "idle_left": pygame.image.load("assets/mario-moves/big_idle_left.png"),
        "walk_right": [
            pygame.image.load("assets/mario-moves/big_walk1_right.png"),
            pygame.image.load("assets/mario-moves/big_walk2_right.png"),
            pygame.image.load("assets/mario-moves/big_walk3_right.png")
        ],
        "walk_left": [
            pygame.image.load("assets/mario-moves/big_walk1_left.png"),
            pygame.image.load("assets/mario-moves/big_walk2_left.png"),
            pygame.image.load("assets/mario-moves/big_walk3_left.png")
        ],
        "turn_left_to_right": pygame.image.load("assets/mario-moves/big_turn_left_to_right.png"),
        "turn_right_to_left": pygame.image.load("assets/mario-moves/big_turn_right_to_left.png"),
        "jump_right": pygame.image.load("assets/mario-moves/big_jump_right.png"),
        "jump_left": pygame.image.load("assets/mario-moves/big_jump_left.png")
    }
}

scaling_factor = 2 
for size in mario_sprites:
    for direction in mario_sprites[size]:
        if isinstance(mario_sprites[size][direction], list): 
            mario_sprites[size][direction] = [
                pygame.transform.scale(sprite, (sprite.get_width() * scaling_factor, sprite.get_height() * scaling_factor))
                for sprite in mario_sprites[size][direction]
            ]
        else:
            mario_sprites[size][direction] = pygame.transform.scale(
                mario_sprites[size][direction], 
                (mario_sprites[size][direction].get_width() * scaling_factor, 
                 mario_sprites[size][direction].get_height() * scaling_factor)
            )

def load_map(filename):
    tmx_data = pytmx.load_pygame(filename, pixelalpha=True)
    return tmx_data

def draw_map(tmx_data, surface, scale_factor, camera_x, camera_y):
    camera_rect = pygame.Rect(camera_x, camera_y, scaled_bg_width, scaled_bg_height)
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    tile_width = tmx_data.tilewidth * scale_factor
                    tile_height = tmx_data.tileheight * scale_factor
                    screen_x = x * tile_width
                    screen_y = y * tile_height
                    if camera_rect.colliderect(pygame.Rect(screen_x, screen_y, tile_width, tile_height)):
                        scaled_tile = pygame.transform.scale(tile, (tile_width, tile_height))
                        surface.blit(scaled_tile, (screen_x - camera_x, screen_y - camera_y))

def get_collision_rects(tmx_data, scale_factor):
    collision_rects = []
    for obj in tmx_data.objects:
        if obj.name in ["ground", "bricks", "pipes", "coins"]:
            rect = pygame.Rect(obj.x * scale_factor, obj.y * scale_factor, obj.width * scale_factor, obj.height * scale_factor)
            collision_rects.append(rect)
    return collision_rects


def handle_collisions(player_rect, player_vx, player_vy, collision_rects):
    player_rect.x += player_vx
    for rect in collision_rects:
        if player_rect.colliderect(rect):
            if player_vx > 0:
                player_rect.right = rect.left
            elif player_vx < 0:
                player_rect.left = rect.right

    player_rect.y += player_vy
    on_ground = False
    for rect in collision_rects:
        if player_rect.colliderect(rect):
            if player_vy > 0:
                player_rect.bottom = rect.top
                player_vy = 0
                on_ground = True
            elif player_vy < 0:
                player_rect.top = rect.bottom
                player_vy = 0

    return player_rect, player_vy, on_ground



player = pygame.Rect(100, 495, 100, 100) 
small_hitbox = (100, 100) 
big_hitbox = (100, 200) 
player_speed = 5
player_direction = "right"
prev_direction = "right"
player_walking = False
player_size = "small"  
animation_frame = 0
frame_delay = 3.5
frame_counter = 0

camera_x = 0

MIDDLE_X = 370  # middle 

velocity = 10
deceleration = 0.6  
turn_delay = 0  
max_turn_delay = 10  
acceleration = 0.2 
max_speed = 4 

slide_factor = 0.3 

jumping = False
jump_velocity = 0
jump_acceleration = -1.25  
jump_max_height = 150
jump_min_height = 0 

key_state = {"right": False, "left": False, "jump": False}
music_muted = False


# Game loop
running = True
while running:
    screen.fill((255, 255, 255))
    screen.blit(background_scaled, (-camera_x, 0))



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:  
                key_state["right"] = True
            if event.key == pygame.K_a:  
                key_state["left"] = True
            if event.key == pygame.K_SPACE: 
                if not jumping:  
                    jumping = True
                    jump_velocity = 15
            if event.key == pygame.K_m:  
                if music_muted:
                    pygame.mixer.music.set_volume(0.5)
                else:
                    pygame.mixer.music.set_volume(0.0)
                music_muted = not music_muted
            if event.key == pygame.K_q:  
                running = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d:  
                key_state["right"] = False
            if event.key == pygame.K_a:  
                key_state["left"] = False
            if event.key == pygame.K_SPACE: 
                key_state["jump"] = False

    if player_size == "small":
        player.size = small_hitbox
    else:
        player.size = big_hitbox

    if key_state["right"]:
        if player_direction == "left" and player_walking:
            if turn_delay == 0:
                turn_delay = max_turn_delay
            player_direction = "right"
            player_walking = False
        else:
            if velocity < max_speed:
                velocity += acceleration
            player_walking = True
    elif key_state["left"]:
        if player_direction == "right" and player_walking:
            if turn_delay == 0:
                turn_delay = max_turn_delay
            player_direction = "left"
            player_walking = False
        else:
            if velocity > -max_speed:
                velocity -= acceleration
            player_walking = True
    else:
        player_walking = False

    if not player_walking:
        if velocity > 0:
            velocity -= deceleration
            if velocity < 0:
                velocity = 0
        elif velocity < 0:
            velocity += deceleration
            if velocity > 0:
                velocity = 0

    if velocity == 0:
        velocity -= slide_factor if player_direction == "right" else -slide_factor
        if abs(velocity) < slide_factor:
            velocity = 0

    if jumping:
        player.y -= jump_velocity  
        jump_velocity += jump_acceleration
        if player.y >= 495:
            player.y = 495
            jumping = False
            jump_velocity = 0

    player.x += velocity



    if player.x < 0:
        player.x = 0

    if player.x > MIDDLE_X:
        player.x = MIDDLE_X

    if player.x == MIDDLE_X and player_walking and player_direction == "right":
        if camera_x + WIDTH < scaled_bg_width:
            camera_x += player_speed

    if camera_x + WIDTH > scaled_bg_width:
        camera_x = scaled_bg_width - WIDTH

    if player_walking:
        if turn_delay > 0:
            if player_direction == "left":
                current_sprite = mario_sprites[player_size]["turn_right_to_left"]
            else:
                current_sprite = mario_sprites[player_size]["turn_left_to_right"]
            turn_delay -= 1
        else:
            frame_counter += 1
            if frame_counter >= frame_delay:
                frame_counter = 0
                animation_frame = (animation_frame + 1) % len(mario_sprites[player_size][f"walk_{player_direction}"])
            current_sprite = mario_sprites[player_size][f"walk_{player_direction}"][animation_frame]
    else:
        current_sprite = mario_sprites[player_size][f"idle_{player_direction}"]

    if jumping:
        if player_direction == "right":
            current_sprite = mario_sprites[player_size]["jump_right"]
        else:
            current_sprite = mario_sprites[player_size]["jump_left"]

    screen.blit(current_sprite, (player.x, player.y))
    pygame.display.flip()
    clock.tick(6-0)

pygame.quit()



