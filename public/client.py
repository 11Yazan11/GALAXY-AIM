from player import *
import threading

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




class Game:
    def __init__(self, wnx, wny, color, name):
        self.wnx = wnx
        self.wny = wny
        self.color = color
        self.name = name
        self.game_state = []
        self.player_data = None
        self.myId = None
        self.keys = pygame.key.get_pressed()
        self.clock = pygame.time.Clock()  # Pygame clock to control FPS
        self.fps = 60  # Set the target FPS

        sio.on('mydata', self.get_my_data, namespace='/game') 
        sio.on('gameStateUpdate', self.get_game_data, namespace='/game')
        sio.on('disconnect', self.disconnect, namespace='/game')

        self.createScreen()
        

    def maximize_window(self):
        hwnd = pygame.display.get_wm_info()['window']  # Get window handle
        ctypes.windll.user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE (3)

    def createScreen(self):
        try:
            sio.connect('http://localhost:3001', namespaces=['/game'])
        except Exception as e:
            print(f"Failed to connect to the server: {e}")

        data = {'color': self.color, 'name': self.name}
        print('emitting user data')
        sio.emit('userdata', data, namespace='/game')
            

        self.screen = pygame.display.set_mode((self.wnx, self.wny), pygame.RESIZABLE)
        self.maximize_window()
        pygame.display.set_caption("Galaxy Aim")
        
    
    def renderScreen(self):
        self.screen.fill((20, 20, 20))

    def updater(self):
        self.renderScreen()
        self.keys = pygame.key.get_pressed()
        self.draw_data()
        self.send_inputs()
        self.send_angle()
        self.send_bullets()
       

    def draw_data(self):
        for obj in self.game_state:
            player = Player(self, obj['x'], obj['y'], obj['w'], obj['h'], obj['color'], obj['name'], obj['angle'], obj['bullets'], obj['kills'], obj['id'])
            player.draw()

    def send_inputs(self):
        sio.emit('playerInput', {
        "id": self.myId,
        "up": self.keys[pygame.K_UP],
        "down": self.keys[pygame.K_DOWN],
        "left": self.keys[pygame.K_LEFT],
        "right": self.keys[pygame.K_RIGHT],
    }, namespace='/game')

    def send_bullets(self):
        pass

    def send_angle(self):
        pass

    

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sio.disconnect()
                    return
            self.updater()
            pygame.display.flip()
            self.clock.tick(self.fps)

    # SERVER RECEIVING
    def disconnect(self, *args):
        if self.myId:
            sio.emit('disconnect_notice', {'id': self.myId}, namespace='/game')
        print("Disconnected from the server.")
        pygame.quit()
        sys.exit()
    
    def get_my_data(self, data):
        self.player_data = data

    def get_game_data(self, data):
        self.game_state = data


    
    
    #-----------------


if __name__ == "__main__":
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT, (255, 0, 0), "Player")
    game.run()



