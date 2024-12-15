import pygame
import pytmx

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60
PLAYER_WIDTH = 16
PLAYER_HEIGHT = 16
GRAVITY = 0.5
JUMP_STRENGTH = -8 
MOVE_SPEED = 3
SCALE_FACTOR = 2  # scale factor for ghics
MIDDLE_X = SCREEN_WIDTH // 2  # middle of the screen (400)

pygame.init()

pygame.mixer.music.load("assets/sounds/overworld.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(loops=-1, start=0.0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mary")
clock = pygame.time.Clock()

# mario sprites
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

def scale_mario_sprites(mario_size):
    for key in mario_sprites[mario_size]:
        if isinstance(mario_sprites[mario_size][key], list):
            mario_sprites[mario_size][key] = [pygame.transform.scale(img, (img.get_width() * SCALE_FACTOR, img.get_height() * SCALE_FACTOR)) for img in mario_sprites[mario_size][key]]
        else:
            mario_sprites[mario_size][key] = pygame.transform.scale(mario_sprites[mario_size][key], (mario_sprites[mario_size][key].get_width() * SCALE_FACTOR, mario_sprites[mario_size][key].get_height() * SCALE_FACTOR))

def load_map(filename):
    tmx_data = pytmx.load_pygame(filename, pixelalpha=True)
    return tmx_data

def draw_map(tmx_data, surface, scale_factor, camera_x, camera_y):
    camera_rect = pygame.Rect(camera_x, camera_y, SCREEN_WIDTH, SCREEN_HEIGHT)
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

def main():
    tmx_data = load_map("level/level1-1.tmx")
    collision_rects = get_collision_rects(tmx_data, SCALE_FACTOR)

    player_rect = pygame.Rect(100, 100, PLAYER_WIDTH * SCALE_FACTOR, PLAYER_HEIGHT * SCALE_FACTOR)
    player_vx = 0
    player_vy = 0
    on_ground = False
    player_size = "small"  # Start as small Mario

    facing_right = True

    camera_x = 0
    camera_y = 0

    running = True
    frame_counter = 0

    scale_mario_sprites(player_size)

    mario_at_middle = False  

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player_vx = 0

        if keys[pygame.K_a]:
            player_vx = -MOVE_SPEED * SCALE_FACTOR
            facing_right = False
            mario_at_middle = False  

        if keys[pygame.K_d]:
            player_vx = MOVE_SPEED * SCALE_FACTOR
            facing_right = True

        if keys[pygame.K_SPACE] and on_ground:
            player_vy = JUMP_STRENGTH * SCALE_FACTOR
            on_ground = False

        player_vy += GRAVITY
        player_rect, player_vy, on_ground = handle_collisions(player_rect, player_vx, player_vy, collision_rects)

        # Prevent Mario from going off-screen
        if player_rect.left < 0:
            player_rect.left = 0
        if player_rect.right > 4000:
            player_rect.right = SCREEN_WIDTH
        if player_rect.top < 0:
            player_rect.top = 0
        if player_rect.bottom > SCREEN_HEIGHT:
            player_rect.bottom = SCREEN_HEIGHT
            player_vy = 0
            on_ground = True

        if player_rect.left < 0:
            player_rect.left = 0
        if player_rect.bottom > SCREEN_HEIGHT:
            player_rect.bottom = SCREEN_HEIGHT
            player_vy = 0
            on_ground = True

        if player_rect.centerx >= MIDDLE_X and player_vx > 0:
            camera_adjust = min(player_rect.centerx - MIDDLE_X, MOVE_SPEED * SCALE_FACTOR)
            camera_x += camera_adjust

        max_camera_x = (tmx_data.width * tmx_data.tilewidth * SCALE_FACTOR - SCREEN_WIDTH)
        if camera_x < 0:
            camera_x = 0
        elif camera_x > max_camera_x:
            camera_x = max_camera_x

        screen.fill((0, 0, 0))

        draw_map(tmx_data, screen, SCALE_FACTOR, camera_x, camera_y)

        sprite_list = None
        if player_vx != 0:
            sprite_list = mario_sprites[player_size]["walk_right"] if facing_right else mario_sprites[player_size]["walk_left"]
        elif player_vy != 0:
            sprite_list = [mario_sprites[player_size]["jump_right"] if facing_right else mario_sprites[player_size]["jump_left"]]
        else:
            sprite_list = [mario_sprites[player_size]["idle_right"] if facing_right else mario_sprites[player_size]["idle_left"]]

        sprite_index = (frame_counter // 10) % len(sprite_list)
        player_surface = sprite_list[sprite_index]

        screen.blit(player_surface, (player_rect.x - camera_x, player_rect.y - camera_y))

        pygame.display.flip()
        clock.tick(FPS)
        frame_counter += 1

    pygame.quit()

if __name__ == "__main__":
    main()