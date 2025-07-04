import pygame, json, sys, time, os, random
from datetime import datetime, timedelta

# -------------------- Case-Insensitive File Loading --------------------
def load_file_case_insensitive(file_path):
    """
    Attempts to load a file in a case-insensitive manner.
    Returns the correct path if found, None if not found.
    """
    if os.path.exists(file_path):
        return file_path
    
    # Get directory and filename
    directory = os.path.dirname(file_path)
    target_filename = os.path.basename(file_path)
    
    # If directory is empty, use current directory
    if not directory:
        directory = "."
    
    # Check if directory exists
    if not os.path.exists(directory):
        return None
    
    # List all files in directory and compare case-insensitively
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
MISSION_POINTS_COLOR = (60, 180, 255)

# --- Animation Timings ---
HATCH_ANIM_DURATION = 1500
PET_ANIM_SPEED = 120
EFFECT_DURATION = 1.5 # How long heart/smile icons last, in seconds
SCROLL_SPEED = 30 # For pet management list

# --- Game Progression ---
MAX_PET_SLOTS = 15
# Prices to unlock slots 6, 7, 8, ..., 15 (10 prices total)
PET_SLOT_UNLOCK_PRICES = [50, 150, 400, 1000, 2500, 5000, 10000, 20000, 50000, 100000]

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
    title_img = pygame.image.load("GUI/title_screen2.png"); title_img = pygame.transform.scale(title_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error: print("Warning: title_screen2.png not found."); title_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
try:
    bg_img = pygame.image.load("GUI/background.jpg").convert(); bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error: print("Warning: background.jpg not found."); bg_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); bg_img.fill((30,10,40))
try:
    trash_can_img_original = pygame.image.load("GUI/trashcan.png").convert_alpha(); trash_can_img = pygame.transform.scale(trash_can_img_original, (48, 48))
except pygame.error: print("Warning: GUI/trashcan.png not found."); trash_can_img = None
try:
    coin_img_original = pygame.image.load("ENTITY/currency.jpg").convert_alpha(); coin_img = pygame.transform.scale(coin_img_original, (48, 48))
except pygame.error: print("Warning: ENTITY/currency.jpg not found."); coin_img = pygame.Surface((48,48)); coin_img.fill((255,215,0))
try:
    clock_img_original = pygame.image.load("ENTITY/clock.png").convert_alpha(); clock_img = pygame.transform.scale(clock_img_original, (48, 48))
except pygame.error: print("Warning: ENTITY/clock.png not found."); clock_img = pygame.Surface((48,48)); clock_img.fill(WHITE)
# --- Load Music ---
try:
    theme_song_path = load_file_case_insensitive("MUSIC/theme.mp3")
    if not theme_song_path:
        print("Warning: Music file 'MUSIC/theme.mp3' not found.")
except Exception as e:
    print(f"Warning: Could not prepare music. Error: {e}")
    theme_song_path = None
try:
    with open("CHARACTER/flash.json") as f: frame_data = json.load(f)["frames"]
except FileNotFoundError: print("FATAL ERROR: CHARACTER/flash.json not found."); pygame.quit(); sys.exit()
try:
    map_image_original = pygame.image.load("GUI/map.jpg").convert(); play_map_img = pygame.transform.scale(map_image_original, (SCREEN_WIDTH, SCREEN_HEIGHT))
except pygame.error: print("Warning: GUI/map.jpg not found."); play_map_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); play_map_img.fill(GRAY)
map_rect = play_map_img.get_rect()
try:
    fence_img = pygame.image.load("ENTITY/fence.png").convert_alpha(); fence_img = pygame.transform.scale(fence_img, (64, 64))
except pygame.error: print("Warning: ENTITY/fence.png not found."); fence_img = pygame.Surface((64,64)); fence_img.fill(PANEL_BORDER_COLOR)
try:
    hatch_img = pygame.image.load("GUI/hatch.png").convert_alpha()
except pygame.error: print("Warning: GUI/hatch.png not found."); hatch_img = pygame.Surface((128, 64), pygame.SRCALPHA); hatch_img.fill((180, 140, 80))
try:
    lock_img_original = pygame.image.load("GUI/lock.png").convert_alpha(); lock_img = pygame.transform.scale(lock_img_original, (64, 64))
except pygame.error: print("Warning: GUI/lock.png not found."); lock_img = pygame.Surface((64, 64), pygame.SRCALPHA); pygame.draw.rect(lock_img, GRAY, (16, 32, 32, 32), border_radius=5); pygame.draw.arc(lock_img, GRAY, (8, 8, 48, 48), 0, 3.14, 8)
try:
    sold_out_img_original = pygame.image.load("GUI/sold.png").convert_alpha()
    sold_out_img = pygame.transform.scale(sold_out_img_original, (128, 128))
except pygame.error: print("Warning: GUI/sold.png not found."); sold_out_img = pygame.Surface((128, 128), pygame.SRCALPHA); sold_out_text = font_small.render("SOLD", True, (200, 0, 0)); sold_out_img.blit(sold_out_text, (30, 50))
try:
    backpack_img_original = pygame.image.load("GUI/backpack.png").convert_alpha()
    backpack_img = pygame.transform.scale(backpack_img_original, (64, 64))
    backpack_rect = backpack_img.get_rect(midleft=(20, SCREEN_HEIGHT // 2))
except pygame.error: print("Warning: GUI/backpack.png not found."); backpack_img = pygame.Surface((64, 64)); backpack_img.fill(PANEL_BORDER_COLOR); backpack_rect = backpack_img.get_rect(midleft=(20, SCREEN_HEIGHT // 2))
try:
    pet_menu_icon_original = pygame.image.load("GUI/paw_icon.png").convert_alpha()
    pet_menu_icon = pygame.transform.scale(pet_menu_icon_original, (64, 64))
    pet_menu_rect = pet_menu_icon.get_rect(midleft=(20, backpack_rect.bottom + 40))
except pygame.error:
    print("Warning: GUI/paw_icon.png not found."); pet_menu_icon = pygame.Surface((64, 64), pygame.SRCALPHA);
    pygame.draw.circle(pet_menu_icon, PANEL_BORDER_COLOR, (32, 32), 30); pygame.draw.circle(pet_menu_icon, TEXT_COLOR, (32, 32), 26)
    pet_menu_rect = pet_menu_icon.get_rect(midleft=(20, backpack_rect.bottom + 40))

### MODIFIED BLOCK START ###
# This block replaces the original mission icon loading.
# It now creates the icon from a character sprite.
try:
    # Temporarily create a character object to extract its sprite.
    # We use a known character sheet path and the already loaded frame_data.
    # A Ninja character is chosen for the "mission" theme.
    mission_char_sheet_path = "CHARACTER/Ninja_P1.png"
    # The NguoiChamSoc class can load the animations from the sheet.
    mission_char_source = NguoiChamSoc("MissionIconChar", mission_char_sheet_path, frame_data, scale=1.0)
    
    # Get the first frame of the 'IdleSouth' (forward-facing) animation.
    mission_icon_original = mission_char_source.get_current_image("IdleSouth")
    
    # Scale the extracted sprite to the desired icon size.
    mission_icon = pygame.transform.scale(mission_icon_original, (64, 64))
    
    # Create its rectangle for positioning and clicks.
    mission_icon_rect = mission_icon.get_rect(midleft=(20, pet_menu_rect.bottom + 40))

except Exception as e:
    # This is a fallback in case the character files are missing.
    print(f"Warning: Could not create mission icon from character sprite. Error: {e}")
    mission_icon = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.rect(mission_icon, PANEL_BORDER_COLOR, (10, 5, 44, 54), 0, 5)
    pygame.draw.rect(mission_icon, TEXT_COLOR, (10, 5, 44, 54), 3, 5)
    mission_icon_rect = mission_icon.get_rect(midleft=(20, pet_menu_rect.bottom + 40))
### MODIFIED BLOCK END ###

try:
    heart_img = pygame.image.load("GUI/heart.png").convert_alpha(); heart_img = pygame.transform.scale(heart_img, (32, 32))
except pygame.error: print("Warning: GUI/heart.png not found."); heart_img = pygame.Surface((32,32), pygame.SRCALPHA); pygame.draw.circle(heart_img, (255, 105, 180), (16,16), 14, 0)
try:
    smile_img = pygame.image.load("GUI/smile.png").convert_alpha(); smile_img = pygame.transform.scale(smile_img, (32, 32))
except pygame.error: print("Warning: GUI/smile.png not found."); smile_img = pygame.Surface((32,32), pygame.SRCALPHA); pygame.draw.circle(smile_img, HAPPINESS_COLOR, (16,16), 14, 0)

try:
    with open("JSON/items_p.json") as f: item_data = json.load(f)
except FileNotFoundError: print("FATAL ERROR: items_p.json not found."); pygame.quit(); sys.exit()
try:
    with open("JSON/pets_p.json") as f: pet_data = json.load(f)
except FileNotFoundError: print("FATAL ERROR: pets.json not found."); pygame.quit(); sys.exit()

try:
    with open("JSON/missions.json") as f: mission_definitions = json.load(f)
except FileNotFoundError: print("FATAL ERROR: missions.json not found."); pygame.quit(); sys.exit()

item_images = {}
for item_id, data in item_data.items():
    try:
        img = pygame.image.load(data["image_path"]).convert_alpha()
        item_images[item_id] = pygame.transform.scale(img, (96, 96))
    except pygame.error: print(f"Warning: Item image not found at {data['image_path']}"); img_placeholder = pygame.Surface((96, 96), pygame.SRCALPHA); img_placeholder.fill((255, 0, 255)); item_images[item_id] = img_placeholder


# -------------------- Helper Functions --------------------
def load_pet_animation_frames(pet_id, anim_key="idle", scale=1.0):
    if pet_id not in pet_data:
        print(f"Error: Pet ID '{pet_id}' not found in pets.json")
        return []
    
    p_data = pet_data[pet_id]
    frames = []
    
    # Simplified: All pets now use the "frames" type.
    path_prefix = p_data['animation_paths'].get(anim_key)
    if not path_prefix: return []
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

    if not frames:
        print(f"Warning: No animation frames loaded for pet '{pet_id}' with key '{anim_key}'")

    return frames

pet_icons = {}
for pet_id in pet_data:
    idle_frames = load_pet_animation_frames(pet_id, "idle", scale=1.0)
    if idle_frames:
        pet_icons[pet_id] = pygame.transform.scale(idle_frames[0], (64, 64))
    else:
        print(f"Warning: Could not create icon for '{pet_id}'")
        img_placeholder = pygame.Surface((64, 64), pygame.SRCALPHA); img_placeholder.fill((0, 255, 0)); pet_icons[pet_id] = img_placeholder


profile_file = "profiles.json"
correct_profile_path = load_file_case_insensitive(profile_file)
if correct_profile_path:
    with open(correct_profile_path) as f: profiles = json.load(f)
else: profiles = [None, None, None]

# --- Global Storage ---
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
                else: # Handle malformed or empty file
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
        try: self.sheet = pygame.image.load(sheet_path).convert_alpha()
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
            self.image = pygame.image.load(image_path).convert_alpha()
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
    
    def add_pet(self, pet_id, name=None): # Add optional name parameter
        new_pet_instance_id = max([p['instance_id'] for p in self.pets] + [0]) + 1
        base_stats = pet_data.get(pet_id, {}).get("base_stats", {"health": 100, "happiness": 100, "hunger": 100})
        
        # Use the provided name, or choose a random one as a fallback
        # .strip() removes accidental spaces before/after the name
        pet_name = name.strip() if name and name.strip() else random.choice(PET_NAMES)
        
        new_pet = {
            "instance_id": new_pet_instance_id,
            "pet_id": pet_id,
            "name": pet_name, # Use the determined name
            "health": base_stats["health"],
            "happiness": base_stats["happiness"],
            "hunger": base_stats["hunger"]
        }
        self.pets.append(new_pet)
        print(f"Added new pet: {pet_name} the {pet_id} (Instance: {new_pet_instance_id})")
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
    DRIFT_SPEED = 20 # Pixels per second for floating icons

    def __init__(self, pet_instance_data):
        self.instance_data = pet_instance_data
        self.pet_id = self.instance_data['pet_id']
        self.definition = pet_data[self.pet_id]
        
        self.x, self.y = random.randint(100, SCREEN_WIDTH - 100), random.randint(100, SCREEN_HEIGHT - 200)
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
        self.effects = [] # For storing heart/smile popups

    def load_animations(self):
        anim_type = self.definition['animation_type']
        if anim_type == "frames":
            self.animations['idle'] = load_pet_animation_frames(self.pet_id, 'idle', self.scale)
            self.animations['walk'] = load_pet_animation_frames(self.pet_id, 'walk', self.scale)
        elif anim_type == "spritesheet":
            if self.definition.get("directional"):
                for tag in ["IdleSouth", "IdleNorth", "IdleEast", "IdleWest", "WalkSouth", "WalkNorth", "WalkEast", "WalkWest"]:
                    self.animations[tag] = load_pet_animation_frames(self.pet_id, tag, self.scale)
            else: # Non-directional spritesheet
                self.animations['idle'] = load_pet_animation_frames(self.pet_id, 'idle', self.scale)
                self.animations['walk'] = load_pet_animation_frames(self.pet_id, 'walk', self.scale)

    def show_effect(self, effect_type):
        for _ in range(5): # Create a burst of 5 icons
            offset_x = random.randint(-40, 40)
            offset_y = random.randint(-80, -20) # Pop up from above the pet
            self.effects.append({
                'type': effect_type,
                'start_time': time.time(),
                'offset': (offset_x, offset_y) # Store relative offset
            })

    def update(self, dt):
        # Stat decay
        decay = self.definition['stat_decay_rate']
        self.instance_data['hunger'] = max(0, self.instance_data['hunger'] - decay['hunger'] * (dt / 1000.0))
        self.instance_data['happiness'] = max(0, self.instance_data['happiness'] - decay['happiness'] * (dt / 1000.0))
        if self.instance_data['hunger'] <= 0:
            self.instance_data['health'] = max(0, self.instance_data['health'] - decay['health'] * (dt / 1000.0))

        # AI movement
        if time.time() - self.state_timer > self.next_state_change:
            self.state = "walk" if self.state == "idle" else "idle"
            self.state_timer = time.time()
            self.next_state_change = random.uniform(2, 5)
            if self.state == "walk":
                self.direction = random.choice(["North", "South", "East", "West"])
            self.frame_index = 0

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

        # Animation timing
        self.anim_timer += dt
        if self.anim_timer > PET_ANIM_SPEED:
            self.anim_timer = 0
            frames = self.get_current_animation_frames()
            if frames:
                self.frame_index = (self.frame_index + 1) % len(frames)
        
        # Update effects (remove old ones)
        current_time = time.time()
        self.effects = [e for e in self.effects if current_time - e['start_time'] < EFFECT_DURATION]
    
    def get_current_animation_frames(self):
        # --- CORRECTED LOGIC ---
        if self.definition.get("directional"): 
            key = f"{self.state.capitalize()}{self.direction}"
            return self.animations.get(key, self.animations.get("IdleSouth", []))
        else: # For frame-based pets and non-directional spritesheets
            key = self.state
            return self.animations.get(key, self.animations.get("idle", []))


    def draw(self, surface):
        # Draw the pet
        frames = self.get_current_animation_frames()
        if not frames: return
        self.frame_index = self.frame_index % len(frames)
        image = frames[self.frame_index]
        
        # --- CORRECTED LOGIC: Flip non-directional pets when moving west ---
        if not self.definition.get("directional") and self.direction == 'West':
            image = pygame.transform.flip(image, True, False)

        rect = image.get_rect(center=(self.x, self.y))
        surface.blit(image, rect)
        if DEBUG_MODE: pygame.draw.rect(surface, (255,0,0), rect, 1)

        # Draw any active effects
        current_time = time.time()
        for effect in self.effects:
            elapsed_time = current_time - effect['start_time']
            
            # Calculate position: Follow pet, drift upwards
            draw_x = self.x + effect['offset'][0]
            draw_y = self.y + effect['offset'][1] - (elapsed_time * self.DRIFT_SPEED)

            # Calculate fade-out
            alpha = max(0, 255 * (1 - (elapsed_time / EFFECT_DURATION)))
            
            img_to_draw = None
            if effect['type'] == 'heart' and heart_img:
                img_to_draw = heart_img
            elif effect['type'] == 'smile' and smile_img:
                img_to_draw = smile_img
            
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
        bar_height = 25
        padding = 10
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

        if pet_instance['hunger'] < 20:
            warning_text = font_info.render("Pet need to be feed", True, HEALTH_COLOR)
            hunger_bar_rect = pygame.Rect(start_x, start_y + hunger_y_offset, width, bar_height)
            warning_rect = warning_text.get_rect(centerx=hunger_bar_rect.centerx, top=hunger_bar_rect.bottom + 5)
            surface.blit(warning_text, warning_rect)

class CuaHang:
    def __init__(self):
        self.restock_interval = 300; self.last_restock_time = 0
        self.current_stock = {}
        self.all_sellable_items = [k for k in item_data.keys() if k != "egg_common"]
        self.restock()
    def update(self):
        if time.time() - self.last_restock_time > self.restock_interval: print("Shop is restocking..."); self.restock()
    def restock(self):
        self.current_stock = {}
        # Slot 1: Always the Common Egg
        self.current_stock["egg_common"] = {"price": item_data["egg_common"]["price"], "quantity": 1}
        # Slots 2-8: 7 random items
        num_random_items = min(7, len(self.all_sellable_items))
        items_to_sell = random.sample(self.all_sellable_items, num_random_items)
        for item_id in items_to_sell:
            data = item_data[item_id]
            quantity = 1 if data.get("category") == "egg" else 3
            self.current_stock[item_id] = {"price": data["price"], "quantity": quantity}
        self.last_restock_time = time.time()
        
    def buy_item(self, item_id, player_currency, player_inventory):
        if item_id in self.current_stock:
            stock_info = self.current_stock[item_id]

            if stock_info["quantity"] <= 0:
                return "Sold out!"

            if player_currency.money >= stock_info["price"]:
                player_currency.money -= stock_info["price"]
                player_inventory.add_item(item_id)
                stock_info["quantity"] -= 1
                print(f"Bought {item_id} for {stock_info['price']}. Stock left: {stock_info['quantity']}")
                return "Purchase successful!"
            else:
                print("Not enough money.")
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
        if slot_key in self.slots:
            del self.slots[slot_key]

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
                            print(f"Unlocked slot {i+1} for {price} coins.")
                            save_profiles()
                        else:
                            print("Not enough money.")
                return {'action': 'none'}
        return None
        
    def draw(self, surface, mouse_pos):
        overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); surface.blit(overlay,(0,0))
        table_w = (self.cols*self.box_size)+((self.cols-1)*self.padding); table_h=(self.rows*self.box_size)+((self.rows-1)*self.padding);
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
                    egg_info = self.slots[slot_key]; egg_id = egg_info['item_id']
                    egg_data_def = item_data.get(egg_id, {})
                    total_hatch_time = egg_data_def.get("data", {}).get("hatch_time_seconds", 3600)
                    remaining_time = total_hatch_time - (time.time() - egg_info['start_time'])
                    if egg_img := item_images.get(egg_id):
                        egg_rect = egg_img.get_rect(centerx=box_rect.centerx, bottom=hatch_rect.top + 150)
                        surface.blit(egg_img, egg_rect)
                    if remaining_time > 0:
                        timer_text = font_info.render(TienTe.format_time(remaining_time), True, WHITE)
                        timer_rect = timer_text.get_rect(centerx=box_rect.centerx, bottom=box_rect.bottom - 15)
                        bg_rect = timer_rect.inflate(10, 5); bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
                        bg_surf.fill((0, 0, 0, 150)); surface.blit(bg_surf, bg_rect); surface.blit(timer_text, timer_rect)
                    else:
                        ready_text = font_small.render("READY!", True, READY_COLOR)
                        surface.blit(ready_text, ready_text.get_rect(centerx=box_rect.centerx, bottom=box_rect.bottom - 15))
                    border_color = READY_COLOR if remaining_time <= 0 else PANEL_BORDER_COLOR
                    pygame.draw.rect(surface, BUTTON_HOVER_COLOR if box_rect.collidepoint(mouse_pos) else border_color, box_rect, 5, 10)
                else:
                    plus_rect = self.plus_text.get_rect(centerx=box_rect.centerx, bottom=hatch_rect.top + 100)
                    surface.blit(self.plus_text, plus_rect)
                    pygame.draw.rect(surface, BUTTON_HOVER_COLOR if box_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR, box_rect, 5, 10)
            else:
                pygame.draw.rect(surface, LOCKED_SLOT_COLOR, box_rect, 0, 10)
                surface.blit(lock_img, lock_img.get_rect(center=box_rect.center))
                price_index = i - 4
                if 0 <= price_index < len(UNLOCK_PRICES):
                    price = UNLOCK_PRICES[price_index]
                    price_text = font_info.render(str(price), True, TEXT_COLOR)
                    surface.blit(price_text, (box_rect.centerx - price_text.get_width() - 5, box_rect.bottom - 40))
                    surface.blit(pygame.transform.scale(coin_img, (32, 32)), (box_rect.centerx + 5, box_rect.bottom - 45))
                pygame.draw.rect(surface, BUTTON_HOVER_COLOR if box_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR, box_rect, 5, 10)

class MissionManager:
    def __init__(self, profile_data, player_inventory, player_currency):
        self.profile = profile_data
        self.inventory = player_inventory
        self.currency = player_currency
        self.mission_message = ""
        self.mission_message_timer = 0
        
        # Define weekly rewards
        self.weekly_rewards = {
            200: {"type": "item", "id": "random_food", "desc": "Random Food Item"},
            500: {"type": "item", "id": "best_toy", "desc": "Best Toy"},
            1000: {"type": "item", "id": "best_egg", "desc": "Most Valuable Egg"}
        }
        
        self.check_and_reset_missions()

    def get_start_of_week_date(self):
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        return start_of_week.strftime("%Y-%m-%d")

    def check_and_reset_missions(self):
        today_str = datetime.today().strftime("%Y-%m-%d")
        week_start_str = self.get_start_of_week_date()

        # Daily Reset
        if self.profile.get('last_mission_reset_date') != today_str:
            print("Generating new daily missions for", today_str)
            self.profile['last_mission_reset_date'] = today_str
            self.generate_new_daily_missions()

        # Weekly Reset
        if self.profile.get('last_weekly_reset_date') != week_start_str:
            print("Resetting weekly mission progress for week starting", week_start_str)
            self.profile['last_weekly_reset_date'] = week_start_str
            self.profile['weekly_mission_points'] = 0
            self.profile['claimed_weekly_rewards'] = []
        
    def generate_new_daily_missions(self):
        self.profile['daily_missions'] = []
        # Filter out comments from the mission definitions
        possible_missions = [k for k, v in mission_definitions.items() if not v.get("is_comment")]
        
        # Ensure we don't pick more missions than available
        num_to_pick = min(4, len(possible_missions))
        chosen_mission_ids = random.sample(possible_missions, num_to_pick)
        
        for mission_id in chosen_mission_ids:
            self.profile['daily_missions'].append({
                "id": mission_id,
                "progress": 0,
                "claimed": False
            })

    def update_mission_progress(self, event_type, value=1):
        if not self.profile.get('daily_missions'): return

        for mission in self.profile['daily_missions']:
            mission_def = mission_definitions.get(mission['id'])
            if not mission_def or mission['claimed']:
                continue
            
            if mission_def['type'] == event_type:
                mission['progress'] += value
        
    def claim_daily_reward(self, mission_index):
        if not 0 <= mission_index < len(self.profile['daily_missions']): return
        
        mission = self.profile['daily_missions'][mission_index]
        mission_def = mission_definitions[mission['id']]
        
        if mission['claimed'] or mission['progress'] < mission_def['target']: return
        
        # Grant rewards
        reward = mission_def['reward']
        if 'money' in reward:
            self.currency.money += reward['money']
        if 'items' in reward:
            for item_id, qty in reward['items'].items():
                self.inventory.add_item(item_id, qty)
        
        # Add points and mark as claimed
        self.profile['weekly_mission_points'] = self.profile.get('weekly_mission_points', 0) + mission_def['points']
        mission['claimed'] = True
        self.set_message(f"Claimed: {mission_def['title']}!")
        save_profiles()
        
    def claim_weekly_reward(self, points_milestone):
        if points_milestone in self.profile.get('claimed_weekly_rewards', []): return
        if self.profile.get('weekly_mission_points', 0) < points_milestone: return

        reward_info = self.weekly_rewards[points_milestone]
        item_id_to_add = reward_info['id']
        
        if item_id_to_add == "random_food":
            food_items = [k for k, v in item_data.items() if v.get('category') == 'food']
            if food_items: self.inventory.add_item(random.choice(food_items))
        
        elif item_id_to_add == "best_toy":
            toys = [(k, v['price']) for k, v in item_data.items() if v.get('category') == 'toy']
            if toys:
                best_toy_id = max(toys, key=lambda item: item[1])[0]
                self.inventory.add_item(best_toy_id)
        
        elif item_id_to_add == "best_egg":
            # Dynamically find the most expensive egg
            eggs = [(k, v['price']) for k, v in item_data.items() if v.get('category') == 'egg']
            if eggs:
                best_egg_id = max(eggs, key=lambda item: item[1])[0]
                self.inventory.add_item(best_egg_id)

        self.profile['claimed_weekly_rewards'].append(points_milestone)
        self.set_message(f"Claimed weekly reward: {reward_info['desc']}!")
        save_profiles()

    def set_message(self, text):
        self.mission_message = text
        self.mission_message_timer = time.time()

    def draw(self, surface, mouse_pos):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180)); surface.blit(overlay, (0, 0))
        
        # Main panel
        panel_rect = pygame.Rect(0, 0, 1200, 800); panel_rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        pygame.draw.rect(surface, PANEL_FILL_COLOR, panel_rect, 0, 15); pygame.draw.rect(surface, PANEL_BORDER_COLOR, panel_rect, 6, 15)
        
        # Title
        title_text = font.render("MISSIONS", True, TEXT_COLOR)
        surface.blit(title_text, title_text.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + 30))

        # --- Daily Missions Section ---
        daily_title = font_small.render("Daily Tasks", True, TEXT_COLOR)
        surface.blit(daily_title, (panel_rect.left + 50, panel_rect.top + 100))
        
        start_y = panel_rect.top + 150
        for i, mission in enumerate(self.profile.get('daily_missions', [])):
            mission_def = mission_definitions[mission['id']]
            y_pos = start_y + i * 110
            
            # Background box
            mission_box = pygame.Rect(panel_rect.left + 50, y_pos, 700, 100)
            pygame.draw.rect(surface, LOCKED_SLOT_COLOR, mission_box, 0, 10)
            
            # Text
            mission_title_text = font_small.render(mission_def['title'], True, TEXT_COLOR)
            surface.blit(mission_title_text, (mission_box.left + 20, mission_box.top + 15))
            mission_desc_text = font_info.render(mission_def['description'], True, GRAY)
            surface.blit(mission_desc_text, (mission_box.left + 20, mission_box.top + 55))
            
            # Progress Bar
            progress = min(mission['progress'], mission_def['target'])
            progress_ratio = progress / mission_def['target']
            bar_w, bar_h = 300, 25
            bar_x, bar_y = mission_box.left + 380, mission_box.top + 50
            pygame.draw.rect(surface, GRAY, (bar_x, bar_y, bar_w, bar_h), 0, 5)
            pygame.draw.rect(surface, BOOST_COLOR, (bar_x, bar_y, bar_w * progress_ratio, bar_h), 0, 5)
            progress_text = font_info.render(f"{progress}/{mission_def['target']}", True, WHITE)
            surface.blit(progress_text, progress_text.get_rect(center=(bar_x + bar_w/2, bar_y + bar_h/2)))
            
            # Claim Button
            claim_btn_rect = pygame.Rect(mission_box.right + 30, y_pos, 150, 100)
            can_claim = progress_ratio >= 1 and not mission['claimed']
            
            btn_color = DISABLED_COLOR
            btn_text_str = "Claimed"
            if not mission['claimed']:
                if can_claim:
                    btn_color = BUTTON_HOVER_COLOR if claim_btn_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR
                    btn_text_str = "Claim"
                else:
                    btn_color = DISABLED_COLOR
                    btn_text_str = f"{mission_def['points']} pts"
                    
            pygame.draw.rect(surface, btn_color, claim_btn_rect, 0, 10)
            btn_text_surf = font_small.render(btn_text_str, True, WHITE)
            surface.blit(btn_text_surf, btn_text_surf.get_rect(center=claim_btn_rect.center))

        # --- Weekly Progress Section ---
        weekly_panel = pygame.Rect(panel_rect.left + 50, panel_rect.bottom - 200, panel_rect.width - 100, 150)
        pygame.draw.rect(surface, LOCKED_SLOT_COLOR, weekly_panel, 0, 10)
        
        weekly_title = font_small.render("Weekly Progress", True, TEXT_COLOR)
        surface.blit(weekly_title, (weekly_panel.left + 20, weekly_panel.top + 15))
        
        # Weekly Progress Bar
        w_bar_w, w_bar_h = weekly_panel.width - 40, 30
        w_bar_x, w_bar_y = weekly_panel.left + 20, weekly_panel.top + 50
        current_points = self.profile.get('weekly_mission_points', 0)
        points_ratio = min(current_points / 1000.0, 1.0)
        pygame.draw.rect(surface, GRAY, (w_bar_x, w_bar_y, w_bar_w, w_bar_h), 0, 8)
        pygame.draw.rect(surface, MISSION_POINTS_COLOR, (w_bar_x, w_bar_y, w_bar_w * points_ratio, w_bar_h), 0, 8)
        points_text = font_small.render(f"{current_points} / 1000", True, WHITE)
        surface.blit(points_text, points_text.get_rect(center= (w_bar_x + w_bar_w/2, w_bar_y + w_bar_h/2)))
        
        # Weekly Reward Milestones
        for points_needed, reward_info in self.weekly_rewards.items():
            milestone_x = w_bar_x + w_bar_w * (points_needed / 1000.0)
            reward_box = pygame.Rect(0, 0, 120, 50); reward_box.midtop = (milestone_x, w_bar_y + w_bar_h + 5)
            
            is_claimed = points_needed in self.profile.get('claimed_weekly_rewards', [])
            can_claim = current_points >= points_needed and not is_claimed
            
            box_color = DISABLED_COLOR
            if is_claimed:
                box_color = BOOST_COLOR
            elif can_claim:
                box_color = BUTTON_HOVER_COLOR if reward_box.collidepoint(mouse_pos) else READY_COLOR
            
            pygame.draw.rect(surface, box_color, reward_box, 0, 8)
            reward_text = font_info.render(reward_info['desc'], True, WHITE)
            surface.blit(reward_text, reward_text.get_rect(center=reward_box.center))
            pygame.draw.line(surface, box_color, (milestone_x, w_bar_y), (milestone_x, w_bar_y + w_bar_h), 2)
            
        # Message display
        if self.mission_message and time.time() - self.mission_message_timer < 2.5:
            msg_surf = font_small.render(self.mission_message, True, WHITE); msg_rect = msg_surf.get_rect(center=(panel_rect.centerx, panel_rect.bottom - 220))
            bg_rect = msg_rect.inflate(20, 10); bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA); bg_surf.fill((0, 0, 0, 160))
            screen.blit(bg_surf, bg_rect); screen.blit(msg_surf, msg_rect)

# -------------------- Load Characters & Game Objects --------------------
char_paths = [f"CHARACTER/{var}_P{i}.png" for var in ["Hero","Modern_Hero","Ninja","Peasant","Warrior"] for i in range(1,4)]
char_objs = [NguoiChamSoc(p.split("/")[-1].replace(".png",""), p, frame_data, 3.0) for p in char_paths]
for c, p in zip(char_objs, char_paths): c.sheet_path = p
shop = Building("GUI/shop.png", (0, 5), (256, 256), "Press 'E' to enter Shop", "shop_menu")
home = Building("GUI/home2.png", (275, -12), (260, 260), "Press 'E' to enter Home", "home_menu")
world_buildings = [shop, home]
try: shopkeeper = NguoiChamSoc("Shopkeeper", "CHARACTER/Ninja_Style_2_P2.png", frame_data, 10.0)
except Exception as e: print(f"Warning: Could not load shopkeeper character asset: {e}"); shopkeeper = None
path_center_x, path_width, fence_y, fence_step = SCREEN_WIDTH*0.45, 150, SCREEN_HEIGHT-120, 48
fence_objects = [(i*fence_step, fence_y) for i in range(int(path_center_x//fence_step))]
start_x = path_center_x + path_width; fence_objects.extend([(start_x+i*fence_step, fence_y) for i in range(int((SCREEN_WIDTH-start_x)//fence_step)+1)])


# -------------------- Game State Variables --------------------
scene, loading_start = "loading", time.time(); selection_idx, selected, player = 0, None, None
selected_profile_idx, player_name_input = None, ""
pet_name_input = ""
confirming_delete,confirming_escape, delete_target_index = False,False,None
game_currency, current_map = None, "world"
incubator_manager = None
player_inventory = None; shop_manager = CuaHang();
inventory_selected_item_id = None
incubator_selection_slot = None
shop_message, shop_message_timer = "", 0
UNLOCK_PRICES = [20, 30, 40, 50] # For Incubators
mission_manager = None

pet_management_selected_instance_id = None
pet_list_scroll_y = 0 
pet_menu_message = ""
pet_menu_message_timer = 0
is_dragging_scrollbar = False
scrollbar_drag_offset_y = 0
scrollbar_handle_rect = pygame.Rect(0,0,0,0)

money_generation_timer = 0
hatching_info = None 
hatching_animation_frames = []
hatching_frame_index = 0
hatching_timer = 0
hatched_pet_info = None
active_pets = []

# --- Storage Menu state ---
storage_scene_tab = 'items' # or 'pets'
storage_player_scroll_y = 0
storage_global_scroll_y = 0
storage_selected_player_idx = None
storage_selected_global_idx = None
storage_message = ""
storage_message_timer = 0

# --- Pet Interaction Variables ---
interaction_menu_open = False
interaction_pet = None
interaction_submenu = None 
clickable_interaction_rects = {}


def load_hatching_animation(egg_id):
    if egg_id not in item_data: return []
    base_path = item_data[egg_id]["image_path"].replace("_1.png", "_")
    frames = []
    for i in range(1, 23):
        path = f"{base_path}{i}.png"
        try:
            img = pygame.image.load(path).convert_alpha()
            frames.append(img)
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
    chosen_pet_id = random.choices(pet_ids, weights=chances, k=1)[0]
    return chosen_pet_id

def draw_item_effects(surface, effects_dict, start_pos):
    y_offset = 0
    line_height = 28
    
    effects_title = font_info.render("Effects:", True, TEXT_COLOR)
    surface.blit(effects_title, (start_pos[0], start_pos[1]))
    y_offset += line_height

    for stat, value in effects_dict.items():
        if value > 0:
            text = f"+{value} {stat.capitalize()}"
            color = BOOST_COLOR
            effect_text = font_info.render(text, True, color)
            surface.blit(effect_text, (start_pos[0] + 10, start_pos[1] + y_offset))
            y_offset += line_height
    return y_offset


# -------------------- Save/Load Functions --------------------
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
        profile['unlocked_pet_slots'] = profiles[selected_profile_idx].get('unlocked_pet_slots', 5) # Save the slot count
        profile['last_map'] = current_map
        
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
            
            # --- Money generation from ACTIVE pets ---
            total_money_generated = 0
            for pet_obj in active_pets:
                pet_instance = pet_obj.instance_data
                pet_def = pet_obj.definition
                if not pet_def: continue

                avg_stat_percent = (pet_instance['health'] + pet_instance['happiness'] + pet_instance['hunger']) / 3.0
                avg_stat_ratio = avg_stat_percent / 100.0
                base_money = pet_def.get('base_money_per_minute', 0)
                money_from_this_pet = int(base_money * avg_stat_ratio)
                total_money_generated += money_from_this_pet
            
            if total_money_generated > 0:
                game_currency.money += total_money_generated
                print(f"Your active pets generated {total_money_generated} coins!")
                if mission_manager:
                    mission_manager.update_mission_progress('earn_money', value=total_money_generated)
            
            # --- Stat decay for INACTIVE pets ---
            all_pets_in_inventory = player_inventory.get_all_pets()
            active_instance_ids = [p.instance_data['instance_id'] for p in active_pets]
            for pet_instance in all_pets_in_inventory:
                if pet_instance['instance_id'] not in active_instance_ids:
                    pet_def = pet_data.get(pet_instance['pet_id'], {})
                    if not pet_def: continue

                    decay_rates = pet_def.get('stat_decay_rate', {})
                    decay_hunger = decay_rates.get('hunger', 0) * 60
                    decay_happiness = decay_rates.get('happiness', 0) * 60
                    
                    pet_instance['hunger'] = max(0, pet_instance['hunger'] - decay_hunger)
                    pet_instance['happiness'] = max(0, pet_instance['happiness'] - decay_happiness)
                    
                    if pet_instance['hunger'] <= 0:
                        decay_health = decay_rates.get('health', 0) * 60
                        pet_instance['health'] = max(0, pet_instance['health'] - decay_health)


    # --- Event Handling ---
    for e in pygame.event.get():
        if e.type == pygame.QUIT: 
            save_and_quit()
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            is_dragging_scrollbar = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            if confirming_escape: # If menu is already open, close it.
                confirming_escape = False
            elif interaction_menu_open: # If a pop-up is open, close it.
                interaction_menu_open = False
                interaction_pet = None
                interaction_submenu = None
            elif scene in ["shop_menu", "home_menu", "inventory_menu", "pet_management_menu", "storage_menu"]: # If in a menu, go back to play.
                scene = "play"
                is_dragging_scrollbar = False # Ensure dragging stops on scene change
            elif scene == "incubator_egg_select": # Special case for egg selection.
                scene = "home_menu"
            elif scene == "hatching_animation": # Don't allow escape during this animation.
                pass
            else: # As a last resort, open the escape confirmation menu.
                confirming_escape = True

        # --- If the escape menu is open, it captures all input. ---
        if confirming_escape:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if yes_button_rect.collidepoint(e.pos):
                    save_and_quit()
                elif no_button_rect.collidepoint(e.pos):
                    confirming_escape = False
            # Block any other events from propagating to the scenes below.
            continue
        ### CHANGED BLOCK END ###
        if scene == "name_input":
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    if player_name_input.strip():
                        profiles[selected_profile_idx]={
                            "name":player_name_input.strip(), "char":None, "money": 10, "play_time": 0, 
                            "unlocked_incubators": [True,True,True,True,False,False,False,False], 
                            "inventory": {}, "incubator_slots": {}, "pets": [], "active_pet_instances": [], 
                            "last_map": "world", "unlocked_pet_slots": 5,
                            "daily_missions": [], "last_mission_reset_date": "none", 
                            "weekly_mission_points": 0, "last_weekly_reset_date": "none",
                            "claimed_weekly_rewards": []
                        }
                        save_profiles()
                        incubator_manager = Trung(profiles[selected_profile_idx]['unlocked_incubators'], {})
                        game_currency=TienTe(10,0); player_inventory=TuiDo({}, [])
                        mission_manager = MissionManager(profiles[selected_profile_idx], player_inventory, game_currency)
                        scene="char_select"
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
                                # --- FIX FOR OLD/CORRUPTED SAVE FILES ---
                                if 'unlocked_pet_slots' not in profile or profile['unlocked_pet_slots'] < 5:
                                    profile['unlocked_pet_slots'] = 5
                                if 'active_pet_instances' not in profile: profile['active_pet_instances'] = []
                                if 'last_map' not in profile: profile['last_map'] = 'world'
                                # --- Start the music here! ---
                                if theme_song_path and not pygame.mixer.music.get_busy():
                                    pygame.mixer.music.load(theme_song_path)
                                    pygame.mixer.music.play(loops=-1) # -1 means loop forever
                                
                                if 'daily_missions' not in profile: profile['daily_missions'] = []
                                if 'last_mission_reset_date' not in profile: profile['last_mission_reset_date'] = "none"
                                if 'weekly_mission_points' not in profile: profile['weekly_mission_points'] = 0
                                if 'last_weekly_reset_date' not in profile: profile['last_weekly_reset_date'] = "none"
                                if 'claimed_weekly_rewards' not in profile: profile['claimed_weekly_rewards'] = []
                                
                                money=profile.get("money",10); play_time=profile.get("play_time",0)
                                inventory_data=profile.get("inventory",{})
                                pets_data_saved = profile.get("pets", [])
                                game_currency=TienTe(money,play_time); player_inventory=TuiDo(inventory_data, pets_data_saved)
                                unlocked_data = profile.get("unlocked_incubators",[True,True,True,True,False,False,False,False])
                                slots_data = profile.get("incubator_slots", {})
                                incubator_manager = Trung(unlocked_data, slots_data)
                                
                                mission_manager = MissionManager(profile, player_inventory, game_currency)

                                active_pets.clear()
                                active_ids = profile.get('active_pet_instances', [])
                                for inst_id in active_ids:
                                    pet_instance = player_inventory.get_pet_by_instance_id(inst_id)
                                    if pet_instance:
                                        active_pets.append(ThuCung(pet_instance))

                                current_map = profile.get('last_map', 'world')

                                if profile.get("char"):
                                    selected=next((c for c in char_objs if c.name==profile["char"]),None)
                                    if selected: player=NguoiChamSoc(selected.name,selected.sheet_path,frame_data,2.0); player.x,player.y=SCREEN_WIDTH//2,SCREEN_HEIGHT//2; scene="play"
                                    else: scene="char_select"
                                else: scene="char_select"
                            break
        elif scene == "char_select":
            # Handle Mouse Clicks
            if e.type == pygame.MOUSEBUTTONDOWN:
                x,y=e.pos
                is_arrow_click = False
                # Left arrow click
                if 100<x<140 and SCREEN_HEIGHT//2-30<y<SCREEN_HEIGHT//2+30:
                    selection_idx=(selection_idx-1)%len(char_objs)
                    is_arrow_click = True
                # Right arrow click
                elif SCREEN_WIDTH-140<x<SCREEN_WIDTH-100 and SCREEN_HEIGHT//2-30<y<SCREEN_HEIGHT//2+30:
                    selection_idx=(selection_idx+1)%len(char_objs)
                    is_arrow_click = True

                # If the click was not on an arrow, select the character
                if not is_arrow_click:
                    selected=char_objs[selection_idx]
                    profiles[selected_profile_idx]["char"]=selected.name
                    save_profiles()
                    player=NguoiChamSoc(selected.name,selected.sheet_path,frame_data,2.0)
                    player.x,player.y=SCREEN_WIDTH//2,SCREEN_HEIGHT//2
                    scene="play"

            # Handle Keyboard Presses
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    selection_idx = (selection_idx - 1) % len(char_objs)
                elif e.key == pygame.K_RIGHT:
                    selection_idx = (selection_idx + 1) % len(char_objs)
                elif e.key == pygame.K_RETURN: # The 'Enter' key
                    # Select the current character
                    selected=char_objs[selection_idx]
                    profiles[selected_profile_idx]["char"]=selected.name
                    save_profiles()
                    player=NguoiChamSoc(selected.name,selected.sheet_path,frame_data,2.0)
                    player.x,player.y=SCREEN_WIDTH//2,SCREEN_HEIGHT//2
                    scene="play"

            # This part remains the same, to keep the character animating
            for char_obj in char_objs:
                char_obj.update(dt)
        elif scene == "play":
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_e:
                    if interaction_menu_open:
                        interaction_menu_open = False; interaction_pet = None; interaction_submenu = None
                        continue
                    
                    interacted_with_building = False
                    if current_map == "world":
                        for building in world_buildings:
                            can_interact, target_scene = building.check_interaction_and_draw_prompt(screen, player, False)
                            if can_interact: 
                                scene = target_scene
                                if scene == "storage_menu": # Reset storage UI state
                                    storage_selected_player_idx, storage_selected_global_idx = None, None
                                    storage_player_scroll_y, storage_global_scroll_y = 0, 0
                                interacted_with_building = True
                                break
                            
                    if not interacted_with_building and current_map == "pet_area":
                        closest_pet = None
                        min_dist = 100 
                        for pet in active_pets:
                            dist = pygame.math.Vector2(player.x, player.y).distance_to((pet.x, pet.y))
                            if dist < min_dist:
                                min_dist = dist
                                closest_pet = pet
                        if closest_pet:
                            interaction_pet = closest_pet
                            interaction_menu_open = True
                            interaction_submenu = None
                            interacted_with_building = True 

                    if not interacted_with_building:
                        inventory_selected_item_id = None; scene = "inventory_menu"
                elif e.key == pygame.K_r:
                    if not interaction_menu_open:
                        pet_management_selected_instance_id = None
                        pet_list_scroll_y = 0
                        scene = "pet_management_menu"

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if backpack_rect.collidepoint(mouse_pos) and not interaction_menu_open:
                    inventory_selected_item_id = None; scene = "inventory_menu"
                elif pet_menu_rect.collidepoint(mouse_pos) and not interaction_menu_open:
                    pet_management_selected_instance_id = None; pet_list_scroll_y = 0; scene = "pet_management_menu"
                elif mission_icon_rect.collidepoint(mouse_pos) and not interaction_menu_open:
                    scene = "mission_menu"
                elif interaction_menu_open:
                    for action, rect in clickable_interaction_rects.items():
                        if rect.collidepoint(mouse_pos):
                            if action == 'feed_btn':
                                interaction_submenu = 'feed'
                            elif action == 'play_btn':
                                interaction_submenu = 'play'
                            elif action in ['exit_interaction', 'cancel_interaction']:
                                interaction_menu_open = False; interaction_pet = None; interaction_submenu = None
                            else: 
                                item_id = action
                                item_info = item_data[item_id]
                                item_effects = item_info["data"]["effects"]
                                
                                interaction_pet.instance_data['hunger'] = min(100, interaction_pet.instance_data['hunger'] + item_effects.get('hunger', 0))
                                interaction_pet.instance_data['happiness'] = min(100, interaction_pet.instance_data['happiness'] + item_effects.get('happiness', 0))
                                interaction_pet.instance_data['health'] = min(100, interaction_pet.instance_data['health'] + item_effects.get('health', 0))

                                if item_info['category'] == 'food': 
                                    interaction_pet.show_effect('heart')
                                    if mission_manager: mission_manager.update_mission_progress('feed')
                                elif item_info['category'] == 'toy': 
                                    interaction_pet.show_effect('smile')
                                    if mission_manager: mission_manager.update_mission_progress('play')

                                player_inventory.remove_item(item_id)
                                
                                interaction_menu_open = False; interaction_pet = None; interaction_submenu = None
                            break
        elif scene == "shop_menu":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_e: scene = "play"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                shop_items_all = list(shop_manager.current_stock.items())
                COLS, ROWS = 4, 2; BOX_SIZE, PADDING = 150, 20
                TABLE_W = (COLS * BOX_SIZE) + ((COLS - 1) * PADDING)
                TABLE_X = (SCREEN_WIDTH - TABLE_W) // 2
                TABLE_Y = max(150, (SCREEN_HEIGHT - (ROWS * (BOX_SIZE+PADDING))) // 2 + 50)
                for i, (item_id, _) in enumerate(shop_items_all):
                    r, c = divmod(i, COLS); box_x = TABLE_X + c * (BOX_SIZE + PADDING); box_y = TABLE_Y + r * (BOX_SIZE + PADDING); box_rect = pygame.Rect(box_x, box_y, BOX_SIZE, BOX_SIZE)
                    if box_rect.collidepoint(mouse_pos):
                        # Get info *before* the purchase
                        price = shop_manager.current_stock[item_id]['price']
                        item_category = item_data.get(item_id, {}).get('category')
                        
                        message = shop_manager.buy_item(item_id, game_currency, player_inventory)
                        
                        if "successful" in message and mission_manager:
                            # Update spending mission
                            mission_manager.update_mission_progress('spend_money', value=price)
                            
                            # Update category-specific missions
                            if item_category == 'egg':
                                mission_manager.update_mission_progress('buy_egg')
                            elif item_category == 'food':
                                mission_manager.update_mission_progress('buy_food')
                            elif item_category == 'toy':
                                mission_manager.update_mission_progress('buy_toy')

                        shop_message = message; shop_message_timer = time.time()
                        break
        elif scene == "home_menu":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_e: scene = "play"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and incubator_manager:
                click_result = incubator_manager.handle_click(mouse_pos, game_currency)
                if click_result:
                    if click_result['action'] == 'select_egg':
                        incubator_selection_slot = click_result['slot']; scene = "incubator_egg_select"
                    elif click_result['action'] == 'hatch':
                        hatching_info = {'slot_key': click_result['slot_key'], 'egg_id': click_result['egg_id']}
                        hatching_animation_frames = load_hatching_animation(hatching_info['egg_id'])
                        hatching_frame_index = 0; hatching_timer = 0; hatched_pet_info = None
                        scene = "hatching_animation"
        elif scene == "incubator_egg_select":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: scene = "home_menu"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and incubator_manager:
                player_eggs = player_inventory.get_eggs()
                select_panel_rect = pygame.Rect(0,0,800,500); select_panel_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
                EGG_COLS, EGG_BOX_SIZE, EGG_PADDING = 4, 120, 20
                for i, (egg_id, qty) in enumerate(player_eggs):
                    r,c=divmod(i, EGG_COLS); box_x = select_panel_rect.left + 50 + c*(EGG_BOX_SIZE+EGG_PADDING); box_y = select_panel_rect.top + 100 + r*(EGG_BOX_SIZE+EGG_PADDING)
                    egg_box_rect = pygame.Rect(box_x, box_y, EGG_BOX_SIZE, EGG_BOX_SIZE)
                    if egg_box_rect.collidepoint(mouse_pos):
                        player_inventory.remove_item(egg_id)
                        incubator_manager.place_egg(incubator_selection_slot, egg_id)
                        save_profiles(); scene = "home_menu"
                        break
        elif scene == "inventory_menu":
            if e.type == pygame.KEYDOWN and e.key in [pygame.K_e, pygame.K_ESCAPE]: scene = "play"; inventory_selected_item_id = None
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                items_in_inv = player_inventory.get_all_items()
                for i,(item_id,qty) in enumerate(items_in_inv):
                    r,c=divmod(i,10); box_x=100+(SCREEN_WIDTH*0.6-10*(80+10)+10)//2+c*(80+10); box_y=100+80+50+r*(80+10); item_rect=pygame.Rect(box_x,box_y,80,80)
                    if item_rect.collidepoint(mouse_pos): inventory_selected_item_id=item_id; break
        elif scene == "pet_management_menu":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                scene = "play"
                is_dragging_scrollbar = False # Reset on exit

            if e.type == pygame.MOUSEWHEEL:
                list_panel_rect = pygame.Rect(100, 100, 400, SCREEN_HEIGHT - 200)
                if list_panel_rect.collidepoint(mouse_pos):
                    pet_list_scroll_y -= e.y * SCROLL_SPEED

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if scrollbar_handle_rect.collidepoint(e.pos):
                    is_dragging_scrollbar = True
                    scrollbar_drag_offset_y = e.pos[1] - scrollbar_handle_rect.y
                else:
                    list_panel_rect = pygame.Rect(100, 100, 400, SCREEN_HEIGHT - 200)
                    list_content_rect = list_panel_rect.inflate(-40, -220)
                    list_content_rect.top = list_panel_rect.top + 120

                    if list_content_rect.collidepoint(mouse_pos):
                        pets_in_inv = player_inventory.get_all_pets()
                        ROW_H, PADDING_Y = 80, 10
                        for i, pet in enumerate(pets_in_inv):
                            adjusted_mouse_y = mouse_pos[1] - list_content_rect.top + pet_list_scroll_y
                            row_y_pos = i * (ROW_H + PADDING_Y)
                            pet_row_rect_virtual = pygame.Rect(0, row_y_pos, list_content_rect.width, ROW_H)
                            if pet_row_rect_virtual.collidepoint(mouse_pos[0] - list_content_rect.left, adjusted_mouse_y):
                                pet_management_selected_instance_id = pet['instance_id']
                                break

                    selected_pet_instance = player_inventory.get_pet_by_instance_id(pet_management_selected_instance_id)
                    if selected_pet_instance:
                        info_panel_rect = pygame.Rect(520, 100, SCREEN_WIDTH - 620, SCREEN_HEIGHT - 200)
                        already_out = any(p.instance_data['instance_id'] == pet_management_selected_instance_id for p in active_pets)
                        bring_out_rect = pygame.Rect(0, 0, 250, 60)
                        bring_out_rect.midbottom = (info_panel_rect.centerx, info_panel_rect.bottom - 30)

                        if bring_out_rect.collidepoint(mouse_pos):
                            if already_out:
                                active_pets = [p for p in active_pets if p.instance_data['instance_id'] != pet_management_selected_instance_id]
                            else:
                                unlocked_slots = profiles[selected_profile_idx]['unlocked_pet_slots']
                                if len(active_pets) < unlocked_slots:
                                    active_pets.append(ThuCung(selected_pet_instance))
                    # Unlock slot button
                    unlocked_slots = profiles[selected_profile_idx]['unlocked_pet_slots']
                    if unlocked_slots < MAX_PET_SLOTS:
                        price_index = unlocked_slots - 5
                        if 0 <= price_index < len(PET_SLOT_UNLOCK_PRICES):
                            unlock_button_rect = pygame.Rect(list_panel_rect.left + 20, list_panel_rect.bottom - 70, list_panel_rect.width - 40, 50)
                            if unlock_button_rect.collidepoint(mouse_pos):
                                price = PET_SLOT_UNLOCK_PRICES[price_index]
                                if game_currency.money >= price:
                                    game_currency.money -= price
                                    profiles[selected_profile_idx]['unlocked_pet_slots'] += 1
                                    if mission_manager:
                                        mission_manager.update_mission_progress('unlock_pet_slot')
                                    pet_menu_message = "Slot unlocked!"; pet_menu_message_timer = time.time()
                                else:
                                    pet_menu_message = "Not enough coins!"; pet_menu_message_timer = time.time()
        elif scene == "storage_menu":
            # Define UI layout for event handling
            PANEL_MARGIN, TOP_MARGIN, BOTTOM_MARGIN = 150, 120, 100
            PANEL_Y = TOP_MARGIN
            PANEL_HEIGHT = SCREEN_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN
            PLAYER_PANEL_W = (SCREEN_WIDTH / 2) - PANEL_MARGIN
            PLAYER_PANEL_RECT = pygame.Rect(50, PANEL_Y, PLAYER_PANEL_W, PANEL_HEIGHT)
            GLOBAL_PANEL_RECT = pygame.Rect(SCREEN_WIDTH - 50 - PLAYER_PANEL_W, PANEL_Y, PLAYER_PANEL_W, PANEL_HEIGHT)
            
            if e.type == pygame.KEYDOWN and e.key in [pygame.K_e]:
                scene = "play"; storage_selected_player_idx, storage_selected_global_idx = None, None

            if e.type == pygame.MOUSEBUTTONDOWN:
                # Tab switching
                items_tab_rect = pygame.Rect(SCREEN_WIDTH/2 - 220, 50, 200, 50)
                pets_tab_rect = pygame.Rect(SCREEN_WIDTH/2 + 20, 50, 200, 50)
                if items_tab_rect.collidepoint(mouse_pos):
                    storage_scene_tab = 'items'; storage_selected_player_idx, storage_selected_global_idx = None, None
                elif pets_tab_rect.collidepoint(mouse_pos):
                    storage_scene_tab = 'pets'; storage_selected_player_idx, storage_selected_global_idx = None, None

                # Transfer buttons
                store_button_rect = pygame.Rect(SCREEN_WIDTH/2 - 40, SCREEN_HEIGHT/2 - 60, 80, 80)
                retrieve_button_rect = pygame.Rect(SCREEN_WIDTH/2 - 40, SCREEN_HEIGHT/2 + 40, 80, 80)

                # Transfer Player -> Global (Store)
                if storage_selected_player_idx is not None and store_button_rect.collidepoint(mouse_pos):
                    if storage_scene_tab == 'items':
                        item_id = player_inventory.get_all_items()[storage_selected_player_idx][0]
                        if player_inventory.remove_item(item_id):
                            global_storage_data['items'][item_id] = global_storage_data['items'].get(item_id, 0) + 1
                            storage_message = f"Moved 1 {item_data[item_id]['name']} to storage."
                    else: # pets
                        pet_to_move = player_inventory.get_all_pets()[storage_selected_player_idx]
                        if any(p.instance_data['instance_id'] == pet_to_move['instance_id'] for p in active_pets):
                            storage_message = "Cannot move an active pet!"
                        else:
                            player_inventory.pets.remove(pet_to_move)
                            global_storage_data['pets'].append(pet_to_move)
                            storage_message = f"Moved {pet_to_move['name']} to storage."
                    
                    save_profiles(); save_global_storage()
                    storage_selected_player_idx, storage_selected_global_idx = None, None
                    storage_message_timer = time.time()
                
                # Transfer Global -> Player (Retrieve)
                elif storage_selected_global_idx is not None and retrieve_button_rect.collidepoint(mouse_pos):
                    if storage_scene_tab == 'items':
                        item_id = sorted(global_storage_data['items'].items())[storage_selected_global_idx][0]
                        global_storage_data['items'][item_id] -= 1
                        if global_storage_data['items'][item_id] == 0:
                            del global_storage_data['items'][item_id]
                        player_inventory.add_item(item_id)
                        storage_message = f"Moved 1 {item_data[item_id]['name']} to inventory."
                    else: # pets
                        pet_to_move = sorted(global_storage_data['pets'], key=lambda p: p['instance_id'])[storage_selected_global_idx]
                        global_storage_data['pets'].remove(pet_to_move)
                        player_inventory.pets.append(pet_to_move)
                        storage_message = f"Moved {pet_to_move['name']} to inventory."

                    save_profiles(); save_global_storage()
                    storage_selected_player_idx, storage_selected_global_idx = None, None
                    storage_message_timer = time.time()

                # Item/Pet Selection is handled in the drawing loop
                else:
                    pass
            
            if e.type == pygame.MOUSEWHEEL:
                if PLAYER_PANEL_RECT.collidepoint(mouse_pos):
                    storage_player_scroll_y -= e.y * SCROLL_SPEED
                elif GLOBAL_PANEL_RECT.collidepoint(mouse_pos):
                    storage_global_scroll_y -= e.y * SCROLL_SPEED

        elif scene == "hatching_animation":
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if hatched_pet_info and incubator_manager:
                    pet_name_input = "" 
                    scene = "pet_naming"
        
        elif scene == "pet_naming":
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    player_inventory.add_pet(hatched_pet_info['pet_id'], pet_name_input)
                    
                    if mission_manager:
                        mission_manager.update_mission_progress('hatch')

                    # Clean up all hatching-related data
                    incubator_manager.clear_slot(hatching_info['slot_key'])
                    save_profiles()
                    hatching_info = None
                    hatching_animation_frames = []
                    hatched_pet_info = None
                    
                    scene = "home_menu"

                elif e.key == pygame.K_BACKSPACE:
                    pet_name_input = pet_name_input[:-1]
                
                elif len(pet_name_input) < 12: 
                    pet_name_input += e.unicode
        
        elif scene == "mission_menu":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                scene = "play"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and mission_manager:
                panel_rect = pygame.Rect(0, 0, 1200, 800); panel_rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
                # Check daily claims
                for i in range(len(mission_manager.profile.get('daily_missions', []))):
                    start_y = panel_rect.top + 150
                    y_pos = start_y + i * 110
                    claim_btn_rect = pygame.Rect(panel_rect.left + 50 + 700 + 30, y_pos, 150, 100)
                    if claim_btn_rect.collidepoint(mouse_pos):
                        mission_manager.claim_daily_reward(i)
                        break
                # Check weekly claims
                w_panel_rect = pygame.Rect(panel_rect.left + 50, panel_rect.bottom - 200, panel_rect.width - 100, 150)
                w_bar_x = w_panel_rect.left + 20
                w_bar_w = w_panel_rect.width - 40
                w_bar_y = w_panel_rect.top + 50
                w_bar_h = 30
                for points_needed, _ in mission_manager.weekly_rewards.items():
                    milestone_x = w_bar_x + w_bar_w * (points_needed / 1000.0)
                    reward_box = pygame.Rect(0, 0, 120, 50); reward_box.midtop = (milestone_x, w_bar_y + w_bar_h + 5)
                    if reward_box.collidepoint(mouse_pos):
                        mission_manager.claim_weekly_reward(points_needed)
                        break
    
    # -------------------- Draw Scenes --------------------
    screen.fill((0, 0, 0))
    
    if scene == 'play': clickable_interaction_rects = {}
    if player: player.update(dt)
    if current_map == "pet_area":
        for pet in active_pets: pet.update(dt)

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
            name_y_offset = -20 if profile else 0; name_str,color = (profile.get("name","PROFILE"),TEXT_COLOR) if profile else ("[EMPTY]",GRAY)
            text_surf=font.render(name_str.upper(),True,color); screen.blit(text_surf,text_surf.get_rect(midleft=(PANEL_X+220, row_y+ROW_HEIGHT//2+name_y_offset)))
            if profile:
                pet_count = len(profile.get('pets', []))
                slot_count = profile.get('unlocked_pet_slots', 5)
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
                if hatching_timer > time_per_frame:
                    hatching_frame_index += 1; hatching_timer = 0
                
                if hatching_frame_index >= len(hatching_animation_frames):
                    pet_id = choose_pet_from_egg(hatching_info['egg_id'])
                    if pet_id:
                        print(f"Hatched a {pet_id}!")
                        pet_frames = load_pet_animation_frames(pet_id, "idle", scale=15.0) 
                        if pet_frames:
                             hatched_pet_info = {'pet_id': pet_id, 'frames': pet_frames, 'frame_index': 0, 'timer': 0}
                        else:
                            print(f"Error: Could not load animation for pet '{pet_id}'.")
                            scene = "home_menu"
                    else:
                        print("Error: Could not determine pet from egg."); scene = "home_menu"
                else:
                    current_frame = hatching_animation_frames[hatching_frame_index]
                    scaled_size = (512, 512)
                    scaled_frame = pygame.transform.scale(current_frame, scaled_size)
                    frame_rect = scaled_frame.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                    screen.blit(scaled_frame, frame_rect)
            else:
                print("Error: No hatching animation frames loaded."); scene = "home_menu"
        else:
            pet_frames = hatched_pet_info['frames']
            if pet_frames:
                hatched_pet_info['timer'] += dt
                if hatched_pet_info['timer'] > PET_ANIM_SPEED:
                    hatched_pet_info['frame_index'] = (hatched_pet_info['frame_index'] + 1) % len(pet_frames)
                    hatched_pet_info['timer'] = 0
                
                pet_image = pet_frames[hatched_pet_info['frame_index']]
                pet_rect = pet_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(pet_image, pet_rect)
            
            pet_display_name = pet_data.get(hatched_pet_info['pet_id'], {}).get('name', hatched_pet_info['pet_id'])
            pet_name_text = font_reveal.render(pet_display_name.upper(), True, WHITE)
            name_rect = pet_name_text.get_rect(center=(SCREEN_WIDTH // 2, pet_rect.bottom + 60))
            screen.blit(pet_name_text, name_rect)
            continue_text = font_small.render("Click to continue", True, GRAY)
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
            screen.blit(continue_text, continue_rect)

    elif scene == "pet_naming":
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 220)); screen.blit(overlay, (0, 0))
        if hatched_pet_info and hatched_pet_info.get('frames'):
            pet_image = hatched_pet_info['frames'][0]
            pet_rect = pet_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            screen.blit(pet_image, pet_rect)
        prompt = font.render("Name your new pet:", True, WHITE)
        prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(prompt, prompt_rect)
        name_surface = font.render(pet_name_input + "_", True, WHITE)
        name_rect = name_surface.get_rect(center=(SCREEN_WIDTH // 2, prompt_rect.bottom + 50))
        screen.blit(name_surface, name_rect)
        instr_text = font_small.render("Press Enter to confirm", True, GRAY)
        instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        screen.blit(instr_text, instr_rect)

    elif scene == "mission_menu":
        if mission_manager:
            mission_manager.draw(screen, mouse_pos)
    
    # --- In-Game Scenes ---
    else: 
        screen.blit(play_map_img, (0, 0))
        keys = pygame.key.get_pressed()

        if player:
            dx=dy=0
            speed=300*dt/1000
            if not interaction_menu_open:
                if keys[pygame.K_w]: dy=-speed; player.last_dir="North"
                elif keys[pygame.K_s]: dy=speed; player.last_dir="South"
                if keys[pygame.K_a]: dx=-speed; player.last_dir="West"
                elif keys[pygame.K_d]: dx=speed; player.last_dir="East"

        if current_map == "world":
            for building in world_buildings: building.draw(screen)
            for pos in fence_objects: screen.blit(fence_img, pos)
        elif current_map == "pet_area":
            for pet in active_pets:
                pet.draw(screen)

        if player:
            is_moving = (dx != 0 or dy != 0)
            key = f"Walk{player.last_dir}" if is_moving else f"Idle{player.last_dir}"
            player.draw(screen, (player.x, player.y), key)

        if scene == "play":
            if player:
                player.x += dx
                player.y += dy

                if current_map == "world":
                    player_feet_y = player.get_rect().bottom
                    if fence_y + 50 <= player_feet_y <= fence_y + 100:
                        if not (path_center_x < player.x < path_center_x + path_width):
                            # Determine side and snap accordingly
                            if player_feet_y < fence_y + 75:  # coming from above
                                player.y = fence_y + 50 - player.get_rect().height // 2
                            else:  # coming from below
                                player.y = fence_y + 100 - player.get_rect().height // 2
                
                player_rect = player.get_rect()
                if player_rect.left < 0: player.x = player_rect.width / 2
                if player_rect.right > SCREEN_WIDTH: player.x = SCREEN_WIDTH - player_rect.width / 2
                if current_map == "world" and player_rect.top < 0:
                    player.y = player_rect.height / 2
                if current_map == "pet_area":
                     if player_rect.bottom > SCREEN_HEIGHT: player.y = SCREEN_HEIGHT - player_rect.height / 2

            if current_map == "world":
                if player.y > SCREEN_HEIGHT and path_center_x < player.x < path_center_x+path_width:
                    current_map="pet_area"; player.y=10

                for building in world_buildings: building.check_interaction_and_draw_prompt(screen, player, interaction_menu_open)
            elif current_map == "pet_area":
                if player.y < 0:
                    current_map="world"; player.y=SCREEN_HEIGHT-125
                    active_ids = [p.instance_data['instance_id'] for p in active_pets]
                    profiles[selected_profile_idx]['active_pet_instances'] = active_ids
                    save_profiles()
                else:
                    can_interact_with_pet = False
                    if not interaction_menu_open:
                        for pet in active_pets:
                            dist = pygame.math.Vector2(player.x, player.y).distance_to((pet.x, pet.y))
                            if dist < 100:
                                can_interact_with_pet = True
                                break
                    if can_interact_with_pet:
                        prompt_text = font_small.render("Press 'E' to interact", True, WHITE)
                        prompt_bg = pygame.Surface((prompt_text.get_width() + 20, prompt_text.get_height() + 10), pygame.SRCALPHA)
                        prompt_bg.fill((0, 0, 0, 150)); screen.blit(prompt_bg, (20, SCREEN_HEIGHT - 60)); screen.blit(prompt_text, (30, SCREEN_HEIGHT - 55))
            
            screen.blit(backpack_img, backpack_rect)
            screen.blit(pet_menu_icon, pet_menu_rect)
            screen.blit(mission_icon, mission_icon_rect)

            if interaction_menu_open and interaction_pet:
                if interaction_submenu is None:
                    panel_w, panel_h = 200, 200
                    panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
                    panel_rect.midleft = (interaction_pet.get_rect().right + 10, interaction_pet.get_rect().centery)
                    panel_rect.clamp_ip(screen.get_rect())
                    pygame.draw.rect(screen, PANEL_FILL_COLOR, panel_rect, 0, 15); pygame.draw.rect(screen, PANEL_BORDER_COLOR, panel_rect, 4, 15)
                    pet_name = interaction_pet.instance_data.get('name', 'Pet')
                    name_text = font_small.render(pet_name, True, TEXT_COLOR); name_rect = name_text.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + 15); screen.blit(name_text, name_rect)
                    button_y_start = name_rect.bottom + 15
                    feed_btn_rect = pygame.Rect(panel_rect.x + 20, button_y_start, panel_w - 40, 50)
                    play_btn_rect = pygame.Rect(panel_rect.x + 20, feed_btn_rect.bottom + 10, panel_w - 40, 50)
                    pygame.draw.rect(screen, BUTTON_HOVER_COLOR if feed_btn_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR, feed_btn_rect, 0, 8)
                    feed_text = font_info.render("Feed", True, WHITE); screen.blit(feed_text, feed_text.get_rect(center=feed_btn_rect.center))
                    pygame.draw.rect(screen, BUTTON_HOVER_COLOR if play_btn_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR, play_btn_rect, 0, 8)
                    play_text = font_info.render("Play", True, WHITE); screen.blit(play_text, play_text.get_rect(center=play_btn_rect.center))
                    clickable_interaction_rects['feed_btn'] = feed_btn_rect; clickable_interaction_rects['play_btn'] = play_btn_rect
                else:
                    items_to_show = []; title = ""
                    if interaction_submenu == 'feed': items_to_show = [(k, v) for k, v in player_inventory.items.items() if item_data.get(k, {}).get('category') == 'food']; title = "CHOOSE FOOD"
                    elif interaction_submenu == 'play': items_to_show = [(k, v) for k, v in player_inventory.items.items() if item_data.get(k, {}).get('category') == 'toy']; title = "CHOOSE TOY"
                    panel_w, panel_h = 600, 400
                    panel_rect = pygame.Rect(0, 0, panel_w, panel_h); panel_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                    pygame.draw.rect(screen, PANEL_FILL_COLOR, panel_rect, 0, 15); pygame.draw.rect(screen, PANEL_BORDER_COLOR, panel_rect, 6, 15)
                    title_text = font.render(title, True, TEXT_COLOR); screen.blit(title_text, title_text.get_rect(centerx=panel_rect.centerx, top=panel_rect.top+20))
                    if not items_to_show: none_text = font_small.render("You have none!", True, TEXT_COLOR); screen.blit(none_text, none_text.get_rect(center=panel_rect.center))
                    else:
                        ITEM_COLS, ITEM_BOX_SIZE, ITEM_PADDING = 4, 100, 15
                        for i, (item_id, qty) in enumerate(items_to_show):
                            r,c=divmod(i, ITEM_COLS); box_x=panel_rect.left+50+c*(ITEM_BOX_SIZE+ITEM_PADDING); box_y=panel_rect.top+80+r*(ITEM_BOX_SIZE+ITEM_PADDING)
                            item_box_rect=pygame.Rect(box_x,box_y,ITEM_BOX_SIZE,ITEM_BOX_SIZE); pygame.draw.rect(screen,LOCKED_SLOT_COLOR,item_box_rect,0,8)
                            if item_img := item_images.get(item_id):
                                scaled_img = pygame.transform.scale(item_img, (ITEM_BOX_SIZE-20, ITEM_BOX_SIZE-20))
                                screen.blit(scaled_img, scaled_img.get_rect(center=item_box_rect.center))
                            qty_text = font_info.render(f"x{qty}",True,TEXT_COLOR); screen.blit(qty_text, qty_text.get_rect(right=item_box_rect.right-5, bottom=item_box_rect.bottom-5))
                            pygame.draw.rect(screen, BUTTON_HOVER_COLOR if item_box_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR, item_box_rect, 4, 8)
                            clickable_interaction_rects[item_id] = item_box_rect
                    cancel_btn_rect = pygame.Rect(0,0,150,50); cancel_btn_rect.midbottom = (panel_rect.centerx, panel_rect.bottom - 20)
                    pygame.draw.rect(screen, BUTTON_HOVER_COLOR if cancel_btn_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR, cancel_btn_rect, 0, 8)
                    cancel_text = font.render("Cancel", True, WHITE); screen.blit(cancel_text, cancel_text.get_rect(center=cancel_btn_rect.center))
                    clickable_interaction_rects['cancel_interaction'] = cancel_btn_rect
            
        elif scene == "shop_menu":
            shop_manager.update(); shopkeeper.update(dt)
            overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            
            shop_items_all = list(shop_manager.current_stock.items())
            COLS, ROWS = 4, 2; BOX_SIZE, PADDING = 150, 20
            TABLE_W = (COLS * BOX_SIZE) + ((COLS-1)*PADDING); TABLE_H=(ROWS * (BOX_SIZE+PADDING))-PADDING
            TABLE_X = (SCREEN_WIDTH - TABLE_W)//2; TABLE_Y=max(150, (SCREEN_HEIGHT - TABLE_H)//2 + 50)
            container_rect = pygame.Rect(TABLE_X-PADDING, TABLE_Y-PADDING-80,TABLE_W+2*PADDING,TABLE_H+2*PADDING+80)

            shopkeeper.draw(screen,(container_rect.left-100,container_rect.centery+20),"IdleSouth")
            pygame.draw.rect(screen,PANEL_FILL_COLOR,container_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,container_rect,6,15)
            quote_text = font.render("WHAT DO YOU WANT TO BUY?", True, WHITE); quote_rect = quote_text.get_rect(center=(container_rect.centerx, container_rect.top + 55)); screen.blit(quote_text, quote_rect)
            time_left = int(shop_manager.restock_interval - (time.time() - shop_manager.last_restock_time)); minutes, seconds = divmod(time_left, 60)
            restock_text = font_info.render(f"RESTOCK IN: {minutes:02d}:{seconds:02d}", True, WHITE); restock_rect = restock_text.get_rect(midbottom=(quote_rect.centerx + 120, quote_rect.top + 5)); screen.blit(restock_text, restock_rect)
            
            hovered_item_id = None
            for i,(item_id,stock_info) in enumerate(shop_items_all):
                r,c=divmod(i,COLS); box_x=TABLE_X+c*(BOX_SIZE+PADDING); box_y=TABLE_Y+r*(BOX_SIZE+PADDING); box_rect=pygame.Rect(box_x,box_y,BOX_SIZE,BOX_SIZE)
                if box_rect.collidepoint(mouse_pos): hovered_item_id = item_id
                pygame.draw.rect(screen,(230,200,130),box_rect,0,10)
                if img_to_draw := item_images.get(item_id): screen.blit(img_to_draw,img_to_draw.get_rect(center=(box_rect.centerx,box_rect.centery-10)))
                
                price_text=font_info.render(str(stock_info["price"]),True,TEXT_COLOR); price_icon=pygame.transform.scale(coin_img,(24,24)); total_w=price_text.get_width()+price_icon.get_width()+5; start_x_price=box_rect.centerx-total_w/2
                screen.blit(price_icon,(start_x_price,box_rect.bottom-35)); screen.blit(price_text,(start_x_price+price_icon.get_width()+5,box_rect.bottom-35))
                
                if stock_info["quantity"] > 0:
                    qty_text = font_info.render(f"x{stock_info['quantity']}", True, TEXT_COLOR)
                    screen.blit(qty_text, qty_text.get_rect(topright=(box_rect.right-10, box_rect.top+5)))
                else:
                    scaled_sold_out = pygame.transform.scale(sold_out_img, (BOX_SIZE-20, BOX_SIZE-20))
                    screen.blit(scaled_sold_out, scaled_sold_out.get_rect(center=box_rect.center))

                pygame.draw.rect(screen,BUTTON_HOVER_COLOR if box_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR,box_rect,4,10)
            
            if hovered_item_id and (data := item_data.get(hovered_item_id)):
                info_panel_rect = pygame.Rect(shopkeeper.get_rect().left - 370, shopkeeper.get_rect().centery - 200, 350, 400)
                pygame.draw.rect(screen, PANEL_FILL_COLOR, info_panel_rect, 0, 15); pygame.draw.rect(screen, PANEL_BORDER_COLOR, info_panel_rect, 4, 15)
                name_text=font_small.render(data['name'],True,TEXT_COLOR); name_rect=name_text.get_rect(centerx=info_panel_rect.centerx,top=info_panel_rect.top+20); screen.blit(name_text,name_rect)
                if img_to_draw := item_images.get(hovered_item_id):
                    img_rect=img_to_draw.get_rect(centerx=info_panel_rect.centerx,top=name_rect.bottom+10); screen.blit(img_to_draw,img_rect); desc_y_start=img_rect.bottom+15
                else: desc_y_start=name_rect.bottom+15
                
                lines=[]; current_line=""
                for word in data['description'].split(' '):
                    if font_info.size(current_line+word+" ")[0]<info_panel_rect.width-40: current_line+=word+" "
                    else: lines.append(current_line); current_line=word+" "
                lines.append(current_line)
                
                current_y = desc_y_start
                for line in lines:
                    screen.blit(font_info.render(line,True,TEXT_COLOR),(info_panel_rect.left+20, current_y))
                    current_y += 28
                
                if 'effects' in data.get('data', {}):
                    draw_item_effects(screen, data['data']['effects'], (info_panel_rect.left + 20, current_y + 10))

            if shop_message and time.time() - shop_message_timer < 2.5:
                is_success = "successful" in shop_message.lower(); message_font = font if is_success else font_small; message_color = (0, 100, 0) if is_success else (220, 20, 20)
                msg_surf = message_font.render(shop_message, True, message_color); msg_rect = msg_surf.get_rect(center=(container_rect.centerx, container_rect.bottom + 50)); bg_rect = msg_rect.inflate(20, 10)
                bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA); bg_surf.fill((0, 0, 0, 160)); border_color = (0, 50, 0, 180) if is_success else (50, 0, 0, 180)
                pygame.draw.rect(bg_surf, border_color, bg_surf.get_rect(), 3, 4); screen.blit(bg_surf, bg_rect); screen.blit(msg_surf, msg_rect)
            else: shop_message = ""
            exit_text=font_small.render("Press 'E' or 'Esc' to exit.",True,GRAY); screen.blit(exit_text,(SCREEN_WIDTH//2-exit_text.get_width()//2,SCREEN_HEIGHT-100))
        elif scene == "home_menu" or scene == "incubator_egg_select":
            if incubator_manager: incubator_manager.draw(screen, mouse_pos)
            exit_text=font_small.render("Press 'Esc' to return.",True,GRAY); screen.blit(exit_text,(SCREEN_WIDTH//2-exit_text.get_width()//2,SCREEN_HEIGHT-100))
            if scene == "incubator_egg_select":
                select_panel_rect = pygame.Rect(0,0,800, 500); select_panel_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
                pygame.draw.rect(screen, PANEL_FILL_COLOR, select_panel_rect, 0, 15); pygame.draw.rect(screen, PANEL_BORDER_COLOR, select_panel_rect, 6, 15)
                title_text = font.render("SELECT AN EGG", True, TEXT_COLOR); screen.blit(title_text, title_text.get_rect(centerx=select_panel_rect.centerx, top=select_panel_rect.top + 20))
                player_eggs = player_inventory.get_eggs()
                if not player_eggs:
                    no_eggs_text = font_small.render("You have no eggs!", True, TEXT_COLOR); screen.blit(no_eggs_text, no_eggs_text.get_rect(center=select_panel_rect.center))
                else:
                    EGG_COLS, EGG_BOX_SIZE, EGG_PADDING = 4, 120, 20
                    for i, (egg_id, qty) in enumerate(player_eggs):
                        r,c=divmod(i, EGG_COLS); box_x = select_panel_rect.left + 50 + c*(EGG_BOX_SIZE+EGG_PADDING); box_y = select_panel_rect.top + 100 + r*(EGG_BOX_SIZE+EGG_PADDING)
                        egg_box_rect = pygame.Rect(box_x, box_y, EGG_BOX_SIZE, EGG_BOX_SIZE); pygame.draw.rect(screen, (230,200,130), egg_box_rect, 0, 8)
                        if egg_img := item_images.get(egg_id): screen.blit(pygame.transform.scale(egg_img, (EGG_BOX_SIZE-20, EGG_BOX_SIZE-20)), egg_img.get_rect(center=egg_box_rect.center))
                        qty_text = font_info.render(f"x{qty}",True,TEXT_COLOR); screen.blit(qty_text, (egg_box_rect.right-qty_text.get_width()-5, egg_box_rect.bottom-qty_text.get_height()-5))
                        pygame.draw.rect(screen, BUTTON_HOVER_COLOR if egg_box_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR, egg_box_rect, 4, 8)
        elif scene == "inventory_menu":
            overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            main_panel_rect=pygame.Rect(100,100,SCREEN_WIDTH*0.6,SCREEN_HEIGHT-200); pygame.draw.rect(screen,PANEL_FILL_COLOR,main_panel_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,main_panel_rect,6,15)
            info_panel_rect=pygame.Rect(main_panel_rect.right+20,100,SCREEN_WIDTH-main_panel_rect.right-120,SCREEN_HEIGHT-200); pygame.draw.rect(screen,PANEL_FILL_COLOR,info_panel_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,info_panel_rect,6,15)
            
            title_text = font.render("INVENTORY", True, TEXT_COLOR)
            screen.blit(title_text, title_text.get_rect(centerx=main_panel_rect.centerx, top=main_panel_rect.top + 30))

            INV_COLS,INV_ROWS,INV_BOX_SIZE,INV_PADDING=10,5,80,10; INV_GRID_W=INV_COLS*(INV_BOX_SIZE+INV_PADDING)-INV_PADDING; INV_GRID_X=main_panel_rect.left+(main_panel_rect.width-INV_GRID_W)//2; INV_GRID_Y=main_panel_rect.top+80+50
            
            items_in_inv=player_inventory.get_all_items()
            for i in range(INV_COLS*INV_ROWS):
                r,c=divmod(i,INV_COLS); box_x=INV_GRID_X+c*(INV_BOX_SIZE+INV_PADDING); box_y=INV_GRID_Y+r*(INV_BOX_SIZE+INV_PADDING); box_rect=pygame.Rect(box_x,box_y,INV_BOX_SIZE,INV_BOX_SIZE); pygame.draw.rect(screen,LOCKED_SLOT_COLOR,box_rect,0,8)
                is_selected = False
                if i < len(items_in_inv):
                    item_id, qty = items_in_inv[i]
                    is_selected = (inventory_selected_item_id == item_id)
                    if item_img := item_images.get(item_id): screen.blit(pygame.transform.scale(item_img,(INV_BOX_SIZE-10,INV_BOX_SIZE-10)),pygame.transform.scale(item_img,(INV_BOX_SIZE-10,INV_BOX_SIZE-10)).get_rect(center=box_rect.center))
                    if qty > 1:
                        qty_text=font_info.render(str(qty),True,WHITE); qty_bg=pygame.Surface((qty_text.get_width()+4,qty_text.get_height()),pygame.SRCALPHA); qty_bg.fill((0,0,0,150))
                        screen.blit(qty_bg,(box_rect.right-qty_bg.get_width()-2,box_rect.bottom-qty_bg.get_height()-2)); screen.blit(qty_text,(box_rect.right-qty_text.get_width()-4,box_rect.bottom-qty_text.get_height()-4))
                pygame.draw.rect(screen,BUTTON_HOVER_COLOR if is_selected else PANEL_BORDER_COLOR,box_rect,3 if is_selected else 2,8)
            
            if inventory_selected_item_id and inventory_selected_item_id in item_data:
                data=item_data[inventory_selected_item_id]; name_text=font_small.render(data['name'],True,TEXT_COLOR); name_rect=name_text.get_rect(centerx=info_panel_rect.centerx,top=info_panel_rect.top+30); screen.blit(name_text,name_rect)
                if img_to_draw := item_images.get(inventory_selected_item_id):
                    img_rect=img_to_draw.get_rect(centerx=info_panel_rect.centerx,top=name_rect.bottom+20); screen.blit(img_to_draw,img_rect); desc_y_start=img_rect.bottom+20
                else: desc_y_start=name_rect.bottom+20
                
                lines=[]; current_line=""
                for word in data['description'].split(' '):
                    if font_info.size(current_line+word+" ")[0]<info_panel_rect.width-40: current_line+=word+" "
                    else: lines.append(current_line); current_line=word+" "
                lines.append(current_line)
                
                current_y = desc_y_start
                for line in lines:
                    screen.blit(font_info.render(line,True,TEXT_COLOR),(info_panel_rect.left+20, current_y))
                    current_y += 28

                if 'effects' in data.get('data', {}):
                    draw_item_effects(screen, data['data']['effects'], (info_panel_rect.left + 20, current_y + 10))
            
            exit_text=font_small.render("Press 'E' or 'Esc' to exit.",True,GRAY); screen.blit(exit_text,(SCREEN_WIDTH//2-exit_text.get_width()//2,SCREEN_HEIGHT-60))
        
        elif scene == "pet_management_menu":
            overlay=pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            list_panel_rect=pygame.Rect(100,100,400,SCREEN_HEIGHT-200); pygame.draw.rect(screen,PANEL_FILL_COLOR,list_panel_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,list_panel_rect,6,15)
            info_panel_rect=pygame.Rect(list_panel_rect.right+20,100,SCREEN_WIDTH-list_panel_rect.right-120,SCREEN_HEIGHT-200); pygame.draw.rect(screen,PANEL_FILL_COLOR,info_panel_rect,0,15); pygame.draw.rect(screen,PANEL_BORDER_COLOR,info_panel_rect,6,15)
            
            unlocked_slots = profiles[selected_profile_idx]['unlocked_pet_slots']
            title_text = font.render("My Pets", True, TEXT_COLOR); screen.blit(title_text, title_text.get_rect(centerx=list_panel_rect.centerx, top=list_panel_rect.top + 20))
            slot_count_text = font_small.render(f"Active: {len(active_pets)} / {unlocked_slots}", True, TEXT_COLOR); screen.blit(slot_count_text, slot_count_text.get_rect(centerx=list_panel_rect.centerx, top=list_panel_rect.top + 65))

            pets_in_inv = player_inventory.get_all_pets()
            ROW_H, PADDING_Y = 80, 10
            list_content_rect = list_panel_rect.inflate(-40, -220); list_content_rect.top = list_panel_rect.top + 120
            total_content_height = len(pets_in_inv) * (ROW_H + PADDING_Y)
            max_scroll = max(0, total_content_height - list_content_rect.height)
            scrollbar_track_rect = pygame.Rect(list_panel_rect.right - 25, list_content_rect.top, 15, list_content_rect.height)
            
            # --- SCROLLBAR DRAG UPDATE LOGIC ---
            if is_dragging_scrollbar and max_scroll > 0:
                visible_ratio = list_content_rect.height / total_content_height
                handle_height = max(20, scrollbar_track_rect.height * visible_ratio)
                scrollable_track_space = scrollbar_track_rect.height - handle_height
                
                # Calculate the new handle position based on the mouse
                new_handle_y = mouse_pos[1] - scrollbar_drag_offset_y
                # Get the handle's position relative to the track's top
                relative_y = new_handle_y - scrollbar_track_rect.y
                # Calculate the scroll percentage from the relative position
                scroll_percent = relative_y / scrollable_track_space if scrollable_track_space > 0 else 0
                # Update the main scroll variable
                pet_list_scroll_y = scroll_percent * max_scroll

            pet_list_scroll_y = max(0, min(pet_list_scroll_y, max_scroll))

            list_surface_container = screen.subsurface(list_content_rect)
            list_surface_container.fill(PANEL_FILL_COLOR)
            
            for i, pet in enumerate(pets_in_inv):
                row_y_pos = i * (ROW_H + PADDING_Y) - pet_list_scroll_y
                if row_y_pos + ROW_H > 0 and row_y_pos < list_content_rect.height:
                    pet_row_rect = pygame.Rect(0, row_y_pos, list_content_rect.width, ROW_H)
                    is_selected = pet_management_selected_instance_id == pet['instance_id']
                    row_color = LOCKED_SLOT_COLOR if not is_selected else (240, 210, 140)
                    pygame.draw.rect(list_surface_container, row_color, pet_row_rect, 0, 8)
                    if pet_icon := pet_icons.get(pet['pet_id']): list_surface_container.blit(pet_icon, pet_icon.get_rect(centery=pet_row_rect.centery, left=pet_row_rect.left + 10))
                    pet_name_text = font_small.render(pet['name'], True, TEXT_COLOR); list_surface_container.blit(pet_name_text, pet_name_text.get_rect(centery=pet_row_rect.centery, left=pet_row_rect.left + 90))
                    pygame.draw.rect(list_surface_container, BUTTON_HOVER_COLOR if is_selected else PANEL_BORDER_COLOR, pet_row_rect, 3 if is_selected else 2, 8)

            if max_scroll > 0:
                pygame.draw.rect(screen, LOCKED_SLOT_COLOR, scrollbar_track_rect, 0, 8)
                visible_ratio = list_content_rect.height / total_content_height
                handle_height = max(20, scrollbar_track_rect.height * visible_ratio)
                scroll_ratio = pet_list_scroll_y / max_scroll if max_scroll > 0 else 0
                handle_y = scrollbar_track_rect.top + scroll_ratio * (scrollbar_track_rect.height - handle_height)
                
                # Update the handle rect for the next frame's event check
                scrollbar_handle_rect.update(scrollbar_track_rect.left, handle_y, scrollbar_track_rect.width, handle_height)
                
                pygame.draw.rect(screen, GRAY, scrollbar_handle_rect, 0, 8)
            else:
                scrollbar_handle_rect.update(0,0,0,0) # Reset if not visible
            
            if unlocked_slots < MAX_PET_SLOTS:
                price_index = unlocked_slots - 5 
                if 0 <= price_index < len(PET_SLOT_UNLOCK_PRICES):
                    unlock_button_rect = pygame.Rect(list_panel_rect.left + 20, list_panel_rect.bottom - 70, list_panel_rect.width - 40, 50)
                    pygame.draw.rect(screen, BUTTON_HOVER_COLOR if unlock_button_rect.collidepoint(mouse_pos) else PANEL_BORDER_COLOR, unlock_button_rect, 0, 8)
                    price = PET_SLOT_UNLOCK_PRICES[price_index]
                    btn_text = font_info.render(f"Unlock Slot: {price}", True, WHITE)
                    btn_text_rect = btn_text.get_rect(center=unlock_button_rect.center)
                    coin_icon_small = pygame.transform.scale(coin_img,(24,24))
                    
                    total_width = btn_text.get_width() + coin_icon_small.get_width() + 10
                    text_x = unlock_button_rect.centerx - (total_width / 2)
                    icon_x = text_x + btn_text.get_width() + 10
                    
                    screen.blit(btn_text, (text_x, btn_text_rect.y))
                    screen.blit(coin_icon_small, (icon_x, unlock_button_rect.centery - 12))


            selected_pet_instance = player_inventory.get_pet_by_instance_id(pet_management_selected_instance_id)
            if selected_pet_instance:
                pet_def = pet_data[selected_pet_instance['pet_id']]; pet_name = selected_pet_instance.get('name', pet_def['name'])
                display_name = f"{pet_name} ({pet_def['name']})"; name_text=font_small.render(display_name,True,TEXT_COLOR); name_rect=name_text.get_rect(centerx=info_panel_rect.centerx,top=info_panel_rect.top+30); screen.blit(name_text,name_rect)
                if icon := pet_icons.get(selected_pet_instance['pet_id']):
                    big_icon = pygame.transform.scale(icon, (128, 128)); icon_rect = big_icon.get_rect(centerx=info_panel_rect.centerx, top=name_rect.bottom + 20)
                    screen.blit(big_icon, icon_rect); status_bar_y = icon_rect.bottom + 30
                else: status_bar_y = name_rect.bottom + 30
                ThuCung.draw_status_bars(screen, selected_pet_instance, (info_panel_rect.left + 40, status_bar_y), width=info_panel_rect.width - 80)
                
                if current_map == "pet_area":
                    already_out = any(p.instance_data['instance_id'] == pet_management_selected_instance_id for p in active_pets)
                    slots_full = len(active_pets) >= unlocked_slots
                    btn_rect = pygame.Rect(0,0,250, 60); btn_rect.midbottom = (info_panel_rect.centerx, info_panel_rect.bottom - 30)
                    if already_out:
                        btn_text, btn_color = "Bring Back", PANEL_BORDER_COLOR
                    elif slots_full:
                        btn_text, btn_color = "Slots Full", DISABLED_COLOR
                    else:
                        btn_text, btn_color = "Bring Out", PANEL_BORDER_COLOR
                    
                    pygame.draw.rect(screen, BUTTON_HOVER_COLOR if btn_rect.collidepoint(mouse_pos) and not (not already_out and slots_full) else btn_color, btn_rect, 0, 8)
                    text_surf = font.render(btn_text, True, WHITE); screen.blit(text_surf, text_surf.get_rect(center=btn_rect.center))

            else:
                prompt_text = font_small.render("Select a pet from the list.", True, GRAY)
                screen.blit(prompt_text, prompt_text.get_rect(center=info_panel_rect.center))

            if pet_menu_message and time.time() - pet_menu_message_timer < 2:
                msg_surf = font_small.render(pet_menu_message, True, WHITE)
                msg_rect = msg_surf.get_rect(midbottom=(list_panel_rect.centerx, list_panel_rect.bottom - 80))
                screen.blit(msg_surf, msg_rect)
            else: pet_menu_message = ""

            exit_text=font_small.render("Press 'Esc' to exit.",True,GRAY); screen.blit(exit_text,(SCREEN_WIDTH//2-exit_text.get_width()//2,SCREEN_HEIGHT-60))
            
        elif scene == "storage_menu":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180)); screen.blit(overlay, (0, 0))
            
            # Define UI layout and draw panels
            PANEL_MARGIN, TOP_MARGIN, BOTTOM_MARGIN = 150, 120, 100
            PANEL_Y, PANEL_HEIGHT = TOP_MARGIN, SCREEN_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN
            PLAYER_PANEL_W = (SCREEN_WIDTH / 2) - PANEL_MARGIN
            PLAYER_PANEL_RECT = pygame.Rect(50, PANEL_Y, PLAYER_PANEL_W, PANEL_HEIGHT)
            GLOBAL_PANEL_RECT = pygame.Rect(SCREEN_WIDTH - 50 - PLAYER_PANEL_W, PANEL_Y, PLAYER_PANEL_W, PANEL_HEIGHT)
            
            pygame.draw.rect(screen, PANEL_FILL_COLOR, PLAYER_PANEL_RECT, 0, 15); pygame.draw.rect(screen, PANEL_BORDER_COLOR, PLAYER_PANEL_RECT, 6, 15)
            pygame.draw.rect(screen, PANEL_FILL_COLOR, GLOBAL_PANEL_RECT, 0, 15); pygame.draw.rect(screen, PANEL_BORDER_COLOR, GLOBAL_PANEL_RECT, 6, 15)
            
            player_title = font.render("Your Profile", True, TEXT_COLOR); screen.blit(player_title, player_title.get_rect(centerx=PLAYER_PANEL_RECT.centerx, top=PLAYER_PANEL_RECT.top + 20))
            global_title = font.render("Shared Storage", True, TEXT_COLOR); screen.blit(global_title, global_title.get_rect(centerx=GLOBAL_PANEL_RECT.centerx, top=GLOBAL_PANEL_RECT.top + 20))

            # Draw tabs
            items_tab_rect = pygame.Rect(SCREEN_WIDTH/2 - 220, 50, 200, 50)
            pets_tab_rect = pygame.Rect(SCREEN_WIDTH/2 + 20, 50, 200, 50)
            pygame.draw.rect(screen, PANEL_BORDER_COLOR if storage_scene_tab == 'items' else LOCKED_SLOT_COLOR, items_tab_rect, 0, 8); pygame.draw.rect(screen, PANEL_BORDER_COLOR, items_tab_rect, 4, 8)
            pygame.draw.rect(screen, PANEL_BORDER_COLOR if storage_scene_tab == 'pets' else LOCKED_SLOT_COLOR, pets_tab_rect, 0, 8); pygame.draw.rect(screen, PANEL_BORDER_COLOR, pets_tab_rect, 4, 8)
            items_text = font.render("Items", True, WHITE); screen.blit(items_text, items_text.get_rect(center=items_tab_rect.center))
            pets_text = font.render("Pets", True, WHITE); screen.blit(pets_text, pets_text.get_rect(center=pets_tab_rect.center))

            # Helper to draw one list (player or global)
            def draw_list(panel_rect, is_player_list, scroll_y_ref, selected_idx_ref):
                content_rect = panel_rect.inflate(-40, -120); content_rect.top = panel_rect.top + 80
                list_surface = screen.subsurface(content_rect); list_surface.fill(PANEL_FILL_COLOR)
                
                data_list = []
                if storage_scene_tab == 'items':
                    source = player_inventory.items if is_player_list else global_storage_data['items']
                    data_list = sorted(source.items())
                else: # pets
                    source = player_inventory.pets if is_player_list else global_storage_data['pets']
                    data_list = sorted(source, key=lambda p: p['instance_id'])
                
                total_h = 0
                if storage_scene_tab == 'items': total_h = (len(data_list) // 4 + 1) * 110 if data_list else 0
                else: total_h = len(data_list) * 90
                
                max_scroll = max(0, total_h - content_rect.height)
                scroll_y_ref[0] = max(0, min(scroll_y_ref[0], max_scroll))
                
                newly_selected_idx = None
                
                if storage_scene_tab == 'items':
                    COLS, BOX_SIZE, PADDING = 4, 100, 10
                    for i, (item_id, qty) in enumerate(data_list):
                        r,c = divmod(i, COLS)
                        box_rect = pygame.Rect(20 + c*(BOX_SIZE+PADDING), 20 + r*(BOX_SIZE+PADDING) - scroll_y_ref[0], BOX_SIZE, BOX_SIZE)
                        is_selected = selected_idx_ref == i
                        pygame.draw.rect(list_surface, LOCKED_SLOT_COLOR, box_rect, 0, 8)
                        if img := item_images.get(item_id): list_surface.blit(pygame.transform.scale(img, (80, 80)), img.get_rect(center=box_rect.center))
                        qty_text=font_info.render(f"x{qty}",True,TEXT_COLOR); list_surface.blit(qty_text, qty_text.get_rect(bottomright=box_rect.bottomright))
                        pygame.draw.rect(list_surface, BUTTON_HOVER_COLOR if is_selected else PANEL_BORDER_COLOR, box_rect, 4 if is_selected else 2, 8)
                        
                        abs_box_rect = box_rect.move(content_rect.topleft)
                        if pygame.mouse.get_pressed()[0] and abs_box_rect.collidepoint(mouse_pos):
                            newly_selected_idx = i
                else: # pets
                    ROW_H, PADDING_Y = 80, 10
                    for i, pet in enumerate(data_list):
                        row_rect = pygame.Rect(10, 10 + i*(ROW_H+PADDING_Y) - scroll_y_ref[0], content_rect.width-20, ROW_H)
                        is_selected = selected_idx_ref == i
                        is_active = is_player_list and any(p.instance_data['instance_id'] == pet['instance_id'] for p in active_pets)
                        color = (200,190,120) if is_active else LOCKED_SLOT_COLOR
                        pygame.draw.rect(list_surface, color, row_rect, 0, 8)
                        if icon := pet_icons.get(pet['pet_id']): list_surface.blit(icon, icon.get_rect(centery=row_rect.centery, left=row_rect.left+10))
                        name_text = font_small.render(pet['name'], True, TEXT_COLOR); list_surface.blit(name_text, name_text.get_rect(centery=row_rect.centery, left=row_rect.left+90))
                        pygame.draw.rect(list_surface, BUTTON_HOVER_COLOR if is_selected else PANEL_BORDER_COLOR, row_rect, 4 if is_selected else 2, 8)

                        abs_row_rect = row_rect.move(content_rect.topleft)
                        if pygame.mouse.get_pressed()[0] and abs_row_rect.collidepoint(mouse_pos):
                           newly_selected_idx = i

                return newly_selected_idx

            # Use mutable lists for scroll and selection to allow modification inside the function
            player_scroll_ref = [storage_player_scroll_y]; global_scroll_ref = [storage_global_scroll_y]
            player_sel = draw_list(PLAYER_PANEL_RECT, True, player_scroll_ref, storage_selected_player_idx)
            global_sel = draw_list(GLOBAL_PANEL_RECT, False, global_scroll_ref, storage_selected_global_idx)
            storage_player_scroll_y, storage_global_scroll_y = player_scroll_ref[0], global_scroll_ref[0]
            
            # Update selection state (check for mouse down event to avoid selecting while dragging)
            if pygame.mouse.get_pressed()[0]:
                if player_sel is not None: storage_selected_player_idx = player_sel; storage_selected_global_idx = None
                if global_sel is not None: storage_selected_global_idx = global_sel; storage_selected_player_idx = None

            # Draw transfer buttons
            store_button_rect = pygame.Rect(SCREEN_WIDTH/2 - 40, SCREEN_HEIGHT/2 - 60, 80, 80)
            retrieve_button_rect = pygame.Rect(SCREEN_WIDTH/2 - 40, SCREEN_HEIGHT/2 + 40, 80, 80)
            
            can_store = storage_selected_player_idx is not None
            if can_store and storage_scene_tab == 'pets': # Extra check for active pets
                pet_to_move = player_inventory.get_all_pets()[storage_selected_player_idx]
                if any(p.instance_data['instance_id'] == pet_to_move['instance_id'] for p in active_pets):
                    can_store = False

            # Draw Store button (Player -> Global, points right ->)
            store_color = PANEL_BORDER_COLOR if can_store else DISABLED_COLOR
            pygame.draw.rect(screen, store_color, store_button_rect, 0, 8)
            pygame.draw.polygon(screen, WHITE, [(store_button_rect.right-20, store_button_rect.centery), (store_button_rect.left+20, store_button_rect.top+20), (store_button_rect.left+20, store_button_rect.bottom-20)])
            
            can_retrieve = storage_selected_global_idx is not None
            # Draw Retrieve button (Global -> Player, points left <-)
            retrieve_color = PANEL_BORDER_COLOR if can_retrieve else DISABLED_COLOR
            pygame.draw.rect(screen, retrieve_color, retrieve_button_rect, 0, 8)
            pygame.draw.polygon(screen, WHITE, [(retrieve_button_rect.left+20, retrieve_button_rect.centery), (retrieve_button_rect.right-20, retrieve_button_rect.top+20), (retrieve_button_rect.right-20, retrieve_button_rect.bottom-20)])

            # Message display
            if storage_message and time.time() - storage_message_timer < 2.5:
                msg_surf = font_small.render(storage_message, True, WHITE)
                msg_rect = msg_surf.get_rect(midbottom=(SCREEN_WIDTH/2, SCREEN_HEIGHT-30))
                screen.blit(msg_surf, msg_rect)
            else: storage_message = ""

            exit_text=font_small.render("Press 'E' or 'Esc' to exit.",True,GRAY); screen.blit(exit_text,(SCREEN_WIDTH//2-exit_text.get_width()//2,SCREEN_HEIGHT-60))

    ### CHANGED BLOCK START ###
    # --- Draw Global Overlays (like the Escape Menu) on top of everything else ---
    if confirming_escape:
        # Draw a semi-transparent overlay
        overlay_dark = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay_dark.fill((0, 0, 0, 120))
        screen.blit(overlay_dark, (0, 0))
        
        # Draw the dialog box
        pygame.draw.rect(screen, PANEL_FILL_COLOR, dialog_rect, 0, 10)
        pygame.draw.rect(screen, PANEL_BORDER_COLOR, dialog_rect, 6, 10)
        
        # Draw the text and buttons
        q_text = font_small.render("Do you want to escape?", True, TEXT_COLOR)
        screen.blit(q_text, q_text.get_rect(center=(dialog_rect.centerx, dialog_rect.top + 60)))
        for r, t in [(yes_button_rect, "Yes"), (no_button_rect, "No")]:
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR if r.collidepoint(mouse_pos) else PANEL_BORDER_COLOR, r, 0, 8)
            screen.blit(font.render(t, True, WHITE), font.render(t, True, WHITE).get_rect(center=r.center))
    ### CHANGED BLOCK END ###
    
    if game_currency and scene not in ["hatching_animation", "pet_naming"]: game_currency.draw(screen, show_time=(scene=="play"))
    pygame.display.update()