import pygame
import random
import math
import sys

# Inicialização do Pygame
pygame.init()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("Tiradentes Run & Gun - Entrega Perigosa")
clock = pygame.time.Clock()

# Cores
BACKGROUND = (40, 25, 60)
RED = (220, 60, 50)
GREEN = (50, 200, 100)
BLUE = (60, 150, 220)
YELLOW = (255, 220, 70)
PURPLE = (180, 70, 220)
ORANGE = (255, 150, 50)
BROWN = (150, 100, 70)

# Texturas 3D estilizadas
def create_deliveryman_texture():
    surface = pygame.Surface((50, 80), pygame.SRCALPHA)
    # Corpo (jaqueta)
    pygame.draw.polygon(surface, BLUE, [(25, 10), (10, 30), (40, 30)])
    pygame.draw.rect(surface, BLUE, (10, 30, 30, 40))
    # Calças
    pygame.draw.rect(surface, BROWN, (10, 70, 30, 10))
    # Cabeça
    pygame.draw.circle(surface, (240, 200, 180), (25, 10), 8)
    # Capacete
    pygame.draw.rect(surface, YELLOW, (15, 0, 20, 10), 0, 5)
    # Mochila
    pygame.draw.rect(surface, RED, (40, 35, 8, 20), 0, 3)
    return surface

def create_enemy_texture():
    surface = pygame.Surface((45, 45), pygame.SRCALPHA)
    # Corpo
    pygame.draw.rect(surface, RED, (5, 10, 35, 35), 0, 10)
    # Cabeça
    pygame.draw.circle(surface, (200, 150, 130), (22, 10), 7)
    # Óculos
    pygame.draw.rect(surface, (30, 30, 40), (10, 8, 24, 5))
    pygame.draw.line(surface, (200, 200, 200), (22, 8), (22, 13), 2)
    # Arma
    pygame.draw.rect(surface, (100, 100, 100), (0, 20, 15, 5))
    return surface

def create_delivery_texture():
    surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    # Pacote
    pygame.draw.rect(surface, GREEN, (0, 0, 30, 30), 0, 5)
    pygame.draw.rect(surface, (200, 255, 200), (5, 5, 20, 20))
    # Logo
    pygame.draw.circle(surface, RED, (15, 15), 5)
    return surface

def create_bullet_texture():
    surface = pygame.Surface((15, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(surface, YELLOW, (0, 0, 15, 8))
    pygame.draw.ellipse(surface, ORANGE, (3, 2, 9, 4))
    return surface

def create_motorcycle_texture():
    surface = pygame.Surface((80, 40), pygame.SRCALPHA)
    # Corpo principal
    pygame.draw.ellipse(surface, RED, (0, 10, 80, 20))
    # Rodas
    pygame.draw.circle(surface, (40, 40, 40), (15, 30), 10)
    pygame.draw.circle(surface, (40, 40, 40), (65, 30), 10)
    # Detalhes
    pygame.draw.rect(surface, (200, 200, 200), (40, 5, 30, 10))
    return surface

# Classe do Jogador (Entregador)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.base_image = create_deliveryman_texture()
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(500, 350))
        self.speed = 5
        self.health = 100
        self.last_shot = 0
        self.direction = 1
        self.motorcycle_mode = False
        self.motorcycle_timer = 0
        self.score = 0
        self.deliveries = 0

    def update(self, keys):
        # Ativar modo moto
        if keys[pygame.K_m] and self.motorcycle_timer <= 0:
            self.motorcycle_mode = True
            self.motorcycle_timer = 300  # 5 segundos
            self.speed = 10
            self.image = create_motorcycle_texture()
            old_center = self.rect.center
            self.rect = self.image.get_rect(center=old_center)
        
        # Desativar modo moto quando o timer acabar
        if self.motorcycle_mode and self.motorcycle_timer <= 0:
            self.motorcycle_mode = False
            self.speed = 5
            self.image = self.base_image.copy()
            old_center = self.rect.center
            self.rect = self.image.get_rect(center=old_center)
        
        if self.motorcycle_timer > 0:
            self.motorcycle_timer -= 1
        
        # Movimentação
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = -1
        if keys[pygame.K_d] and self.rect.right < 1000:
            self.rect.x += self.speed
            self.direction = 1
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < 700:
            self.rect.y += self.speed

    def shoot(self, bullets):
        if self.motorcycle_mode:
            return  # Não pode atirar na moto
            
        now = pygame.time.get_ticks()
        if now - self.last_shot > 300:  # Cooldown de 300ms
            offset = 25 if self.direction == 1 else -25
            bullet = Bullet(self.rect.centerx + offset, self.rect.centery, self.direction)
            bullets.add(bullet)
            self.last_shot = now

# Classe dos Projéteis
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = create_bullet_texture()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10 * direction
        self.direction = direction

    def update(self):
        self.rect.x += self.speed
        if (self.direction == 1 and self.rect.left > 1000) or \
           (self.direction == -1 and self.rect.right < 0):
            self.kill()

# Classe dos Inimigos
class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_x):
        super().__init__()
        self.image = create_enemy_texture()
        self.rect = self.image.get_rect()
        
        # Posicionar fora da tela na direção do jogador
        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            self.rect.right = 0
            self.rect.y = random.randint(50, 650)
        elif side == "right":
            self.rect.left = 1000
            self.rect.y = random.randint(50, 650)
        elif side == "top":
            self.rect.bottom = 0
            self.rect.x = random.randint(50, 950)
        else:  # bottom
            self.rect.top = 700
            self.rect.x = random.randint(50, 950)
            
        # Calcular direção para o jogador
        dx = player_x - self.rect.centerx
        dy = 350 - self.rect.centery  # Centro da tela
        dist = max(1, math.sqrt(dx*dx + dy*dy))
        self.vx = dx / dist * 3
        self.vy = dy / dist * 3

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # Remover se sair da tela
        if (self.rect.right < 0 or self.rect.left > 1000 or 
            self.rect.bottom < 0 or self.rect.top > 700):
            self.kill()

# Sistema de entregas
class Delivery(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = create_delivery_texture()
        self.rect = self.image.get_rect(
            center=(random.randint(100, 900), random.randint(100, 600)))
        self.float_offset = random.random() * 10
        self.float_speed = random.uniform(0.05, 0.1)

    def update(self):
        # Animação de flutuação
        self.float_offset += self.float_speed
        self.rect.y += math.sin(self.float_offset) * 0.5

# Classe de Explosão
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = 5
        self.image = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ORANGE, (self.size, self.size), self.size)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 20

    def update(self):
        self.lifetime -= 1
        self.size += 1
        self.image = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        alpha = min(255, self.lifetime * 12)
        pygame.draw.circle(self.image, (255, 150, 50, alpha), 
                          (self.size, self.size), self.size)
        if self.lifetime <= 0:
            self.kill()

# Efeitos visuais de fundo
class BackgroundElement:
    def __init__(self):
        self.x = random.randint(0, 1000)
        self.y = random.randint(0, 700)
        self.size = random.randint(5, 20)
        self.color = (
            random.randint(50, 100),
            random.randint(40, 80),
            random.randint(60, 120)
        )
        self.speed = random.uniform(0.1, 0.5)
        
    def update(self):
        self.y += self.speed
        if self.y > 700:
            self.y = 0
            self.x = random.randint(0, 1000)
            
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, int(self.y)), self.size)

# Criação de grupos
player = Player()
player_group = pygame.sprite.Group(player)

bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
deliveries = pygame.sprite.Group()
explosions = pygame.sprite.Group()

# Criar elementos de fundo
bg_elements = [BackgroundElement() for _ in range(30)]

# Criação de entregas
for _ in range(5):
    deliveries.add(Delivery())

# Sistema de spawn de inimigos
enemy_spawn_timer = 0
font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont(None, 72)

# Loop principal do jogo
running = True
game_over = False
while running:
    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not player.motorcycle_mode and not game_over:
                player.shoot(bullets)
            if event.key == pygame.K_r and game_over:
                # Reiniciar o jogo
                player = Player()
                player_group = pygame.sprite.Group(player)
                bullets.empty()
                enemies.empty()
                deliveries.empty()
                explosions.empty()
                for _ in range(5):
                    deliveries.add(Delivery())
                game_over = False
    
    if game_over:
        # Renderização de tela de game over
        screen.fill((20, 10, 30))
        
        # Desenhar elementos de fundo
        for element in bg_elements:
            element.draw(screen)
        
        # Texto de game over
        game_over_text = title_font.render("FIM DE JOGO", True, RED)
        score_text = font.render(f"Pontuação Final: {player.score}", True, YELLOW)
        delivery_text = font.render(f"Entregas Realizadas: {player.deliveries}", True, GREEN)
        restart_text = font.render("Pressione R para Reiniciar", True, BLUE)
        
        screen.blit(game_over_text, (500 - game_over_text.get_width()//2, 200))
        screen.blit(score_text, (500 - score_text.get_width()//2, 300))
        screen.blit(delivery_text, (500 - delivery_text.get_width()//2, 350))
        screen.blit(restart_text, (500 - restart_text.get_width()//2, 450))
        
        pygame.display.flip()
        clock.tick(60)
        continue
    
    # Input do teclado
    keys = pygame.key.get_pressed()
    player.update(keys)
    
    # Atualização de elementos
    bullets.update()
    enemies.update()
    deliveries.update()
    explosions.update()
    
    # Atualizar elementos de fundo
    for element in bg_elements:
        element.update()
    
    # Spawn de inimigos
    enemy_spawn_timer -= 1
    if enemy_spawn_timer <= 0:
        enemies.add(Enemy(player.rect.centerx))
        enemy_spawn_timer = max(10, 60 - player.score // 50)  # Aumenta dificuldade
    
    # Colisões
    # Balas atingem inimigos
    hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
    for hit in hits:
        player.score += 15
        explosions.add(Explosion(hit.rect.centerx, hit.rect.centery))
    
    # Jogador atingido por inimigos
    hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in hits:
        player.health -= 15
        explosions.add(Explosion(hit.rect.centerx, hit.rect.centery))
        if player.health <= 0:
            game_over = True
    
    # Entrega de pacotes
    deliveries_hit = pygame.sprite.spritecollide(player, deliveries, True)
    for delivery in deliveries_hit:
        player.score += 100
        player.deliveries += 1
        player.health = min(100, player.health + 20)  # Recupera saúde
        explosions.add(Explosion(delivery.rect.centerx, delivery.rect.centery))
        # Criar nova entrega
        deliveries.add(Delivery())
    
    # Renderização
    screen.fill(BACKGROUND)
    
    # Desenhar elementos de fundo
    for element in bg_elements:
        element.draw(screen)
    
    # Desenhar elementos do jogo
    deliveries.draw(screen)
    bullets.draw(screen)
    enemies.draw(screen)
    explosions.draw(screen)
    player_group.draw(screen)
    
    # UI
    # Barra de saúde
    pygame.draw.rect(screen, (100, 20, 20), (20, 20, 204, 24))
    pygame.draw.rect(screen, GREEN, (22, 22, player.health * 2, 20))
    health_text = font.render(f"SAÚDE: {player.health}", True, (240, 240, 240))
    screen.blit(health_text, (30, 23))
    
    # Barra de moto
    if player.motorcycle_timer > 0:
        moto_width = player.motorcycle_timer // 3
        pygame.draw.rect(screen, (40, 40, 60), (20, 60, 204, 14))
        pygame.draw.rect(screen, PURPLE, (22, 62, moto_width, 10))
    
    # Contadores
    score_text = font.render(f"PONTOS: {player.score}", True, YELLOW)
    delivery_text = font.render(f"ENTREGAS: {player.deliveries}", True, BLUE)
    screen.blit(score_text, (800, 20))
    screen.blit(delivery_text, (800, 60))
    
    # Instruções
    if not player.motorcycle_mode:
        controls_text = font.render("M: Moto  ESPAÇO: Atirar", True, (200, 200, 200))
        screen.blit(controls_text, (500 - controls_text.get_width()//2, 650))
    else:
        controls_text = font.render("MOTO ATIVADA - Velocidade aumentada!", True, ORANGE)
        screen.blit(controls_text, (500 - controls_text.get_width()//2, 650))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()