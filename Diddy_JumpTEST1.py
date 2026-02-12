import pygame
import random

pygame.init()
screen_width, screen_height = 400, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Doodle Jump - Procédural")

# Joueur
player_x, player_y = screen_width // 2, screen_height // 2
player_w, player_h = 50, 50
player_vy = 0
gravity = 0.6
jump_power = -19

# Paramètres de difficulté
base_min_gap = 60
base_max_gap = 100
base_fragile_chance = 0.3

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY = (135, 206, 250)

# Plateformes : [x, y, largeur, hauteur, type]
# type = "solid" ou "fragile"

def get_difficulty_params(score):
    fragile_chance = base_fragile_chance + min(score / 50.0, 0.5)
    fragile_chance = min(fragile_chance, 0.8)

    difficulty_factor = min(score / 50.0, 1.0)
    min_gap = int(base_min_gap - 20 * difficulty_factor)
    max_gap = int(base_max_gap - 30 * difficulty_factor)

    min_gap = max(30, min_gap)
    max_gap = max(min_gap + 10, max_gap)

    return fragile_chance, min_gap, max_gap

def create_initial_platforms():
    platforms_local = []

    # Grande plateforme de sécurité tout en bas
    safety_platform_y = screen_height - 20
    platforms_local.append([0, safety_platform_y, screen_width, 20, "solid"])

    # Plateformes normales au-dessus
    spawn_y = screen_height - 80
    fragile_chance, min_gap, max_gap = get_difficulty_params(0)

    for i in range(6):
        x = random.randint(0, screen_width - 60)
        y = spawn_y
        plat_type = "solid"
        if random.random() < fragile_chance:
            plat_type = "fragile"
        platforms_local.append([x, y, 60, 12, plat_type])
        spawn_y -= random.randint(min_gap, max_gap)

    return platforms_local

def draw_text(surface, text, size, x, y, color=BLACK, center=True):
    font = pygame.font.SysFont(None, size)
    txt = font.render(text, True, color)
    rect = txt.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(txt, rect)

def show_start_screen():
    waiting = True
    clock = pygame.time.Clock()
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    waiting = False

        screen.fill(SKY)
        draw_text(screen, "DOODLE JUMP", 72, screen_width // 2, screen_height // 4)
        draw_text(screen, "Touches :", 40, screen_width // 2, screen_height // 2 - 30)
        draw_text(screen, "Gauche : Fleche gauche", 30, screen_width // 2, screen_height // 2 + 10)
        draw_text(screen, "Droite : Fleche droite", 30, screen_width // 2, screen_height // 2 + 40)
        draw_text(screen, "Le personnage saute tout seul", 24, screen_width // 2, screen_height // 2 + 80)
        draw_text(screen, "Plateformes grises = fragiles", 24, screen_width // 2, screen_height // 2 + 110)
        draw_text(screen, "ESPACE ou ENTREE pour commencer", 24,
                  screen_width // 2, screen_height * 3 // 4)

        pygame.display.flip()

# --------- PROGRAMME PRINCIPAL ----------

show_start_screen()

platforms = create_initial_platforms()
score = 0
running = True
clock = pygame.time.Clock()

player_x, player_y = screen_width // 2, screen_height // 2
player_vy = 0

while running:
    clock.tick(60)
    screen.fill(SKY)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Mouvements horizontaux
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= 5
    if keys[pygame.K_RIGHT]:
        player_x += 5

    # Gestion des bords
    if player_x < 0:
        player_x = 0
    if player_x > screen_width - player_w:
        player_x = screen_width - player_w

    # Gravité
    player_vy += gravity
    player_y += player_vy

    player_rect = pygame.Rect(player_x, player_y, player_w, player_h)

    # Collision / saut (correction : on repose le joueur sur la plateforme)
    new_platforms = []
    for plat in platforms:
        plat_rect = pygame.Rect(plat[0], plat[1], plat[2], plat[3])

        # collision seulement en DESCENDANT
        if player_vy > 0 and player_rect.colliderect(plat_rect):
            # On vérifie qu'on est au-dessus de la plateforme
            if player_rect.bottom <= plat_rect.bottom:
                # On cale le bas du joueur pile sur le haut de la plateforme
                player_rect.bottom = plat_rect.top
                player_y = player_rect.y
                player_vy = jump_power
                score += 1

                # Supprimer la plateforme si fragile
                if plat[4] == "fragile":
                    continue

        new_platforms.append(plat)

    platforms = new_platforms

    # Scroll vers le bas quand le joueur monte
    if player_y < screen_height // 3:
        dy = screen_height // 3 - player_y
        player_y = screen_height // 3
        player_rect.y = player_y

        for plat in platforms:
            plat[1] += dy

        # Supprimer celles trop basses
        platforms = [p for p in platforms if p[1] < screen_height]

        # Trouver la plus haute
        if platforms:
            highest_y = min(p[1] for p in platforms)
        else:
            highest_y = screen_height

        fragile_chance, min_gap, max_gap = get_difficulty_params(score)

        # Générer jusqu'à 7 plateformes
        while len(platforms) < 7:
            x = random.randint(0, screen_width - 60)
            y = highest_y - random.randint(min_gap, max_gap)
            plat_type = "solid"
            if random.random() < fragile_chance:
                plat_type = "fragile"
            platforms.append([x, y, 60, 12, plat_type])
            highest_y = y

    # Dessin joueur
    pygame.draw.rect(screen, (0, 255, 0), player_rect)

    # Dessin plateformes
    for plat in platforms:
        if plat[2] == screen_width:  # grande plateforme de départ
            color = (100, 100, 255)
        else:
            color = (160, 82, 45) if plat[4] == "solid" else (200, 200, 200)
        pygame.draw.rect(screen, color, (plat[0], plat[1], plat[2], plat[3]))

    # Score
    font = pygame.font.SysFont(None, 28)
    text = font.render(f"Score : {score}", True, BLACK)
    screen.blit(text, (10, 10))

    # Perte
    if player_y > screen_height:
        running = False

    pygame.display.flip()

pygame.quit()
