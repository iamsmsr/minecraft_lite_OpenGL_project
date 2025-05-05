from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math


# Camera-related variables

# x pos -> to the left
# y pos -> towards me
# z pos -> upwards direction
camera_pos = (0,300,300)

fovY = 120  # Field of view
GRID_LENGTH = 600  # Length of grid lines
rand_var = 423


face_dir = 0
disp = 0
px = 0
py = 0
pz = 50
aerial = False
GRAVITY = 0.005
JUMP_POWER = .9
velocity_z = 0
blocks = []
ordered_blocks = []
fpp = False
look_height = 50

class Block:
    def __init__(self, x, y, z, block_type=0):
        self.x = x  # Center X coordinate
        self.y = y  # Center Y coordinate
        self.z = z  # Center Z coordinate
        self.size = 50 
        
        # Face colors with green top and brown sides/bottom
        self.face_colors = [
            (0.6, 0.4, 0.2),  # Front (dark brown)
            (0.5, 0.35, 0.15), # Back (medium brown)
            (0.7, 0.5, 0.3),   # Left (lighter brown)
            (0.55, 0.4, 0.25),  # Right (medium-dark brown)
            (0.3, 0.7, 0.3),    # Top (green)
            (0.4, 0.3, 0.2)     # Bottom (darkest brown)
        ]

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        global pz
        # Define vertices relative to center
        hs = 25.0
        
        
        # body brown cube
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
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
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
    global px, py, pz, blocks, aerial, velocity_z
    
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
        
            
def cell_center():
    
    global px, py
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
    global face_dir, pz, py, pz, aerial, velocity_z, fpp

    # # Move forward (W key)
    if key == b'w':
        upd_pos(+10)
        check_collisions(-10)
        check_fall()
        if px > 500 or px < -500 or py < -400 or py > 400:
            upd_pos(-10)
    # # Move backward (S key)
    if key == b's':
        upd_pos(-10)
        check_collisions(10)
        check_fall()
        if px > 500 or px < -500 or py < -400 or py > 400:
            upd_pos(+10)
            
    if key == b'f':
        fpp = not fpp
    

    # # Rotate gun left (A key)
    if key == b'a':
        face_dir += 5
        face_dir %= 360
    # # Rotate gun right (D key)
    if key == b'd':
        face_dir -= 5
        face_dir = (face_dir + 360) % 360
    
    if key == b' ' and not aerial:
        
        aerial = True
        velocity_z = JUMP_POWER
         
        
    # # Toggle cheat mode (C key)
    # if key == b'c':

    # # Toggle cheat vision (V key)
    # if key == b'v':

    # # Reset the game if R key is pressed
    # if key == b'r':


def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for adjusting the camera angle and height.
    """
    global camera_pos, look_height
    x, y, z = camera_pos
    # Move camera up (UP arrow key)
    # if key == GLUT_KEY_UP:

    # # Move camera down (DOWN arrow key)
    # if key == GLUT_KEY_DOWN:

    # moving camera left (LEFT arrow key)
    
    if key == GLUT_KEY_LEFT and not fpp:
          # Small angle decrement for smooth movement
        if x < 0:
            y -= 10
        else: 
            y += 10
        if y < 0:
            y = 0
            camera_pos = (x, y, z)
            return
        
        x -= 10
        
        
        
        
    # moving camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT and not fpp:
          # Small angle increment for smooth movement
        if x < 0:
            y += 10
        else:
            y -= 10
        if y < 0:
            y = 0
            camera_pos = (x, y, z)
            return
        x += 10
        
    if key == GLUT_KEY_UP and not fpp:
        z -= 10
        
    if key == GLUT_KEY_DOWN and not fpp:
        if z <= 700:
            z += 10
            
    if key == GLUT_KEY_DOWN:
        if look_height > 0:
            look_height -= 2
        
    if key == GLUT_KEY_UP:
        if look_height <= 700:
            look_height += 2

    camera_pos = (x, y, z)

def create_block():
    
    global px, py, pz, face_dir, blocks
    
    targ_cell_x, targ_cell_y = cell_center()
    
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
        blocks.append(Block(targ_cell_x, targ_cell_y, pz - 75))  
    elif not same_level:
        blocks.append(Block(targ_cell_x, targ_cell_y, pz - 25))
    elif not upper_level:
        blocks.append(Block(targ_cell_x, targ_cell_y, pz + 25))  


def create_block_under():
    global px, py, pz, face_dir, blocks, velocity_z, blocks
    
    targ_cell_x, targ_cell_y = cell_center()
    found_block = Block(targ_cell_x, targ_cell_y, -25)
    for block in blocks:
        
        if block.x == targ_cell_x and block.y == targ_cell_y:
            
            if block.z < pz and found_block.z < block.z:
                
                found_block = block

            

    blocks.append(Block(targ_cell_x, targ_cell_y, found_block.z + 50))

def destroy_block():
    
    global px, py, pz, face_dir, blocks
    
    targ_cell_x, targ_cell_y = cell_center()
    
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
                lower_level = block
            
            if block.z == pz - 25:
                same_level = block
            
            if block.z == pz + 25:
                upper_level = block
    
    if type(upper_level) != bool:
        blocks.remove(upper_level)  
    elif type(same_level) != bool:
        blocks.remove(same_level)
    elif type(lower_level) != bool:
        blocks.remove(lower_level)  

           
def mouseListener(button, state, x, y):
    """
    Handles mouse inputs for firing bullets (left click) and toggling camera mode (right click).
    """
    
    # Left mouse button fires a bullet
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN and not aerial:
        create_block()
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN and aerial:
        create_block_under()
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        destroy_block()
    # # Right mouse button toggles camera tracking mode
    

def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
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
        
    if fpp:
        gluLookAt(cx, cy, pz + 50,  # Camera position
                lx, ly, pz + look_height,  # Look-at target
                0, 0, 1)  # Up vector (z-axis)
    else:
        gluLookAt(x, y, z,  # Camera position
                0, 0, 0,  # Look-at target
                0, 0, 1)  # Up vector (z-axis)



def idle():
    """
    Idle function that runs continuously:
    - Triggers screen redraw for real-time updates.
    """
    # Ensure the screen updates with the latest changes
    
    global px, py, pz, velocity_z, GRAVITY, aerial
    #print(len(bullets), len(enemies), len(cheat_marked_enemy))
    
    if aerial:
        velocity_z -= GRAVITY
        pz += velocity_z
        check_collisions(10)
        
    if pz < 50:
        pz = 50
        velocity_z = 0
        aerial = False
    glutPostRedisplay()

def draw_floor():
    
    start_x = 525
    start_y = -425
    
    side_len = 50
    down_len = 50
    glBegin(GL_QUADS)
    color = 0
    for row in range(21):
        for col in range(21):
            if color: 
                glColor3f(1, 1, 1)
            else:
                glColor3f(0.7, 0.5, 0.95)
            
            glVertex3f(start_x, start_y, 0)
            glVertex3f(start_x - side_len, start_y, 0)
            glVertex3f(start_x - side_len, start_y + down_len, 0)
            glVertex3f(start_x, start_y + down_len, 0)
            
            color = not color
            
            start_x -= side_len
        
        start_x = 525
        start_y += down_len
            
    
    glEnd()


    
    
   
def draw_player():
    
    global face_dir, px, py, pz
    glPushMatrix()
    
    glTranslatef(px, py, pz)
    glRotatef(face_dir, 0, 0, 1)
    
    
    
    #body
    
    glPushMatrix()
    glColor3f(15 / 255, 117 / 255, 68 / 255)
    #glTranslatef(0, 0, 50)
    glScalef(1.0, 1.0, 4.0)
    glutSolidCube(25)
    glPopMatrix()
    
    
    #hands
    #left
    glPushMatrix()
    glColor3f(222 / 255, 197 / 255, 144 / 255)
    glTranslatef(-20, -10, 25)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 3, 25, 10, 10)
    glPopMatrix()
    
    #right
    glPushMatrix()
    glColor3f(222 / 255, 197 / 255, 144 / 255)
    glTranslatef(20, -10, 25)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 3, 25, 10, 10)
    glPopMatrix()
    # head
    # glPushMatrix()
    # glColor3f(0, 0, 0)
    # glTranslatef(0, 0, 100)
    # gluSphere(gluNewQuadric(), 15, 10, 10)
    # glPopMatrix()
    
    
    
    
    
    glPopMatrix()
    
def draw_down_wall():
    
    glPushMatrix()
    glTranslatef(0, 400, 0)
    # glRotatef(90, 0, 1, 0)
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
        
    ordered_blocks.sort(reverse = True, key = lambda x : x[0])
    
    

def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything of the screen
    """
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size

    setupCamera()  # Configure camera perspective


    global face_dir, aerial
    
    draw_floor()
    
    if fpp:
        order_by_player_pos()
        for block in ordered_blocks:
            block[1].draw()
    else: 
        for block in blocks:
            block.draw()
    
    draw_player()
    
    # print(len(blocks))
    


    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()


# Main function to set up OpenGL window and loop
block = Block(100, 100, 25)
blocks.append(block)
# block = Block(150, 100, 25)
# blocks.append(block)
block = Block(150, 100, 75)
blocks.append(block)
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"3D OpenGL Intro")  # Create the window

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    
    main()