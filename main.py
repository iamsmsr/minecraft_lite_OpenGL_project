from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# Animation variables
lang = 0       # Leg angle for walking animation
ldir = 1       # Direction of leg movement
walk = False   # Walking state flag
wt = 0         # Walk time counter

# Arm animation variables
a_ang, a_y, a_z, a_anim, fall = 70, -7, 25, False, False


def rand_x():
    return random.choice([
        random.randint(-580, -250), 
        random.randint(250, 680) ])
def rand_y():
    return random.choice([
        random.randint(-580, -250), 
        random.randint(250, 580) ])   
enm_pos = []
enmt = random.randint(50, 100)
num_enm = random.randint(3, 7) 

# Camera-related variables
camera_pos = (0, 300, 300)
fovY = 120  # Field of view
GRID_LENGTH = 600  # Length of grid lines
rand_var = 423


r, g, b = 0, 0, 0

# globe
face_dir = 0
disp = 0
px = 0
py = 0
pz = 50
aerial = False
GRAVITY = 0.009
JUMP_POWER = 1.2
velocity_z = 0
blocks = []
ordered_blocks = []
fpp = False
look_height = 50
avail_blocks = 20
is_sun = True  
TOTAL_CATTLE = 5
TOTAL_TREE = 5
dead = False
food_inv = 0

# Sky elements
stars = []  
stars_initialized = False
clouds = []
clouds_initialized = False

# Game objects
cattle = []
cattle_kill_count = 0

# Player stats
player_health = 1  
MAX_HEALTH = 5 
player_food = 0    # tree logs


def draw_heart(x, y, is_full=True):
    size = 20  # Size of heart

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Draw heart shape
    if is_full:
        # Full heart (red)
        glColor3f(1.0, 0.0, 0.0)
    else:
        # Empty heart (dark gray)
        glColor3f(0.3, 0.3, 0.3)
    
    glBegin(GL_QUADS)

    glVertex2f(x, y)
    glVertex2f(x + size, y)
    glVertex2f(x + size, y + size)
    glVertex2f(x, y + size)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_food(x, y, is_full=True):
    size = 20  # Size of food icon
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw chicken leg
    if is_full:
        # Full food (brown)
        glColor3f(0.6, 0.3, 0.1)
    else:
        # Empty food (dark gray)
        glColor3f(0.3, 0.3, 0.3)
    
    glBegin(GL_QUADS)
    # Simple rectangle 
    glVertex2f(x, y)
    glVertex2f(x + size, y)
    glVertex2f(x + size, y + size)
    glVertex2f(x, y + size)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_hud():

    for i in range(MAX_HEALTH):  
        is_full = i < player_health
        draw_heart(20 + i * 30, 700, is_full)
    
    # for i in range(5): 
    #     is_full = i < player_food
    #     draw_food(900 - i * 30, 700, is_full)
    global avail_blocks
    draw_text(800, 710, f"Blocks: {avail_blocks}")
    draw_text(800, 690, f"Meat: {food_inv}")


class Cattle:
    def __init__(self, x, y, z):
        global r, g, b
        self.x = x
        self.y = y
        self.z = z
        self.rotation = random.randint(0, 3) * 90  
    
    def draw(self):
        global r, g, b
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z + 25)  # Position at block center
        glRotatef(self.rotation, 0, 0, 1)  # Apply rotation
        
        # Legs
        leg_positions = [
            (-15, -25, -20),  # Back left
            (15, -25, -20),   # Back right
            (-15, 25, -20),   # Front left
            (15, 25, -20)     # Front right
        ]
        
        for pos in leg_positions:
            glPushMatrix()
            glColor3f(r+0.5, g+0.25, b+0.15)  # Dark brown
            glTranslatef(pos[0], pos[1], pos[2])
            glScalef(0.4, 0.4, 1.0)  # Tall thin legs
            glutSolidCube(25)
            glPopMatrix()

        # Body (reddish-brown)
        glPushMatrix()
        glColor3f(r+0.6, g+0.3, b+0.2)  # Brown
        glScalef(1.0, 1.6, 0.8)  # Wider than tall
        glutSolidCube(40)
        glPopMatrix()
        
        # Head
        glPushMatrix()
        glColor3f(r+0.65, g+0.35, b+0.25)  # Lighter brown
        glTranslatef(0, 30, 5)  # Forward and up
        glutSolidCube(25)
        glPopMatrix()
        
        
        
        glPopMatrix()

def spawn_random_cattle(num_cattle=5):
    """Spawn random cattle across the grid"""
    global cattle
    
    for _ in range(num_cattle):
        # Random position on the grid
        cow_x = random.randint(-700, 700)
        cow_y = random.randint(-700, 700)
        
      
        cow_x = round(cow_x / 50) * 50
        cow_y = round(cow_y / 50) * 50
        
       
        if abs(cow_x) <= 100 and abs(cow_y) <= 100:
            continue
            
        
        position_clear = True
        for block in blocks:
            if block.x == cow_x and block.y == cow_y and block.z == 0:
                position_clear = False
                break
                
        for other_cow in cattle:
            if other_cow.x == cow_x and other_cow.y == cow_y:
                position_clear = False
                break
        
        
        if position_clear:
            cattle.append(Cattle(cow_x, cow_y, 25))  # Position at ground level + 25

def initialize_clouds():
    """Generate Minecraft-style clouds"""
    global clouds, clouds_initialized
    
    if not clouds_initialized:
        
        for _ in range(15):
            # Position clouds across the sky
            x = random.uniform(-1500, 1500)
            y = random.uniform(-1500, 1500)
            z = random.uniform(900, 1100)  # Higher clouds
            
            # Cloud size - varies slightly for natural look
            width = random.randint(100, 200)
            depth = random.randint(100, 200)
            height = random.uniform(15, 25)
            
           
            blocks_in_cloud = random.randint(3, 8)
            cloud_blocks = []
            
            for i in range(blocks_in_cloud):
                
                offset_x = random.randint(-80, 80)
                offset_y = random.randint(-80, 80)
                cloud_blocks.append((offset_x, offset_y))
            
            # Cloud movement speed - very slow drift
            move_speed = random.uniform(0.1, 0.3)
            
            clouds.append((x, y, z, width, depth, height, cloud_blocks, move_speed))
        
        clouds_initialized = True

def draw_clouds():
    """Draw Minecraft-style clouds in the sky"""
    global clouds
    

    initialize_clouds()
    

    current_time = time.time()
    
    glPushMatrix()
    

    glColor4f(1.0, 1.0, 1.0, 0.9)
    
    for i, cloud in enumerate(clouds):
        x, y, z, width, depth, height, blocks, speed = cloud
        
    
        x += speed
       
        if x > 2000:
            x = -2000
            
  
        clouds[i] = (x, y, z, width, depth, height, blocks, speed)
        
     
        for block_offset in blocks:
            offset_x, offset_y = block_offset
            
            glPushMatrix()
            glTranslatef(x + offset_x, y + offset_y, z)
            
           
            glScalef(width/100, depth/100, height/100)
            glutSolidCube(100)
            glPopMatrix()
    
    glPopMatrix()

def initialize_stars():
   
    global stars, stars_initialized
    
    if not stars_initialized:
       
        for _ in range(300):
            
            x = random.uniform(-1500, 1500)
            y = random.uniform(-1500, 1500)
            
        
            height_variance = random.uniform(0.7, 1.3)
            base_height = 900
            
           
            distance_from_center = math.sqrt(x*x + y*y)
            
           
            z = base_height + (distance_from_center * 0.2 * height_variance)
            
          
            brightness = random.uniform(0.7, 1.0)
            
            size = random.uniform(1.5, 3.0)
            
            
            blink_rate = random.uniform(2.0, 5.0)
            
            stars.append((x, y, z, brightness, size, blink_rate))
        
        stars_initialized = True

def draw_stars():
    
    global stars
    

    initialize_stars()
    

    current_time = time.time()
    
    
    glPushMatrix()
    
    
    sizes = [3.0, 4.0, 5.0, 6.0]  
    for size in sizes:
        glPointSize(size)
        glBegin(GL_POINTS)
        for star in stars:
            x, y, z, base_brightness, star_size, blink_rate = star
            
           
            if abs(star_size - size) < 0.8: 
            
                blink_factor = 0.65 + 0.35 * math.sin(current_time * blink_rate)
                
        
                brightness = base_brightness * blink_factor
                
        
                glColor3f(brightness, brightness, brightness)
                glVertex3f(x, y, z)
        glEnd()
    
    glPopMatrix()

def draw_sun():
    glPushMatrix()
    # Bright yellow 
    glColor3f(1.0, 0.9, 0.0)  
    glTranslatef(400, -400, 1000)    
    glutSolidSphere(80, 36, 36)    
    glPopMatrix()

def draw_moon():
    glPushMatrix()
    # Simple gray color 
    glColor3f(0.8, 0.8, 0.8)  
    glTranslatef(400, -400, 1000)  
    glutSolidSphere(70, 36, 36)  
    glPopMatrix()

class Block:
    def __init__(self, x, y, z, block_type=0):
        global r, g, b
        self.x = x  # Center X coordinate
        self.y = y  # Center Y coordinate
        self.z = z  # Center Z coordinate
        self.size = 50 
        self.block_type = block_type  # 0=regular, 1=trunk, 2=leaves
        
        # Face colors based on block type
        if block_type == 1:  # Tree trunk
            self.face_colors = [
                (r+0.45, g+0.25, 0.05),  # Trunk brown
                (r+0.4, g+0.22, 0.02),  # Trunk brown
                (r+0.45, g+0.25, 0.05),  # Trunk brown
                (r+0.4, g+0.22, 0.02),  # Trunk brown
                (r+0.45, g+0.25, 0.05),  # Trunk top
                (r+0.4, g+0.22, 0.02)    # Trunk bottom
            ]
        elif block_type == 2:  # Leaves
            self.face_colors = [
                (0.0, g+0.5, 0.0),   # Dark green
                (0.0, g+0.45, 0.0),  # Medium green
                (0.0, g+0.55, 0.0),  # Light green
                (0.0, g+0.5, 0.0),   # Medium green
                (0.0, g+0.6, 0.0),   # Bright green top
                (0.0, g+0.45, 0.0)   # Medium green bottom
            ]
        else:  # Regular block
            self.face_colors = [
                (r+0.6, g+0.4, b+0.2),  # Front (dark brown)
                (r+0.5, g+0.35, b+0.15), # Back (medium brown)
                (r+0.7, g+0.5, b+0.3),   # Left (lighter brown)
                (r+0.55, g+0.4, b+0.25),  # Right (medium-dark brown)
                (r+0.3, g+0.7, b+0.3),    # Top (green)
                (r+0.4, g+0.3, b+0.2)     # Bottom (darkest brown)
            ]

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        global pz
        # Define vertices relative to center
        hs = 25.0
        
        # Body brown cube
        glPushMatrix()
        glColor3f(*self.face_colors[1])
        glutSolidCube(50)
        glPopMatrix()
        
        if self.z <= pz or not fpp:
            glBegin(GL_QUADS)

            # Top face (positive Z)
            glColor3f(*self.face_colors[4])
            glVertex3f(-hs, -hs, hs)
            glVertex3f(hs, -hs, hs)
            glVertex3f(hs, hs, hs)
            glVertex3f(-hs, hs, hs)

            glEnd()
        
        glPopMatrix()

def create_tree(x, y, z=0):

    global blocks
    

    trunk_height = random.randint(2, 4)
    for i in range(trunk_height):
        blocks.append(Block(x, y, z + i*50 + 25, block_type=1))
    
  
    leaf_height = random.randint(2, 3)
    

    for lh in range(leaf_height):
    
        radius = max(1, 2 - lh//2) - 1  
        leaf_z = z + (trunk_height-1)*50 + lh*50
        
        for lx in range(-radius, radius+1):
            for ly in range(-radius, radius+1):
               
                if abs(lx) == radius and abs(ly) == radius and random.random() < 0.7:
                    continue
                blocks.append(Block(x + lx*50, y + ly*50, leaf_z, block_type=2))

def spawn_random_trees(num_trees=15):
   
    for _ in range(num_trees):
       
        tree_x = random.randint(-700, 700)
        tree_y = random.randint(-700, 700)
   
        tree_x, tree_y = cell_center(tree_x, tree_y)
        
   
        if abs(tree_x) <= 100 and abs(tree_y) <= 100:
            continue
            
     
        position_clear = True
        for block in blocks:
            if block.x == tree_x and block.y == tree_y and block.z == 0:
                position_clear = False
                break
       
        if position_clear:
            create_tree(tree_x, tree_y)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
 
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def upd_pos(mov):
    global disp, px, py, face_dir
    angle = math.radians((face_dir + 90) % 90)

    if 0 <= face_dir < 90:
        px += mov * math.sin(angle)
        py -= mov * math.cos(angle)
    elif 90 <= face_dir < 180:
        px += mov * math.cos(angle)
        py += mov * math.sin(angle)
    elif 180 <= face_dir < 270:
        px -= mov * math.sin(angle)
        py += mov * math.cos(angle)
    else:
        px -= mov * math.cos(angle)
        py -= mov * math.sin(angle)

def check_collisions(undo_move):
    global px, py, pz, blocks, aerial, velocity_z, player_health, dead
    
    for block in blocks:
        player_bottom = pz - 25
        
        if abs(px - block.x) < 37.5 and abs(py - block.y) < 37.5:
            if (player_bottom <= block.z + 50 and player_bottom >= block.z + 45):
                # Place player on top of block
                pz = block.z + 25 + 50
                velocity_z = 0
                aerial = False
            
            # Check for head collision
            elif (pz + 50 >= block.z - block.size/2 and
                  pz + 50 <= block.z - block.size/2 + 5):
                # Stop upward movement
                pz = block.z - block.size/2 - 50
                velocity_z = 0
            
            elif abs(pz - block.z) < 75:
                upd_pos(undo_move)
    

    for i in range(len(enm_pos)):
        ex, ey, ez = enm_pos[i]
        if abs(px - ex) < 50 and abs(py - ey) < 50 and abs(pz - ez) < 50:
            player_health -= 1
            
            

            # Remove enemy on collision
            enm_pos.pop(i)

            if player_health <= 0:
                dead = True
            # implement here ?????
            break

def check_fall():
    global px, py, pz, blocks, aerial, velocity_z
    aerial = True
    if pz <= 50:
        aerial = False
        return
    for block in blocks:
        player_bottom = pz - 25
        
        if abs(px - block.x) < 37.5 and abs(py - block.y) < 37.5:
            if (player_bottom <= block.z + 50 and player_bottom >= block.z + 45):
                # Place player on top of block
                pz = block.z + 25 + 50
                velocity_z = 0
                aerial = False

def cell_center(px, py):
    
    cx = 0
    cy = 0
    cond = round(px / 50) * 50
    if abs(px) - abs(cond) <= 25:
        cx = cond
    else:
        if px >= 0:
            cx = cond + 50
        else:
            cx = cond - 50
            
    cond = round(py / 50) * 50
    if abs(py) - abs(cond) <= 25:
        cy = cond
    else:
        if py >= 0:
            cy = cond + 50
        else:
            cy = cond - 50
    
    return (cx, cy)

def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement, gun rotation, camera updates, and cheat mode toggles.
    """
    global food_inv, TOTAL_CATTLE, avail_blocks, look_height, face_dir, px, py, pz, aerial, velocity_z, fpp, walk, wt, r, g, b, blocks, dead, enm_pos, is_sun, JUMP_POWER, GRAVITY, ordered_blocks, TOTAL_TREE, stars,stars_initialized,clouds,clouds_initialized,cattle,cattle_kill_count,player_health,MAX_HEALTH,player_food,dead
    if key == b"r":
        if dead:
            dead = False
            enm_pos = []
            face_dir = 0
            px = 0
            py = 0
            pz = 50
            aerial = False
            GRAVITY = 0.009
            JUMP_POWER = 1.2
            velocity_z = 0
            blocks = []
            ordered_blocks = []
            fpp = False
            look_height = 50
            avail_blocks = 20
            is_sun = True  
            TOTAL_CATTLE = 1
            TOTAL_TREE = 1
            dead = False

            # Sky elements
            stars = []  
            stars_initialized = False
            clouds = []
            clouds_initialized = False

            # Game objects
            cattle = []
            cattle_kill_count = 0

            # Player stats
            player_health = 1  
            MAX_HEALTH = 5 
            player_food = 0    # tree logs
            dead = False
            r, g, b = 0, 0, 0
            food_inv = 0
    if key == b'w':
        walk = True
        wt = 15
        upd_pos(+10)
        check_collisions(-10)
        check_fall()
        if px > 750 or px < -750 or py < -750 or py > 750: 
            upd_pos(-10)
    
    if key == b'e':
        if food_inv > 0:
            food_inv -=1
            player_health += 1
    # Move backward (S key)
    if key == b's':
        walk = True
        wt = 15
        upd_pos(-10)
        check_collisions(10)
        check_fall()
        if px > 750 or px < -750 or py < -750 or py > 750:
            upd_pos(+10)

    # Reset walking animation if not moving
    if key not in [b'w', b's']:
        walk = False
            
    # Toggle first person perspective
    if key == b'f':
        fpp = not fpp

    # Rotate gun left (A key)
    if key == b'a':
        face_dir += 5
        face_dir %= 360
        
    # Rotate gun right (D key)
    if key == b'd':
        face_dir -= 5
        face_dir = (face_dir + 360) % 360
    
    # Jump
    if key == b' ' and not aerial:
        aerial = True
        velocity_z = JUMP_POWER

 
    if key == b'm':
        is_sun = False
        r, g, b = -0.3, -0.3, -0.25
    if key == b'l':
        is_sun = True
        r, g, b = 0, 0, 0

    # Update block colors for day/night cycle
    for block in blocks:
        if block.block_type == 1:  # Trunk
            block.face_colors = [
                (r + 0.45, g + 0.25, 0.05),
                (r + 0.4, g + 0.22, 0.02),
                (r + 0.45, g + 0.25, 0.05),
                (r + 0.4, g + 0.22, 0.02),
                (r + 0.45, g + 0.25, 0.05),
                (r + 0.4, g + 0.22, 0.02)
            ]
        elif block.block_type == 2:  # Leaves
            block.face_colors = [
                (0.0, g + 0.5, 0.0),
                (0.0, g + 0.45, 0.0),
                (0.0, g + 0.55, 0.0),
                (0.0, g + 0.5, 0.0),
                (0.0, g + 0.6, 0.0),
                (0.0, g + 0.45, 0.0)
            ]
        else:  # Regular block
            block.face_colors = [
                (r + 0.6, g + 0.4, b + 0.2),
                (r + 0.5, g + 0.35, b + 0.15),
                (r + 0.7, g + 0.5, b + 0.3),
                (r + 0.55, g + 0.4, b + 0.25),
                (r + 0.3, g + 0.7, b + 0.3),
                (r + 0.4, g + 0.3, b + 0.2)
            ]

def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for adjusting the camera angle and height.
    """
    global camera_pos, look_height
    x, y, z = camera_pos
    
    # Moving camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT and not fpp:
        if x < 0:
            y -= 10
        else: 
            y += 10
        if y < 0:
            y = 0
            camera_pos = (x, y, z)
            return
        
        x -= 10
    
    # Moving camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT and not fpp:
        if x < 0:
            y += 10
        else:
            y -= 10
        if y < 0:
            y = 0
            camera_pos = (x, y, z)
            return
        x += 10
    
    # Move camera up
    if key == GLUT_KEY_UP and not fpp:
        z -= 10
    
    # Move camera down
    if key == GLUT_KEY_DOWN and not fpp:
        if z <= 700:
            z += 10
    
    # Adjust look height down
    if key == GLUT_KEY_DOWN:
        if look_height > 0:
            look_height -= 2
    
    # Adjust look height up
    if key == GLUT_KEY_UP:
        if look_height <= 700:
            look_height += 2

    camera_pos = (x, y, z)

def create_block():
    global px, py, pz, face_dir, blocks, avail_blocks
    

    if avail_blocks < 1:
        return
    targ_cell_x, targ_cell_y = cell_center(px, py)
    
    if 45 <= face_dir < 135:
        targ_cell_x += 50
    elif 135 <= face_dir < 225:
        targ_cell_y += 50
    elif 225 <= face_dir < 315:
        targ_cell_x -= 50
    else:
        targ_cell_y -= 50
    
    lower_level = False or pz <= 50
    same_level = False
    upper_level = False   
    for block in blocks:
        
        if block.x == targ_cell_x and block.y == targ_cell_y:
            if block.z == pz - 75:
                lower_level = True
            
            if block.z == pz - 25:
                same_level = True
            
            if block.z == pz + 25:
                upper_level = True
    
    if not lower_level:
        avail_blocks -= 1
        blocks.append(Block(targ_cell_x, targ_cell_y, pz - 75))  
    elif not same_level:
        avail_blocks -= 1
        blocks.append(Block(targ_cell_x, targ_cell_y, pz - 25))
    elif not upper_level:
        avail_blocks -= 1
        blocks.append(Block(targ_cell_x, targ_cell_y, pz + 25))

def create_block_under():
    global px, py, pz, face_dir, blocks, velocity_z, avail_blocks
    
    if avail_blocks < 1:
        return
    targ_cell_x, targ_cell_y = cell_center(px, py)
    found_block = Block(targ_cell_x, targ_cell_y, -25)
    for block in blocks:
        
        if block.x == targ_cell_x and block.y == targ_cell_y:
            
            if block.z < pz and found_block.z < block.z:
                
                found_block = block

    avail_blocks -= 1
    blocks.append(Block(targ_cell_x, targ_cell_y, found_block.z + 50))
def destroy_block_under():
    global px, py, pz, face_dir, blocks, cattle, player_health, cattle_kill_count, player_food, avail_blocks
    
    targ_cell_x, targ_cell_y = cell_center(px, py)

    found_block = Block(targ_cell_x, targ_cell_y, -25)
    for block in blocks:
        
        if block.x == targ_cell_x and block.y == targ_cell_y:
            
            if block.z < pz and found_block.z < block.z:
                
                found_block = block

    if found_block.z > -25:
        if found_block.block_type == 1:
            avail_blocks += 5
        elif found_block.block_type == 0:
            avail_blocks += 1
        blocks.remove(found_block)
    


    lower_level = False or pz <= 50
    same_level = False
    upper_level = False   
    
    for block in blocks:
        if block.x == targ_cell_x and block.y == targ_cell_y:
            if block.z == pz - 75:
                lower_level = block
            if block.z == pz - 25:
                same_level = block
            if block.z == pz + 25:
                upper_level = block
    
    # Remove regular blocks
    if type(upper_level) != bool:
        avail_blocks += 1
        blocks.remove(upper_level)  
    elif type(same_level) != bool:
        avail_blocks += 1
        blocks.remove(same_level)
    elif type(lower_level) != bool:
        avail_blocks += 1
        blocks.remove(lower_level)
def destroy_block():
    global food_inv, px, py, pz, face_dir, blocks, cattle, player_health, cattle_kill_count, player_food, avail_blocks
    
    targ_cell_x, targ_cell_y = cell_center(px, py)
    
    if 45 <= face_dir < 135:
        targ_cell_x += 50
    elif 135 <= face_dir < 225:
        targ_cell_y += 50
    elif 225 <= face_dir < 315:
        targ_cell_x -= 50
    else:
        targ_cell_y -= 50
    

    tree_blocks = []
    for block in blocks:
        # Use a wider detection range for trees
        if abs(block.x - targ_cell_x) < 80 and abs(block.y - targ_cell_y) < 80:
            if block.block_type == 1 or block.block_type == 2:
                dx = block.x - px
                dy = block.y - py
                dz = block.z - pz
                dist_val = dx*dx + dy*dy + dz*dz
                tree_blocks.append((dist_val, block))
    
    # If found any tree blocks, remove the closest one
    if tree_blocks:
        # Sort by distance (closest first)
        tree_blocks.sort(key=lambda x: x[0])
        closest_tree = tree_blocks[0][1]
        blocks.remove(closest_tree)
        
        if closest_tree.block_type == 1:
            avail_blocks += 5
        # Increase food count
        if player_food < 5:
            player_food += 1
        return  # Return early after destroying a tree
    
    # Then check for cattle
    for i in range(len(cattle)-1, -1, -1):
        cow = cattle[i]
        if abs(cow.x - targ_cell_x) < 100 and abs(cow.y - targ_cell_y) < 100:
            # Remove cattle
            cattle.pop(i)
            cattle_kill_count += 1
            food_inv += 5
            

            # if cattle_kill_count % 2 == 0 and player_health < MAX_HEALTH:
            #     player_health += 1
            #     print(f"Health increased to {player_health}!")
                
            return
    

    for i in range(len(enm_pos)-1, -1, -1):
        ex, ey, ez = enm_pos[i]
        if abs(ex - targ_cell_x) < 100 and abs(ey - targ_cell_y) < 100:
            enm_pos.pop(i)
            return
    

    lower_level = False or pz <= 50
    same_level = False
    upper_level = False   
    
    for block in blocks:
        if block.x == targ_cell_x and block.y == targ_cell_y:
            if block.z == pz - 75:
                lower_level = block
            if block.z == pz - 25:
                same_level = block
            if block.z == pz + 25:
                upper_level = block
    
    # Remove regular blocks
    if type(upper_level) != bool:
        avail_blocks += 1
        blocks.remove(upper_level)  
    elif type(same_level) != bool:
        avail_blocks += 1
        blocks.remove(same_level)
    elif type(lower_level) != bool:
        avail_blocks += 1
        blocks.remove(lower_level)

def mouseListener(button, state, x, y):
    global a_anim, fall
    """
    Handles mouse inputs for block creation and destruction.
    """
    
    # Right mouse button creates blocks
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN and not aerial:
        create_block()
        a_anim = True
        fall = False
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN and aerial:
        create_block_under()
        a_anim = True
        fall = False
    

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not aerial:
        destroy_block()
        a_anim = True
        fall = False
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and aerial:
        destroy_block_under()
        a_anim = True
        fall = False
    

def setupCamera():
    """
    Configures the camera's projection and view settings.
    """
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    gluPerspective(fovY, 1.25, .1, 1500) # Think why aspect ration is 1.25?
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    # Extract camera position and look-at target
    x, y, z = camera_pos
    # Position the camera and set its orientation
    cx = cy = 0
    lx = ly = 0
    global px, py, face_dir, pz, look_height
    angle = math.radians((face_dir + 90) % 90)
    if 0 <= face_dir < 90:
        cx = px + 15 * math.sin(angle)
        lx = px + 25 * math.sin(angle)
        cy = py - 15 * math.cos(angle)
        ly = py - 25 * math.cos(angle)
    elif 90 <= face_dir < 180:
        cx = px + 15 * math.cos(angle)
        lx = px + 25 * math.cos(angle)
        cy = py + 15 * math.sin(angle)
        ly = py + 25 * math.sin(angle)
    elif 180 <= face_dir < 270:
        cx = px - 15 * math.sin(angle)
        lx = px - 25 * math.sin(angle)
        cy = py + 15 * math.cos(angle)
        ly = py + 25 * math.cos(angle)
    else:
        cx = px - 15 * math.cos(angle)
        lx = px - 25 * math.cos(angle)
        cy = py - 15 * math.sin(angle)
        ly = py - 25 * math.sin(angle)
        
    if not fpp:  
        if 0 <= face_dir < 90:
            cx = px - 70 * math.sin(angle)
            lx = px - 25 * math.sin(angle)
            cy = py + 70 * math.cos(angle)
            ly = py + 25 * math.cos(angle)
        elif 90 <= face_dir < 180:
            cx = px - 70 * math.cos(angle)
            lx = px - 25 * math.cos(angle)
            cy = py - 70 * math.sin(angle)
            ly = py - 25 * math.sin(angle)
        elif 180 <= face_dir < 270:
            cx = px + 70 * math.sin(angle)
            lx = px + 25 * math.sin(angle)
            cy = py - 70 * math.cos(angle)
            ly = py - 25 * math.cos(angle)
        else:
            cx = px + 70 * math.cos(angle)
            lx = px + 25 * math.cos(angle)
            cy = py + 70 * math.sin(angle)
            ly = py + 25 * math.sin(angle)
        
    if fpp:
        gluLookAt(cx, cy, pz + 50,  # Camera position
                lx, ly, pz + look_height,  # Look-at target
                0, 0, 1)  # Up vector (z-axis)
    else:
        gluLookAt(cx, cy, pz + 100,  # Camera position
                px, py, pz + look_height,  # Look-at target
                0, 0, 1)  # Up vector (z-axis)

def idle():
    global px, py, pz, velocity_z, GRAVITY, aerial, lang, ldir, walk, wt, a_ang, a_anim, a_y, a_z, fall
    global r, g, b, enm_pos, enmt, num_enm
    
    if aerial:
        velocity_z -= GRAVITY
        pz += velocity_z
        check_collisions(10)
        
    if pz < 50:
        pz = 50
        velocity_z = 0
        aerial = False
        
    # Walking animation
    if walk:
        if wt > 0:
            wt -= 0.5
        else:
            walk = False
        lang += 0.75 * ldir
        if lang > 35 or lang < -34:
            ldir *= -1
    else:
        lang = 0

    # Arm animation for actions
    if a_anim:
        a_ang += 3
        a_y -= 0.5
        a_z += 0.75
        if a_ang >= 150: 
            a_anim = False
            fall = True
    if fall:
        if a_ang >= 70:
            a_ang -= 3
            a_y += 0.5
            a_z -= 0.75
        else:
            fall = False
    

    if not is_sun:  
        if enmt > 0:
            enmt -= 1  
        else:
            num_enm = random.randint(3, 5)  
            new_enm = [(rand_x(), rand_y(), 50) for i in range(num_enm)]  
            enm_pos.extend(new_enm)
            enmt = random.randint(2900, 3500)  

    # Enemy movement towards player
    new_pos = []
    for ex, ey, ez in enm_pos: 
        dx = px - ex
        dy = py - ey
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            ex += 0.25 * (dx / dist) 
            ey += 0.25 * (dy / dist)

        new_pos.append((ex, ey, ez))

    enm_pos = new_pos

    if len(cattle) < TOTAL_CATTLE:
        spawn_random_cattle(TOTAL_CATTLE - len(cattle))

    st = set()

    for block in blocks:
        if block.block_type == 1:
            st.add((block.x, block.y))
    
    spawn_random_trees(TOTAL_TREE - len(st))
            
    glutPostRedisplay()

def draw_floor():
    global r, g, b

    grid_size = 31
    

    start_x = 775
    start_y = -775
    
    side_len = 50
    down_len = 50
    glBegin(GL_QUADS)
    color = 0
    for row in range(grid_size):
        for col in range(grid_size):
            if color:
                glColor3f(r+1, g+1, b+1)
            else:
                glColor3f(r+0.7, g+0.5, b+0.95)
            
            glVertex3f(start_x, start_y, 0)
            glVertex3f(start_x - side_len, start_y, 0)
            glVertex3f(start_x - side_len, start_y + down_len, 0)
            glVertex3f(start_x, start_y + down_len, 0)
            
            color = not color
            
            start_x -= side_len
        
        start_x = 775  
        start_y += down_len
            
    glEnd()

def draw_player():
    global face_dir, px, py, pz, lang, a_ang, r, g, b
    glPushMatrix()
    
    glTranslatef(px, py, pz)
    glRotatef(face_dir, 0, 0, 1)

    #legs
    #right
    glPushMatrix()
    glColor3f(r+(75/255), g+(42/255), b+(244/255))
    glTranslatef(-6, 0, -25)
    glRotate(lang, 1, 0, 0)
    glScalef(1.0, 1.0, 3)
    glutSolidCube(15)
    glPopMatrix()

    #left
    glPushMatrix()
    glColor3f(r+(75/255), g+(42/255), b+(244/255))
    glTranslatef(6, 0, -25)
    glRotate(-lang, 1, 0, 0)
    glScalef(1.0, 1.0, 3)
    glutSolidCube(15)
    glPopMatrix()

    #body   
    glPushMatrix()
    glColor3f(r+(15/255), g+(117/255), b+(68/255))
    glTranslatef(0, 0, 16)
    glScalef(1.0, 1.0, 1.9)
    glutSolidCube(27)
    glPopMatrix()

    #face
    glPushMatrix()
    glColor3f(r+(222/255), g+(197/255), b+(144/255))
    glTranslatef(0, 0, 50)
    glRotatef(90, 1, 0, 0)
    glutSolidCube(20)
    glPopMatrix()
     
    #hands
    #left
    glPushMatrix()
    glColor3f(r+(222/255), g+(197/255), b+(144/255))
    glTranslatef(20, a_y, a_z)
    glRotatef(-a_ang, 1, 0, 0)
    glScalef(1.0, 1.0, 4.0)
    glutSolidCube(13)
    glPopMatrix()
    
    #right
    glPushMatrix()
    glColor3f(r+(222/255), g+(197/255), b+(144/255))
    glTranslatef(-20, a_y, a_z)
    glRotatef(-a_ang, 1, 0, 0)
    glScalef(1.0, 1.0, 4.0)
    glutSolidCube(13)
    glPopMatrix()


    glPushMatrix()
    glColor3f(r+(176/255), g+(90/255), b+(3/255))  
    glTranslatef(0, 0, 60)
    glScalef(1.0, 1.0, 0.1)
    glutSolidCube(20)
    glPopMatrix()

    glPopMatrix()


def enem(tx, ty, tz):
    glPushMatrix()  
    glTranslatef(tx, ty, tz)
    glColor3f(145/255.0,10/255.0,120/255.0)
    
    glPushMatrix()
    glTranslatef(0, 0, 35)
    glScalef(1.0, 1.0, 1.2) 
    glutSolidCube(35)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(10, 3, 0)
    glRotate(-20, 0, 1, 0)
    glScalef(0.50, 0.50, 3.9) 
    glutSolidCube(20)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-10, 3, 0)
    glRotate(20, 0, 1, 0)
    glScalef(0.50, 0.50, 3.9) 
    glutSolidCube(20)
    glPopMatrix()

    glPopMatrix()

# Draw all enemies
def draw_enem(positions):
    for pos in positions:
        enem(pos[0], pos[1], pos[2])

def draw_down_wall():
    glPushMatrix()
    glTranslatef(0, 400, 0)
    glBegin(GL_QUADS)
    glColor(1, 1, 1)
    glVertex3f(500, 0, 0)
    glVertex3f(-500, 0, 0)
    glVertex3f(-500, 0, 100)
    glVertex3f(500, 0, 100)
    glEnd()
    glPopMatrix()

def order_by_player_pos():
    global ordered_blocks, blocks
    
    ordered_blocks = []
    for block in blocks:
        dx = block.x - px
        dy = block.y - py
        dz = block.z - pz
        
        dist_val = dx * dx + dy * dy + dz * dz
        
        ordered_blocks.append((dist_val, block))
        
    ordered_blocks.sort(reverse=True, key=lambda x: x[0])

def draw_sky_background():
   
    global is_sun
    
    # Set up an orthographic projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Set color based on day/night
    if is_sun:
        # Day sky - light blue color
        glColor3f(0.6, 0.8, 1.0)
    else:
        # Night sky - black
        glColor3f(0.0, 0.0, 0.0)
    
    # Draw full screen quad
    glBegin(GL_QUADS)
    glVertex3f(-1, -1, -0.99)
    glVertex3f(1, -1, -0.99)
    glVertex3f(1, 1, -0.99)
    glVertex3f(-1, 1, -0.99)
    glEnd() 

def showScreen():
    """
    Display function to render the game scene
    """
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_sky_background()
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size

    setupCamera()  # Configure camera perspective

    global face_dir, aerial, enm_pos, dead, player_health
    

    if dead:

        draw_text(400, 400, f"You were killed !!!!!!")
        draw_text(400, 380, f"Press R to restart")
        glutSwapBuffers()
        return 



    draw_floor()


    
    # Sky elements
    if is_sun:
        draw_sun()
        draw_clouds()  # Clouds before trees
    else:
        draw_moon()
        draw_stars()
    
    # Combined list of all objects that need depth sorting
    all_objects = []
    
    # Add all blocks with their distances
    for block in blocks:
        dx = block.x - px
        dy = block.y - py
        dz = block.z - pz
        dist_val = dx * dx + dy * dy + dz * dz
        all_objects.append((dist_val, "block", block))
        
    # Add all cattle with their distances
    for cow in cattle:
        dx = cow.x - px
        dy = cow.y - py
        dz = cow.z - pz
        dist_val = dx * dx + dy * dy + dz * dz
        all_objects.append((dist_val, "cow", cow))
        
    # Sort all objects by distance (furthest first)
    all_objects.sort(reverse=True, key=lambda x: x[0])
    
    # Draw all objects in sorted order
    for _, obj_type, obj in all_objects:
        if obj_type == "block":
            obj.draw()
        else:  # obj_type == "cow"
            obj.draw()
    

    draw_enem(enm_pos)
    # Draw the player
    draw_player()

    # Draw HUD elements
    draw_hud()
    

    
    
    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()

# Initial blocks
block = Block(100, 100, 25)
blocks.append(block)
block = Block(150, 100, 75)
blocks.append(block)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(10, 10)  # Window position
    wind = glutCreateWindow(b"Minecraft Clone")  # Create the window

    # Generate random trees and cattle before starting game
    spawn_random_trees(TOTAL_TREE)  
    spawn_random_cattle(TOTAL_CATTLE)
   
    # Register event handlers
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()