

import pygame, json, sys, time, os, random
### MODIFIED - Import datetime and timedelta for timer
from datetime import date, datetime, timedelta

# -------------------- Case-Insensitive File Loading --------------------
def load_file_case_insensitive(file_path):
    """
    Attempts to load a file in a case-insensitive manner.
    Returns the correct path if found, None if not found.
    """
    if os.path.exists(file_path):
        return file_path
    
    directory = os.path.dirname(file_path)
    target_filename = os.path.basename(file_path)
    
    if not directory:
        directory = "."
    
    if not os.path.exists(directory):
        return None
    
    try:
        for actual_filename in os.listdir(directory):
            if actual_filename.lower() == target_filename.lower():
                return os.path.join(directory, actual_filename)
    except OSError:
        pass
    
    return None

def safe_image_load(file_path):
    """
    Safely loads an image with case-insensitive file matching.
    """
    correct_path = load_file_case_insensitive(file_path)
    if correct_path:
        return pygame.image.load(correct_path)
    else:
        raise pygame.error(f"File not found: {file_path}")

def safe_json_load(file_path):
    """
    Safely loads a JSON file with case-insensitive file matching.
    """
    correct_path = load_file_case_insensitive(file_path)
    if correct_path:
        with open(correct_path) as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"File not found: {file_path}")

# -------------------- Initialization --------------------
pygame.init()
pygame.mixer.init()
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Raise Your Pet")

# --- Set to True to see collision boxes for player and fences.
DEBUG_MODE = False

# --- Colors ---
WHITE = (255, 255, 255); GRAY = (100, 100, 100); LOADING_BAR = (200, 200, 200)
TEXT_COLOR = (92, 53, 15); PANEL_FILL_COLOR = (251, 224, 153); PANEL_BORDER_COLOR = (140, 72, 32)
BUTTON_HOVER_COLOR = (255, 170, 70)
LOCKED_SLOT_COLOR = (211, 184, 123)
DISABLED_COLOR = (180, 180, 180)
READY_COLOR = (100, 255, 100)
HEALTH_COLOR = (220, 20, 60); HAPPINESS_COLOR = (255, 215, 0); HUNGER_COLOR = (139, 69, 19)
BOOST_COLOR = (0, 150, 0)
QUEST_PROGRESS_COLOR = (60, 179, 113)
### NEW: Colors for Leveling System
EXP_COLOR = (148, 0, 211) # Purple for EXP bar
LEVEL_UP_COLOR = (255, 255, 0) # Yellow for level up text
### NEW: Rarity Colors
RARITY_COLORS = {
    "Common": GRAY,
    "Rare": (50, 150, 255),
    "Epic": (160, 32, 240),
    "Legendary": HAPPINESS_COLOR
}


# --- Animation Timings ---
HATCH_ANIM_DURATION = 1500
PET_ANIM_SPEED = 120
EFFECT_DURATION = 1.5
SCROLL_SPEED = 30

# --- Game Progression ---
MAX_PET_SLOTS = 15
PET_SLOT_UNLOCK_PRICES = [50, 150, 400, 1000, 2500, 5000, 10000, 20000, 50000, 100000]
### NEW: Pet Leveling System Constants
MAX_PET_LEVEL = 10
# EXP needed to go from level N to N+1.
EXP_FOR_NEXT_LEVEL = [
    600,  # Lvl 0 -> 1 (10 minutes of active time)
    1200, # Lvl 1 -> 2 (20 minutes)
    1800, # Lvl 2 -> 3 (30 minutes)
    2400, # Lvl 3 -> 4 (40 minutes)
    3600, # Lvl 4 -> 5 (1 hour)
    5400, # Lvl 5 -> 6 (1.5 hours)
    7200, # Lvl 6 -> 7 (2 hours)
    9000, # Lvl 7 -> 8 (2.5 hours)
    10800,# Lvl 8 -> 9 (3 hours)
    14400 # Lvl 9 -> 10 (4 hours)
]
EXP_GAIN_RATE = 1.0 # 1 EXP per second of active time


### SECTIONED PET AREA: Define pet sections and path dimensions
LEFT_SECTION_PETS = ["Bear", "Boar", "Fox", "Wolf"]
PATH_WIDTH = 500
PATH_START_X = (SCREEN_WIDTH - PATH_WIDTH) // 2
PATH_END_X = PATH_START_X + PATH_WIDTH

# --- Pet Names ---
PET_NAMES = ["Buddy", "Lucy", "Max", "Bella", "Charlie", "Daisy", "Rocky", "Molly", "Toby", "Sadie", "Coco", "Lola", "Jack", "Zoe", "Milo", "Ruby", "Oscar", "Penny", "Leo", "Rosie", "Pip", "Fuzzy", "Sparky", "Noodle", "Waffles"]

clock = pygame.time.Clock()
try:
    correct_font_path = load_file_case_insensitive("FONT/PixelEmulator.otf")
    if correct_font_path:
        font = pygame.font.Font(correct_font_path, 36); font_small = pygame.font.Font(correct_font_path, 32)
        font_info = pygame.font.Font(correct_font_path, 24)
        font_plus = pygame.font.Font(correct_font_path, 48)
        font_reveal = pygame.font.Font(correct_font_path, 64)
    else:
        raise FileNotFoundError("Font not found")
except (FileNotFoundError, OSError): print("Warning: Font 'PixelEmulator.otf' not found."); font=pygame.font.Font(None, 48); font_small=pygame.font.Font(None, 42); font_info = pygame.font.Font(None, 32); font_plus = pygame.font.Font(None, 60); font_reveal = pygame.font.Font(None, 80)

# -------------------- Load Resources --------------------
try:
    title_img = safe_image_load("GUI/title_screen2.png"); title_img = pygame.transform.scale(title_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error: print("Warning: title_screen2.png not found."); title_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
try:
    bg_img = safe_image_load("GUI/background.jpg").convert(); bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error: print("Warning: background.jpg not found."); bg_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); bg_img.fill((30,10,40))
try:
    trash_can_img_original = safe_image_load("GUI/trashcan.png").convert_alpha(); trash_can_img = pygame.transform.scale(trash_can_img_original, (48, 48))
except pygame.error: print("Warning: GUI/trashcan.png not found."); trash_can_img = None
try:
    coin_img_original = safe_image_load("ENTITY/currency.jpg").convert_alpha(); coin_img = pygame.transform.scale(coin_img_original, (48, 48))
except pygame.error: print("Warning: ENTITY/currency.jpg not found."); coin_img = pygame.Surface((48,48)); coin_img.fill((255,215,0))
try:
    clock_img_original = safe_image_load("ENTITY/clock.png").convert_alpha(); clock_img = pygame.transform.scale(clock_img_original, (48, 48))
except pygame.error: print("Warning: ENTITY/clock.png not found."); clock_img = pygame.Surface((48,48)); clock_img.fill(WHITE)
try:
    theme_song_path = load_file_case_insensitive("MUSIC/theme.mp3")
    if not theme_song_path:
        print("Warning: Music file 'MUSIC/theme.mp3' not found.")
except Exception as e:
    print(f"Warning: Could not prepare music. Error: {e}")
    theme_song_path = None
try:
    frame_data = safe_json_load("CHARACTER/flash.json")["frames"]
except FileNotFoundError: print("FATAL ERROR: CHARACTER/flash.json not found."); pygame.quit(); sys.exit()
try:
    map_image_original = safe_image_load("GUI/map.jpg").convert(); play_map_img = pygame.transform.scale(map_image_original, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error: print("Warning: GUI/map.jpg not found."); play_map_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); play_map_img.fill(GRAY)
map_rect = play_map_img.get_rect()
try:
    fence_img = safe_image_load("ENTITY/fence.png").convert_alpha(); fence_img = pygame.transform.scale(fence_img, (64, 64))
except pygame.error: print("Warning: ENTITY/fence.png not found."); fence_img = pygame.Surface((64,64)); fence_img.fill(PANEL_BORDER_COLOR)
try:
    hatch_img = safe_image_load("GUI/hatch.png").convert_alpha()
except pygame.error: print("Warning: GUI/hatch.png not found."); hatch_img = pygame.Surface((128, 64), pygame.SRCALPHA); hatch_img.fill((180, 140, 80))
try:
    lock_img_original = safe_image_load("GUI/lock.png").convert_alpha(); lock_img = pygame.transform.scale(lock_img_original, (64, 64))
except pygame.error: print("Warning: GUI/lock.png not found."); lock_img = pygame.Surface((64, 64), pygame.SRCALPHA); pygame.draw.rect(lock_img, GRAY, (16, 32, 32, 32), border_radius=5); pygame.draw.arc(lock_img, GRAY, (8, 8, 48, 48), 0, 3.14, 8)
try:
    sold_out_img_original = safe_image_load("GUI/sold.png").convert_alpha()
    sold_out_img = pygame.transform.scale(sold_out_img_original, (128, 128))
except pygame.error: print("Warning: GUI/sold.png not found."); sold_out_img = pygame.Surface((128, 128), pygame.SRCALPHA); sold_out_text = font_small.render("SOLD", True, (200, 0, 0)); sold_out_img.blit(sold_out_text, (30, 50))
try:
    backpack_img_original = safe_image_load("GUI/backpack.png").convert_alpha()
    backpack_img = pygame.transform.scale(backpack_img_original, (64, 64))
    backpack_rect = backpack_img.get_rect(midleft=(20, SCREEN_HEIGHT // 2))
except pygame.error: print("Warning: GUI/backpack.png not found."); backpack_img = pygame.Surface((64, 64)); backpack_img.fill(PANEL_BORDER_COLOR); backpack_rect = backpack_img.get_rect(midleft=(20, SCREEN_HEIGHT // 2))
try:
    pet_menu_icon_original = safe_image_load("GUI/paw_icon.png").convert_alpha()
    pet_menu_icon = pygame.transform.scale(pet_menu_icon_original, (64, 64))
    pet_menu_rect = pet_menu_icon.get_rect(midleft=(20, backpack_rect.bottom + 40))
except pygame.error:
    print("Warning: GUI/paw_icon.png not found."); pet_menu_icon = pygame.Surface((64, 64), pygame.SRCALPHA);
    pygame.draw.circle(pet_menu_icon, PANEL_BORDER_COLOR, (32, 32), 30); pygame.draw.circle(pet_menu_icon, TEXT_COLOR, (32, 32), 26)
    pet_menu_rect = pet_menu_icon.get_rect(midleft=(20, backpack_rect.bottom + 40))
try:
    heart_img = safe_image_load("GUI/heart.png").convert_alpha(); heart_img = pygame.transform.scale(heart_img, (32, 32))
except pygame.error: print("Warning: GUI/heart.png not found."); heart_img = pygame.Surface((32,32), pygame.SRCALPHA); pygame.draw.circle(heart_img, (255, 105, 180), (16,16), 14, 0)
try:
    smile_img = safe_image_load("GUI/smile.png").convert_alpha(); smile_img = pygame.transform.scale(smile_img, (32, 32))
except pygame.error: print("Warning: GUI/smile.png not found."); smile_img = pygame.Surface((32,32), pygame.SRCALPHA); pygame.draw.circle(smile_img, HAPPINESS_COLOR, (16,16), 14, 0)
try:
    mission_icon_original = safe_image_load("GUI/mission_icon.png").convert_alpha()
    mission_icon_img = pygame.transform.scale(mission_icon_original, (64, 64))
    mission_icon_rect = mission_icon_img.get_rect(midleft=(20, pet_menu_rect.bottom + 40))
except pygame.error:
    print("Warning: GUI/mission_icon.png not found."); mission_icon_img = pygame.Surface((64, 64)); mission_icon_img.fill(QUEST_PROGRESS_COLOR)
    mission_icon_rect = mission_icon_img.get_rect(midleft=(20, pet_menu_rect.bottom + 40))
try:
    quest_stand_img_original = safe_image_load("GUI/stand.png").convert_alpha()
    quest_stand_img = pygame.transform.scale(quest_stand_img_original, (110, 110))
except pygame.error:
    print("Warning: GUI/stand.png not found."); quest_stand_img = pygame.Surface((110, 110), pygame.SRCALPHA); quest_stand_img.fill(PANEL_BORDER_COLOR)
try:
    quest_pointer_img_original = safe_image_load("GUI/pointer.png").convert_alpha()
    quest_pointer_img = pygame.transform.scale(quest_pointer_img_original, (48, 48))
except pygame.error:
    print("Warning: GUI/pointer.png not found."); quest_pointer_img = pygame.Surface((48, 48), pygame.SRCALPHA); pygame.draw.polygon(quest_pointer_img, (255, 215, 0), [(0,0), (48,0), (24, 24)])
try:
    challenge_stand_img_original = safe_image_load("GUI/stand2.png").convert_alpha()
    challenge_stand_img = pygame.transform.scale(challenge_stand_img_original, (110, 110))
except pygame.error:
    print("Warning: GUI/stand2.png not found."); challenge_stand_img = pygame.Surface((110, 110), pygame.SRCALPHA); challenge_stand_img.fill(PANEL_BORDER_COLOR)
try:
    chicken_map_img_original = safe_image_load("GUI/map2.png").convert()
    chicken_map_img = pygame.transform.scale(chicken_map_img_original, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error:
    print("Warning: GUI/map2.png not found."); chicken_map_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); chicken_map_img.fill((210, 180, 140))
try:
    music_on_img_original = safe_image_load("GUI/music_on.png").convert_alpha()
    music_on_img = pygame.transform.scale(music_on_img_original, (48, 48))
    music_off_img_original = safe_image_load("GUI/music_off.png").convert_alpha()
    music_off_img = pygame.transform.scale(music_off_img_original, (48, 48))
except pygame.error:
    print("Warning: GUI/music_on.png or GUI/music_off.png not found.")
    music_on_img = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.circle(music_on_img, WHITE, (24, 24), 20, 2)
    pygame.draw.polygon(music_on_img, WHITE, [(16, 16), (16, 32), (32, 24)])
    music_off_img = music_on_img.copy()
    pygame.draw.line(music_off_img, (255,0,0), (8,8), (40,40), 4)

### DECORATIONS: Load new decoration assets
try:
    pet_house_img_original = safe_image_load("GUI/pet_house.png").convert_alpha()
    pet_house_img = pygame.transform.scale(pet_house_img_original, (256, 256))
except pygame.error:
    print("Warning: GUI/pet_house.png not found.")
    pet_house_img = pygame.Surface((256, 256), pygame.SRCALPHA); pet_house_img.fill((150, 75, 0))
try:
    pond_img_original = safe_image_load("GUI/pond.png").convert_alpha()
    pond_img = pygame.transform.scale(pond_img_original, (400, 200))
except pygame.error:
    print("Warning: GUI/pond.png not found.")
    pond_img = pygame.Surface((400, 200), pygame.SRCALPHA); pond_img.fill((0, 100, 200))
try:
    tree_img_original = safe_image_load("GUI/tree.png").convert_alpha()
    tree_img = pygame.transform.scale(tree_img_original, (128, 160))
except pygame.error:
    print("Warning: GUI/tree.png not found.")
    tree_img = pygame.Surface((128, 160), pygame.SRCALPHA); tree_img.fill((0, 100, 0))

try:
    item_data = safe_json_load("JSON/items_p.json")
except FileNotFoundError: print("FATAL ERROR: items_p.json not found."); pygame.quit(); sys.exit()
try:
    pet_data = safe_json_load("JSON/pets_p.json")
except FileNotFoundError: print("FATAL ERROR: pets.json not found."); pygame.quit(); sys.exit()
try:
    missions_data = safe_json_load("JSON/missions.json") 
    missions_data = {k: v for k, v in missions_data.items() if not v.get("is_comment", False)}
except FileNotFoundError: print("FATAL ERROR: missions.json not found. Please create this file."); pygame.quit(); sys.exit()
try:
    enemy_data = safe_json_load("JSON/enemies.json")
except FileNotFoundError: print("FATAL ERROR: enemies.json not found. Please create this file."); pygame.quit(); sys.exit()

item_images = {}
for item_id, data in item_data.items():
    try:
        img = safe_image_load(data["image_path"]).convert_alpha()
        item_images[item_id] = pygame.transform.scale(img, (96, 96))
    except pygame.error: print(f"Warning: Item image not found at {data['image_path']}"); img_placeholder = pygame.Surface((96, 96), pygame.SRCALPHA); img_placeholder.fill((255, 0, 255)); item_images[item_id] = img_placeholder

# -------------------- Helper Functions --------------------
def load_pet_animation_frames(pet_id, anim_key="idle", scale=1.0):
    if pet_id not in pet_data:
        print(f"Error: Pet ID '{pet_id}' not found in pets.json")
        return []
    
    p_data = pet_data[pet_id]
    
    path_prefix = p_data['animation_paths'].get(anim_key)
    if not path_prefix: return []

    if anim_key == "attack":
        all_attack_frames = []
        anim_num = 1
        while True:
            sub_frames = []
            i = 1
            path_test = load_file_case_insensitive(f"{path_prefix}{pet_id}_{anim_num}_1.png")
            if path_test:
                 while True:
                    path = f"{path_prefix}{pet_id}_{anim_num}_{i}.png"
                    try:
                        img = safe_image_load(path).convert_alpha()
                        w, h = img.get_width(), img.get_height()
                        sub_frames.append(pygame.transform.scale(img, (int(w * scale), int(h * scale))))
                        i += 1
                    except (FileNotFoundError, pygame.error):
                        break
            else:
                if anim_num == 1:
                    while True:
                        path = f"{path_prefix}{pet_id}_{i}.png"
                        try:
                            img = safe_image_load(path).convert_alpha()
                            w, h = img.get_width(), img.get_height()
                            sub_frames.append(pygame.transform.scale(img, (int(w * scale), int(h * scale))))
                            i += 1
                        except (FileNotFoundError, pygame.error):
                            break
                if sub_frames:
                    all_attack_frames.append(sub_frames)
                break

            if sub_frames:
                all_attack_frames.append(sub_frames)
            else:
                break
            anim_num += 1

        if not all_attack_frames:
             print(f"Warning: No attack frames found for '{pet_id}'")
        return all_attack_frames

    else:
        frames = []
        i = 1
        while True:
            path = f"{path_prefix}{pet_id}_{i}.png"
            try:
                img = safe_image_load(path).convert_alpha()
                w, h = img.get_width(), img.get_height()
                frames.append(pygame.transform.scale(img, (int(w * scale), int(h * scale))))
                i += 1
            except (FileNotFoundError, pygame.error):
                if i == 1: print(f"Warning: Could not find first frame for '{pet_id}' at '{path}'")
                break
        return frames

def load_enemy_animation_frames(enemy_id, anim_key="idle", scale=1.0):
    if enemy_id not in enemy_data:
        print(f"Error: Enemy ID '{enemy_id}' not found in enemies.json")
        return []

    e_data = enemy_data[enemy_id]
    frames = []
    path_prefix = e_data['animation_paths'].get(anim_key)
    if not path_prefix:
        print(f"Warning: Animation key '{anim_key}' not found for enemy '{enemy_id}'")
        return []

    i = 1
    while True:
        path = f"{path_prefix}{enemy_id}_{i}.png"
        try:
            img = safe_image_load(path).convert_alpha()
            w, h = img.get_width(), img.get_height()
            frames.append(pygame.transform.scale(img, (int(w * scale), int(h * scale))))
            i += 1
        except (FileNotFoundError, pygame.error):
            if i == 1:
                print(f"Warning: Could not find first frame for '{enemy_id}' with anim '{anim_key}' at '{path}'")
            break
    return frames

def draw_text_wrapped(surface, text, font, color, rect, line_spacing=5, centered=False):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < rect.width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    y = rect.top
    for line in lines:
        line_surface = font.render(line, True, color)
        if centered:
            line_rect = line_surface.get_rect(centerx=rect.centerx, top=y)
        else:
            line_rect = line_surface.get_rect(left=rect.left, top=y)
        
        surface.blit(line_surface, line_rect)
        y += font.get_height() + line_spacing
    
    return y

pet_icons = {}
for pet_id in pet_data:
    idle_frames = load_pet_animation_frames(pet_id, "idle", scale=1.0)
    if idle_frames:
        pet_icons[pet_id] = pygame.transform.scale(idle_frames[0], (64, 64))
    else:
        print(f"Warning: Could not create icon for '{pet_id}'")
        img_placeholder = pygame.Surface((64, 64), pygame.SRCALPHA); img_placeholder.fill((0, 255, 0)); pet_icons[pet_id] = img_placeholder

profile_file = "profiles.json";
correct_profile_path = load_file_case_insensitive(profile_file)
if correct_profile_path:
    with open(correct_profile_path) as f: profiles = json.load(f)
else: profiles = [None, None, None]

global_storage_file = "global_storage.json"
global_storage_data = {"items": {}, "pets": []}

def load_global_storage():
    global global_storage_data
    correct_path = load_file_case_insensitive(global_storage_file)
    if correct_path:
        try:
            with open(correct_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'items' in data and 'pets' in data:
                    global_storage_data = data
                else:
                    print(f"Warning: '{global_storage_file}' is malformed or empty. Initializing.")
                    global_storage_data = {"items": {}, "pets": []}
        except (json.JSONDecodeError, IOError):
             print(f"Warning: Could not read '{global_storage_file}'. Initializing.")
             global_storage_data = {"items": {}, "pets": []}

def save_global_storage():
    with open(global_storage_file, 'w') as f:
        json.dump(global_storage_data, f, indent=2)
    print("Global storage saved.")

load_global_storage()

def save_profiles():
    with open(profile_file, "w") as f: json.dump(profiles, f, indent=2)

# -------------------- Game Classes --------------------
class TienTe:
    def __init__(self, start_money=0, start_time_seconds=0):
        self.money = start_money; self.total_time_played = start_time_seconds; self.session_start_time = time.time()
        self.font = font_small; self.coin_icon = coin_img; self.clock_icon = clock_img
    def get_current_play_time(self): return self.total_time_played + (time.time() - self.session_start_time)
    @staticmethod
    def format_time(total_seconds):
        total_seconds = int(total_seconds); hours = total_seconds // 3600; minutes = (total_seconds % 3600) // 60; seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    def draw(self, surface, show_time=True):
        money_text = self.font.render(str(self.money), True, WHITE)
        money_rect = money_text.get_rect(topright=(SCREEN_WIDTH - 60, 20)); surface.blit(money_text, money_rect)
        surface.blit(self.coin_icon, (money_rect.left - 58, 10))
        if show_time:
            time_text = self.font.render(self.format_time(self.get_current_play_time()), True, WHITE)
            time_rect = time_text.get_rect(topright=(SCREEN_WIDTH - 60, 80)); surface.blit(time_text, time_rect)
            surface.blit(self.clock_icon, (time_rect.left - 58, 70))

class NguoiChamSoc:
    def __init__(self, name, sheet_path, frame_data, scale):
        self.name = name; self.sheet_path = sheet_path
        try: self.sheet = safe_image_load(sheet_path).convert_alpha()
        except pygame.error: self.sheet = pygame.Surface((32, 32), pygame.SRCALPHA); self.sheet.fill((255, 0, 255))
        self.scale = scale; self.animations = {}; self.frame_index, self.timer = 0, 0; self.x, self.y = 0, 0; self.last_dir = 'South'
        self.load_animations(frame_data)
    def load_animations(self, frame_data):
        tags = ["IdleSouth","IdleNorth","IdleEast","IdleWest","WalkSouth","WalkNorth","WalkEast","WalkWest"]
        for tag in tags:
            frames = sorted([(k,v["frame"]) for k,v in frame_data.items() if f"#{tag}" in k], key=lambda x: x[0])
            images = [pygame.transform.scale(self.sheet.subsurface(pygame.Rect(f["x"],f["y"],f["w"],f["h"])), (int(f["w"]*self.scale), int(f["h"]*self.scale))) for _,f in frames]
            self.animations[tag] = images
    def update(self, dt):
        self.timer += dt
        if self.timer > 150:
            key = "IdleSouth"; length = len(self.animations.get(key,[])); self.frame_index = (self.frame_index +1) % length if length > 0 else 0
            self.timer = 0
    def get_current_image(self, key="IdleSouth"): frames = self.animations.get(key) or self.animations.get("IdleSouth", [pygame.Surface((32,32))]); return frames[self.frame_index % len(frames)]
    def get_rect(self): return self.get_current_image().get_rect(center=(self.x, self.y))
    def draw(self, surf, pos, key="IdleSouth"): image_to_draw = self.get_current_image(key); rect = image_to_draw.get_rect(center=pos); surf.blit(image_to_draw, rect)

class Building:
    def __init__(self, image_path, pos, scale_size, interaction_text, target_scene):
        self.interaction_text = interaction_text
        self.target_scene = target_scene
        try:
            self.image = safe_image_load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, scale_size)
        except pygame.error: 
            print(f"Warning: Building image not found at {image_path}. Creating placeholder.")
            self.image = pygame.Surface(scale_size)
            self.image.fill(PANEL_BORDER_COLOR)
        
        self.rect = self.image.get_rect(topleft=pos)
        self.interaction_rect = self.rect.inflate(-150, -190)
        self.is_valid = True
        
    def draw(self, surface):
        if self.is_valid:
            surface.blit(self.image, self.rect)
            
    def check_interaction_and_draw_prompt(self, surface, player, interaction_blocked):
        if not self.is_valid or not player or interaction_blocked: return False, None
        player_can_interact = self.interaction_rect.colliderect(player.get_rect())
        if player_can_interact:
            prompt_text = font_small.render(self.interaction_text, True, WHITE)
            prompt_bg = pygame.Surface((prompt_text.get_width() + 20, prompt_text.get_height() + 10), pygame.SRCALPHA)
            prompt_bg.fill((0, 0, 0, 150)); surface.blit(prompt_bg, (20, SCREEN_HEIGHT - 60)); surface.blit(prompt_text, (30, SCREEN_HEIGHT - 55))
        return player_can_interact, self.target_scene

class TuiDo:
    def __init__(self, initial_items=None, initial_pets=None):
        self.items = initial_items if initial_items is not None else {}
        self.pets = initial_pets if initial_pets is not None else []
    def add_item(self, item_id, quantity=1):
        self.items[item_id] = self.items.get(item_id, 0) + quantity
        print(f"Added {quantity} of {item_id} to inventory. New total: {self.items[item_id]}")
    def remove_item(self, item_id, quantity=1):
        if item_id in self.items and self.items[item_id] >= quantity:
            self.items[item_id] -= quantity
            if self.items[item_id] == 0: del self.items[item_id]
            return True
        return False
    def add_pet(self, pet_id):
        new_pet_instance_id = max([p['instance_id'] for p in self.pets] + [0]) + 1
        base_stats = pet_data.get(pet_id, {}).get("base_stats", {"health": 100, "happiness": 100, "hunger": 100})
        random_name = random.choice(PET_NAMES)
        new_pet = {
            "instance_id": new_pet_instance_id,
            "pet_id": pet_id,
            "name": random_name,
            "health": base_stats["health"],
            "happiness": base_stats["happiness"],
            "hunger": base_stats["hunger"],
            ### NEW: Initialize level and experience for new pets
            "level": 0,
            "experience": 0
        }
        self.pets.append(new_pet)
        print(f"Added new pet: {random_name} the {pet_id} (Instance: {new_pet_instance_id})")
        return new_pet
    def get_all_items(self): return sorted(self.items.items())
    def get_all_pets(self): return sorted(self.pets, key=lambda p: p['instance_id'])
    def get_pet_by_instance_id(self, instance_id):
        for pet in self.pets:
            if pet['instance_id'] == instance_id:
                return pet
        return None
    def get_eggs(self):
        return sorted([(k, v) for k, v in self.items.items() if item_data.get(k, {}).get('category') == 'egg'])

class ThuCung:
    DRIFT_SPEED = 20

    def __init__(self, pet_instance_data):
        self.instance_data = pet_instance_data
        ### NEW: Ensure level and experience exist for backward compatibility
        self.instance_data.setdefault('level', 0)
        self.instance_data.setdefault('experience', 0)

        self.pet_id = self.instance_data['pet_id']
        self.definition = pet_data[self.pet_id]
        
        self.section = "right"
        pet_base_id = self.pet_id.split('_')[0]
        if pet_base_id in LEFT_SECTION_PETS:
            self.section = "left"

        if self.section == "left":
            self.x = random.randint(100, PATH_START_X - 100)
        else:
            self.x = random.randint(PATH_END_X + 100, SCREEN_WIDTH - 100)
        self.y = random.randint(100, SCREEN_HEIGHT - 200)

        self.scale = 3.0
        self.scale_modifier = self.definition.get("scale_modifier", 1.0)
        self.scale *= self.scale_modifier
        self.animations = {}
        self.load_animations()

        self.state = "idle"
        self.direction = "South"
        self.frame_index, self.anim_timer = 0, 0
        self.state_timer = time.time()
        self.next_state_change = random.uniform(3, 7)
        self.speed = 100
        self.effects = []

    def load_animations(self):
        self.animations['idle'] = load_pet_animation_frames(self.pet_id, 'idle', self.scale)
        self.animations['walk'] = load_pet_animation_frames(self.pet_id, 'walk', self.scale)

    def show_effect(self, effect_type):
        for _ in range(5):
            offset_x = random.randint(-40, 40)
            offset_y = random.randint(-80, -20)
            self.effects.append({
                'type': effect_type,
                'start_time': time.time(),
                'offset': (offset_x, offset_y)
            })

    def update(self, dt):
        # Stat decay
        decay = self.definition['stat_decay_rate']
        self.instance_data['hunger'] = max(0, self.instance_data['hunger'] - decay['hunger'] * (dt / 1000.0))
        self.instance_data['happiness'] = max(0, self.instance_data['happiness'] - decay['happiness'] * (dt / 1000.0))
        if self.instance_data['hunger'] <= 0:
            self.instance_data['health'] = max(0, self.instance_data['health'] - decay['health'] * (dt / 1000.0))

        ### NEW: Experience and Leveling logic
        current_level = self.instance_data.get('level', 0)
        if current_level < MAX_PET_LEVEL:
            # Pet only gains exp if all stats are above 0
            stats_ok = (self.instance_data['health'] > 0 and 
                        self.instance_data['happiness'] > 0 and 
                        self.instance_data['hunger'] > 0)
            
            if stats_ok:
                self.instance_data['experience'] += EXP_GAIN_RATE * (dt / 1000.0)
                
                exp_needed = EXP_FOR_NEXT_LEVEL[current_level]
                if self.instance_data['experience'] >= exp_needed:
                    self.instance_data['level'] += 1
                    self.instance_data['experience'] -= exp_needed
                    self.show_effect('level_up') # Show a level up visual effect
                    print(f"{self.instance_data['name']} leveled up to level {self.instance_data['level']}!")

        # State machine for movement
        if time.time() - self.state_timer > self.next_state_change:
            self.state = "walk" if self.state == "idle" else "idle"
            self.state_timer = time.time()
            self.next_state_change = random.uniform(2, 5)
            self.frame_index = 0
            if self.state == "walk":
                self.direction = random.choice(["North", "South", "East", "West"])

        if self.state == "walk":
            dx, dy = 0, 0
            move_dist = self.speed * (dt / 1000.0)
            if self.direction == "North": dy = -move_dist
            elif self.direction == "South": dy = move_dist
            elif self.direction == "East": dx = move_dist
            elif self.direction == "West": dx = -move_dist
            
            self.x += dx
            self.y += dy
            rect = self.get_rect()

            ### DECORATIONS: Add collision check for pets
            collided_with_decor = False
            for dec_rect in decoration_collision_rects:
                if rect.colliderect(dec_rect):
                    collided_with_decor = True
                    break
            
            if collided_with_decor:
                self.x -= dx  # Reverse the move to not get stuck inside the object
                self.y -= dy
                self.state = "idle"  # Force the pet to stop moving
                self.frame_index = 0
                self.state_timer = time.time() # Reset the state timer...
                self.next_state_change = random.uniform(0.5, 1.5) # ...to make a new path decision quickly
                return # Stop processing movement for this frame
            
            fence_buffer = rect.width / 2
            if self.section == "left":
                if rect.left < 0:
                    self.x = rect.width / 2
                    if self.direction == "West": self.direction = "East"
                if rect.right > PATH_START_X:
                    self.x = PATH_START_X - fence_buffer
                    if self.direction == "East": self.direction = "West"
            elif self.section == "right":
                if rect.left < PATH_END_X:
                    self.x = PATH_END_X + fence_buffer
                    if self.direction == "West": self.direction = "East"
                if rect.right > SCREEN_WIDTH:
                    self.x = SCREEN_WIDTH - rect.width / 2
                    if self.direction == "East": self.direction = "West"
            
            if rect.top < 0 or rect.bottom > SCREEN_HEIGHT:
                self.y -= dy
                self.direction = random.choice(["North", "South"])

        self.anim_timer += dt
        if self.anim_timer > PET_ANIM_SPEED:
            self.anim_timer = 0
            frames = self.get_current_animation_frames()
            if frames:
                self.frame_index = (self.frame_index + 1) % len(frames)
        
        current_time = time.time()
        self.effects = [e for e in self.effects if current_time - e['start_time'] < EFFECT_DURATION]
    
    def get_current_animation_frames(self):
        if self.definition.get("directional"): 
            key = f"{self.state.capitalize()}{self.direction}"
            return self.animations.get(key, [])
        else:
            key = self.state
            return self.animations.get(key, [])

    def draw(self, surface):
        frames = self.get_current_animation_frames()
        if not frames: return
        self.frame_index = self.frame_index % len(frames)
        image = frames[self.frame_index]
        
        if not self.definition.get("directional") and self.direction == 'West':
            image = pygame.transform.flip(image, True, False)

        rect = image.get_rect(center=(self.x, self.y))
        surface.blit(image, rect)
        if DEBUG_MODE: pygame.draw.rect(surface, (255,0,0), rect, 1)

        current_time = time.time()
        for effect in self.effects:
            elapsed_time = current_time - effect['start_time']
            draw_x = self.x + effect['offset'][0]
            draw_y = self.y + effect['offset'][1] - (elapsed_time * self.DRIFT_SPEED)
            alpha = max(0, 255 * (1 - (elapsed_time / EFFECT_DURATION)))
            
            img_to_draw = None
            if effect['type'] == 'heart' and heart_img:
                img_to_draw = heart_img
            elif effect['type'] == 'smile' and smile_img:
                img_to_draw = smile_img
            ### NEW: Draw level up text effect
            elif effect['type'] == 'level_up':
                lvl_up_text = font.render("LVL UP!", True, LEVEL_UP_COLOR)
                lvl_up_text.set_alpha(alpha)
                surface.blit(lvl_up_text, lvl_up_text.get_rect(center=(draw_x, draw_y)))
                continue  # Skip the rest of the loop for this effect type
            
            if img_to_draw:
                img_copy = img_to_draw.copy()
                img_copy.set_alpha(alpha)
                surface.blit(img_copy, img_copy.get_rect(center=(draw_x, draw_y)))

    def get_rect(self):
        frames = self.get_current_animation_frames()
        if not frames: return pygame.Rect(self.x, self.y, 32, 32)
        self.frame_index = self.frame_index % len(frames)
        return frames[self.frame_index].get_rect(center=(self.x, self.y))

    @staticmethod
    def draw_status_bars(surface, pet_instance, pos, width=300):
        bar_height = 25; padding = 10
        start_x, start_y = pos

        def draw_bar(y_offset, label, value, color):
            bg_rect = pygame.Rect(start_x, start_y + y_offset, width, bar_height)
            fill_rect = pygame.Rect(start_x, start_y + y_offset, int(width * (value / 100.0)), bar_height)
            pygame.draw.rect(surface, GRAY, bg_rect, 0, 5)
            pygame.draw.rect(surface, color, fill_rect, 0, 5)
            pygame.draw.rect(surface, PANEL_BORDER_COLOR, bg_rect, 2, 5)
            label_text = font_info.render(label, True, TEXT_COLOR)
            surface.blit(label_text, (bg_rect.x + 5, bg_rect.centery - label_text.get_height() // 2))

        draw_bar(0, "Health", pet_instance['health'], HEALTH_COLOR)
        draw_bar(bar_height + padding, "Happy", pet_instance['happiness'], HAPPINESS_COLOR)
        
        hunger_y_offset = 2 * (bar_height + padding)
        draw_bar(hunger_y_offset, "Hunger", pet_instance['hunger'], HUNGER_COLOR)

        ### NEW: Draw Level and Experience bar
        level = pet_instance.get('level', 0)
        exp_y_offset = 3 * (bar_height + padding)
        level_label = f"Lvl: {level}"
        
        if level < MAX_PET_LEVEL:
            experience = pet_instance.get('experience', 0)
            exp_needed = EXP_FOR_NEXT_LEVEL[level]
            exp_percent = (experience / exp_needed) * 100.0 if exp_needed > 0 else 100
            draw_bar(exp_y_offset, level_label, exp_percent, EXP_COLOR)
        else: # Max level
            draw_bar(exp_y_offset, f"Lvl: {level} (MAX)", 100, EXP_COLOR)
        
        # Adjust warning text position
        if pet_instance['hunger'] < 20:
            warning_text = font_info.render("Pet need to be feed", True, HEALTH_COLOR)
            hunger_bar_rect = pygame.Rect(start_x, start_y + hunger_y_offset, width, bar_height)
            warning_rect = warning_text.get_rect(centerx=hunger_bar_rect.centerx, top=start_y + exp_y_offset + bar_height + 5)
            surface.blit(warning_text, warning_rect)
class CuaHang:
    def __init__(self):
        self.restock_interval = 300; self.last_restock_time = 0
        self.current_stock = {}
        self.all_sellable_items = [k for k,v in item_data.items() if v.get("price")]
        self.restock()
    def update(self):
        if time.time() - self.last_restock_time > self.restock_interval: print("Shop is restocking..."); self.restock()
    def restock(self):
        self.current_stock = {}
        if "egg_common" in item_data and "price" in item_data["egg_common"]:
            self.current_stock["egg_common"] = {"price": item_data["egg_common"]["price"], "quantity": 1}
        
        sellable_now = [item for item in self.all_sellable_items if item != "egg_common"]
        num_random_items = min(7, len(sellable_now))
        items_to_sell = random.sample(sellable_now, num_random_items)

        for item_id in items_to_sell:
            data = item_data[item_id]
            quantity = 1 if data.get("category") == "egg" else 3
            self.current_stock[item_id] = {"price": data["price"], "quantity": quantity}
        self.last_restock_time = time.time()
        
    def buy_item(self, item_id, player_currency, player_inventory, quest_manager):
        if item_id in self.current_stock:
            stock_info = self.current_stock[item_id]
            if stock_info["quantity"] <= 0: return "Sold out!"
            if player_currency.money >= stock_info["price"]:
                price = stock_info["price"]
                player_currency.money -= price
                player_inventory.add_item(item_id)
                stock_info["quantity"] -= 1
                if quest_manager:
                    quest_manager.track_action("spend_money", amount=price)
                    item_category = item_data[item_id].get("category")
                    if item_category == "egg": quest_manager.track_action("buy_egg")
                    elif item_category == "food": quest_manager.track_action("buy_food")
                    elif item_category == "toy": quest_manager.track_action("buy_toy")
                print(f"Bought {item_id} for {price}. Stock left: {stock_info['quantity']}")
                return "Purchase successful!"
            else:
                return "You don't have enough coins!"
        return "Item not in stock."

class Trung:
    def __init__(self, unlocked_slots_data, incubator_slots_data):
        self.unlocked_incubators = unlocked_slots_data
        self.slots = incubator_slots_data
        self.cols, self.rows = 4, 2
        self.box_size, self.padding = 200, 30
        table_w = (self.cols * self.box_size) + ((self.cols - 1) * self.padding)
        table_h = (self.rows * self.box_size) + ((self.rows - 1) * self.padding)
        self.table_x = (SCREEN_WIDTH - table_w) // 2
        self.table_y = (SCREEN_HEIGHT - table_h) / 2 + 50
        self.plus_text = font_plus.render("+", True, WHITE)

    def place_egg(self, slot_index, egg_id):
        self.slots[str(slot_index)] = {"item_id": egg_id, "start_time": time.time()}

    def clear_slot(self, slot_key):
        if slot_key in self.slots: del self.slots[slot_key]

    def handle_click(self, mouse_pos, player_currency):
        for i in range(self.cols * self.rows):
            r, c = divmod(i, self.cols)
            box_x = self.table_x + c * (self.box_size + self.padding)
            box_y = self.table_y + r * (self.box_size + self.padding)
            box_rect = pygame.Rect(box_x, box_y, self.box_size, self.box_size)
            if box_rect.collidepoint(mouse_pos):
                slot_key = str(i)
                if self.unlocked_incubators[i]:
                    if slot_key in self.slots:
                        egg_info = self.slots[slot_key]
                        egg_data_def = item_data.get(egg_info['item_id'], {})
                        hatch_time = egg_data_def.get("data", {}).get("hatch_time_seconds", 3600)
                        if time.time() - egg_info['start_time'] >= hatch_time:
                            return {'action': 'hatch', 'slot_key': slot_key, 'egg_id': egg_info['item_id']}
                    else:
                        return {'action': 'select_egg', 'slot': i}
                else:
                    price_index = i - 4
                    if 0 <= price_index < len(UNLOCK_PRICES):
                        price = UNLOCK_PRICES[price_index]
                        if player_currency.money >= price:
                            player_currency.money -= price
                            self.unlocked_incubators[i] = True
                            save_profiles()
                return {'action': 'none'}
        return None
        
    def draw(self, surface, mouse_pos):
        overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); surface.blit(overlay,(0,0))
        table_w=(self.cols*self.box_size)+((self.cols-1)*self.padding); table_h=(self.rows*self.box_size)+((self.rows-1)*self.padding);
        container_rect=pygame.Rect(self.table_x-self.padding,self.table_y-self.padding-80,table_w+2*self.padding,table_h+2*self.padding+80)
        pygame.draw.rect(surface,PANEL_FILL_COLOR,container_rect,0,15); pygame.draw.rect(surface,PANEL_BORDER_COLOR,container_rect,6,15)
        title_text=font.render("INCUBATORS",True,TEXT_COLOR); surface.blit(title_text,title_text.get_rect(center=(container_rect.centerx,container_rect.top+45)))
        for i in range(self.cols * self.rows):
            r, c = divmod(i, self.cols)
            box_x = self.table_x + c * (self.box_size + self.padding)
            box_y = self.table_y + r * (self.box_size + self.padding)
            box_rect = pygame.Rect(box_x, box_y, self.box_size, self.box_size)
            slot_key = str(i)
            if self.unlocked_incubators[i]:
                orig_w, orig_h = hatch_img.get_size(); scaled_h = int(orig_h * (self.box_size / orig_w))
                scaled_hatch = pygame.transform.scale(hatch_img, (self.box_size, scaled_h))
                hatch_rect = scaled_hatch.get_rect(midbottom=box_rect.midbottom); hatch_rect.y += 10; hatch_rect.x -= 10
                surface.blit(scaled_hatch, hatch_rect)
                if slot_key in self.slots:
                    egg_info=self.slots[slot_key]; egg_id=egg_info['item_id']; egg_data_def=item_data.get(egg_id,{})
                    total_hatch_time=egg_data_def.get("data",{}).get("hatch_time_seconds",3600); remaining_time=total_hatch_time-(time.time()-egg_info['start_time'])
                    if egg_img:=item_images.get(egg_id):
                        egg_rect=egg_img.get_rect(centerx=box_rect.centerx,bottom=hatch_rect.top+150); surface.blit(egg_img,egg_rect)
                    if remaining_time > 0:
                        timer_text=font_info.render(TienTe.format_time(remaining_time),True,WHITE); timer_rect=timer_text.get_rect(centerx=box_rect.centerx,bottom=box_rect.bottom-15)
                        bg_rect=timer_rect.inflate(10,5); bg_surf=pygame.Surface(bg_rect.size,pygame.SRCALPHA); bg_surf.fill((0,0,0,150)); surface.blit(bg_surf,bg_rect); surface.blit(timer_text,timer_rect)
                    else:
                        ready_text=font_small.render("READY!",True,READY_COLOR); surface.blit(ready_text,ready_text.get_rect(centerx=box_rect.centerx,bottom=box_rect.bottom-15))
                    border_color=READY_COLOR if remaining_time<=0 else PANEL_BORDER_COLOR
                    pygame.draw.rect(surface,BUTTON_HOVER_COLOR if box_rect.collidepoint(mouse_pos) else border_color,box_rect,5,10)
                else:
                    plus_rect=self.plus_text.get_rect(centerx=box_rect.centerx,bottom=hatch_rect.top+100); surface.blit(self.plus_text,plus_rect)
                    pygame.draw.rect(surface,BUTTON_HOVER_COLOR if box_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,box_rect,5,10)
            else:
                pygame.draw.rect(surface,LOCKED_SLOT_COLOR,box_rect,0,10); surface.blit(lock_img,lock_img.get_rect(center=box_rect.center))
                price_index=i-4
                if 0<=price_index<len(UNLOCK_PRICES):
                    price=UNLOCK_PRICES[price_index]; price_text=font_info.render(str(price),True,TEXT_COLOR)
                    surface.blit(price_text,(box_rect.centerx-price_text.get_width()-5,box_rect.bottom-40)); surface.blit(pygame.transform.scale(coin_img,(32,32)),(box_rect.centerx+5,box_rect.bottom-45))
                pygame.draw.rect(surface,BUTTON_HOVER_COLOR if box_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,box_rect,5,10)

class QuestManager:
    def __init__(self, profile_data, all_missions, inventory, currency):
        self.profile = profile_data
        self.all_missions = all_missions
        self.inventory = inventory
        self.currency = currency
        
        if 'quests' not in self.profile:
            self.profile['quests'] = {'daily_quests':[],'progress':{},'claimed':[],'last_reset_day':0,'quests_accepted_today':False}
        self.quest_data = self.profile['quests']

    def reset_if_needed(self):
        today = date.today().toordinal()
        if self.quest_data['last_reset_day'] != today:
            print("New day detected. Resetting daily quests status.")
            self.quest_data['last_reset_day'] = today
            self.quest_data['claimed'] = []
            self.quest_data['progress'] = {}
            self.quest_data['daily_quests'] = []
            self.quest_data['quests_accepted_today'] = False
            save_profiles()

    def assign_daily_quests(self):
        if self.quest_data['quests_accepted_today']: return

        print("Assigning new daily quests.")
        possible_quests = list(self.all_missions.keys())
        num_to_select = min(3, len(possible_quests))
        self.quest_data['daily_quests'] = random.sample(possible_quests, num_to_select)
        self.quest_data['quests_accepted_today'] = True
        save_profiles()

    def track_action(self, action_type, amount=1):
        if not self.quest_data['quests_accepted_today']: return
        for quest_id in self.quest_data['daily_quests']:
            if quest_id in self.quest_data['claimed']: continue
            
            mission = self.all_missions.get(quest_id)
            if mission and mission['type'] == action_type:
                current_progress = self.quest_data['progress'].get(quest_id, 0)
                self.quest_data['progress'][quest_id] = current_progress + amount
                print(f"Quest '{quest_id}' progress: {self.quest_data['progress'][quest_id]}/{mission['target']}")
    
    def claim_reward(self, quest_id):
        if quest_id not in self.quest_data['daily_quests'] or quest_id in self.quest_data['claimed']:
            return False, "Quest not active or already claimed."

        mission = self.all_missions.get(quest_id)
        current_progress = self.quest_data['progress'].get(quest_id, 0)

        if mission and current_progress >= mission['target']:
            reward = mission['reward']
            if 'money' in reward: self.currency.money += reward['money']
            if 'items' in reward:
                for item_id, qty in reward['items'].items(): self.inventory.add_item(item_id, qty)
            
            self.quest_data['claimed'].append(quest_id)
            save_profiles()
            return True, "Reward claimed!"
        else:
            return False, "Quest not complete."
            
    def get_time_until_next_reset(self):
        now = datetime.now()
        tomorrow = now.date() + timedelta(days=1)
        midnight = datetime.combine(tomorrow, datetime.min.time())
        time_left = midnight - now
        return time_left.total_seconds()

class Enemy(ThuCung):
    def __init__(self, enemy_id):
        self.enemy_id = enemy_id
        self.definition = enemy_data[self.enemy_id]
        
        self.x, self.y = random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT - 200)
        self.scale = 2.0
        self.animations = {}
        self.load_animations()

        self.health = self.definition.get("health", 10)
        self.max_health = self.health

        self.state = "idle"
        self.direction = "South"
        self.frame_index, self.anim_timer = 0, 0
        self.state_timer = time.time()
        self.next_state_change = random.uniform(3, 7)
        self.speed = 80
        self.effects = []

    def load_animations(self):
        self.animations['idle'] = load_enemy_animation_frames(self.enemy_id, 'idle', self.scale)
        self.animations['walk'] = load_enemy_animation_frames(self.enemy_id, 'walk', self.scale)

    def update(self, dt):
        if time.time() - self.state_timer > self.next_state_change:
            self.state = "walk" if self.state == "idle" else "idle"
            self.state_timer = time.time()
            self.next_state_change = random.uniform(2, 5)
            self.frame_index = 0
            if self.state == "walk":
                self.direction = random.choice(["North", "South", "East", "West"])

        if self.state == "walk":
            dx, dy = 0, 0
            move_dist = self.speed * (dt / 1000.0)
            if self.direction == "North": dy = -move_dist
            elif self.direction == "South": dy = move_dist
            elif self.direction == "East": dx = move_dist
            elif self.direction == "West": dx = -move_dist
            self.x += dx
            self.y += dy
            rect = self.get_rect()
            if rect.left < 0 or rect.right > SCREEN_WIDTH: self.x -= dx; self.direction = random.choice(["East", "West"])
            if rect.top < 0 or rect.bottom > SCREEN_HEIGHT-120: self.y -= dy; self.direction = random.choice(["North", "South"])

        self.anim_timer += dt
        if self.anim_timer > PET_ANIM_SPEED:
            self.anim_timer = 0
            frames = self.get_current_animation_frames()
            if frames:
                self.frame_index = (self.frame_index + 1) % len(frames)

    def draw(self, surface):
        super().draw(surface)
        bar_w, bar_h = 60, 8
        bar_x = self.x - bar_w // 2
        bar_y = self.get_rect().top - 15
        health_pct = self.health / self.max_health
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surface, HEALTH_COLOR, (bar_x, bar_y, bar_w * health_pct, bar_h))

class ChallengePet(ThuCung):
    def __init__(self, pet_instance_data):
        super().__init__(pet_instance_data)
        self.speed = 250
        self.state = "idle"
        self.is_attacking = False
        self.attack_anim_timer = 0
        self.attack_anim_duration = 500
        self.damage = self.definition.get("damage", 10)
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100
        self.animations['attack_styles'] = load_pet_animation_frames(self.pet_id, 'attack', self.scale)
        self.current_attack_frames = []

    def attack(self):
        if not self.is_attacking and self.animations['attack_styles']:
            self.is_attacking = True; self.state = 'attack'; self.frame_index = 0; self.anim_timer = 0; self.attack_anim_timer = 0
            self.current_attack_frames = random.choice(self.animations['attack_styles'])

    def update(self, dt):
        if self.is_attacking:
            self.attack_anim_timer += dt
            if self.attack_anim_timer >= self.attack_anim_duration:
                self.is_attacking = False; self.state = 'idle'; self.attack_anim_timer = 0
            else:
                self.anim_timer += dt
                if self.current_attack_frames and self.anim_timer > PET_ANIM_SPEED / 2:
                    self.anim_timer = 0
                    self.frame_index = (self.frame_index + 1) % len(self.current_attack_frames)
            return

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        speed = self.speed * (dt / 1000.0)

        if keys[pygame.K_w]: dy -= speed; self.direction = "North"
        if keys[pygame.K_s]: dy += speed; self.direction = "South"
        if keys[pygame.K_a]: dx -= speed; self.direction = "West"
        if keys[pygame.K_d]: dx += speed; self.direction = "East"

        self.state = "walk" if dx != 0 or dy != 0 else "idle"
        self.x += dx; self.y += dy

        rect = self.get_rect()
        if rect.left < 0: self.x = rect.width / 2
        if rect.right > SCREEN_WIDTH: self.x = SCREEN_WIDTH - rect.width / 2
        if rect.top < 0: self.y = rect.height / 2
        if rect.bottom > SCREEN_HEIGHT: self.y = SCREEN_HEIGHT - rect.height / 2

        self.anim_timer += dt
        if self.anim_timer > PET_ANIM_SPEED:
            self.anim_timer = 0
            frames = self.get_current_animation_frames()
            if frames:
                self.frame_index = (self.frame_index + 1) % len(frames)

    def get_current_animation_frames(self):
        if self.state == 'attack':
            return self.current_attack_frames
        return super().get_current_animation_frames()

# -------------------- Load Characters & Game Objects --------------------
char_paths = [f"CHARACTER/{var}_P{i}.png" for var in ["Hero","Modern_Hero","Ninja","Peasant","Warrior"] for i in range(1,4)]
char_objs = [NguoiChamSoc(p.split("/")[-1].replace(".png",""), p, frame_data, 3.0) for p in char_paths]
for c, p in zip(char_objs, char_paths): c.sheet_path = p
shop = Building("GUI/shop.png", (0, 5), (256, 256), "Press 'E' to enter Shop", "shop_menu")
home = Building("GUI/home2.png", (275, -12), (260, 260), "Press 'E' to enter Home", "home_menu")
storage = Building("GUI/storage.png", (home.rect.right + 50, 33), (170, 170), "Press 'E' to open Storage", "storage_menu")
world_buildings = [shop, home, storage]
try: shopkeeper = NguoiChamSoc("Shopkeeper", "CHARACTER/Ninja_Style_2_P2.png", frame_data, 10.0)
except Exception as e: print(f"Warning: Could not load shopkeeper character asset: {e}"); shopkeeper = None

quest_giver_npc = NguoiChamSoc("QuestGiver", "CHARACTER/Ninja_Style_2_P4.png", frame_data, 2.0)
quest_giver_npc_large = NguoiChamSoc("QuestGiver", "CHARACTER/Ninja_Style_2_P4.png", frame_data, 16.0)
quest_stand_rect = quest_stand_img.get_rect(topright=(SCREEN_WIDTH - 550, 620))
quest_giver_npc.x = quest_stand_rect.centerx
quest_giver_npc.y = quest_stand_rect.centery + 10
quest_interaction_rect = quest_stand_rect.inflate(-50, -50)

challenge_npc_world = NguoiChamSoc("ChallengeNPC", "CHARACTER/Ninja_Style_2_P3.png", frame_data, 2.0)
challenge_npc_map = NguoiChamSoc("ChallengeNPC_Map", "CHARACTER/Ninja_Style_2_P3.png", frame_data, 2.0)
challenge_npc_large = NguoiChamSoc("ChallengeNPC_Large", "CHARACTER/Ninja_Style_2_P3.png", frame_data, 16.0)
challenge_stand_rect = challenge_stand_img.get_rect(topleft=(SCREEN_WIDTH - 1000, 620))
challenge_npc_world.x = challenge_stand_rect.centerx
challenge_npc_world.y = challenge_stand_rect.centery + 20
challenge_npc_map.x = SCREEN_WIDTH // 2
challenge_npc_map.y = 150
challenge_interaction_rect = challenge_stand_rect.inflate(-50, -50)

pointer_text_surface = font_info.render("Quest", True, TEXT_COLOR)
challenge_pointer_text_surface = font_info.render("Challenge", True, TEXT_COLOR)

path_center_x, path_width, fence_y, fence_step = SCREEN_WIDTH*0.45, 150, SCREEN_HEIGHT-120, 48
fence_objects = [(i*fence_step, fence_y) for i in range(int(path_center_x//fence_step))]
start_x = path_center_x + path_width; fence_objects.extend([(start_x+i*fence_step, fence_y) for i in range(int((SCREEN_WIDTH-start_x)//fence_step)+1)])

### SECTIONED PET AREA: Create vertical fence lines and their interaction rects
fence_img_vertical_left = pygame.transform.rotate(fence_img, 90)
fence_img_vertical_right = pygame.transform.rotate(fence_img, -90)
left_fence_line = [(PATH_START_X - fence_img_vertical_left.get_width()//2, i * 48) for i in range(SCREEN_HEIGHT // 48 + 1)]
right_fence_line = [(PATH_END_X - fence_img_vertical_right.get_width()//2, i * 48) for i in range(SCREEN_HEIGHT // 48 + 1)]
left_fence_interaction_rect = pygame.Rect(PATH_START_X - 50, 0, 100, SCREEN_HEIGHT)
right_fence_interaction_rect = pygame.Rect(PATH_END_X - 50, 0, 100, SCREEN_HEIGHT)

### DECORATIONS: Define positions and collision rects
pet_house_rect = pet_house_img.get_rect(topright=(SCREEN_WIDTH - 50, 50))
pond_rect = pond_img.get_rect(bottomright=(SCREEN_WIDTH - 80, SCREEN_HEIGHT - 50))
trees_rects = [
    tree_img.get_rect(center=(150, 200)),
    tree_img.get_rect(center=(300, 500)),
    tree_img.get_rect(center=(100, SCREEN_HEIGHT - 150)),
    tree_img.get_rect(center=(PATH_START_X - 150, SCREEN_HEIGHT // 2 + 100))
]
decorations_to_draw = {}
decorations_to_draw['pet_house'] = {'img': pet_house_img, 'rect': pet_house_rect, 'y_sort': pet_house_rect.bottom}
decorations_to_draw['pond'] = {'img': pond_img, 'rect': pond_rect, 'y_sort': pond_rect.centery}
for i, r in enumerate(trees_rects):
    decorations_to_draw[f'tree_{i}'] = {'img': tree_img, 'rect': r, 'y_sort': r.bottom}
pond_collision_rect = pond_rect.inflate(0, -pond_rect.height * 0.6)
pond_collision_rect.bottom = pond_rect.bottom
pet_house_collision_rect = pygame.Rect(pet_house_rect.left + 30, pet_house_rect.bottom - 60, pet_house_rect.width - 60, 60)
tree_collision_rects = [pygame.Rect(r.centerx - 20, r.bottom - 30, 40, 30) for r in trees_rects]
decoration_collision_rects = [pet_house_collision_rect, pond_collision_rect] + tree_collision_rects

# -------------------- Game State Variables --------------------
scene, loading_start = "loading", time.time(); selection_idx, selected, player = 0, None, None
selected_profile_idx, player_name_input = None, ""
confirming_delete,confirming_escape, delete_target_index = False,False,None
game_currency, current_map = None, "world"
incubator_manager = None; player_inventory = None; shop_manager = CuaHang();
inventory_selected_item_id = None; incubator_selection_slot = None
shop_message, shop_message_timer = "", 0
UNLOCK_PRICES = [20, 30, 40, 50]
pet_management_selected_instance_id = None; pet_list_scroll_y = 0 
pet_menu_message = ""; pet_menu_message_timer = 0
is_dragging_scrollbar = False; scrollbar_drag_offset_y = 0; scrollbar_handle_rect = pygame.Rect(0,0,0,0)
money_generation_timer = 0; hatching_info = None; hatching_animation_frames = []
hatching_frame_index = 0; hatching_timer = 0; hatched_pet_info = None; active_pets = []
storage_scene_tab = 'items'; storage_player_scroll_y = 0; storage_global_scroll_y = 0
storage_selected_player_idx = None; storage_selected_global_idx = None
storage_message = ""; storage_message_timer = 0
interaction_menu_open = False; interaction_pet = None; interaction_submenu = None 
clickable_interaction_rects = {}
player_location_in_pet_area = "path"
quest_manager = None; quest_menu_message = ""; quest_menu_message_timer = 0
quest_dialogue_yes_rect = pygame.Rect(0,0,0,0); quest_dialogue_no_rect = pygame.Rect(0,0,0,0)
### MODIFIED: Renamed and added rects for new dialogue flows
challenge_fight_yes_rect = pygame.Rect(0,0,0,0); challenge_fight_no_rect = pygame.Rect(0,0,0,0)
challenge_main_fight_rect = pygame.Rect(0,0,0,0); challenge_main_sell_rect = pygame.Rect(0,0,0,0)
challenge_pre_sell_yes_rect = pygame.Rect(0,0,0,0); challenge_pre_sell_no_rect = pygame.Rect(0,0,0,0)
is_music_playing = True; music_button_rect = pygame.Rect(SCREEN_WIDTH - 68, SCREEN_HEIGHT - 68, 48, 48)
active_challenge_pet = None; active_enemies = []; challenge_spawn_timer = 0
CHALLENGE_SPAWN_INTERVAL = 300000; challenge_pet_selection_scroll_y = 0
storage_transfer_popup_active = False
storage_transfer_info = {} # Holds item_id, direction, quantity, max_quantity, is_dragging_slider
sell_quantity = 1
max_sell_quantity = 0
is_dragging_sell_slider = False

def load_hatching_animation(egg_id):
    if egg_id not in item_data: return []
    base_path = item_data[egg_id]["image_path"].replace("_1.png", "_")
    frames = []
    for i in range(1, 23):
        path = f"{base_path}{i}.png"
        try:
            frames.append(safe_image_load(path).convert_alpha())
        except pygame.error:
            break
    return frames

def choose_pet_from_egg(egg_id):
    if egg_id not in item_data: return None
    egg_details = item_data[egg_id].get("data", {})
    possible_pets = egg_details.get("possible_pets", [])
    if not possible_pets: return None
    pet_ids = [p["pet_id"] for p in possible_pets]
    chances = [p["chance"] for p in possible_pets]
    return random.choices(pet_ids, weights=chances, k=1)[0]

def draw_item_effects(surface, effects_dict, start_pos):
    y_offset = 0; line_height = 28
    effects_title = font_info.render("Effects:", True, TEXT_COLOR)
    surface.blit(effects_title, (start_pos[0], start_pos[1]))
    y_offset += line_height
    for stat, value in effects_dict.items():
        if value > 0:
            text = f"+{value} {stat.capitalize()}"
            effect_text = font_info.render(text, True, BOOST_COLOR)
            surface.blit(effect_text, (start_pos[0] + 10, start_pos[1] + y_offset))
            y_offset += line_height
    return y_offset

def save_and_quit():
    if game_currency and selected_profile_idx is not None and incubator_manager and player_inventory:
        print("Saving game data...")
        for pet_obj in active_pets:
            for p_inv_pet in player_inventory.pets:
                if p_inv_pet['instance_id'] == pet_obj.instance_data['instance_id']:
                    p_inv_pet.update(pet_obj.instance_data)
                    break
        
        profile = profiles[selected_profile_idx]
        profile['money'] = game_currency.money
        profile['play_time'] = game_currency.get_current_play_time()
        profile['unlocked_incubators'] = incubator_manager.unlocked_incubators
        profile['incubator_slots'] = incubator_manager.slots
        profile['inventory'] = player_inventory.items
        profile['pets'] = player_inventory.pets
        profile['active_pet_instances'] = [p.instance_data['instance_id'] for p in active_pets]
        profile['unlocked_pet_slots'] = profiles[selected_profile_idx].get('unlocked_pet_slots', 5)
        profile['last_map'] = "world" if current_map == "chicken_map" else current_map

        save_profiles()
        save_global_storage()
        print("Save complete.")
    pygame.quit()
    sys.exit()

# -------------------- Main Loop --------------------
while True:
    dt = clock.tick(60); mouse_pos = pygame.mouse.get_pos()
    PANEL_WIDTH,ROW_HEIGHT,NUM_ROWS=1100,120,3; PANEL_X=SCREEN_WIDTH//2-PANEL_WIDTH//2; PANEL_Y=250; panel_rect=pygame.Rect(PANEL_X,PANEL_Y,PANEL_WIDTH,ROW_HEIGHT*NUM_ROWS)
    dialog_rect=pygame.Rect(0,0,600,250); dialog_rect.center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2); yes_button_rect=pygame.Rect(dialog_rect.left+50,dialog_rect.bottom-90,200,60); no_button_rect=pygame.Rect(dialog_rect.right-250,dialog_rect.bottom-90,200,60)
    
    if player_inventory and game_currency and scene not in ["loading", "profile_save", "char_select", "name_input"]:
        money_generation_timer += dt
        if money_generation_timer >= 60000:
            money_generation_timer -= 60000
            total_money_generated = 0
            for pet_obj in active_pets:
                pet_instance = pet_obj.instance_data; pet_def = pet_obj.definition
                if not pet_def: continue
                
                ### MODIFIED: Add level bonus to money generation
                pet_level = pet_instance.get('level', 0)
                level_bonus = 1.0 + (pet_level / 10.0)

                avg_stat_percent = (pet_instance['health']+pet_instance['happiness']+pet_instance['hunger'])/3.0
                avg_stat_ratio = avg_stat_percent / 100.0
                base_money = pet_def.get('base_money_per_minute', 0)
                
                money_for_pet = base_money * avg_stat_ratio * level_bonus
                total_money_generated += int(money_for_pet)
            
            if total_money_generated > 0:
                game_currency.money += total_money_generated
                if quest_manager: quest_manager.track_action("earn_money", amount=total_money_generated)
                print(f"Your active pets generated {total_money_generated} coins!")
            
            active_instance_ids = [p.instance_data['instance_id'] for p in active_pets]
            for pet_instance in player_inventory.get_all_pets():
                if pet_instance['instance_id'] not in active_instance_ids:
                    pet_def = pet_data.get(pet_instance['pet_id'], {})
                    if not pet_def: continue
                    decay_rates = pet_def.get('stat_decay_rate', {})
                    pet_instance['hunger'] = max(0, pet_instance['hunger'] - decay_rates.get('hunger',0)*60)
                    pet_instance['happiness'] = max(0, pet_instance['happiness'] - decay_rates.get('happiness',0)*60)
                    if pet_instance['hunger']<=0: pet_instance['health']=max(0,pet_instance['health']-decay_rates.get('health',0)*60)

    if current_map == "chicken_map" and scene == "play":
        challenge_spawn_timer += dt
        if challenge_spawn_timer >= CHALLENGE_SPAWN_INTERVAL:
            challenge_spawn_timer = 0
            active_enemies.clear()
            chicken_types = ["Chicken", "Dark_Brown_Chicken", "Dark_Chicken", "Light_Brown_Chicken"]
            for _ in range(10):
                c_type = random.choice(chicken_types)
                if c_type in enemy_data: active_enemies.append(Enemy(c_type))
            print(f"Spawned {len(active_enemies)} chickens in the challenge map.")

    for e in pygame.event.get():
        if e.type == pygame.QUIT: save_and_quit()
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            is_dragging_scrollbar = False
            if storage_transfer_popup_active: storage_transfer_info['is_dragging'] = False
            is_dragging_sell_slider = False
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if music_button_rect.collidepoint(mouse_pos) and scene not in ["loading", "profile_save", "char_select", "name_input"]:
                is_music_playing = not is_music_playing
                if is_music_playing: pygame.mixer.music.unpause()
                else: pygame.mixer.music.pause()
                continue

        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            if confirming_escape: confirming_escape = False
            elif storage_transfer_popup_active: storage_transfer_popup_active = False
            elif interaction_menu_open: interaction_menu_open = False; interaction_pet = None; interaction_submenu = None
            elif scene in ["shop_menu", "home_menu", "inventory_menu", "pet_management_menu", "storage_menu", "quest_menu", "quest_dialogue", "challenge_main_dialogue", "challenge_pre_sell_dialogue", "challenge_dialogue", "challenge_sell_dialogue", "challenge_pet_select"]:
                scene = "play"; is_dragging_scrollbar = False
            elif scene == "incubator_egg_select": scene = "home_menu"
            elif scene == "hatching_animation": pass
            else: confirming_escape = True

        if confirming_escape:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if yes_button_rect.collidepoint(e.pos): save_and_quit()
                elif no_button_rect.collidepoint(e.pos): confirming_escape = False
            continue

        if scene == "name_input":
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    if player_name_input.strip():
                        profiles[selected_profile_idx]={"name":player_name_input.strip(),"char":None,"money":10,"play_time":0,"unlocked_incubators":[True,True,True,True,False,False,False,False],"inventory":{},"incubator_slots":{},"pets":[],"active_pet_instances":[],"last_map":"world","unlocked_pet_slots":5,"quests":{'daily_quests':[],'progress':{},'claimed':[],'last_reset_day':0,'quests_accepted_today':False}}
                        save_profiles()
                        incubator_manager=Trung(profiles[selected_profile_idx]['unlocked_incubators'],{}); game_currency=TienTe(10,0); player_inventory=TuiDo({},[]); scene="char_select"
                elif e.key == pygame.K_BACKSPACE: player_name_input=player_name_input[:-1]
                else: player_name_input+=e.unicode
            continue
        elif scene == "profile_save":
            if e.type == pygame.MOUSEBUTTONDOWN:
                if confirming_delete:
                    if yes_button_rect.collidepoint(e.pos): profiles[delete_target_index]=None; save_profiles(); confirming_delete=False
                    elif no_button_rect.collidepoint(e.pos): confirming_delete=False
                else:
                    for i in range(NUM_ROWS):
                        row_rect=pygame.Rect(PANEL_X,PANEL_Y+(i*ROW_HEIGHT),PANEL_WIDTH,ROW_HEIGHT)
                        if trash_can_img and profiles[i] is not None and pygame.Rect(PANEL_X+PANEL_WIDTH-80,PANEL_Y+(i*ROW_HEIGHT)+ROW_HEIGHT//2-24,48,48).collidepoint(e.pos): confirming_delete=True; delete_target_index=i; break
                        if row_rect.collidepoint(e.pos):
                            selected_profile_idx=i; profile=profiles[i]
                            if profile is None: player_name_input=""; scene="name_input"
                            else:
                                if 'unlocked_pet_slots' not in profile or profile['unlocked_pet_slots']<5: profile['unlocked_pet_slots']=5
                                if 'active_pet_instances' not in profile: profile['active_pet_instances']=[]
                                if 'last_map' not in profile: profile['last_map']='world'
                                if 'quests' not in profile: profile['quests']={'daily_quests':[],'progress':{},'claimed':[],'last_reset_day':0,'quests_accepted_today':False}
                                if 'quests_accepted_today' not in profile['quests']: profile['quests']['quests_accepted_today']=False

                                ### NEW: Backwards compatibility for pet levels in save files
                                pets_data_saved = profile.get("pets", [])
                                for pet in pets_data_saved:
                                    pet.setdefault('level', 0)
                                    pet.setdefault('experience', 0)

                                if theme_song_path and not pygame.mixer.music.get_busy():
                                    pygame.mixer.music.load(theme_song_path); pygame.mixer.music.play(loops=-1)
                                    if not is_music_playing: pygame.mixer.music.pause()
                                
                                money=profile.get("money",10); play_time=profile.get("play_time",0)
                                inventory_data=profile.get("inventory",{}); 
                                game_currency=TienTe(money,play_time); player_inventory=TuiDo(inventory_data,pets_data_saved)
                                unlocked_data=profile.get("unlocked_incubators",[True,True,True,True,False,False,False,False]); slots_data=profile.get("incubator_slots",{})
                                incubator_manager=Trung(unlocked_data,slots_data)
                                quest_manager=QuestManager(profile,missions_data,player_inventory,game_currency); quest_manager.reset_if_needed()
                                
                                active_pets.clear()
                                for inst_id in profile.get('active_pet_instances',[]):
                                    pet_instance=player_inventory.get_pet_by_instance_id(inst_id)
                                    if pet_instance: active_pets.append(ThuCung(pet_instance))
                                
                                if profile.get("char"):
                                    selected=next((c for c in char_objs if c.name==profile["char"]),None)
                                    if selected:
                                        player=NguoiChamSoc(selected.name,selected.sheet_path,frame_data,2.0)
                                        player.x,player.y=SCREEN_WIDTH//2,SCREEN_HEIGHT//2
                                        saved_map = profile.get('last_map','world')
                                        if saved_map=="chicken_map":
                                            current_map='world'; scene="challenge_pet_select"
                                        else: current_map=saved_map; scene="play"
                                    else: scene="char_select"
                                else: scene="char_select"
                            break
        elif scene == "char_select":
            if e.type == pygame.MOUSEBUTTONDOWN:
                x,y=e.pos; is_arrow_click=False
                if 100<x<140 and SCREEN_HEIGHT//2-30<y<SCREEN_HEIGHT//2+30: selection_idx=(selection_idx-1)%len(char_objs); is_arrow_click=True
                elif SCREEN_WIDTH-140<x<SCREEN_WIDTH-100 and SCREEN_HEIGHT//2-30<y<SCREEN_HEIGHT//2+30: selection_idx=(selection_idx+1)%len(char_objs); is_arrow_click=True
                if not is_arrow_click:
                    selected=char_objs[selection_idx]; profiles[selected_profile_idx]["char"]=selected.name; save_profiles()
                    player=NguoiChamSoc(selected.name,selected.sheet_path,frame_data,2.0); player.x,player.y=SCREEN_WIDTH//2,SCREEN_HEIGHT//2; scene="play"
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT: selection_idx=(selection_idx-1)%len(char_objs)
                elif e.key == pygame.K_RIGHT: selection_idx=(selection_idx+1)%len(char_objs)
                elif e.key == pygame.K_RETURN:
                    selected=char_objs[selection_idx]; profiles[selected_profile_idx]["char"]=selected.name; save_profiles()
                    player=NguoiChamSoc(selected.name,selected.sheet_path,frame_data,2.0); player.x,player.y=SCREEN_WIDTH//2,SCREEN_HEIGHT//2; scene="play"
            for char_obj in char_objs: char_obj.update(dt)
        elif scene == "play":
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_j and active_challenge_pet and not active_challenge_pet.is_attacking:
                    active_challenge_pet.attack()
                    pet_rect=active_challenge_pet.get_rect(); attack_hitbox=pet_rect.inflate(50,20)
                    if active_challenge_pet.direction=="East": attack_hitbox.left=pet_rect.centerx
                    elif active_challenge_pet.direction=="West": attack_hitbox.right=pet_rect.centerx
                    elif active_challenge_pet.direction=="North": attack_hitbox.bottom=pet_rect.centery
                    elif active_challenge_pet.direction=="South": attack_hitbox.top=pet_rect.centery
                    for enemy in active_enemies[:]:
                        if attack_hitbox.colliderect(enemy.get_rect()):
                            enemy.health-=active_challenge_pet.damage
                            if enemy.health<=0:
                                active_enemies.remove(enemy)
                                if random.random()<enemy.definition['drop_chance']:
                                    drop_id=enemy.definition['drop_item']
                                    player_inventory.add_item(drop_id)
                                if quest_manager: quest_manager.track_action("defeat_enemy")
                elif e.key == pygame.K_q: scene = "quest_menu"
                elif e.key == pygame.K_e:
                    if interaction_menu_open: interaction_menu_open=False; interaction_pet=None; interaction_submenu=None; continue
                    
                    interacted_with_something = False
                    if current_map == "world":
                        for building in world_buildings:
                            can_interact, target_scene = building.check_interaction_and_draw_prompt(screen, player, False)
                            if can_interact:
                                scene = target_scene
                                if scene == "storage_menu": storage_selected_player_idx, storage_selected_global_idx = None, None; storage_player_scroll_y, storage_global_scroll_y = 0, 0
                                interacted_with_something = True; break
                        if not interacted_with_something and player and quest_interaction_rect.colliderect(player.get_rect()): scene = "quest_dialogue"; interacted_with_something = True
                        if not interacted_with_something and player and challenge_interaction_rect.colliderect(player.get_rect()):
                            scene = "challenge_main_dialogue"
                            interacted_with_something = True
                    elif current_map == "chicken_map":
                        if active_challenge_pet and challenge_npc_map and challenge_npc_map.get_rect().inflate(40,40).colliderect(active_challenge_pet.get_rect()):
                            current_map="world"; active_challenge_pet=None; active_enemies.clear()
                            if player: player.x,player.y = challenge_stand_rect.centerx,challenge_stand_rect.bottom+20
                            interacted_with_something=True
                        ### MODIFIED: Allow opening inventory in challenge map
                        else:
                            inventory_selected_item_id = None
                            scene = "inventory_menu"
                            interacted_with_something = True
                    elif current_map == "pet_area" and player:
                        player_rect=player.get_rect(); interacted_with_fence=False
                        if left_fence_interaction_rect.colliderect(player_rect):
                            if player_location_in_pet_area=="path": player.x=PATH_START_X-player_rect.width/2-10; player_location_in_pet_area="left"
                            elif player_location_in_pet_area=="left": player.x=PATH_START_X+player_rect.width/2+10; player_location_in_pet_area="path"
                            interacted_with_fence=True
                        elif right_fence_interaction_rect.colliderect(player_rect):
                            if player_location_in_pet_area=="path": player.x=PATH_END_X+player_rect.width/2+10; player_location_in_pet_area="right"
                            elif player_location_in_pet_area=="right": player.x=PATH_END_X-player_rect.width/2-10; player_location_in_pet_area="path"
                            interacted_with_fence=True

                        if not interacted_with_fence:
                            closest_pet = None; min_dist = 100 
                            for pet in active_pets:
                                if player and pygame.math.Vector2(player.x,player.y).distance_to((pet.x,pet.y)) < min_dist:
                                    min_dist = pygame.math.Vector2(player.x,player.y).distance_to((pet.x,pet.y)); closest_pet=pet
                            if closest_pet: interaction_pet=closest_pet; interaction_menu_open=True; interaction_submenu=None
                        interacted_with_something = True

                    if not interacted_with_something and not active_challenge_pet: inventory_selected_item_id = None; scene = "inventory_menu"
                elif e.key == pygame.K_r:
                    if not interaction_menu_open: pet_management_selected_instance_id=None; pet_list_scroll_y=0; scene="pet_management_menu"

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if backpack_rect.collidepoint(mouse_pos) and not interaction_menu_open: inventory_selected_item_id=None; scene="inventory_menu"
                elif pet_menu_rect.collidepoint(mouse_pos) and not interaction_menu_open: pet_management_selected_instance_id=None; pet_list_scroll_y=0; scene="pet_management_menu"
                elif mission_icon_rect.collidepoint(mouse_pos) and not interaction_menu_open: scene="quest_menu"
                elif interaction_menu_open:
                    for action, rect in clickable_interaction_rects.items():
                        if rect.collidepoint(mouse_pos):
                            if action=='feed_btn': interaction_submenu='feed'
                            elif action=='play_btn': interaction_submenu='play'
                            elif action in ['exit_interaction','cancel_interaction']: interaction_menu_open=False; interaction_pet=None; interaction_submenu=None
                            else: 
                                item_id=action; item_info=item_data[item_id]; item_effects=item_info["data"]["effects"]
                                interaction_pet.instance_data['hunger']=min(100,interaction_pet.instance_data['hunger']+item_effects.get('hunger',0))
                                interaction_pet.instance_data['happiness']=min(100,interaction_pet.instance_data['happiness']+item_effects.get('happiness',0))
                                interaction_pet.instance_data['health']=min(100,interaction_pet.instance_data['health']+item_effects.get('health',0))
                                if item_info['category']=='food': interaction_pet.show_effect('heart');
                                if quest_manager: quest_manager.track_action("feed")
                                elif item_info['category']=='toy': interaction_pet.show_effect('smile');
                                if quest_manager: quest_manager.track_action("play")
                                player_inventory.remove_item(item_id)
                                interaction_menu_open=False; interaction_pet=None; interaction_submenu=None
                            break
        elif scene == "shop_menu":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_e: scene = "play"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                shop_items_all=list(shop_manager.current_stock.items()); COLS,ROWS=4,2; BOX_SIZE,PADDING=150,20
                TABLE_W=(COLS*BOX_SIZE)+((COLS-1)*PADDING); TABLE_X=(SCREEN_WIDTH-TABLE_W)//2; TABLE_Y=max(150,(SCREEN_HEIGHT-(ROWS*(BOX_SIZE+PADDING)))//2+50)
                for i,(item_id,_) in enumerate(shop_items_all):
                    r,c=divmod(i,COLS); box_x=TABLE_X+c*(BOX_SIZE+PADDING); box_y=TABLE_Y+r*(BOX_SIZE+PADDING); box_rect=pygame.Rect(box_x,box_y,BOX_SIZE,BOX_SIZE)
                    if box_rect.collidepoint(mouse_pos):
                        message=shop_manager.buy_item(item_id,game_currency,player_inventory,quest_manager)
                        shop_message=message; shop_message_timer=time.time(); break
        elif scene == "home_menu":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_e: scene = "play"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and incubator_manager:
                click_result = incubator_manager.handle_click(mouse_pos, game_currency)
                if click_result:
                    if click_result['action'] == 'select_egg': incubator_selection_slot=click_result['slot']; scene="incubator_egg_select"
                    elif click_result['action'] == 'hatch':
                        hatching_info={'slot_key':click_result['slot_key'],'egg_id':click_result['egg_id']}; hatching_animation_frames=load_hatching_animation(hatching_info['egg_id'])
                        hatching_frame_index=0; hatching_timer=0; hatched_pet_info=None; scene="hatching_animation"
        elif scene == "incubator_egg_select":
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and incubator_manager:
                player_eggs=player_inventory.get_eggs(); select_panel_rect=pygame.Rect(0,0,800,500); select_panel_rect.center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2)
                EGG_COLS,EGG_BOX_SIZE,EGG_PADDING = 4,120,20
                for i,(egg_id,qty) in enumerate(player_eggs):
                    r,c=divmod(i,EGG_COLS); box_x=select_panel_rect.left+50+c*(EGG_BOX_SIZE+EGG_PADDING); box_y=select_panel_rect.top+100+r*(EGG_BOX_SIZE+EGG_PADDING)
                    egg_box_rect = pygame.Rect(box_x,box_y,EGG_BOX_SIZE,EGG_BOX_SIZE)
                    if egg_box_rect.collidepoint(mouse_pos):
                        player_inventory.remove_item(egg_id); incubator_manager.place_egg(incubator_selection_slot,egg_id); save_profiles(); scene="home_menu"; break
        elif scene == "inventory_menu":
            if e.type == pygame.KEYDOWN and e.key in [pygame.K_e, pygame.K_ESCAPE]: scene="play"; inventory_selected_item_id=None
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                items_in_inv=player_inventory.get_all_items()
                for i,(item_id,qty) in enumerate(items_in_inv):
                    r,c=divmod(i,10); box_x=100+(SCREEN_WIDTH*0.6-10*(80+10)+10)//2+c*(80+10); box_y=100+80+50+r*(80+10); item_rect=pygame.Rect(box_x,box_y,80,80)
                    if item_rect.collidepoint(mouse_pos): inventory_selected_item_id=item_id; break
        elif scene == "pet_management_menu":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r: scene="play"; is_dragging_scrollbar=False
            if e.type == pygame.MOUSEWHEEL:
                list_panel_rect = pygame.Rect(100,100,400,SCREEN_HEIGHT-200)
                if list_panel_rect.collidepoint(mouse_pos): pet_list_scroll_y-=e.y*SCROLL_SPEED
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if scrollbar_handle_rect.collidepoint(e.pos): is_dragging_scrollbar=True; scrollbar_drag_offset_y=e.pos[1]-scrollbar_handle_rect.y
                else:
                    list_panel_rect=pygame.Rect(100,100,400,SCREEN_HEIGHT-200)
                    list_content_rect=list_panel_rect.inflate(-40,-220); list_content_rect.top=list_panel_rect.top+120
                    if list_content_rect.collidepoint(mouse_pos):
                        pets_in_inv=player_inventory.get_all_pets(); ROW_H,PADDING_Y=80,10
                        for i,pet in enumerate(pets_in_inv):
                            adjusted_mouse_y=mouse_pos[1]-list_content_rect.top+pet_list_scroll_y
                            row_y_pos=i*(ROW_H+PADDING_Y)
                            pet_row_rect_virtual=pygame.Rect(0,row_y_pos,list_content_rect.width,ROW_H)
                            if pet_row_rect_virtual.collidepoint(mouse_pos[0]-list_content_rect.left,adjusted_mouse_y):
                                pet_management_selected_instance_id=pet['instance_id']; break
                    selected_pet_instance=player_inventory.get_pet_by_instance_id(pet_management_selected_instance_id)
                    if selected_pet_instance:
                        info_panel_rect=pygame.Rect(520,100,SCREEN_WIDTH-620,SCREEN_HEIGHT-200)
                        already_out=any(p.instance_data['instance_id']==pet_management_selected_instance_id for p in active_pets)
                        bring_out_rect=pygame.Rect(0,0,250,60); bring_out_rect.midbottom=(info_panel_rect.centerx,info_panel_rect.bottom-30)
                        if bring_out_rect.collidepoint(mouse_pos):
                            if already_out: active_pets=[p for p in active_pets if p.instance_data['instance_id']!=pet_management_selected_instance_id]
                            else:
                                unlocked_slots=profiles[selected_profile_idx]['unlocked_pet_slots']
                                if len(active_pets)<unlocked_slots: active_pets.append(ThuCung(selected_pet_instance))
                    unlocked_slots=profiles[selected_profile_idx]['unlocked_pet_slots']
                    if unlocked_slots<MAX_PET_SLOTS:
                        price_index=unlocked_slots-5
                        if 0<=price_index<len(PET_SLOT_UNLOCK_PRICES):
                            unlock_button_rect=pygame.Rect(list_panel_rect.left+20,list_panel_rect.bottom-70,list_panel_rect.width-40,50)
                            if unlock_button_rect.collidepoint(mouse_pos):
                                price=PET_SLOT_UNLOCK_PRICES[price_index]
                                if game_currency.money>=price:
                                    game_currency.money-=price; profiles[selected_profile_idx]['unlocked_pet_slots']+=1
                                    if quest_manager: quest_manager.track_action("unlock_pet_slot")
                                    pet_menu_message="Slot unlocked!"; pet_menu_message_timer=time.time()
                                else: pet_menu_message="Not enough coins!"; pet_menu_message_timer=time.time()
        elif scene == "storage_menu":
            if e.type == pygame.KEYDOWN and e.key in [pygame.K_e]: scene = "play"
            
            popup_width, popup_height = 500, 300
            popup_rect = pygame.Rect(0, 0, popup_width, popup_height); popup_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            
            if storage_transfer_popup_active:
                if e.type == pygame.MOUSEMOTION and storage_transfer_info.get('is_dragging', False):
                    slider_rect = pygame.Rect(popup_rect.left + 100, popup_rect.centery + 10, popup_rect.width - 200, 20)
                    relative_x = e.pos[0] - slider_rect.x
                    percent = max(0, min(1, relative_x / slider_rect.width))
                    new_qty = 1 + round(percent * (storage_transfer_info['max_quantity'] - 1))
                    storage_transfer_info['quantity'] = new_qty
                
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    slider_rect = pygame.Rect(popup_rect.left + 100, popup_rect.centery + 10, popup_rect.width - 200, 20)
                    minus_rect = pygame.Rect(popup_rect.left + 40, popup_rect.centery, 40, 40)
                    plus_rect = pygame.Rect(popup_rect.right - 80, popup_rect.centery, 40, 40)
                    confirm_rect = pygame.Rect(popup_rect.centerx - 150, popup_rect.bottom - 80, 120, 50)
                    cancel_rect = pygame.Rect(popup_rect.centerx + 30, popup_rect.bottom - 80, 120, 50)
                    
                    if slider_rect.collidepoint(e.pos):
                        storage_transfer_info['is_dragging'] = True
                        relative_x = e.pos[0] - slider_rect.x
                        percent = max(0, min(1, relative_x / slider_rect.width))
                        new_qty = 1 + round(percent * (storage_transfer_info['max_quantity'] - 1))
                        storage_transfer_info['quantity'] = new_qty
                    elif minus_rect.collidepoint(e.pos):
                        storage_transfer_info['quantity'] = max(1, storage_transfer_info['quantity'] - 1)
                    elif plus_rect.collidepoint(e.pos):
                        storage_transfer_info['quantity'] = min(storage_transfer_info['max_quantity'], storage_transfer_info['quantity'] + 1)
                    elif cancel_rect.collidepoint(e.pos):
                        storage_transfer_popup_active = False
                    elif confirm_rect.collidepoint(e.pos):
                        info = storage_transfer_info; qty_to_move = info['quantity']
                        if info['direction'] == 'store':
                            if player_inventory.remove_item(info['item_id'], qty_to_move):
                                global_storage_data['items'][info['item_id']] = global_storage_data['items'].get(info['item_id'], 0) + qty_to_move
                                storage_message = f"Stored {qty_to_move} {item_data[info['item_id']]['name']}."
                        elif info['direction'] == 'retrieve':
                            global_storage_data['items'][info['item_id']] -= qty_to_move
                            if global_storage_data['items'][info['item_id']] == 0: del global_storage_data['items'][info['item_id']]
                            player_inventory.add_item(info['item_id'], qty_to_move)
                            storage_message = f"Retrieved {qty_to_move} {item_data[info['item_id']]['name']}."
                        
                        save_profiles(); save_global_storage(); storage_transfer_popup_active = False
                        storage_selected_player_idx, storage_selected_global_idx = None, None
                        storage_message_timer = time.time()
                continue

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                items_tab_rect = pygame.Rect(SCREEN_WIDTH/2-220, 50, 200, 50); pets_tab_rect = pygame.Rect(SCREEN_WIDTH/2+20, 50, 200, 50)
                if items_tab_rect.collidepoint(mouse_pos): storage_scene_tab = 'items'; storage_selected_player_idx, storage_selected_global_idx = None, None
                elif pets_tab_rect.collidepoint(mouse_pos): storage_scene_tab = 'pets'; storage_selected_player_idx, storage_selected_global_idx = None, None
                
                store_button_rect = pygame.Rect(SCREEN_WIDTH/2-40, SCREEN_HEIGHT/2-60, 80, 80); retrieve_button_rect = pygame.Rect(SCREEN_WIDTH/2-40, SCREEN_HEIGHT/2+40, 80, 80)

                if store_button_rect.collidepoint(mouse_pos) and storage_selected_player_idx is not None:
                    if storage_scene_tab == 'items':
                        item_id, quantity = sorted(player_inventory.get_all_items())[storage_selected_player_idx]
                        storage_transfer_popup_active = True
                        storage_transfer_info = {"item_id": item_id, "direction": "store", "quantity": 1, "max_quantity": quantity, "is_dragging": False}
                    else:
                        pet_to_move = player_inventory.get_all_pets()[storage_selected_player_idx]
                        if any(p.instance_data['instance_id'] == pet_to_move['instance_id'] for p in active_pets):
                            storage_message = "Cannot move an active pet!"; storage_message_timer = time.time()
                        else:
                            player_inventory.pets.remove(pet_to_move); global_storage_data['pets'].append(pet_to_move)
                            storage_message = f"Moved {pet_to_move['name']} to storage."; storage_message_timer = time.time()
                            save_profiles(); save_global_storage(); storage_selected_player_idx = None
                
                elif retrieve_button_rect.collidepoint(mouse_pos) and storage_selected_global_idx is not None:
                    if storage_scene_tab == 'items':
                        item_id, quantity = sorted(global_storage_data['items'].items())[storage_selected_global_idx]
                        storage_transfer_popup_active = True
                        storage_transfer_info = {"item_id": item_id, "direction": "retrieve", "quantity": 1, "max_quantity": quantity, "is_dragging": False}
                    else:
                        pet_to_move = sorted(global_storage_data['pets'], key=lambda p: p['instance_id'])[storage_selected_global_idx]
                        global_storage_data['pets'].remove(pet_to_move); player_inventory.pets.append(pet_to_move)
                        storage_message = f"Moved {pet_to_move['name']} to inventory."; storage_message_timer = time.time()
                        save_profiles(); save_global_storage(); storage_selected_global_idx = None

            if e.type == pygame.MOUSEWHEEL:
                PANEL_MARGIN,TOP_MARGIN,BOTTOM_MARGIN=150,120,100; PANEL_Y=TOP_MARGIN; PANEL_HEIGHT=SCREEN_HEIGHT-TOP_MARGIN-BOTTOM_MARGIN
                PLAYER_PANEL_W=(SCREEN_WIDTH/2)-PANEL_MARGIN; PLAYER_PANEL_RECT=pygame.Rect(50,PANEL_Y,PLAYER_PANEL_W,PANEL_HEIGHT)
                GLOBAL_PANEL_RECT=pygame.Rect(SCREEN_WIDTH-50-PLAYER_PANEL_W,PANEL_Y,PLAYER_PANEL_W,PANEL_HEIGHT)
                if PLAYER_PANEL_RECT.collidepoint(mouse_pos): storage_player_scroll_y -= e.y * SCROLL_SPEED
                elif GLOBAL_PANEL_RECT.collidepoint(mouse_pos): storage_global_scroll_y -= e.y * SCROLL_SPEED
        elif scene == "hatching_animation":
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if hatched_pet_info and incubator_manager:
                    player_inventory.add_pet(hatched_pet_info['pet_id']); incubator_manager.clear_slot(hatching_info['slot_key'])
                    if quest_manager: quest_manager.track_action("hatch")
                    save_profiles(); hatching_info=None; hatching_animation_frames=[]; hatched_pet_info=None; scene="home_menu"
        elif scene == "quest_dialogue":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_e: scene="play"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if quest_dialogue_yes_rect.collidepoint(mouse_pos):
                    if quest_manager: quest_manager.assign_daily_quests()
                    scene="quest_menu"
                elif quest_dialogue_no_rect.collidepoint(mouse_pos): scene="play"
        ### MODIFIED: Updated event handling for the new challenge flow
        elif scene == "challenge_main_dialogue":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_e: scene = "play"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                dialogue_panel = pygame.Rect(100,SCREEN_HEIGHT/2-150,SCREEN_WIDTH-550,300) # Re-define for click detection
                challenge_main_fight_rect = pygame.Rect(dialogue_panel.centerx - 220, dialogue_panel.bottom - 100, 200, 60)
                challenge_main_sell_rect = pygame.Rect(dialogue_panel.centerx + 20, dialogue_panel.bottom - 100, 200, 60)
                if challenge_main_fight_rect.collidepoint(mouse_pos):
                    scene = "challenge_dialogue"
                elif challenge_main_sell_rect.collidepoint(mouse_pos):
                    scene = "challenge_pre_sell_dialogue"
        elif scene == "challenge_pre_sell_dialogue":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_e: scene = "play"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if challenge_pre_sell_no_rect.collidepoint(mouse_pos):
                    scene = "play"
                elif challenge_pre_sell_yes_rect.collidepoint(mouse_pos):
                    if player_inventory.items.get("item_chicken_meat", 0) > 0:
                        max_sell_quantity = player_inventory.items["item_chicken_meat"]
                        sell_quantity = 1
                        scene = "challenge_sell_dialogue"
                    else:
                        storage_message = "You don't have any chicken!"
                        storage_message_timer = time.time()
                        scene = "play"
        elif scene == "challenge_dialogue":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_e: scene="play"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if challenge_fight_yes_rect.collidepoint(mouse_pos): scene="challenge_pet_select"
                elif challenge_fight_no_rect.collidepoint(mouse_pos): scene="play"
        elif scene == "challenge_sell_dialogue":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_e: scene = "play"
            
            # Re-define rects inside the event loop for correct positioning
            dialog_rect=pygame.Rect(0,0,700,350); dialog_rect.center=(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2)

            if e.type == pygame.MOUSEMOTION and is_dragging_sell_slider:
                slider_rect = pygame.Rect(dialog_rect.centerx - 150, dialog_rect.centery, 300, 20)
                relative_x = e.pos[0] - slider_rect.x
                percent = max(0, min(1, relative_x / slider_rect.width))
                new_qty = 1 + round(percent * (max_sell_quantity - 1))
                sell_quantity = new_qty
            
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                slider_rect = pygame.Rect(dialog_rect.centerx - 150, dialog_rect.centery, 300, 20)
                minus_rect = pygame.Rect(slider_rect.left - 60, slider_rect.centery - 10, 40, 40)
                plus_rect = pygame.Rect(slider_rect.right + 20, slider_rect.centery - 10, 40, 40)
                sell_rect = pygame.Rect(dialog_rect.centerx - 150, dialog_rect.bottom - 80, 120, 50)
                cancel_rect = pygame.Rect(dialog_rect.centerx + 30, dialog_rect.bottom - 80, 120, 50)
                
                if slider_rect.collidepoint(e.pos):
                    is_dragging_sell_slider = True
                    relative_x = e.pos[0] - slider_rect.x
                    percent = max(0, min(1, relative_x / slider_rect.width))
                    new_qty = 1 + round(percent * (max_sell_quantity - 1))
                    sell_quantity = new_qty
                elif minus_rect.collidepoint(e.pos):
                    sell_quantity = max(1, sell_quantity - 1)
                elif plus_rect.collidepoint(e.pos):
                    sell_quantity = min(max_sell_quantity, sell_quantity + 1)
                elif cancel_rect.collidepoint(e.pos):
                    scene = "play"
                elif sell_rect.collidepoint(e.pos):
                    if player_inventory.remove_item("item_chicken_meat", sell_quantity):
                        revenue = sell_quantity * 20
                        game_currency.money += revenue
                        storage_message = f"Sold {sell_quantity} meat for {revenue} coins."
                        storage_message_timer = time.time()
                    scene = "play"
        elif scene == "quest_menu":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_q: scene="play"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if not quest_manager: continue
                quest_panel_rect=pygame.Rect(0,0,900,600); quest_panel_rect.center=(SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
                start_y=quest_panel_rect.top+100
                for i,quest_id in enumerate(quest_manager.quest_data['daily_quests']):
                    quest_box_y=start_y+i*150
                    claim_button_rect=pygame.Rect(quest_panel_rect.right-200,quest_box_y+45,150,60)
                    if claim_button_rect.collidepoint(mouse_pos):
                        success,message=quest_manager.claim_reward(quest_id)
                        quest_menu_message=message; quest_menu_message_timer=time.time(); break
        elif scene == "challenge_pet_select":
            if e.type == pygame.MOUSEWHEEL:
                list_panel_rect = pygame.Rect(0,0,500,SCREEN_HEIGHT-200); list_panel_rect.center = (SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
                if list_panel_rect.collidepoint(mouse_pos): challenge_pet_selection_scroll_y-=e.y*SCROLL_SPEED
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                eligible_pets = [p for p in player_inventory.get_all_pets() if pet_data.get(p['pet_id'],{}).get('can_attack')]
                list_panel_rect = pygame.Rect(0,0,500,SCREEN_HEIGHT-200); list_panel_rect.center = (SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
                list_content_rect = list_panel_rect.inflate(-40,-120); list_content_rect.top=list_panel_rect.top+80
                if list_content_rect.collidepoint(mouse_pos):
                    ROW_H,PADDING_Y=80,10
                    for i,pet in enumerate(eligible_pets):
                        adjusted_mouse_y=mouse_pos[1]-list_content_rect.top+challenge_pet_selection_scroll_y
                        row_y_pos=i*(ROW_H+PADDING_Y)
                        pet_row_rect_virtual=pygame.Rect(0,row_y_pos,list_content_rect.width,ROW_H)
                        if pet_row_rect_virtual.collidepoint(mouse_pos[0]-list_content_rect.left,adjusted_mouse_y):
                            active_challenge_pet=ChallengePet(pet); current_map="chicken_map"; scene="play"
                            challenge_spawn_timer=CHALLENGE_SPAWN_INTERVAL; break

    # -------------------- Draw Scenes --------------------
    screen.fill((0, 0, 0))
    
    if scene == 'play': clickable_interaction_rects = {}
    if player: player.update(dt)
    if quest_giver_npc: quest_giver_npc.update(dt)
    if challenge_npc_world: challenge_npc_world.update(dt)
    if challenge_npc_map: challenge_npc_map.update(dt)
    if current_map == "pet_area":
        for pet in active_pets: pet.update(dt)
    if active_enemies:
        for enemy in active_enemies: enemy.update(dt)
    if active_challenge_pet:
        active_challenge_pet.update(dt)

    if scene == "loading":
        screen.blit(title_img,(0,0)); elapsed=time.time()-loading_start; pct=min(elapsed/3,1); w,h=400,30; x,y=(SCREEN_WIDTH-w)//2,int(SCREEN_HEIGHT*0.85); pygame.draw.rect(screen,GRAY,(x,y,w,h),1,10); pygame.draw.rect(screen,LOADING_BAR,(x+2,y+2,int((w-4)*pct),h-4),0,8)
        if pct>=1: time.sleep(0.5); scene="profile_save"
    elif scene == "name_input":
        screen.blit(bg_img,(0,0)); overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0)); prompt=font.render("Enter your name:",True,WHITE); screen.blit(prompt,(SCREEN_WIDTH//2-prompt.get_width()//2,SCREEN_HEIGHT//2-100)); name_surface=font.render(player_name_input+"_",True,WHITE); screen.blit(name_surface,(SCREEN_WIDTH//2-name_surface.get_width()//2,SCREEN_HEIGHT//2))
    elif scene == "profile_save":
        screen.blit(bg_img,(0,0)); overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,100)); screen.blit(overlay,(0,0)); title_label=font.render("SELECT A PROFILE",True,WHITE); screen.blit(title_label,(SCREEN_WIDTH//2-title_label.get_width()//2,150)); pygame.draw.rect(screen,PANEL_FILL_COLOR,panel_rect,0,10)
        for i in range(NUM_ROWS):
            row_y=PANEL_Y+(i*ROW_HEIGHT); profile=profiles[i]; char=None; screen.blit(font.render(f"{i+1}.",True,TEXT_COLOR),font.render(f"{i+1}.",True,TEXT_COLOR).get_rect(center=(PANEL_X+50,row_y+ROW_HEIGHT//2)))
            if profile and profile.get("char"): char=next((c for c in char_objs if c.name==profile["char"]),None)
            if char: char.update(dt); char.draw(screen,(PANEL_X+130,row_y+ROW_HEIGHT//2))
            name_y_offset=-20 if profile else 0; name_str,color=(profile.get("name","PROFILE"),TEXT_COLOR) if profile else ("[EMPTY]",GRAY)
            text_surf=font.render(name_str.upper(),True,color); screen.blit(text_surf,text_surf.get_rect(midleft=(PANEL_X+220,row_y+ROW_HEIGHT//2+name_y_offset)))
            if profile:
                pet_count = len(profile.get('pets',[])); slot_count=profile.get('unlocked_pet_slots',5)
                info_text_str=f"Money: {profile.get('money',0)} Time: {TienTe.format_time(profile.get('play_time',0))} Pets: {pet_count} Slots: {slot_count}"; info_surface=font_info.render(info_text_str,True,TEXT_COLOR)
                info_rect=info_surface.get_rect(midleft=(PANEL_X+220,row_y+ROW_HEIGHT//2+25)); screen.blit(info_surface,info_rect)
            if profile and trash_can_img: screen.blit(trash_can_img,trash_can_img.get_rect(center=(PANEL_X+PANEL_WIDTH-60,row_y+ROW_HEIGHT//2)))
            if i<NUM_ROWS-1: pygame.draw.line(screen,PANEL_BORDER_COLOR,(PANEL_X,row_y+ROW_HEIGHT),(PANEL_X+PANEL_WIDTH,row_y+ROW_HEIGHT),4)
        pygame.draw.rect(screen,PANEL_BORDER_COLOR,panel_rect,6,10)
        if confirming_delete:
            overlay_dark=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay_dark.fill((0,0,0,120)); screen.blit(overlay_dark,(0,0)); pygame.draw.rect(screen,PANEL_FILL_COLOR,dialog_rect,0,10); pygame.draw.rect(screen,PANEL_BORDER_COLOR,dialog_rect,6,10); q_text=font_small.render("Delete this save profile?",True,TEXT_COLOR); screen.blit(q_text,q_text.get_rect(center=(dialog_rect.centerx,dialog_rect.top+60)))
            for r,t in [(yes_button_rect,"Yes"),(no_button_rect,"No")]: pygame.draw.rect(screen,BUTTON_HOVER_COLOR if r.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,r,0,8); screen.blit(font.render(t,True,WHITE),font.render(t,True,WHITE).get_rect(center=r.center))
    elif scene == "char_select":
        screen.blit(bg_img,(0,0)); overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,80)); screen.blit(overlay,(0,0)); label=font.render("Choose your character",True,WHITE); screen.blit(label,(SCREEN_WIDTH//2-label.get_width()//2,100)); char=char_objs[selection_idx]; large_char=NguoiChamSoc(char.name,char.sheet_path,frame_data,10.0); large_char.frame_index=char.frame_index; large_char.draw(screen,(SCREEN_WIDTH//2,SCREEN_HEIGHT//2)); pygame.draw.polygon(screen,WHITE,[(100,SCREEN_HEIGHT//2),(140,SCREEN_HEIGHT//2-30),(140,SCREEN_HEIGHT//2+30)]); pygame.draw.polygon(screen,WHITE,[(SCREEN_WIDTH-100,SCREEN_HEIGHT//2),(SCREEN_WIDTH-140,SCREEN_HEIGHT//2-30),(SCREEN_WIDTH-140,SCREEN_HEIGHT//2+30)])
    elif scene == "hatching_animation":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 220)); screen.blit(overlay, (0, 0))
        if not hatched_pet_info:
            if hatching_animation_frames:
                time_per_frame = HATCH_ANIM_DURATION / len(hatching_animation_frames)
                hatching_timer += dt
                if hatching_timer > time_per_frame: hatching_frame_index += 1; hatching_timer = 0
                if hatching_frame_index >= len(hatching_animation_frames):
                    pet_id = choose_pet_from_egg(hatching_info['egg_id'])
                    if pet_id:
                        pet_frames = load_pet_animation_frames(pet_id, "idle", scale=15.0) 
                        if pet_frames: hatched_pet_info = {'pet_id': pet_id, 'frames': pet_frames, 'frame_index': 0, 'timer': 0}
                        else: scene = "home_menu"
                    else: scene = "home_menu"
                else:
                    current_frame=hatching_animation_frames[hatching_frame_index]; scaled_frame=pygame.transform.scale(current_frame,(512,512))
                    frame_rect=scaled_frame.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2)); screen.blit(scaled_frame,frame_rect)
            else: scene = "home_menu"
        else:
            pet_frames = hatched_pet_info['frames']
            if pet_frames:
                hatched_pet_info['timer'] += dt
                if hatched_pet_info['timer'] > PET_ANIM_SPEED:
                    hatched_pet_info['frame_index'] = (hatched_pet_info['frame_index'] + 1) % len(pet_frames)
                    hatched_pet_info['timer'] = 0
                pet_image = pet_frames[hatched_pet_info['frame_index']]; pet_rect = pet_image.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2)); screen.blit(pet_image,pet_rect)
            pet_display_name = pet_data.get(hatched_pet_info['pet_id'],{}).get('name',hatched_pet_info['pet_id'])
            pet_name_text = font_reveal.render(pet_display_name.upper(),True,WHITE); name_rect=pet_name_text.get_rect(center=(SCREEN_WIDTH//2,pet_rect.bottom+60)); screen.blit(pet_name_text,name_rect)
            continue_text=font_small.render("Click to continue",True,GRAY); continue_rect=continue_text.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT-80)); screen.blit(continue_text,continue_rect)

    else: 
        if current_map == "chicken_map": screen.blit(chicken_map_img, (0, 0))
        else: screen.blit(play_map_img, (0, 0))

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if player and not active_challenge_pet:
            speed=300*dt/1000
            if not interaction_menu_open and not scene.endswith("dialogue"):
                if keys[pygame.K_w]: dy=-speed; player.last_dir="North"
                elif keys[pygame.K_s]: dy=speed; player.last_dir="South"
                if keys[pygame.K_a]: dx=-speed; player.last_dir="West"
                elif keys[pygame.K_d]: dx=speed; player.last_dir="East"

        if current_map == "world":
            for building in world_buildings: building.draw(screen)
            for pos in fence_objects: screen.blit(fence_img, pos)
            if quest_giver_npc: quest_giver_npc.draw(screen, (quest_giver_npc.x, quest_giver_npc.y))
            screen.blit(quest_stand_img, quest_stand_rect)
            bob_offset=(1+(time.time()*3)%1)*-5; pointer_pos=(quest_stand_rect.centerx-quest_pointer_img.get_width()/2,quest_stand_rect.top-30+bob_offset)
            screen.blit(quest_pointer_img,pointer_pos); screen.blit(pointer_text_surface,(pointer_pos[0]-(pointer_text_surface.get_width()-quest_pointer_img.get_width())/2,pointer_pos[1]-25))
            if challenge_npc_world: challenge_npc_world.draw(screen, (challenge_npc_world.x, challenge_npc_world.y))
            screen.blit(challenge_stand_img, challenge_stand_rect)
            bob_offset_ch=(1+(time.time()*3.2)%1)*-5; pointer_pos_ch=(challenge_stand_rect.centerx-quest_pointer_img.get_width()/2,challenge_stand_rect.top-30+bob_offset_ch)
            screen.blit(quest_pointer_img,pointer_pos_ch); screen.blit(challenge_pointer_text_surface,(pointer_pos_ch[0]-(challenge_pointer_text_surface.get_width()-quest_pointer_img.get_width())/2,pointer_pos_ch[1]-25))
            if player and not active_challenge_pet:
                is_moving = (dx != 0 or dy != 0)
                key = f"Walk{player.last_dir}" if is_moving else f"Idle{player.last_dir}"
                player.draw(screen, (player.x, player.y), key)
        
        elif current_map == "pet_area":
            screen.blit(pond_img, pond_rect) 
            
            sorted_sprites = [] 
            if player:
                is_moving = (dx != 0 or dy != 0)
                player_img = player.get_current_image(f"Walk{player.last_dir}" if is_moving else f"Idle{player.last_dir}")
                sorted_sprites.append({'image': player_img, 'pos': player.get_rect().topleft, 'y_sort': player.get_rect().bottom})
            for pet in active_pets:
                pet_img = pet.get_current_animation_frames()[pet.frame_index]
                if not pet.definition.get("directional") and pet.direction == 'West': pet_img = pygame.transform.flip(pet_img, True, False)
                sorted_sprites.append({'image': pet_img, 'pos': pet.get_rect().topleft, 'y_sort': pet.get_rect().bottom})
            for key, data in decorations_to_draw.items():
                if key != 'pond': sorted_sprites.append({'image': data['img'], 'pos': data['rect'].topleft, 'y_sort': data['y_sort']})
            
            sorted_sprites.sort(key=lambda s: s['y_sort'])
            
            for sprite in sorted_sprites: screen.blit(sprite['image'], sprite['pos'])

            for pos in left_fence_line: screen.blit(fence_img_vertical_left, pos)
            for pos in right_fence_line: screen.blit(fence_img_vertical_right, pos)
            
            if DEBUG_MODE:
                for rect in decoration_collision_rects: pygame.draw.rect(screen, (0, 255, 255), rect, 2)
        
        elif current_map == "chicken_map":
            if challenge_npc_map: challenge_npc_map.draw(screen, (challenge_npc_map.x, challenge_npc_map.y))
            for enemy in active_enemies: enemy.draw(screen)

        if active_challenge_pet:
            active_challenge_pet.draw(screen)

        if scene == "play":
            if player and not active_challenge_pet:
                player.x += dx
                player.y += dy
                if current_map == "pet_area":
                    player_feet_rect = pygame.Rect(player.get_rect().left, player.get_rect().bottom - 20, player.get_rect().width, 20)
                    for dec_rect in decoration_collision_rects:
                        if player_feet_rect.colliderect(dec_rect): player.x -= dx; player.y -= dy; break
                player_rect = player.get_rect()
                if current_map == "world":
                    player_feet_y = player_rect.bottom
                    if fence_y + 50 <= player_feet_y <= fence_y + 100:
                        if not (path_center_x < player.x < path_center_x + path_width): player.y -= dy
                    if player_rect.left < 0: player.x = player_rect.width / 2
                    if player_rect.right > SCREEN_WIDTH: player.x = SCREEN_WIDTH - player_rect.width / 2
                    if player_rect.top < 0: player.y = player_rect.height / 2
                elif current_map == "pet_area":
                    if player_location_in_pet_area == "path":
                        if player_rect.left < PATH_START_X: player.x = PATH_START_X + player_rect.width / 2
                        if player_rect.right > PATH_END_X: player.x = PATH_END_X - player_rect.width / 2
                    elif player_location_in_pet_area == "left":
                        if player_rect.left < 0: player.x = player_rect.width / 2
                        if player_rect.right > PATH_START_X: player.x = PATH_START_X - player_rect.width / 2
                    elif player_location_in_pet_area == "right":
                        if player_rect.left < PATH_END_X: player.x = PATH_END_X + player_rect.width / 2
                        if player_rect.right > SCREEN_WIDTH: player.x = SCREEN_WIDTH - player_rect.width / 2
                    if player_rect.bottom > SCREEN_HEIGHT: player.y = SCREEN_HEIGHT - player_rect.height / 2
                elif current_map == "chicken_map":
                    if player_rect.left < 0: player.x = player_rect.width / 2
                    if player_rect.right > SCREEN_WIDTH: player.x = SCREEN_WIDTH - player_rect.width / 2
                    if player_rect.top < 0: player.y = player_rect.height / 2
                    if player_rect.bottom > SCREEN_HEIGHT: player.y = SCREEN_HEIGHT - player_rect.height / 2
            
            if current_map == "world":
                if player and player.y > SCREEN_HEIGHT and path_center_x < player.x < path_center_x + path_width:
                    current_map = "pet_area"; player.y = 10; player.x = SCREEN_WIDTH // 2; player_location_in_pet_area = "path"
            elif current_map == "pet_area":
                if player and player.y < 0:
                    current_map = "world"; player.y = SCREEN_HEIGHT - 50
                    active_ids = [p.instance_data['instance_id'] for p in active_pets]; profiles[selected_profile_idx]['active_pet_instances'] = active_ids; save_profiles()
            
            if current_map == "world":
                interaction_is_possible = False
                for building in world_buildings:
                    can_interact, _ = building.check_interaction_and_draw_prompt(screen, player, interaction_menu_open)
                    if can_interact: interaction_is_possible = True
                
                if not interaction_is_possible and player and quest_interaction_rect.colliderect(player.get_rect()):
                    prompt_text=font_small.render("Press 'E' for daily quests",True,WHITE); prompt_bg=pygame.Surface((prompt_text.get_width()+20,prompt_text.get_height()+10),pygame.SRCALPHA); prompt_bg.fill((0,0,0,150)); screen.blit(prompt_bg,(20,SCREEN_HEIGHT-60)); screen.blit(prompt_text,(30,SCREEN_HEIGHT-55))
                elif not interaction_is_possible and player and challenge_interaction_rect.colliderect(player.get_rect()):
                    prompt_text=font_small.render("Press 'E' to interact",True,WHITE); prompt_bg=pygame.Surface((prompt_text.get_width()+20,prompt_text.get_height()+10),pygame.SRCALPHA); prompt_bg.fill((0,0,0,150)); screen.blit(prompt_bg,(20,SCREEN_HEIGHT-60)); screen.blit(prompt_text,(30,SCREEN_HEIGHT-55))

            elif current_map == "pet_area":
                can_interact_with_fence = False
                if not interaction_menu_open and player:
                    if left_fence_interaction_rect.colliderect(player.get_rect()) or right_fence_interaction_rect.colliderect(player.get_rect()): can_interact_with_fence = True
                
                if can_interact_with_fence:
                    prompt_text=font_small.render("Press 'E' to cross fence",True,WHITE); prompt_bg=pygame.Surface((prompt_text.get_width()+20,prompt_text.get_height()+10),pygame.SRCALPHA); prompt_bg.fill((0,0,0,150)); screen.blit(prompt_bg,(20,SCREEN_HEIGHT-60)); screen.blit(prompt_text,(30,SCREEN_HEIGHT-55))
                else:
                    can_interact_with_pet=False
                    if not interaction_menu_open:
                        for pet in active_pets:
                            if player and pygame.math.Vector2(player.x,player.y).distance_to((pet.x,pet.y))<100:
                                if(player_location_in_pet_area == pet.section): can_interact_with_pet = True; break
                    if can_interact_with_pet:
                        prompt_text=font_small.render("Press 'E' to interact",True,WHITE); prompt_bg=pygame.Surface((prompt_text.get_width()+20,prompt_text.get_height()+10),pygame.SRCALPHA); prompt_bg.fill((0,0,0,150)); screen.blit(prompt_bg,(20,SCREEN_HEIGHT-60)); screen.blit(prompt_text,(30,SCREEN_HEIGHT-55))
            
            elif current_map == "chicken_map":
                if active_challenge_pet and challenge_npc_map and challenge_npc_map.get_rect().inflate(40,40).colliderect(active_challenge_pet.get_rect()):
                    prompt_text=font_small.render("Press 'E' to go home",True,WHITE); prompt_bg=pygame.Surface((prompt_text.get_width()+20,prompt_text.get_height()+10),pygame.SRCALPHA); prompt_bg.fill((0,0,0,150)); screen.blit(prompt_bg,(20,SCREEN_HEIGHT-60)); screen.blit(prompt_text,(30,SCREEN_HEIGHT-55))

            screen.blit(backpack_img, backpack_rect); screen.blit(pet_menu_icon, pet_menu_rect); screen.blit(mission_icon_img, mission_icon_rect)

            if interaction_menu_open and interaction_pet:
                if interaction_submenu is None:
                    panel_w,panel_h=200,200; panel_rect=pygame.Rect(0,0,panel_w,panel_h); panel_rect.midleft=(interaction_pet.get_rect().right+10,interaction_pet.get_rect().centery)
                    panel_rect.clamp_ip(screen.get_rect()); pygame.draw.rect(screen,PANEL_FILL_COLOR,panel_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,panel_rect,4,15)
                    pet_name=interaction_pet.instance_data.get('name','Pet'); name_text=font_small.render(pet_name,True,TEXT_COLOR); name_rect=name_text.get_rect(centerx=panel_rect.centerx,top=panel_rect.top+15); screen.blit(name_text,name_rect)
                    button_y_start=name_rect.bottom+15; feed_btn_rect=pygame.Rect(panel_rect.x+20,button_y_start,panel_w-40,50); play_btn_rect=pygame.Rect(panel_rect.x+20,feed_btn_rect.bottom+10,panel_w-40,50)
                    pygame.draw.rect(screen,BUTTON_HOVER_COLOR if feed_btn_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,feed_btn_rect,0,8); feed_text=font_info.render("Feed",True,WHITE); screen.blit(feed_text,feed_text.get_rect(center=feed_btn_rect.center))
                    pygame.draw.rect(screen,BUTTON_HOVER_COLOR if play_btn_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,play_btn_rect,0,8); play_text=font_info.render("Play",True,WHITE); screen.blit(play_text,play_text.get_rect(center=play_btn_rect.center))
                    clickable_interaction_rects['feed_btn']=feed_btn_rect; clickable_interaction_rects['play_btn']=play_btn_rect
                else:
                    items_to_show=[]; title=""
                    if interaction_submenu=='feed': items_to_show=[(k,v) for k,v in player_inventory.items.items() if item_data.get(k,{}).get('category')=='food']; title="CHOOSE FOOD"
                    elif interaction_submenu=='play': items_to_show=[(k,v) for k,v in player_inventory.items.items() if item_data.get(k,{}).get('category')=='toy']; title="CHOOSE TOY"
                    panel_w,panel_h=600,400; panel_rect=pygame.Rect(0,0,panel_w,panel_h); panel_rect.center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2)
                    pygame.draw.rect(screen,PANEL_FILL_COLOR,panel_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,panel_rect,6,15)
                    title_text=font.render(title,True,TEXT_COLOR); screen.blit(title_text,title_text.get_rect(centerx=panel_rect.centerx,top=panel_rect.top+20))
                    if not items_to_show: none_text=font_small.render("You have none!",True,TEXT_COLOR); screen.blit(none_text,none_text.get_rect(center=panel_rect.center))
                    else:
                        ITEM_COLS,ITEM_BOX_SIZE,ITEM_PADDING = 4,100,15
                        for i,(item_id,qty) in enumerate(items_to_show):
                            r,c=divmod(i,ITEM_COLS); box_x=panel_rect.left+50+c*(ITEM_BOX_SIZE+ITEM_PADDING); box_y=panel_rect.top+80+r*(ITEM_BOX_SIZE+ITEM_PADDING)
                            item_box_rect=pygame.Rect(box_x,box_y,ITEM_BOX_SIZE,ITEM_BOX_SIZE); pygame.draw.rect(screen,LOCKED_SLOT_COLOR,item_box_rect,0,8)
                            if item_img:=item_images.get(item_id):
                                scaled_img=pygame.transform.scale(item_img,(ITEM_BOX_SIZE-20,ITEM_BOX_SIZE-20)); screen.blit(scaled_img,scaled_img.get_rect(center=item_box_rect.center))
                            qty_text=font_info.render(f"x{qty}",True,TEXT_COLOR); screen.blit(qty_text,qty_text.get_rect(right=item_box_rect.right-5,bottom=item_box_rect.bottom-5))
                            pygame.draw.rect(screen,BUTTON_HOVER_COLOR if item_box_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,item_box_rect,4,8)
                            clickable_interaction_rects[item_id]=item_box_rect
                    cancel_btn_rect=pygame.Rect(0,0,150,50); cancel_btn_rect.midbottom=(panel_rect.centerx,panel_rect.bottom-20)
                    pygame.draw.rect(screen,BUTTON_HOVER_COLOR if cancel_btn_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,cancel_btn_rect,0,8)
                    cancel_text=font.render("Cancel",True,WHITE); screen.blit(cancel_text,cancel_text.get_rect(center=cancel_btn_rect.center)); clickable_interaction_rects['cancel_interaction']=cancel_btn_rect
        elif scene == "shop_menu":
            shop_manager.update(); shopkeeper.update(dt); overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            shop_items_all=list(shop_manager.current_stock.items()); COLS,ROWS=4,2; BOX_SIZE,PADDING=150,20
            TABLE_W=(COLS*BOX_SIZE)+((COLS-1)*PADDING); TABLE_H=(ROWS*(BOX_SIZE+PADDING))-PADDING
            TABLE_X=(SCREEN_WIDTH-TABLE_W)//2; TABLE_Y=max(150,(SCREEN_HEIGHT-TABLE_H)//2+50)
            container_rect=pygame.Rect(TABLE_X-PADDING,TABLE_Y-PADDING-80,TABLE_W+2*PADDING,TABLE_H+2*PADDING+80)
            shopkeeper.draw(screen,(container_rect.left-100,container_rect.centery+20),"IdleSouth")
            pygame.draw.rect(screen,PANEL_FILL_COLOR,container_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,container_rect,6,15)
            quote_text=font.render("WHAT DO YOU WANT TO BUY?",True,WHITE); quote_rect=quote_text.get_rect(center=(container_rect.centerx,container_rect.top+55)); screen.blit(quote_text,quote_rect)
            time_left=int(shop_manager.restock_interval-(time.time()-shop_manager.last_restock_time)); minutes,seconds=divmod(time_left,60)
            restock_text=font_info.render(f"RESTOCK IN: {minutes:02d}:{seconds:02d}",True,WHITE); restock_rect=restock_text.get_rect(midbottom=(quote_rect.centerx+120,quote_rect.top+5)); screen.blit(restock_text,restock_rect)
            hovered_item_id=None
            for i,(item_id,stock_info) in enumerate(shop_items_all):
                r,c=divmod(i,COLS); box_x=TABLE_X+c*(BOX_SIZE+PADDING); box_y=TABLE_Y+r*(BOX_SIZE+PADDING); box_rect=pygame.Rect(box_x,box_y,BOX_SIZE,BOX_SIZE)
                if box_rect.collidepoint(mouse_pos): hovered_item_id=item_id
                pygame.draw.rect(screen,(230,200,130),box_rect,0,10)
                if img_to_draw:=item_images.get(item_id): screen.blit(img_to_draw,img_to_draw.get_rect(center=(box_rect.centerx,box_rect.centery-10)))
                price_text=font_info.render(str(stock_info["price"]),True,TEXT_COLOR); price_icon=pygame.transform.scale(coin_img,(24,24)); total_w=price_text.get_width()+price_icon.get_width()+5; start_x_price=box_rect.centerx-total_w/2
                screen.blit(price_icon,(start_x_price,box_rect.bottom-35)); screen.blit(price_text,(start_x_price+price_icon.get_width()+5,box_rect.bottom-35))
                if stock_info["quantity"]>0:
                    qty_text=font_info.render(f"x{stock_info['quantity']}",True,TEXT_COLOR); screen.blit(qty_text,qty_text.get_rect(topright=(box_rect.right-10,box_rect.top+5)))
                else:
                    scaled_sold_out=pygame.transform.scale(sold_out_img,(BOX_SIZE-20,BOX_SIZE-20)); screen.blit(scaled_sold_out,scaled_sold_out.get_rect(center=box_rect.center))
                pygame.draw.rect(screen,BUTTON_HOVER_COLOR if box_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,box_rect,4,10)
            
            if hovered_item_id and (data := item_data.get(hovered_item_id)):
                ### FIX: Made info panel taller and aligned it with the shop grid top
                info_panel_rect = pygame.Rect(container_rect.right + 20, container_rect.top, 350, 500)
                pygame.draw.rect(screen, PANEL_FILL_COLOR, info_panel_rect, 0, 15)
                pygame.draw.rect(screen, PANEL_BORDER_COLOR, info_panel_rect, 4, 15)
                
                name_text = font_small.render(data['name'], True, TEXT_COLOR)
                name_rect = name_text.get_rect(centerx=info_panel_rect.centerx, top=info_panel_rect.top + 20)
                screen.blit(name_text, name_rect)

                if img_to_draw := item_images.get(hovered_item_id):
                    img_rect = img_to_draw.get_rect(centerx=info_panel_rect.centerx, top=name_rect.bottom + 10)
                    screen.blit(img_to_draw, img_rect)
                    current_y_pos = img_rect.bottom + 15
                else:
                    current_y_pos = name_rect.bottom + 15

                desc_rect = pygame.Rect(info_panel_rect.left + 20, current_y_pos, info_panel_rect.width - 40, 200)
                y_after_desc = draw_text_wrapped(screen, data['description'], font_info, TEXT_COLOR, desc_rect)
                current_y_pos = y_after_desc + 10

                if data.get("category") == "egg" and "possible_pets" in data.get("data", {}):
                    possible_pets = data["data"]["possible_pets"]
                    pets_header = font_info.render("Possible Pets:", True, TEXT_COLOR)
                    screen.blit(pets_header, (info_panel_rect.left + 20, current_y_pos))
                    current_y_pos += pets_header.get_height() + 5

                    for pet_info in possible_pets:
                        pet_id = pet_info['pet_id']
                        chance = pet_info['chance']
                        pet_def = pet_data.get(pet_id, {})
                        pet_name = pet_def.get('name', 'Unknown')
                        rarity = pet_def.get('rarity', 'Common')
                        rarity_color = RARITY_COLORS.get(rarity, WHITE)
                        pet_chance_text = font_info.render(f" - {pet_name} ({int(chance * 100)}%)", True, rarity_color)
                        screen.blit(pet_chance_text, (info_panel_rect.left + 25, current_y_pos))
                        current_y_pos += pet_chance_text.get_height() + 2
                
                if 'effects' in data.get('data', {}):
                    draw_item_effects(screen, data['data']['effects'], (info_panel_rect.left + 20, current_y_pos))

            if shop_message and time.time()-shop_message_timer<2.5:
                is_success="successful" in shop_message.lower(); message_font=font if is_success else font_small; message_color=(0,100,0) if is_success else (220,20,20)
                msg_surf=message_font.render(shop_message,True,message_color); msg_rect=msg_surf.get_rect(center=(container_rect.centerx,container_rect.bottom+50)); bg_rect=msg_rect.inflate(20,10)
                bg_surf=pygame.Surface(bg_rect.size,pygame.SRCALPHA); bg_surf.fill((0,0,0,160)); border_color=(0,50,0,180) if is_success else (50,0,0,180)
                pygame.draw.rect(bg_surf,border_color,bg_surf.get_rect(),3,4); screen.blit(bg_surf,bg_rect); screen.blit(msg_surf,msg_rect)
            else: shop_message=""
            exit_text=font_small.render("Press 'E' or 'Esc' to exit.",True,GRAY); screen.blit(exit_text,(SCREEN_WIDTH//2-exit_text.get_width()//2,SCREEN_HEIGHT-100))
        elif scene == "home_menu" or scene == "incubator_egg_select":
            if incubator_manager: incubator_manager.draw(screen,mouse_pos)
            exit_text=font_small.render("Press 'Esc' to return.",True,GRAY); screen.blit(exit_text,(SCREEN_WIDTH//2-exit_text.get_width()//2,SCREEN_HEIGHT-100))
            if scene == "incubator_egg_select":
                select_panel_rect=pygame.Rect(0,0,800,500); select_panel_rect.center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2)
                pygame.draw.rect(screen,PANEL_FILL_COLOR,select_panel_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,select_panel_rect,6,15)
                title_text=font.render("SELECT AN EGG",True,TEXT_COLOR); screen.blit(title_text,title_text.get_rect(centerx=select_panel_rect.centerx,top=select_panel_rect.top+20))
                player_eggs=player_inventory.get_eggs()
                if not player_eggs: no_eggs_text=font_small.render("You have no eggs!",True,TEXT_COLOR); screen.blit(no_eggs_text,no_eggs_text.get_rect(center=select_panel_rect.center))
                else:
                    EGG_COLS,EGG_BOX_SIZE,EGG_PADDING=4,120,20
                    for i,(egg_id,qty) in enumerate(player_eggs):
                        r,c=divmod(i,EGG_COLS); box_x=select_panel_rect.left+50+c*(EGG_BOX_SIZE+EGG_PADDING); box_y=select_panel_rect.top+100+r*(EGG_BOX_SIZE+EGG_PADDING)
                        egg_box_rect=pygame.Rect(box_x,box_y,EGG_BOX_SIZE,EGG_BOX_SIZE); pygame.draw.rect(screen,(230,200,130),egg_box_rect,0,8)
                        if egg_img:=item_images.get(egg_id): screen.blit(pygame.transform.scale(egg_img,(EGG_BOX_SIZE-20,EGG_BOX_SIZE-20)),egg_img.get_rect(center=egg_box_rect.center))
                        qty_text=font_info.render(f"x{qty}",True,TEXT_COLOR); screen.blit(qty_text,(egg_box_rect.right-qty_text.get_width()-5,egg_box_rect.bottom-qty_text.get_height()-5))
                        pygame.draw.rect(screen,BUTTON_HOVER_COLOR if egg_box_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,egg_box_rect,4,8)
        elif scene == "inventory_menu":
            overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            main_panel_rect=pygame.Rect(100,100,SCREEN_WIDTH*0.6,SCREEN_HEIGHT-200); pygame.draw.rect(screen,PANEL_FILL_COLOR,main_panel_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,main_panel_rect,6,15)
            info_panel_rect=pygame.Rect(main_panel_rect.right+20,100,SCREEN_WIDTH-main_panel_rect.right-120,SCREEN_HEIGHT-200); pygame.draw.rect(screen,PANEL_FILL_COLOR,info_panel_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,info_panel_rect,6,15)
            title_text=font.render("INVENTORY",True,TEXT_COLOR); screen.blit(title_text,title_text.get_rect(centerx=main_panel_rect.centerx,top=main_panel_rect.top+30))
            INV_COLS,INV_ROWS,INV_BOX_SIZE,INV_PADDING=10,5,80,10; INV_GRID_W=INV_COLS*(INV_BOX_SIZE+INV_PADDING)-INV_PADDING; INV_GRID_X=main_panel_rect.left+(main_panel_rect.width-INV_GRID_W)//2; INV_GRID_Y=main_panel_rect.top+80+50
            items_in_inv=player_inventory.get_all_items()
            for i in range(INV_COLS*INV_ROWS):
                r,c=divmod(i,INV_COLS); box_x=INV_GRID_X+c*(INV_BOX_SIZE+INV_PADDING); box_y=INV_GRID_Y+r*(INV_BOX_SIZE+INV_PADDING); box_rect=pygame.Rect(box_x,box_y,INV_BOX_SIZE,INV_BOX_SIZE); pygame.draw.rect(screen,LOCKED_SLOT_COLOR,box_rect,0,8)
                is_selected=False
                if i<len(items_in_inv):
                    item_id,qty=items_in_inv[i]; is_selected=(inventory_selected_item_id==item_id)
                    if item_img:=item_images.get(item_id): screen.blit(pygame.transform.scale(item_img,(INV_BOX_SIZE-10,INV_BOX_SIZE-10)),pygame.transform.scale(item_img,(INV_BOX_SIZE-10,INV_BOX_SIZE-10)).get_rect(center=box_rect.center))
                    if qty>1:
                        qty_text=font_info.render(str(qty),True,WHITE); qty_bg=pygame.Surface((qty_text.get_width()+4,qty_text.get_height()),pygame.SRCALPHA); qty_bg.fill((0,0,0,150))
                        screen.blit(qty_bg,(box_rect.right-qty_bg.get_width()-2,box_rect.bottom-qty_bg.get_height()-2)); screen.blit(qty_text,(box_rect.right-qty_text.get_width()-4,box_rect.bottom-qty_text.get_height()-4))
                pygame.draw.rect(screen,BUTTON_HOVER_COLOR if is_selected else PANEL_BORDER_COLOR,box_rect,3 if is_selected else 2,8)
            if inventory_selected_item_id and (data := item_data.get(inventory_selected_item_id)):
                name_text = font_small.render(data['name'], True, TEXT_COLOR)
                name_rect = name_text.get_rect(centerx=info_panel_rect.centerx, top=info_panel_rect.top + 30)
                screen.blit(name_text, name_rect)

                if img_to_draw := item_images.get(inventory_selected_item_id):
                    img_rect = img_to_draw.get_rect(centerx=info_panel_rect.centerx, top=name_rect.bottom + 20)
                    screen.blit(img_to_draw, img_rect)
                    current_y_pos = img_rect.bottom + 20
                else:
                    current_y_pos = name_rect.bottom + 20

                desc_rect = pygame.Rect(info_panel_rect.left + 20, current_y_pos, info_panel_rect.width - 40, 200)
                y_after_desc = draw_text_wrapped(screen, data['description'], font_info, TEXT_COLOR, desc_rect)
                current_y_pos = y_after_desc + 10

                if data.get("category") == "egg" and "possible_pets" in data.get("data", {}):
                    possible_pets = data["data"]["possible_pets"]
                    pets_header = font_info.render("Possible Pets:", True, TEXT_COLOR)
                    screen.blit(pets_header, (info_panel_rect.left + 20, current_y_pos))
                    current_y_pos += pets_header.get_height() + 5

                    for pet_info in possible_pets:
                        pet_id = pet_info['pet_id']
                        chance = pet_info['chance']
                        pet_def = pet_data.get(pet_id, {})
                        pet_name = pet_def.get('name', 'Unknown')
                        rarity = pet_def.get('rarity', 'Common')
                        rarity_color = RARITY_COLORS.get(rarity, WHITE)
                        pet_chance_text = font_info.render(f" - {pet_name} ({int(chance * 100)}%)", True, rarity_color)
                        screen.blit(pet_chance_text, (info_panel_rect.left + 25, current_y_pos))
                        current_y_pos += pet_chance_text.get_height() + 2

                if 'effects' in data.get('data', {}):
                    draw_item_effects(screen, data['data']['effects'], (info_panel_rect.left + 20, current_y_pos))
            exit_text=font_small.render("Press 'E' or 'Esc' to exit.",True,GRAY); screen.blit(exit_text,(SCREEN_WIDTH//2-exit_text.get_width()//2,SCREEN_HEIGHT-60))
        elif scene == "pet_management_menu":
            overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            list_panel_rect=pygame.Rect(100,100,400,SCREEN_HEIGHT-200); pygame.draw.rect(screen,PANEL_FILL_COLOR,list_panel_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,list_panel_rect,6,15)
            info_panel_rect=pygame.Rect(list_panel_rect.right+20,100,SCREEN_WIDTH-list_panel_rect.right-120,SCREEN_HEIGHT-200); pygame.draw.rect(screen,PANEL_FILL_COLOR,info_panel_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,info_panel_rect,6,15)
            unlocked_slots=profiles[selected_profile_idx]['unlocked_pet_slots']
            title_text=font.render("My Pets",True,TEXT_COLOR); screen.blit(title_text,title_text.get_rect(centerx=list_panel_rect.centerx,top=list_panel_rect.top+20))
            slot_count_text=font_small.render(f"Active: {len(active_pets)} / {unlocked_slots}",True,TEXT_COLOR); screen.blit(slot_count_text,slot_count_text.get_rect(centerx=list_panel_rect.centerx,top=list_panel_rect.top+65))
            pets_in_inv=player_inventory.get_all_pets(); ROW_H,PADDING_Y=80,10
            list_content_rect=list_panel_rect.inflate(-40,-220); list_content_rect.top=list_panel_rect.top+120
            total_content_height=len(pets_in_inv)*(ROW_H+PADDING_Y); max_scroll=max(0,total_content_height-list_content_rect.height)
            scrollbar_track_rect=pygame.Rect(list_panel_rect.right-25,list_content_rect.top,15,list_content_rect.height)
            if is_dragging_scrollbar and max_scroll>0:
                visible_ratio=list_content_rect.height/total_content_height; handle_height=max(20,scrollbar_track_rect.height*visible_ratio)
                scrollable_track_space=scrollbar_track_rect.height-handle_height; new_handle_y=mouse_pos[1]-scrollbar_drag_offset_y
                relative_y=new_handle_y-scrollbar_track_rect.y; scroll_percent=relative_y/scrollable_track_space if scrollable_track_space>0 else 0
                pet_list_scroll_y=scroll_percent*max_scroll
            pet_list_scroll_y=max(0,min(pet_list_scroll_y,max_scroll))
            list_surface_container=screen.subsurface(list_content_rect); list_surface_container.fill(PANEL_FILL_COLOR)
            for i,pet in enumerate(pets_in_inv):
                row_y_pos=i*(ROW_H+PADDING_Y)-pet_list_scroll_y
                if row_y_pos+ROW_H>0 and row_y_pos<list_content_rect.height:
                    pet_row_rect=pygame.Rect(0,row_y_pos,list_content_rect.width,ROW_H); is_selected=pet_management_selected_instance_id==pet['instance_id']
                    row_color=LOCKED_SLOT_COLOR if not is_selected else (240,210,140); pygame.draw.rect(list_surface_container,row_color,pet_row_rect,0,8)
                    if pet_icon:=pet_icons.get(pet['pet_id']): list_surface_container.blit(pet_icon,pet_icon.get_rect(centery=pet_row_rect.centery,left=pet_row_rect.left+10))
                    pet_name_text=font_small.render(pet['name'],True,TEXT_COLOR); list_surface_container.blit(pet_name_text,pet_name_text.get_rect(centery=pet_row_rect.centery,left=pet_row_rect.left+90))
                    ### NEW: Display pet level in the list view
                    pet_level = pet.get('level', 0)
                    level_text = font_info.render(f"Lvl: {pet_level}", True, TEXT_COLOR)
                    list_surface_container.blit(level_text, level_text.get_rect(centery=pet_row_rect.centery, right=pet_row_rect.right - 15))
                    pygame.draw.rect(list_surface_container,BUTTON_HOVER_COLOR if is_selected else PANEL_BORDER_COLOR,pet_row_rect,3 if is_selected else 2,8)
            if max_scroll>0:
                pygame.draw.rect(screen,LOCKED_SLOT_COLOR,scrollbar_track_rect,0,8)
                visible_ratio=list_content_rect.height/total_content_height; handle_height=max(20,scrollbar_track_rect.height*visible_ratio)
                scroll_ratio=pet_list_scroll_y/max_scroll if max_scroll>0 else 0
                handle_y=scrollbar_track_rect.top+scroll_ratio*(scrollbar_track_rect.height-handle_height)
                scrollbar_handle_rect.update(scrollbar_track_rect.left,handle_y,scrollbar_track_rect.width,handle_height)
                pygame.draw.rect(screen,GRAY,scrollbar_handle_rect,0,8)
            else: scrollbar_handle_rect.update(0,0,0,0)
            if unlocked_slots<MAX_PET_SLOTS:
                price_index=unlocked_slots-5 
                if 0<=price_index<len(PET_SLOT_UNLOCK_PRICES):
                    unlock_button_rect=pygame.Rect(list_panel_rect.left+20,list_panel_rect.bottom-70,list_panel_rect.width-40,50)
                    pygame.draw.rect(screen,BUTTON_HOVER_COLOR if unlock_button_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,unlock_button_rect,0,8)
                    price=PET_SLOT_UNLOCK_PRICES[price_index]; btn_text=font_info.render(f"Unlock Slot: {price}",True,WHITE)
                    btn_text_rect=btn_text.get_rect(center=unlock_button_rect.center); coin_icon_small=pygame.transform.scale(coin_img,(24,24))
                    total_width=btn_text.get_width()+coin_icon_small.get_width()+10; text_x=unlock_button_rect.centerx-total_width/2; icon_x=text_x+btn_text.get_width()+10
                    screen.blit(btn_text,(text_x,btn_text_rect.y)); screen.blit(coin_icon_small,(icon_x,unlock_button_rect.centery-12))
            selected_pet_instance=player_inventory.get_pet_by_instance_id(pet_management_selected_instance_id)
            if selected_pet_instance:
                pet_def=pet_data[selected_pet_instance['pet_id']]; pet_name=selected_pet_instance.get('name',pet_def['name'])
                display_name=f"{pet_name} ({pet_def['name']})"; name_text=font_small.render(display_name,True,TEXT_COLOR); name_rect=name_text.get_rect(centerx=info_panel_rect.centerx,top=info_panel_rect.top+30); screen.blit(name_text,name_rect)
                
                ### MODIFIED: Draw pet rarity
                rarity = pet_def.get('rarity', 'Unknown')
                rarity_color = RARITY_COLORS.get(rarity, WHITE)
                rarity_text = font_info.render(f"Rarity: {rarity}", True, rarity_color)
                rarity_rect = rarity_text.get_rect(centerx=info_panel_rect.centerx, top=name_rect.bottom + 5)
                screen.blit(rarity_text, rarity_rect)
                icon_y_start = rarity_rect.bottom + 20
                
                if icon:=pet_icons.get(selected_pet_instance['pet_id']):
                    big_icon=pygame.transform.scale(icon,(128,128)); icon_rect=big_icon.get_rect(centerx=info_panel_rect.centerx,top=icon_y_start)
                    screen.blit(big_icon,icon_rect); status_bar_y=icon_rect.bottom+30
                else: status_bar_y=icon_y_start
                ThuCung.draw_status_bars(screen,selected_pet_instance,(info_panel_rect.left+40,status_bar_y),width=info_panel_rect.width-80)
                if current_map=="pet_area":
                    already_out=any(p.instance_data['instance_id']==pet_management_selected_instance_id for p in active_pets); slots_full=len(active_pets)>=unlocked_slots
                    btn_rect=pygame.Rect(0,0,250,60); btn_rect.midbottom=(info_panel_rect.centerx,info_panel_rect.bottom-30)
                    if already_out: btn_text,btn_color="Bring Back",PANEL_BORDER_COLOR
                    elif slots_full: btn_text,btn_color="Slots Full",DISABLED_COLOR
                    else: btn_text,btn_color="Bring Out",PANEL_BORDER_COLOR
                    pygame.draw.rect(screen,BUTTON_HOVER_COLOR if btn_rect.collidepoint(mouse_pos) and not(not already_out and slots_full) else btn_color,btn_rect,0,8)
                    text_surf=font.render(btn_text,True,WHITE); screen.blit(text_surf,text_surf.get_rect(center=btn_rect.center))
            else:
                prompt_text=font_small.render("Select a pet from the list.",True,GRAY); screen.blit(prompt_text,prompt_text.get_rect(center=info_panel_rect.center))
            if pet_menu_message and time.time()-pet_menu_message_timer<2:
                msg_surf=font_small.render(pet_menu_message,True,WHITE); msg_rect=msg_surf.get_rect(midbottom=(list_panel_rect.centerx,list_panel_rect.bottom-80)); screen.blit(msg_surf,msg_rect)
            else: pet_menu_message=""
            exit_text=font_small.render("Press 'R' or 'Esc' to exit.",True,GRAY); screen.blit(exit_text,(SCREEN_WIDTH//2-exit_text.get_width()//2,SCREEN_HEIGHT-60))
        elif scene == "storage_menu":
            overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            PANEL_MARGIN,TOP_MARGIN,BOTTOM_MARGIN=150,120,100; PANEL_Y,PANEL_HEIGHT=TOP_MARGIN,SCREEN_HEIGHT-TOP_MARGIN-BOTTOM_MARGIN
            PLAYER_PANEL_W=(SCREEN_WIDTH/2)-PANEL_MARGIN; PLAYER_PANEL_RECT=pygame.Rect(50,PANEL_Y,PLAYER_PANEL_W,PANEL_HEIGHT)
            GLOBAL_PANEL_RECT=pygame.Rect(SCREEN_WIDTH-50-PLAYER_PANEL_W,PANEL_Y,PLAYER_PANEL_W,PANEL_HEIGHT)
            pygame.draw.rect(screen,PANEL_FILL_COLOR,PLAYER_PANEL_RECT,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,PLAYER_PANEL_RECT,6,15)
            pygame.draw.rect(screen,PANEL_FILL_COLOR,GLOBAL_PANEL_RECT,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,GLOBAL_PANEL_RECT,6,15)
            player_title=font.render("Your Profile",True,TEXT_COLOR); screen.blit(player_title,player_title.get_rect(centerx=PLAYER_PANEL_RECT.centerx,top=PLAYER_PANEL_RECT.top+20))
            global_title=font.render("Shared Storage",True,TEXT_COLOR); screen.blit(global_title,global_title.get_rect(centerx=GLOBAL_PANEL_RECT.centerx,top=GLOBAL_PANEL_RECT.top+20))
            items_tab_rect=pygame.Rect(SCREEN_WIDTH/2-220,50,200,50); pets_tab_rect=pygame.Rect(SCREEN_WIDTH/2+20,50,200,50)
            pygame.draw.rect(screen,PANEL_BORDER_COLOR if storage_scene_tab=='items' else LOCKED_SLOT_COLOR,items_tab_rect,0,8); pygame.draw.rect(screen,PANEL_BORDER_COLOR,items_tab_rect,4,8)
            pygame.draw.rect(screen,PANEL_BORDER_COLOR if storage_scene_tab=='pets' else LOCKED_SLOT_COLOR,pets_tab_rect,0,8); pygame.draw.rect(screen,PANEL_BORDER_COLOR,pets_tab_rect,4,8)
            items_text=font.render("Items",True,WHITE); screen.blit(items_text,items_text.get_rect(center=items_tab_rect.center))
            pets_text=font.render("Pets",True,WHITE); screen.blit(pets_text,pets_text.get_rect(center=pets_tab_rect.center))
            def draw_list(panel_rect,is_player_list,scroll_y_ref,selected_idx_ref):
                content_rect=panel_rect.inflate(-40,-120); content_rect.top=panel_rect.top+80
                list_surface=screen.subsurface(content_rect); list_surface.fill(PANEL_FILL_COLOR)
                data_list=[]; source=player_inventory.items if is_player_list else global_storage_data['items']
                if storage_scene_tab=='items': data_list=sorted(source.items())
                else: source=player_inventory.pets if is_player_list else global_storage_data['pets']; data_list=sorted(source,key=lambda p:p['instance_id'])
                total_h=0
                if storage_scene_tab=='items': total_h=(len(data_list)//4+1)*110 if data_list else 0
                else: total_h=len(data_list)*90
                max_scroll=max(0,total_h-content_rect.height); scroll_y_ref[0]=max(0,min(scroll_y_ref[0],max_scroll))
                newly_selected_idx=None
                if storage_scene_tab=='items':
                    COLS,BOX_SIZE,PADDING=4,100,10
                    for i,(item_id,qty) in enumerate(data_list):
                        r,c=divmod(i,COLS); box_rect=pygame.Rect(20+c*(BOX_SIZE+PADDING),20+r*(BOX_SIZE+PADDING)-scroll_y_ref[0],BOX_SIZE,BOX_SIZE)
                        is_selected=selected_idx_ref==i; pygame.draw.rect(list_surface,LOCKED_SLOT_COLOR,box_rect,0,8)
                        if img:=item_images.get(item_id): list_surface.blit(pygame.transform.scale(img,(80,80)),img.get_rect(center=box_rect.center))
                        qty_text=font_info.render(f"x{qty}",True,TEXT_COLOR); list_surface.blit(qty_text,qty_text.get_rect(bottomright=box_rect.bottomright))
                        pygame.draw.rect(list_surface,BUTTON_HOVER_COLOR if is_selected else PANEL_BORDER_COLOR,box_rect,4 if is_selected else 2,8)
                        abs_box_rect=box_rect.move(content_rect.topleft)
                        if pygame.mouse.get_pressed()[0] and abs_box_rect.collidepoint(mouse_pos) and not storage_transfer_popup_active: newly_selected_idx=i
                else:
                    ROW_H,PADDING_Y=80,10
                    for i,pet in enumerate(data_list):
                        row_rect=pygame.Rect(10,10+i*(ROW_H+PADDING_Y)-scroll_y_ref[0],content_rect.width-20,ROW_H)
                        is_selected=selected_idx_ref==i; is_active=is_player_list and any(p.instance_data['instance_id']==pet['instance_id'] for p in active_pets)
                        color=(200,190,120) if is_active else LOCKED_SLOT_COLOR; pygame.draw.rect(list_surface,color,row_rect,0,8)
                        if icon:=pet_icons.get(pet['pet_id']): 
                            list_surface.blit(icon,icon.get_rect(centery=row_rect.centery,left=row_rect.left+10))
                        name_text=font_small.render(pet['name'],True,TEXT_COLOR); 
                        list_surface.blit(name_text,name_text.get_rect(centery=row_rect.centery,left=row_rect.left+90))
                        pygame.draw.rect(list_surface,BUTTON_HOVER_COLOR if is_selected else PANEL_BORDER_COLOR,row_rect,4 if is_selected else 2,8)
                        abs_row_rect=row_rect.move(content_rect.topleft)
                        if pygame.mouse.get_pressed()[0] and abs_row_rect.collidepoint(mouse_pos) and not storage_transfer_popup_active: newly_selected_idx=i
                return newly_selected_idx
            player_scroll_ref=[storage_player_scroll_y]; global_scroll_ref=[storage_global_scroll_y]
            player_sel=draw_list(PLAYER_PANEL_RECT,True,player_scroll_ref,storage_selected_player_idx)
            global_sel=draw_list(GLOBAL_PANEL_RECT,False,global_scroll_ref,storage_selected_global_idx)
            storage_player_scroll_y,storage_global_scroll_y=player_scroll_ref[0],global_scroll_ref[0]
            if pygame.mouse.get_pressed()[0]:
                if player_sel is not None: storage_selected_player_idx=player_sel; storage_selected_global_idx=None
                if global_sel is not None: storage_selected_global_idx=global_sel; storage_selected_player_idx=None
            store_button_rect=pygame.Rect(SCREEN_WIDTH/2-40,SCREEN_HEIGHT/2-60,80,80); retrieve_button_rect=pygame.Rect(SCREEN_WIDTH/2-40,SCREEN_HEIGHT/2+40,80,80)
            can_store=storage_selected_player_idx is not None
            if can_store and storage_scene_tab=='pets':
                pet_to_move=player_inventory.get_all_pets()[storage_selected_player_idx]
                if any(p.instance_data['instance_id']==pet_to_move['instance_id'] for p in active_pets): can_store=False
            store_color=PANEL_BORDER_COLOR if can_store else DISABLED_COLOR; pygame.draw.rect(screen,store_color,store_button_rect,0,8); pygame.draw.polygon(screen,WHITE,[(store_button_rect.right-20,store_button_rect.centery),(store_button_rect.left+20,store_button_rect.top+20),(store_button_rect.left+20,store_button_rect.bottom-20)])
            can_retrieve=storage_selected_global_idx is not None; retrieve_color=PANEL_BORDER_COLOR if can_retrieve else DISABLED_COLOR
            pygame.draw.rect(screen,retrieve_color,retrieve_button_rect,0,8); pygame.draw.polygon(screen,WHITE,[(retrieve_button_rect.left+20,retrieve_button_rect.centery),(retrieve_button_rect.right-20,retrieve_button_rect.top+20),(retrieve_button_rect.right-20,retrieve_button_rect.bottom-20)])
            if storage_message and time.time()-storage_message_timer<2.5:
                msg_surf=font_small.render(storage_message,True,WHITE); msg_rect=msg_surf.get_rect(midbottom=(SCREEN_WIDTH/2,SCREEN_HEIGHT-30)); screen.blit(msg_surf,msg_rect)
            else: storage_message=""
            exit_text=font_small.render("Press 'E' or 'Esc' to exit.",True,GRAY); screen.blit(exit_text,exit_text.get_rect(midbottom=(SCREEN_WIDTH/2,SCREEN_HEIGHT-30)))
            if storage_transfer_popup_active:
                popup_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); popup_overlay.fill((0, 0, 0, 180)); screen.blit(popup_overlay, (0, 0))
                popup_width, popup_height = 500, 300
                popup_rect = pygame.Rect(0, 0, popup_width, popup_height); popup_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
                pygame.draw.rect(screen, PANEL_FILL_COLOR, popup_rect, 0, 15); pygame.draw.rect(screen, PANEL_BORDER_COLOR, popup_rect, 6, 15)
                info = storage_transfer_info; item_name = item_data[info['item_id']]['name']
                title_text = font_small.render(f"Move {item_name}", True, TEXT_COLOR); screen.blit(title_text, title_text.get_rect(centerx=popup_rect.centerx, top=popup_rect.top + 20))
                
                qty_text = font_small.render(f"Quantity: {info['quantity']}", True, TEXT_COLOR); screen.blit(qty_text, qty_text.get_rect(centerx=popup_rect.centerx, top=popup_rect.top + 80))
                
                slider_rect = pygame.Rect(popup_rect.left + 100, popup_rect.centery + 10, popup_rect.width - 200, 20)
                minus_rect = pygame.Rect(popup_rect.left + 40, popup_rect.centery, 40, 40); plus_rect = pygame.Rect(popup_rect.right - 80, popup_rect.centery, 40, 40)
                confirm_rect = pygame.Rect(popup_rect.centerx - 150, popup_rect.bottom - 80, 120, 50); cancel_rect = pygame.Rect(popup_rect.centerx + 30, popup_rect.bottom - 80, 120, 50)
                
                pygame.draw.rect(screen, GRAY, minus_rect, 0, 8); screen.blit(font.render("-", True, WHITE), font.render("-", True, WHITE).get_rect(center=minus_rect.center))
                pygame.draw.rect(screen, GRAY, plus_rect, 0, 8); screen.blit(font.render("+", True, WHITE), font.render("+", True, WHITE).get_rect(center=plus_rect.center))
                pygame.draw.rect(screen, GRAY, slider_rect, 0, 10)
                handle_x = slider_rect.left + (slider_rect.width - 20) * ((info['quantity'] - 1) / max(1, info['max_quantity'] - 1)) if info['max_quantity'] > 1 else slider_rect.left
                handle_rect = pygame.Rect(handle_x, slider_rect.y, 20, 20)
                pygame.draw.rect(screen, PANEL_BORDER_COLOR, handle_rect, 0, 10)
                
                pygame.draw.rect(screen, PANEL_BORDER_COLOR, confirm_rect, 0, 8); screen.blit(font_small.render("OK", True, WHITE), font_small.render("OK", True, WHITE).get_rect(center=confirm_rect.center))
                pygame.draw.rect(screen, PANEL_BORDER_COLOR, cancel_rect, 0, 8); screen.blit(font_small.render("Cancel", True, WHITE), font_small.render("Cancel", True, WHITE).get_rect(center=cancel_rect.center))
        elif scene == "quest_dialogue":
            if current_map=="world":
                for building in world_buildings: building.draw(screen)
                for pos in fence_objects: screen.blit(fence_img,pos)
                if player: player.draw(screen,(player.x,player.y),f"Idle{player.last_dir}")
            overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            if quest_giver_npc_large: quest_giver_npc_large.update(dt); quest_giver_npc_large.draw(screen,(SCREEN_WIDTH-250,SCREEN_HEIGHT/2))
            dialogue_panel=pygame.Rect(100,SCREEN_HEIGHT/2-150,SCREEN_WIDTH-550,300); pygame.draw.rect(screen,PANEL_FILL_COLOR,dialogue_panel,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,dialogue_panel,6,15)
            quote="Care for a challenge? The rewards are great!"; draw_text_wrapped(screen,quote,font_small,TEXT_COLOR,pygame.Rect(dialogue_panel.x+40,dialogue_panel.y+50,dialogue_panel.width-80,100),centered=True)
            quest_dialogue_yes_rect=pygame.Rect(dialogue_panel.centerx-220,dialogue_panel.bottom-100,200,60); quest_dialogue_no_rect=pygame.Rect(dialogue_panel.centerx+20,dialogue_panel.bottom-100,200,60)
            pygame.draw.rect(screen,BUTTON_HOVER_COLOR if quest_dialogue_yes_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,quest_dialogue_yes_rect,0,8); pygame.draw.rect(screen,BUTTON_HOVER_COLOR if quest_dialogue_no_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,quest_dialogue_no_rect,0,8)
            yes_text=font.render("Yes",True,WHITE); screen.blit(yes_text,yes_text.get_rect(center=quest_dialogue_yes_rect.center)); no_text=font.render("No",True,WHITE); screen.blit(no_text,no_text.get_rect(center=quest_dialogue_no_rect.center))
        ### MODIFIED: New and updated drawing logic for the challenge dialogues
        elif scene == "challenge_main_dialogue":
            if current_map=="world":
                for building in world_buildings: building.draw(screen);
                for pos in fence_objects: screen.blit(fence_img,pos)
                if player: player.draw(screen,(player.x,player.y),f"Idle{player.last_dir}")
            overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            if challenge_npc_large: challenge_npc_large.update(dt); challenge_npc_large.draw(screen,(SCREEN_WIDTH-250,SCREEN_HEIGHT/2))
            dialogue_panel=pygame.Rect(100,SCREEN_HEIGHT/2-150,SCREEN_WIDTH-550,300); pygame.draw.rect(screen,PANEL_FILL_COLOR,dialogue_panel,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,dialogue_panel,6,15)
            quote="What can I help you with?"; draw_text_wrapped(screen,quote,font_small,TEXT_COLOR,pygame.Rect(dialogue_panel.x+40,dialogue_panel.y+50,dialogue_panel.width-80,100),centered=True)
            challenge_main_fight_rect = pygame.Rect(dialogue_panel.centerx - 220, dialogue_panel.bottom - 100, 200, 60)
            challenge_main_sell_rect = pygame.Rect(dialogue_panel.centerx + 20, dialogue_panel.bottom - 100, 200, 60)
            pygame.draw.rect(screen,BUTTON_HOVER_COLOR if challenge_main_fight_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,challenge_main_fight_rect,0,8)
            pygame.draw.rect(screen,BUTTON_HOVER_COLOR if challenge_main_sell_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,challenge_main_sell_rect,0,8)
            fight_text=font.render("FIGHT",True,WHITE); screen.blit(fight_text,fight_text.get_rect(center=challenge_main_fight_rect.center))
            sell_text=font.render("SELL",True,WHITE); screen.blit(sell_text,sell_text.get_rect(center=challenge_main_sell_rect.center))
        elif scene == "challenge_pre_sell_dialogue":
            if current_map=="world":
                for building in world_buildings: building.draw(screen);
                for pos in fence_objects: screen.blit(fence_img,pos)
                if player: player.draw(screen,(player.x,player.y),f"Idle{player.last_dir}")
            overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            if challenge_npc_large: challenge_npc_large.update(dt); challenge_npc_large.draw(screen,(SCREEN_WIDTH-250,SCREEN_HEIGHT/2))
            dialogue_panel=pygame.Rect(100,SCREEN_HEIGHT/2-150,SCREEN_WIDTH-550,300); pygame.draw.rect(screen,PANEL_FILL_COLOR,dialogue_panel,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,dialogue_panel,6,15)
            quote="Do you have any chicken?"; draw_text_wrapped(screen,quote,font_small,TEXT_COLOR,pygame.Rect(dialogue_panel.x+40,dialogue_panel.y+50,dialogue_panel.width-80,100),centered=True)
            challenge_pre_sell_yes_rect=pygame.Rect(dialogue_panel.centerx-220,dialogue_panel.bottom-100,200,60); challenge_pre_sell_no_rect=pygame.Rect(dialogue_panel.centerx+20,dialogue_panel.bottom-100,200,60)
            pygame.draw.rect(screen,BUTTON_HOVER_COLOR if challenge_pre_sell_yes_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,challenge_pre_sell_yes_rect,0,8); pygame.draw.rect(screen,BUTTON_HOVER_COLOR if challenge_pre_sell_no_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,challenge_pre_sell_no_rect,0,8)
            yes_text=font.render("Yes",True,WHITE); screen.blit(yes_text,yes_text.get_rect(center=challenge_pre_sell_yes_rect.center)); no_text=font.render("No",True,WHITE); screen.blit(no_text,no_text.get_rect(center=challenge_pre_sell_no_rect.center))
        elif scene == "challenge_dialogue":
            if current_map=="world":
                for building in world_buildings: building.draw(screen);
                for pos in fence_objects: screen.blit(fence_img,pos)
                if player: player.draw(screen,(player.x,player.y),f"Idle{player.last_dir}")
            overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            if challenge_npc_large: challenge_npc_large.update(dt); challenge_npc_large.draw(screen,(SCREEN_WIDTH-250,SCREEN_HEIGHT/2))
            dialogue_panel=pygame.Rect(100,SCREEN_HEIGHT/2-150,SCREEN_WIDTH-550,300); pygame.draw.rect(screen,PANEL_FILL_COLOR,dialogue_panel,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,dialogue_panel,6,15)
            quote="These chickens are tough... can you help me?"; draw_text_wrapped(screen,quote,font_small,TEXT_COLOR,pygame.Rect(dialogue_panel.x+40,dialogue_panel.y+50,dialogue_panel.width-80,100),centered=True)
            challenge_fight_yes_rect=pygame.Rect(dialogue_panel.centerx-220,dialogue_panel.bottom-100,200,60); challenge_fight_no_rect=pygame.Rect(dialogue_panel.centerx+20,dialogue_panel.bottom-100,200,60)
            pygame.draw.rect(screen,BUTTON_HOVER_COLOR if challenge_fight_yes_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,challenge_fight_yes_rect,0,8); pygame.draw.rect(screen,BUTTON_HOVER_COLOR if challenge_fight_no_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,challenge_fight_no_rect,0,8)
            yes_text=font.render("Yes",True,WHITE); screen.blit(yes_text,yes_text.get_rect(center=challenge_fight_yes_rect.center)); no_text=font.render("No",True,WHITE); screen.blit(no_text,no_text.get_rect(center=challenge_fight_no_rect.center))
        elif scene == "challenge_sell_dialogue":
            if current_map=="world":
                for building in world_buildings: building.draw(screen);
                for pos in fence_objects: screen.blit(fence_img,pos)
                if player: player.draw(screen,(player.x,player.y),f"Idle{player.last_dir}")
            overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            if challenge_npc_large: challenge_npc_large.update(dt); challenge_npc_large.draw(screen,(SCREEN_WIDTH-250,SCREEN_HEIGHT/2))
            
            dialog_rect=pygame.Rect(0,0,700,350); dialog_rect.center=(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2)
            pygame.draw.rect(screen,PANEL_FILL_COLOR,dialog_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,dialog_rect,6,15)
            
            quote="I'll buy that chicken meat! How many pieces?"; draw_text_wrapped(screen,quote,font_small,TEXT_COLOR,pygame.Rect(dialog_rect.x+40,dialog_rect.y+20,dialog_rect.width-80,100),centered=True)
            
            qty_text = font_small.render(f"Sell: {sell_quantity}", True, TEXT_COLOR); screen.blit(qty_text, qty_text.get_rect(centerx=dialog_rect.centerx, top=dialog_rect.y + 110))

            slider_rect = pygame.Rect(dialog_rect.centerx - 150, dialog_rect.centery, 300, 20)
            minus_rect = pygame.Rect(slider_rect.left - 60, slider_rect.centery - 10, 40, 40); plus_rect = pygame.Rect(slider_rect.right + 20, slider_rect.centery - 10, 40, 40)
            pygame.draw.rect(screen, GRAY, minus_rect, 0, 8); screen.blit(font.render("-", True, WHITE), font.render("-", True, WHITE).get_rect(center=minus_rect.center))
            pygame.draw.rect(screen, GRAY, plus_rect, 0, 8); screen.blit(font.render("+", True, WHITE), font.render("+", True, WHITE).get_rect(center=plus_rect.center))
            pygame.draw.rect(screen, GRAY, slider_rect, 0, 10)
            handle_x = slider_rect.left + (slider_rect.width - 20) * ((sell_quantity - 1) / max(1, max_sell_quantity - 1)) if max_sell_quantity > 1 else slider_rect.left
            handle_rect = pygame.Rect(handle_x, slider_rect.y, 20, 20)
            pygame.draw.rect(screen, PANEL_BORDER_COLOR, handle_rect, 0, 10)

            revenue = sell_quantity * 20
            revenue_text = font_small.render(f"For: {revenue}", True, TEXT_COLOR)
            rev_rect = revenue_text.get_rect(centerx=dialog_rect.centerx - 20, top=slider_rect.bottom + 20); screen.blit(revenue_text, rev_rect)
            screen.blit(pygame.transform.scale(coin_img, (32, 32)), (rev_rect.right + 10, rev_rect.y))

            sell_rect = pygame.Rect(dialog_rect.centerx - 150, dialog_rect.bottom - 80, 120, 50); cancel_rect = pygame.Rect(dialog_rect.centerx + 30, dialog_rect.bottom - 80, 120, 50)
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR if sell_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR, sell_rect, 0, 8); screen.blit(font_small.render("Sell", True, WHITE), font_small.render("Sell", True, WHITE).get_rect(center=sell_rect.center))
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR if cancel_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR, cancel_rect, 0, 8); screen.blit(font_small.render("Cancel", True, WHITE), font_small.render("Cancel", True, WHITE).get_rect(center=cancel_rect.center))
        elif scene == "quest_menu":
            overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            quest_panel_rect=pygame.Rect(0,0,900,650); quest_panel_rect.center=(SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
            pygame.draw.rect(screen,PANEL_FILL_COLOR,quest_panel_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,quest_panel_rect,6,15)
            title_text=font.render("DAILY QUESTS",True,TEXT_COLOR); screen.blit(title_text,title_text.get_rect(centerx=quest_panel_rect.centerx,top=quest_panel_rect.top+20))
            time_left=quest_manager.get_time_until_next_reset(); timer_text=TienTe.format_time(time_left); reset_text=font_info.render(f"Resets in: {timer_text}",True,GRAY); screen.blit(reset_text,reset_text.get_rect(centerx=quest_panel_rect.centerx,top=quest_panel_rect.top+60))
            if quest_manager and quest_manager.quest_data['quests_accepted_today']:
                start_y=quest_panel_rect.top+110
                for i,quest_id in enumerate(quest_manager.quest_data['daily_quests']):
                    mission=missions_data.get(quest_id)
                    if not mission: continue
                    quest_box_rect=pygame.Rect(quest_panel_rect.left+50,start_y+i*160,quest_panel_rect.width-100,140); pygame.draw.rect(screen,LOCKED_SLOT_COLOR,quest_box_rect,0,10)
                    q_title=font_small.render(mission['title'],True,TEXT_COLOR); screen.blit(q_title,(quest_box_rect.left+20,quest_box_rect.top+10))
                    desc_rect=pygame.Rect(quest_box_rect.left+20,quest_box_rect.top+50,450,50); draw_text_wrapped(screen,mission['description'],font_info,GRAY,desc_rect,line_spacing=2)
                    progress=quest_manager.quest_data['progress'].get(quest_id,0); target=mission['target']; progress_pct=min(progress/target,1.0)
                    prog_bar_w,prog_bar_h=300,25; prog_bar_rect=pygame.Rect(quest_box_rect.left+20,quest_box_rect.bottom-prog_bar_h-10,prog_bar_w,prog_bar_h)
                    pygame.draw.rect(screen,GRAY,prog_bar_rect,0,5); pygame.draw.rect(screen,QUEST_PROGRESS_COLOR,(prog_bar_rect.x,prog_bar_rect.y,prog_bar_w*progress_pct,prog_bar_h),0,5)
                    progress_text=font_info.render(f"{min(progress,target)} / {target}",True,WHITE); screen.blit(progress_text,progress_text.get_rect(center=prog_bar_rect.center))
                    reward_x=prog_bar_rect.right+30
                    if 'money' in mission['reward']:
                        reward_money_text=font_small.render(str(mission['reward']['money']),True,TEXT_COLOR); screen.blit(reward_money_text,(reward_x,prog_bar_rect.centery-reward_money_text.get_height()//2)); screen.blit(pygame.transform.scale(coin_img,(32,32)),(reward_x+reward_money_text.get_width()+10,prog_bar_rect.centery-16)); reward_x+=reward_money_text.get_width()+60
                    if 'items' in mission['reward']:
                        for item_id,qty in mission['reward']['items'].items():
                           if item_img:=item_images.get(item_id):
                               screen.blit(pygame.transform.scale(item_img,(48,48)),(reward_x,prog_bar_rect.centery-24)); qty_text=font_info.render(f"x{qty}",True,TEXT_COLOR); screen.blit(qty_text,(reward_x+50,prog_bar_rect.centery-12)); reward_x+=100
                    is_complete=progress>=target; is_claimed=quest_id in quest_manager.quest_data['claimed']; btn_rect=pygame.Rect(quest_box_rect.right-200,quest_box_rect.centery-30,150,60)
                    btn_color=DISABLED_COLOR; btn_text_str="Claim"
                    if is_claimed: btn_text_str="Claimed"
                    elif is_complete: btn_text_str="Claim"; btn_color=PANEL_BORDER_COLOR
                    if btn_rect.collidepoint(mouse_pos) and is_complete and not is_claimed: btn_color=BUTTON_HOVER_COLOR
                    pygame.draw.rect(screen,btn_color,btn_rect,0,8); btn_text=font.render(btn_text_str,True,WHITE); screen.blit(btn_text,btn_text.get_rect(center=btn_rect.center))
                    pygame.draw.rect(screen,PANEL_BORDER_COLOR,quest_box_rect,4,10)
            else:
                prompt_text="Visit the quest giver to get today's quests!"; text_area_rect=quest_panel_rect.inflate(-80,-200); text_area_rect.center=quest_panel_rect.center; draw_text_wrapped(screen,prompt_text,font_small,TEXT_COLOR,text_area_rect,centered=True)
            if quest_menu_message and time.time()-quest_menu_message_timer<2:
                msg_surf=font_small.render(quest_menu_message,True,WHITE); msg_rect=msg_surf.get_rect(midbottom=(quest_panel_rect.centerx,quest_panel_rect.bottom-20)); screen.blit(msg_surf,msg_rect)
            else: quest_menu_message=""
            exit_text=font_small.render("Press 'Q' or 'Esc' to exit.",True,GRAY); screen.blit(exit_text,(SCREEN_WIDTH//2-exit_text.get_width()//2,SCREEN_HEIGHT-60))
        elif scene == "challenge_pet_select":
            overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            list_panel_rect=pygame.Rect(0,0,500,SCREEN_HEIGHT-200); list_panel_rect.center=(SCREEN_WIDTH/2,SCREEN_HEIGHT/2); pygame.draw.rect(screen,PANEL_FILL_COLOR,list_panel_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,list_panel_rect,6,15)
            title_text=font.render("Choose Your Fighter",True,TEXT_COLOR); screen.blit(title_text,title_text.get_rect(centerx=list_panel_rect.centerx,top=list_panel_rect.top+20))
            eligible_pets=[p for p in player_inventory.get_all_pets() if pet_data.get(p['pet_id'],{}).get('can_attack')]
            if not eligible_pets:
                none_text=font_small.render("No attacking pets available!",True,GRAY); screen.blit(none_text,none_text.get_rect(center=list_panel_rect.center))
            else:
                ROW_H,PADDING_Y=80,10; list_content_rect=list_panel_rect.inflate(-40,-120); list_content_rect.top=list_panel_rect.top+80
                total_content_height=len(eligible_pets)*(ROW_H+PADDING_Y); max_scroll=max(0,total_content_height-list_content_rect.height)
                challenge_pet_selection_scroll_y=max(0,min(challenge_pet_selection_scroll_y,max_scroll))
                list_surface_container=screen.subsurface(list_content_rect); list_surface_container.fill(PANEL_FILL_COLOR)
                for i,pet in enumerate(eligible_pets):
                    row_y_pos=i*(ROW_H+PADDING_Y)-challenge_pet_selection_scroll_y
                    if row_y_pos+ROW_H>0 and row_y_pos<list_content_rect.height:
                        pet_row_rect=pygame.Rect(0,row_y_pos,list_content_rect.width,ROW_H)
                        is_hovered=pet_row_rect.collidepoint(mouse_pos[0]-list_content_rect.left,mouse_pos[1]-list_content_rect.top)
                        row_color=(240,210,140) if is_hovered else LOCKED_SLOT_COLOR; pygame.draw.rect(list_surface_container,row_color,pet_row_rect,0,8)
                        if pet_icon:=pet_icons.get(pet['pet_id']): list_surface_container.blit(pet_icon,pet_icon.get_rect(centery=pet_row_rect.centery,left=pet_row_rect.left+10))
                        pet_name_text=font_small.render(pet['name'],True,TEXT_COLOR); list_surface_container.blit(pet_name_text,pet_name_text.get_rect(centery=pet_row_rect.centery,left=pet_row_rect.left+90))
                        pet_damage=pet_data[pet['pet_id']].get('damage',0); damage_text=font_info.render(f"DMG: {pet_damage}",True,TEXT_COLOR); list_surface_container.blit(damage_text,damage_text.get_rect(centery=pet_row_rect.centery,right=pet_row_rect.right-20))
                        pygame.draw.rect(list_surface_container,BUTTON_HOVER_COLOR if is_hovered else PANEL_BORDER_COLOR,pet_row_rect,3,8)
            exit_text=font_small.render("Press 'Esc' to cancel.",True,GRAY); screen.blit(exit_text,exit_text.get_rect(midbottom=(list_panel_rect.centerx,list_panel_rect.bottom-10)))

    if confirming_escape:
        overlay_dark=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay_dark.fill((0,0,0,120)); screen.blit(overlay_dark,(0,0))
        pygame.draw.rect(screen,PANEL_FILL_COLOR,dialog_rect,0,10); pygame.draw.rect(screen,PANEL_BORDER_COLOR,dialog_rect,6,10)
        q_text=font_small.render("Do you want to escape?",True,TEXT_COLOR); screen.blit(q_text,q_text.get_rect(center=(dialog_rect.centerx,dialog_rect.top+60)))
        for r,t in [(yes_button_rect,"Yes"),(no_button_rect,"No")]:
            pygame.draw.rect(screen,BUTTON_HOVER_COLOR if r.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,r,0,8)
            screen.blit(font.render(t,True,WHITE),font.render(t,True,WHITE).get_rect(center=r.center))

    if game_currency and scene != "hatching_animation": game_currency.draw(screen, show_time=(scene=="play"))
    
    if scene not in ["loading","profile_save","char_select","name_input"]:
        if is_music_playing: screen.blit(music_on_img,music_button_rect)
        else: screen.blit(music_off_img,music_button_rect)

    pygame.display.update()