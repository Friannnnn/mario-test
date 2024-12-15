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
tmx_data = pytmx.load_pygame("level/level1-1.tmx")  # Adjust path to your .tmx file

# Tile size from the Tiled map (usually 32x32 or 64x64)
TILE_SIZE = tmx_data.tilewidth

# Scale factor for tiles
scale_factor = 2  # Increase scale to make tiles larger
scaled_tile_size = TILE_SIZE * scale_factor  # Define scaled tile size

# Player settings
mario_sprites = {
    "small": {
        "idle_right": pygame.image.load("assets/mario-moves/small_idle_right.png"),
        "idle_left": pygame.image.load("assets/mario-moves/small_idle_left.png"),
        "walk_right": [
            pygame.image.load("assets/mario-moves/small_walk3_right.png"),
            pygame.image.load("assets/mario-moves/small_walk2_right.png"),
            pygame.image.load("assets/mario-moves/small_walk1_right.png")
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

# Scaled player settings
for size in mario_sprites:
    for direction in mario_sprites[size]:
        if isinstance(mario_sprites[size][direction], list):
            mario_sprites[size][direction] = [
                pygame.transform.scale(sprite, (sprite.get_width() * scale_factor, sprite.get_height() * scale_factor))
                for sprite in mario_sprites[size][direction]
            ]
        else:
            mario_sprites[size][direction] = pygame.transform.scale(
                mario_sprites[size][direction],
                (mario_sprites[size][direction].get_width() * scale_factor,
                 mario_sprites[size][direction].get_height() * scale_factor)
            )

# Player setup
player = pygame.Rect(100, 495, 100, 100)
player_speed = 3
player_direction = "right"
player_walking = False
player_size = "small"
camera_x = 0
MIDDLE_X = 400  # middle
key_state = {"right": False, "left": False, "jump": False}
jumping = False  
jump_velocity = 0
gravity = 1
jump_height = 15

def draw_map():
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer): 
            for x, y, gid in layer: 
                if gid:  
                    tile_image = tmx_data.get_tile_image_by_gid(gid)  
                    if tile_image:
                       
                        screen_x = (x * scaled_tile_size) - camera_x
                        screen_y = y * scaled_tile_size

                        # Use integer positions for perfect pixel alignment
                        screen.blit(tile_image, (int(screen_x), int(screen_y)))

def find_ground_start(player_rect):
    """Find the y-coordinate for Mario to stand on the ground."""
    tile_x = player_rect.centerx // scaled_tile_size  

    for y in range(player_rect.bottom // scaled_tile_size, tmx_data.height):
        tile_y = y
        tile = tmx_data.layerat(0).tile_at(tile_x, tile_y)  
        if tile and tile.gid == 19:  # Check if the tile's GID is 19 (ground)
            return tile_y * scaled_tile_size - player_rect.height  # Adjust Mario's Y position to the ground
    return player_rect.bottom  # If no ground found, return the default position

# Function to check if Mario is standing on the ground based on the Tiled map
def check_ground_collision(player_rect):
    """Check if Mario is standing on the ground."""
    player_bottom = player_rect.bottom
    tile_x = player_rect.centerx // scaled_tile_size
    tile_y = player_bottom // scaled_tile_size
    tile = tmx_data.layerat(0).tile_at(tile_x, tile_y)  # Get the tile at this position
    if tile and tile.gid == 19:  # Check if the tile's GID is 19 (ground)
        return True
    return False

# Function to update the camera position to follow Mario
def update_camera():
    """Update the camera position to follow Mario."""
    global camera_x

    if player.x > MIDDLE_X:
        camera_x += player_speed

    # Ensure the camera position remains within integer bounds
    camera_x = max(0, camera_x)
    camera_x = min(camera_x, tmx_data.width * scaled_tile_size - WIDTH)

# Game loop
running = True
player.y = find_ground_start(player)  # Set initial position of Mario

while running:
    screen.fill((255, 255, 255))  # Clear screen
    
    # Draw the Tiled map
    draw_map()

    # Update camera position
    update_camera()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:  
                key_state["right"] = True
            if event.key == pygame.K_a:  
                key_state["left"] = True
            if event.key == pygame.K_SPACE and not jumping: 
                jumping = True
                jump_velocity = -jump_height  # Set initial jump velocity
            if event.key == pygame.K_m:  # Toggle mute on 'M' key press
                if music_muted:
                    pygame.mixer.music.set_volume(0.5)  # Restore volume
                else:
                    pygame.mixer.music.set_volume(0.0)  # Mute
                music_muted = not music_muted  # Toggle mute state
            if event.key == pygame.K_q:  
                running = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d:  
                key_state["right"] = False
            if event.key == pygame.K_a: 
                key_state["left"] = False

    # Handle jumping
    if jumping:
        player.y += jump_velocity
        jump_velocity += gravity  # Apply gravity

        # Check if Mario hits the ground
        if check_ground_collision(player):
            jumping = False
            player.y = find_ground_start(player)  # Reset to ground position
            jump_velocity = 0  # Reset jump velocity

    # Determine current sprite based on movement and jumping
    if player_walking:
        if player_direction == "left":
            current_sprite = mario_sprites[player_size]["turn_right_to_left"]
        else:
            current_sprite = mario_sprites[player_size]["turn_left_to_right"]
    elif jumping:
        if player_direction == "right":
            current_sprite = mario_sprites[player_size]["jump_right"]
        else:
            current_sprite = mario_sprites[player_size]["jump_left"]
    else:
        current_sprite = mario_sprites[player_size][f"idle_{player_direction}"]

    # Blit Mario on the screen with the updated coordinates
    screen.blit(current_sprite, (int(player.x - camera_x), int(player.y)))

    pygame.display.flip()  # Update the screen
    clock.tick(60)  # Maintain 60 frames per second

pygame.quit()
