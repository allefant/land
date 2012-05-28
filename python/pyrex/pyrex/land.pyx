import runner

class LandException(Exception):
    def __init__(self, text):
        self.text = text
    def __str__(self):
        return self.text

def version():
    return (0, 0, 0, "SVN", "0.0.0 (SVN Revision 41)")

class Shortcut(runner.Runner):
    def __init__(self, init, tick, draw, exit):
        self.init_cb = init
        self.tick_cb = tick
        self.draw_cb = draw
        self.exit_cb = exit
    
    def init(self):
        if self.init_cb: self.init_cb()

    def tick(self):
        import main, keyboard
        if keyboard.pressed(keyboard.ESC): main.quit()
        if main.closebutton(): main.quit()
        if self.tick_cb: self.tick_cb()

    def draw(self):
        if self.draw_cb: self.draw_cb()

    def destroy(self):
        if self.exit_cb: self.exit_cb()

def run(w = 640, h = 480, depth = 0, refresh = 0, rate = 60,
    init = None, tick = None, draw = None, exit = None):
    import display
    main.init()
    main.set_display_parameters(w, h, depth, refresh,
        display.WINDOWED | display.OPENGL)
    main.set_frequency(rate)
    shortcut = Shortcut(init, tick, draw, exit)
    main.set_initial_runner(shortcut)
    main.main()