import pygame
import socketio
import sys
import math
import ctypes
import threading
import time



pygame.init()
sio = socketio.Client()
screen_info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h

@sio.on('connect', namespace='/game')
def on_connect():
    print("Connected to the server!")


def set_interval(func, interval):
    def wrapper():
        set_interval(func, interval)  # Reschedule the function
        func()
    t = threading.Timer(interval, wrapper)
    t.start()
    return t  # Return the Timer object to control it later

def current_time_ms():
    return int(time.time() * 1000)



class InputField:
    def __init__(self, x, y, width, height, placeholder, font, max_length=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (100, 100, 100)
        self.active = False
        self.text = ''
        self.placeholder = placeholder
        self.font = font
        self.max_length = max_length
        self.text_surface = self.font.render(self.placeholder, True, (150, 150, 150))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif len(self.text) < self.max_length:
                    self.text += event.unicode

    def update(self):
        if self.active:
            self.text_surface = self.font.render(self.text, True, (255, 255, 255))
        else:
            self.text_surface = self.font.render(self.text if self.text else self.placeholder, True, (150, 150, 150))

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surface, (self.rect.x + 10, self.rect.y + 10))

    def get_text(self):
        return self.text


class Slider:
    def __init__(self, x, y, width, min_value, max_value, initial_value, font, label):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_value = min_value
        self.max_value = max_value+29
        self.value = initial_value
        self.font = font
        self.label = label
        self.slider_rect = pygame.Rect(x+10 + (self.value - self.min_value) / (self.max_value - self.min_value) * width - 10, y, 20, 20)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.slider_rect.collidepoint(event.pos):
                self.active = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.active = False

        if event.type == pygame.MOUSEMOTION and self.active:
            new_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width-20))
            self.value = self.min_value + (new_x - self.rect.x) / self.rect.width * (self.max_value - self.min_value)
            self.slider_rect.x = new_x  # Center the slider handle

    def update(self):
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, (100, 100, 100), self.rect)
        pygame.draw.rect(screen, (255, 0, 0), self.slider_rect)
        label_surface = self.font.render(f'{self.label}: {int(self.value)}', True, str(self.label))
        screen.blit(label_surface, (self.rect.x + self.rect.width + 10, self.rect.y))


    def get_value(self):
        return self.value





class Button:
    def __init__(self, x, y, w, h, name):
        self.name = name
        self.rect = pygame.Rect(x, y, w, h)
        self.namesurface = pygame.font.Font(size=30).render(name, True, 'white')
        self.clicked = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
        if event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos):
                self.clicked = False

    def draw(self, screen):
        is_hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        color = (10, 10, 10) if not is_hovered else (30, 30, 30)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (30, 30, 30), self.rect, 1)
        screen.blit(self.namesurface, (self.rect.centerx - self.namesurface.get_width()/2, self.rect.centery - self.namesurface.get_height()/2))






class Menu:
   def __init__(self, game):
        self.isRunning = True
        self.isClosed = False
        self.game = game
        self.font = pygame.font.Font(size=100)
        self.name_input = InputField(self.game.wnx // 5, self.game.wny / 2.5, 400, 40, "Enter Name", pygame.font.Font(None, 32))
        self.red_slider = Slider(self.game.wnx // 5, self.game.wny / 2, 200, 0, 255, 0, pygame.font.Font(None, 32), "Red")
        self.green_slider = Slider(self.game.wnx // 5, self.game.wny / 2 + 40, 200, 0, 255, 0, pygame.font.Font(None, 32), "Green")
        self.blue_slider = Slider(self.game.wnx // 5, self.game.wny / 2 + 80, 200, 0, 255, 0, pygame.font.Font(None, 32), "Blue")
        self.settings_button = Button(0, self.game.wny/16-40, 200, 40, "SETTINGS")
        self.credits_button = Button(200, self.game.wny/16-40, 200, 40, "CREDITS")
        self.backtm_button = Button(270, 470, 100, 70, "BACK")
        self.FINAL_color = (0, 0, 0)
        self.FINAL_name = 'GUEST'
        self.credits_enabled = False
    
        


   def renderScreen(self):
        self.game.screen.blit(self.game.menu_bg, (-50, -50))
        self.game.screen.blit(self.game.settings_bg, (220, 220))
    


   def renderItems(self):
    # Create a transparent surface for the polygon
    
    shadow_surface = pygame.Surface((self.game.wnx, self.game.wny), pygame.SRCALPHA)
    if self.credits_button.clicked:
        self.credits_enabled = True
    
    self.name_input.update()
    self.name_input.draw(self.game.screen)
    self.red_slider.update()
    self.red_slider.draw(self.game.screen)
    self.green_slider.update()
    self.green_slider.draw(self.game.screen)
    self.blue_slider.update()
    self.blue_slider.draw(self.game.screen)

    

    # Define polygon points
    polygon_points = [
        (self.game.wnx, 0),
        (self.game.wnx, self.game.wny),
        (self.game.wnx - self.game.wnx / 3, self.game.wny),
        (self.game.wnx - self.game.wnx / 4, 0)
    ]

    ship_drawing_points = lambda x, y : [
        (100+x, 100+y),
        (140+x, 140+y),
        (180+x, 100+y),
        (140+x, 200+y),
        (100+x, 100+y),
    ]

    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()

    # Check if the mouse is inside the polygon
    is_hovered = pygame.draw.polygon(shadow_surface, (0, 0, 0, 0), polygon_points).collidepoint(mouse_pos)

    # Adjust transparency based on hover state
    a = 200 if is_hovered else 160
    b = 150

    # Draw the polygon with the calculated transparency on the shadow surface
    pygame.draw.polygon(shadow_surface, (10, 10, 10, a), polygon_points)
    pygame.draw.polygon(shadow_surface, (10, 10, 10, b), ship_drawing_points(0, -40))
    pygame.draw.polygon(shadow_surface, (10, 10, 10, b), ship_drawing_points(300, -40))
    pygame.draw.polygon(shadow_surface, (10, 10, 10, b), ship_drawing_points(600, -40))

    # Blit the shadow surface onto the main screen
    self.game.screen.blit(shadow_surface, (0, 0))

    # Render the "PLAY" text
    PLAY_TEXT = 'PLAY'
    text_x = self.game.wnx - self.game.wnx / 3 + 150
    text_y = self.game.wny - 190
    glow_color = (255, 255, 255) if is_hovered else (200, 200, 200)  
    text_color = (200, 200, 200) if is_hovered else (120, 120, 120)
    # Call the renderGlowText method to draw glowing text
    play = self.font.render(PLAY_TEXT, True, text_color)
    self.game.screen.blit(play, (text_x, text_y))
    play_button_rect = pygame.Rect(text_x, text_y, play.get_width(), play.get_height())
    color_rect_x, color_rect_y = 255, 500  # Ensure these coordinates are visible within your screen
    color_rect_width, color_rect_height = 300, 100
    preview_color = (self.red_slider.value, self.green_slider.value, self.blue_slider.value)
    pygame.draw.rect(self.game.screen, preview_color, (color_rect_x, color_rect_y, color_rect_width, color_rect_height), border_radius=10)
    pygame.draw.rect(self.game.screen, 'black', (color_rect_x, color_rect_y, color_rect_width, color_rect_height), 5, border_radius=10)
    pygame.draw.rect(self.game.screen, 'black', (0, 0, self.game.wnx, self.game.wny/16))
    self.settings_button.draw(self.game.screen)
    self.credits_button.draw(self.game.screen)

    


    self.FINAL_color = preview_color
    self.FINAL_name = self.name_input.get_text()

    if play_button_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] and self.FINAL_name.strip() != '' and self.FINAL_color != (0, 0, 0):
            self.isRunning = False
            self.game.screen.fill((0, 0, 0))
            loading_text = pygame.font.Font(None, 48).render("Connecting to server...", True, (255, 255, 255))
            self.game.screen.blit(loading_text, (self.game.wnx // 2 - loading_text.get_width() // 2, self.game.wny // 2 - loading_text.get_height() // 2))
            pygame.display.flip()
    


    


   def renderCredits(self):
       self.credits = pygame.font.Font(size=40).render("FROM YAZAN ALJUNDI, 2024.", True, (20, 4, 4))
       self.credits1 = pygame.font.Font(size=20).render("ⓘ You are not allowed to reproduce this game.", True, (0, 0, 0))

       self.game.screen.blit(self.credits, (250, 300))
       self.game.screen.blit(self.credits1, (250, 400))
       self.backtm_button.draw(self.game.screen)
       if self.backtm_button.clicked:
           self.credits_enabled = False
   
   def updater(self):
        self.renderScreen()
        if self.credits_enabled == False:
            self.renderItems()
        else:
            self.renderCredits()

   def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.isClosed = True
            self.name_input.handle_event(event)
            self.red_slider.handle_event(event)
            self.green_slider.handle_event(event)
            self.blue_slider.handle_event(event)
            self.settings_button.handle_event(event)
            self.credits_button.handle_event(event)
            self.backtm_button.handle_event(event)
        self.updater()
        pygame.display.flip()


   def exit(self):
        return self.FINAL_name, self.FINAL_color
    

class Game:
    def __init__(self, wnx, wny):
        self.wnx = wnx
        self.wny = wny
        self.previous_state = []
        self.current_state = []
        self.all_walls = []
        self.player_data = None
        self.keys = pygame.key.get_pressed()
        self.clock = pygame.time.Clock()  # Pygame clock to control FPS
        self.fps = 60  # Set the target FPS
        self.last_update_time = pygame.time.get_ticks()
        self.to_send_name = ''
        self.to_send_color = ()
        self.is_sliding = False
        self.logo = pygame.image.load('assets/images/ga_logo.jpg')
        sio.on('mydata', self.get_my_data, namespace='/game') 
        sio.on('gameStateUpdate', self.get_game_data, namespace='/game')
        sio.on('disconnect', self.disconnect, namespace='/game')
        
        self.screen = pygame.display.set_mode((self.wnx, self.wny), pygame.RESIZABLE)
        self.maximize_window()
        pygame.display.set_caption("Galaxy Aim")
        self.loadTextures()
        self.menu = Menu(self)

        

    def maximize_window(self):
        hwnd = pygame.display.get_wm_info()['window']  # Get window handle
        ctypes.windll.user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE (3)

    def runMenu(self):
        while self.menu.isRunning:
            self.menu.run()
            if self.menu.isClosed:
                return "leave"
        
        self.to_send_name, self.to_send_color = self.menu.exit()
        return "continue"

    def loadTextures(self):
        self.menu_bg = pygame.transform.scale(pygame.image.load('assets/images/bg.jpg').convert(), (self.wnx+100, self.wny+100))
        self.settings_bg = pygame.transform.scale(pygame.image.load('assets/images/settings_bg.jpg').convert(), (470, 400))
        self.pl_lvl_1 = pygame.image.load('assets/images/lvl1_pl.png').convert_alpha()
        self.pl_lvl_2 = pygame.image.load('assets/images/lvl2_pl.png').convert_alpha()
        self.pl_lvl_3 = pygame.image.load('assets/images/lvl3_pl.png').convert_alpha()
        self.player_images = {"1":self.pl_lvl_1,
                              "2":self.pl_lvl_2,
                              "3":self.pl_lvl_3}
        self.bullet_images = {
            "1":{
                "s":pygame.image.load('assets/images/bullets/lvl1/s.jpg'),
                "m":pygame.image.load('assets/images/bullets/lvl1/m.jpg'),
                "e":pygame.image.load('assets/images/bullets/lvl1/e.jpg')
            }
        }
        

    def createScreen(self):
        try:
            sio.connect('http://localhost:3001', namespaces=['/game'])
        except Exception as e:
            print(f"Failed to connect to the server: {e}")

        data = {'color': self.to_send_color, 'name': self.to_send_name}
        sio.emit('userdata', data, namespace='/game')
            
        
    
    def renderScreen(self):
        # Clear the screen with a base color
        self.screen.fill((20, 20, 20))
        pygame.display.set_icon(self.logo)
        pygame.display.update()

        # Define grid spacing and line color
        grid_spacing = 50  # Distance between grid lines
        line_color = (40, 40, 40)  # Light gray color for grid lines

        # Calculate the offset for grid lines based on player's position
        player_x = self.player_data['x'] if self.player_data else 0
        player_y = self.player_data['y'] if self.player_data else 0

        offset_x = player_x % grid_spacing
        offset_y = player_y % grid_spacing

        # Draw vertical grid lines
        for x in range(-grid_spacing, self.wnx + grid_spacing, grid_spacing):
            pygame.draw.line(self.screen, line_color, 
                            (x - offset_x, 0), (x - offset_x, self.wny))

        # Draw horizontal grid lines
        for y in range(-grid_spacing, self.wny + grid_spacing, grid_spacing):
            pygame.draw.line(self.screen, line_color, 
                            (0, y - offset_y), (self.wnx, y - offset_y))




    def updater(self):
        self.renderScreen()
        self.keys = pygame.key.get_pressed()

        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.last_update_time

        self.draw_data()
        self.send_inputs()
        self.send_angle()
        self.send_bullets()
       

    def sliding(self):
        pass


    def draw_data(self):
        if not self.player_data or not self.current_state:
            return 


        for wall in self.all_walls:
            # Calculate relative position of the wall to the player
            relative_x = wall[0] - self.player_data['x']
            relative_y = wall[1] - self.player_data['y']

            # Translate to screen coordinates
            x = self.wnx / 2 + relative_x
            y = self.wny / 2 + relative_y

            # Check if the wall is within the visible screen area
            if -wall[2] < x < self.wnx and -wall[3] < y < self.wny:
                pygame.draw.rect(self.screen, (10, 10, 10), (x, y, wall[2], wall[3]))
                pygame.draw.rect(self.screen, (100, 100, 100), (x, y, wall[2], wall[3]), 2)
        
        for player in self.current_state:
            for bullet in player['bullets']:
                if isinstance(bullet, dict) and 'x' in bullet and 'y' in bullet:
                    relative_x = bullet['x'] - self.player_data['x']
                    relative_y = bullet['y'] - self.player_data['y']
                    x = self.wnx / 2 - bullet['r']/2 + relative_x
                    y = self.wny / 2 - bullet['r']/2 + relative_y
                    owner = next((p for p in self.current_state if p['id'] == bullet['ownerId']), None)
                    color = owner['color'] if owner else 'white'
                    pygame.draw.circle(self.screen, color, (x, y), bullet['r'])
                    pygame.draw.circle(self.screen, 'white', (x, y), bullet['r'], width=2)
                    #self.screen.blit(pygame.transform.scale(self.bullet_images[str(player['level'])]['m'], (bullet['r']*3, bullet['r']*3)), (x, y))






        current_time = current_time_ms()
        interpolation_factor = min(1.0, max(0.0, (current_time - self.state_timestamp) / (1000 / self.fps)))
        interp_x = 0
        interp_y = 0
        aura_surface = pygame.Surface((self.wnx, self.wny), pygame.SRCALPHA)
        pygame.draw.circle(aura_surface, (self.player_data['color'][0], self.player_data['color'][1], self.player_data['color'][2], 50), (self.wnx/2, self.wny/2), self.player_data['w']/1.5)
        for obj in self.current_state:
            if obj['id'] != self.player_data['id']:
                if self.previous_state:
                    prev_obj = next((p for p in self.previous_state if p['id'] == obj['id']), None)
                    if prev_obj:
                        interp_x = prev_obj['x'] + (obj['x'] - prev_obj['x']) * interpolation_factor
                        interp_y = prev_obj['y'] + (obj['y'] - prev_obj['y']) * interpolation_factor
                    else:
                        interp_x, interp_y = obj['x'], obj['y']
                else:
                    interp_x, interp_y = obj['x'], obj['y']

                relative_x = interp_x - self.player_data['x']
                relative_y = interp_y - self.player_data['y']
                x = self.wnx / 2 - obj['w']/2 + relative_x
                y = self.wny / 2 - obj['h']/2 + relative_y
                player_rect = pygame.Rect(x, y, obj['w'], obj['h'])
                pygame.draw.circle(aura_surface, (obj['color'][0], obj['color'][1], obj['color'][2], 50), (player_rect.centerx, player_rect.centery), player_rect.w/1.5)
                opl_img = self.player_images[str(obj['level'])]
                opl_img_resized = pygame.transform.scale(opl_img, (player_rect.w, player_rect.h))
                opl_img_rotated = pygame.transform.rotate(opl_img_resized, obj['angle'] - 90)
                rotated_rect = opl_img_rotated.get_rect(center=(x + player_rect.w // 2, y + player_rect.h // 2))
                self.screen.blit(opl_img_rotated, rotated_rect.topleft)
                their_name = pygame.font.Font(size=20).render(obj['name'], True, (100, 100, 100))
                self.screen.blit(their_name, (x+obj['w']/2 - their_name.get_width()/2, y+obj['h'] + 20))


                

        self.screen.blit(aura_surface, (0, 0))
        pl_img = self.player_images[str(self.player_data['level'])]
        pl_img_resized = pygame.transform.scale(pl_img, (self.player_data['w'], self.player_data['h']))
        pl_img_rotated = pygame.transform.rotate(pl_img_resized, self.player_data['angle'] - 90)
        rotated_rect = pl_img_rotated.get_rect(center=(self.wnx / 2, self.wny / 2))
        self.screen.blit(pl_img_rotated, rotated_rect.topleft)
        our_name = pygame.font.Font(size=20).render(self.player_data['name'], True, (100, 100, 100))
        self.screen.blit(our_name, (self.wnx / 2 - our_name.get_width()/2, self.wny / 2 + 65))


    def send_inputs(self):
        if(self.keys[pygame.K_UP] or self.is_sliding): # will make/improve/use sliding later
            sio.emit('playerInput', namespace='/game')

    def send_bullets(self):
        pass
            

    def send_angle(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calculate the player's center position (middle of the screen)
        player_x = self.wnx / 2
        player_y = self.wny / 2

        # Calculate the angle using the arctangent of the difference in positions
        angle = math.degrees(math.atan2(player_y - mouse_y, mouse_x - player_x))

        # Emit the angle to the server
        sio.emit('playerAngle', angle, namespace='/game')

    

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sio.disconnect()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    sio.emit('bullet', namespace='/game')
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                         self.is_sliding = not self.is_sliding
            self.updater()
            pygame.display.flip()
            self.clock.tick(self.fps)

    # SERVER RECEIVING
    def disconnect(self, *args):
        sio.emit('disconnect_notice', namespace='/game')
        print("Disconnected from the server.")
        pygame.quit()
        sys.exit()
    
    def get_my_data(self, data):
        self.player_data = data


    def get_game_data(self, data):
        self.previous_state = self.current_state.copy()
        self.current_state = data['state']
        try:
            self.player_data = next(p for p in self.current_state if p['id'] == self.player_data['id'])
        except (StopIteration, KeyError, TypeError):
            print("Player data sync failed: player ID not found or invalid data structure.")
        self.state_timestamp = data['timestamp']
        self.all_walls = data['walls']






    
    
    #-----------------


if __name__ == "__main__":
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    if game.runMenu() == "continue":
        game.createScreen()
        game.run()


