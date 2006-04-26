import land

land.init()

class Game(land.runner.Runner):

    def init(self):
        self.font = land.text.Font("../../data/DejaVuSans.ttf", 12)

    def tick(self):
        if land.keyboard.pressed(land.keyboard.ESC) or land.closebutton():
            land.quit()

    def draw(self):
        land.display.clear(0, 0, 0, 0)
        land.display.color(1, 1, 1, 1)
        self.font.set_pos(320, 240)
        self.font.write("%d%%" % 100, centered = True)

game = Game()

land.set_display_parameters(640, 480, 32, 100,
    land.display.WINDOWED | land.display.OPENGL)
land.set_initial_runner(game)
land.main()

