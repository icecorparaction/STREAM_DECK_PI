import pygame
import sys
import os
import math

# Настройки экрана
SCREEN_W, SCREEN_H = 800, 590
GRID_COLS = 3
GRID_ROWS = 2
ICON_SIZE = 100
PADDING = 50
PAGE_COUNT = 2

# Цвета Steam Deck + Raspberry Pi
DECK_BG = (10, 14, 20)
HIGHLIGHT_COLOR = (62, 126, 180)
TEXT_COLOR = (230, 230, 230)
GRADIENT_COLOR = (40, 44, 52, 180)
RASPBERRY_RED = (195, 42, 46)
TASKBAR_HEIGHT = 0
DRAG_COLOR = (62, 126, 180, 180)

# Приложения
APPS = [
    ("YouTube", "youtube.png", "youtube"),
    ("Minecraft", "minecraft.png", "tlauncher"),
    ("CapCut", "capcut.png", "capcut"),
    ("Браузер", "browser.png", "browser"),
    ("Файлы", "filemanager.png", "filemanager"),
    ("Терминал", "terminal.png", "terminal"),
    ("Настройки", "settings.png", "settings"),
    ("Громкость ↑", "volume_up.png", "volume_up"),
    ("Громкость ↓", "volume_down.png", "volume_down"),
    ("Яркость ↑", "brightness_up.png", "brightness_up"),
    ("Яркость ↓", "brightness_down.png", "brightness_down"),
    ("Выход", "exit.png", "exit")
]

# Pygame init
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
pygame.display.set_caption("Steam Deck Launcher")
font = pygame.font.SysFont("Segoe UI", 24)
small_font = pygame.font.SysFont("Segoe UI", 14)
clock = pygame.time.Clock()

# Загрузка фоновой текстуры
background = pygame.image.load("background.jpg")
background = pygame.transform.scale(background, (SCREEN_W, SCREEN_H))

# Создаем градиентный оверлей
def create_gradient_surface():
    gradient = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    for y in range(SCREEN_H):
        alpha = int(180 * (1 - math.exp(-y / (SCREEN_H / 2))))
        pygame.draw.line(gradient, (*GRADIENT_COLOR[:3], alpha), (0, y), (SCREEN_W, y))
    return gradient

gradient_overlay = create_gradient_surface()

# Загрузка иконок
icon_path = "icons"
icons = []
for app in APPS:
    try:
        icon_img = pygame.image.load(os.path.join(icon_path, app[1])).convert_alpha()
        icon_img = pygame.transform.smoothscale(icon_img, (ICON_SIZE, ICON_SIZE))
        icons.append(icon_img)
    except:
        placeholder = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(placeholder, (100, 100, 100), (0, 0, ICON_SIZE, ICON_SIZE), 2)
        icons.append(placeholder)

# Создаем увеличенные иконки
enlarged_icons = []
for icon in icons:
    enlarged = pygame.transform.smoothscale(icon, (int(ICON_SIZE * 1.15), int(ICON_SIZE * 1.15)))
    enlarged_icons.append(enlarged)

current_page = 0
swipe_start = None
hover_index = None
# Переменные для перетаскивания
dragging = False
drag_index = None
drag_icon = None
drag_pos = (0, 0)
drop_target = None
drop_highlight = None
drag_start_pos = None
DRAG_THRESHOLD = 5  # Порог для начала перетаскивания

def draw_selected_highlight(center, size):
    highlight_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(highlight_surf, (*HIGHLIGHT_COLOR, 60), (size//2, size//2), size//2)
    screen.blit(highlight_surf, (center[0]-size//2, center[1]-size//2))

def draw_drop_highlight(center, size):
    highlight_surf = pygame.Surface((size+20, size+20), pygame.SRCALPHA)
    pygame.draw.rect(highlight_surf, (*HIGHLIGHT_COLOR, 120), (0, 0, size+20, size+20), 5, border_radius=15)
    screen.blit(highlight_surf, (center[0]-(size+20)//2, center[1]-(size+20)//2))

def draw_taskbar():
    return

def get_icon_position(index):
    if index is None:
        return (0, 0)
    
    page = index // (GRID_COLS * GRID_ROWS)
    if page != current_page:
        return (0, 0)
    
    idx_in_page = index % (GRID_COLS * GRID_ROWS)
    col = idx_in_page % GRID_COLS
    row = idx_in_page // GRID_COLS

    x = PADDING + col * ((SCREEN_W - 2 * PADDING) // GRID_COLS)
    y = TASKBAR_HEIGHT + PADDING + row * ((SCREEN_H - TASKBAR_HEIGHT - 2 * PADDING) // GRID_ROWS)
    return (x, y)

def get_icon_center(index):
    x, y = get_icon_position(index)
    return (x + ICON_SIZE // 2, y + ICON_SIZE // 2)

def get_icon_under_mouse():
    mouse_pos = pygame.mouse.get_pos()
    if mouse_pos[1] < TASKBAR_HEIGHT:
        return -1
    
    idx_base = current_page * GRID_COLS * GRID_ROWS
    for idx, icon in enumerate(icons[idx_base:idx_base + GRID_COLS*GRID_ROWS]):
        col = idx % GRID_COLS
        row = idx // GRID_COLS
        x = PADDING + col * ((SCREEN_W - 2 * PADDING) // GRID_COLS)
        y = TASKBAR_HEIGHT + PADDING + row * ((SCREEN_H - TASKBAR_HEIGHT - 2 * PADDING) // GRID_ROWS)
        rect = pygame.Rect(x, y, ICON_SIZE, ICON_SIZE)
        if rect.collidepoint(mouse_pos):
            return idx_base + idx
    return None

def draw_page(page_index):
    screen.blit(background, (0, 0))
    screen.blit(gradient_overlay, (0, 0))
    
    apps_on_page = APPS[page_index*GRID_COLS*GRID_ROWS:(page_index+1)*GRID_COLS*GRID_ROWS]
    icons_on_page = icons[page_index*GRID_COLS*GRID_ROWS:(page_index+1)*GRID_COLS*GRID_ROWS]
    enlarged_on_page = enlarged_icons[page_index*GRID_COLS*GRID_ROWS:(page_index+1)*GRID_COLS*GRID_ROWS]

    for idx, (app, icon, big_icon) in enumerate(zip(apps_on_page, icons_on_page, enlarged_on_page)):
        global_idx = page_index*GRID_COLS*GRID_ROWS + idx
        
        if dragging and global_idx == drag_index:
            continue
            
        col = idx % GRID_COLS
        row = idx // GRID_COLS

        x = PADDING + col * ((SCREEN_W - 2 * PADDING) // GRID_COLS)
        y = TASKBAR_HEIGHT + PADDING + row * ((SCREEN_H - TASKBAR_HEIGHT - 2 * PADDING) // GRID_ROWS)
        center_pos = (x + ICON_SIZE // 2, y + ICON_SIZE // 2)
        
        if hover_index == global_idx:
            draw_selected_highlight(center_pos, int(ICON_SIZE * 1.3))
            screen.blit(big_icon, big_icon.get_rect(center=center_pos))
        else:
            screen.blit(icon, icon.get_rect(center=center_pos))

        label = font.render(app[0], True, TEXT_COLOR)
        label_rect = label.get_rect(center=(center_pos[0], center_pos[1] + ICON_SIZE//2 + 20))
        screen.blit(label, label_rect)
    
    if drop_highlight:
        draw_drop_highlight(drop_highlight, ICON_SIZE)
    
    if dragging and drag_icon:
        transparent_icon = drag_icon.copy()
        transparent_icon.fill((255, 255, 255, 180), None, pygame.BLEND_RGBA_MULT)
        screen.blit(transparent_icon, transparent_icon.get_rect(center=drag_pos))
    
    if PAGE_COUNT > 1:
        for i in range(PAGE_COUNT):
            color = HIGHLIGHT_COLOR if i == page_index else (100, 100, 100)
            pygame.draw.circle(screen, color, (SCREEN_W//2 - (PAGE_COUNT-1)*10 + i*20, SCREEN_H - 20), 6)
    
    draw_taskbar()

    pygame.display.flip()

def main():
    global current_page, swipe_start, hover_index
    global dragging, drag_index, drag_icon, drag_pos, drop_target, drop_highlight, drag_start_pos
    
    while True:
        if not dragging:
            hover_index = get_icon_under_mouse()
        draw_page(current_page)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    idx = get_icon_under_mouse()
                    
                    if idx is not None and idx >= 0:
                        # Запоминаем позицию для определения перетаскивания
                        drag_start_pos = event.pos
                        drag_index = idx
                        drag_icon = enlarged_icons[idx]
                    
                    elif idx == -1:  # Клик по панели задач
                        pass
                    
                elif event.button == 4:  # колесо вверх
                    current_page = max(0, current_page - 1)
                elif event.button == 5:  # колесо вниз
                    current_page = min(PAGE_COUNT - 1, current_page + 1)
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    idx = get_icon_under_mouse()
                    
                    if dragging:
                        # Завершение перетаскивания
                        dragging = False
                        
                        if drop_target is not None and drop_target != drag_index:
                            # Меняем местами приложения
                            APPS[drag_index], APPS[drop_target] = APPS[drop_target], APPS[drag_index]
                            icons[drag_index], icons[drop_target] = icons[drop_target], icons[drag_index]
                            enlarged_icons[drag_index], enlarged_icons[drop_target] = enlarged_icons[drop_target], enlarged_icons[drag_index]
                        
                        drag_index = None
                        drag_icon = None
                        drop_target = None
                        drop_highlight = None
                    
                    elif drag_start_pos and idx == drag_index:
                        # Обработка клика (если не было перетаскивания)
                        cmd = APPS[idx][2]
                        print(cmd, flush=True)
                        if cmd == "exit":
                            pygame.quit(); sys.exit()
                    
                    drag_start_pos = None
                    
            elif event.type == pygame.MOUSEMOTION:
                if drag_start_pos and drag_index is not None:
                    # Проверяем, началось ли перетаскивание
                    dx = abs(event.pos[0] - drag_start_pos[0])
                    dy = abs(event.pos[1] - drag_start_pos[1])
                    
                    if not dragging and (dx > DRAG_THRESHOLD or dy > DRAG_THRESHOLD):
                        dragging = True
                        drop_highlight = get_icon_center(drag_index)
                
                if dragging:
                    # Обновление позиции перетаскиваемой иконки
                    drag_pos = event.pos
                    
                    # Поиск цели для перемещения
                    target_idx = get_icon_under_mouse()
                    if target_idx is not None and target_idx != drag_index:
                        drop_target = target_idx
                        drop_highlight = get_icon_center(target_idx)
                    else:
                        drop_target = None
                        drop_highlight = None
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_page = max(0, current_page - 1)
                elif event.key == pygame.K_RIGHT:
                    current_page = min(PAGE_COUNT - 1, current_page + 1)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                    
            elif event.type == pygame.FINGERDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                swipe_start = pygame.mouse.get_pos()
                
            elif event.type == pygame.FINGERUP or event.type == pygame.MOUSEBUTTONUP:
                if not dragging and swipe_start:
                    end_x = pygame.mouse.get_pos()[0]
                    delta = swipe_start[0] - end_x
                    if delta > 50:
                        current_page = min(PAGE_COUNT - 1, current_page + 1)
                    elif delta < -50:
                        current_page = max(0, current_page - 1)
                    swipe_start = None
                    
        clock.tick(15)

if __name__ == "__main__":
    main()
