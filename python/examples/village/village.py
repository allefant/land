import land

land.init()

class Game(land.runner.Runner):

    def init(self):
        print "Init from python"

    def enter(self):
        print "Enter from python"

    def tick(self):
        if land.keyboard.check(land.keyboard.ESC):
            land.quit()

    def draw(self):
        land.display.color(0.9, 0.7, 0.5)
        mx = land.display.width() / 2
        my = land.display.height() / 2
        r = 100
        land.display.filled_circle(mx - r, my - r, mx + r, my + r)

    def leave(self):
        print "Leave from python"

    def destroy(self):
        print "Destroy from python"

game = Game()

land.set_display_parameters(640, 480, 32, 100,
    land.display.WINDOWED | land.display.OPENGL)
land.set_frequency(60)
land.set_initial_runner(game)
land.main()

