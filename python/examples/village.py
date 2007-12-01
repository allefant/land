#!/usr/bin/env python
import land, random

land.init()

class Game(land.runner.Runner):

    def init(self):
        print "Init from python"
        self.image = land.image.Image(72, 72)
        land.display.select_image(self.image)
        mx = 16; my = 16; r = 16
        land.display.clear(1, 1, 1, 0)
        land.display.color(0, 0, 0, 1)
        land.display.filled_circle(mx - r, my - r, mx + r, my + r)
        land.display.unselect_image()

        w = 640 / 32
        h = 480 / 32
        self.jitter = []
        for k in range(w * h):
            self.jitter += [(0, 0)]

    def enter(self):
        print "Enter from python"

    def tick(self):
        if land.keyboard.pressed(land.keyboard.ESC) or land.closebutton():
            land.quit()
        w = 640 / 32
        h = 480 / 32

      
        for k in range(w * h):
            x, y = self.jitter[k]
            self.jitter[k] = (x + random.random() - 0.5, y + random.random() - 0.5)

    def draw(self):
        land.display.clear(0.7, 0.1, 0, 0)
        mx = land.display.width() / 2
        my = land.display.height() / 2

        k = 0
        for i in range(640 / 32):
            for j in range(480 / 32):
                self.image.draw(i * 32 + self.jitter[k][0], j * 32 + self.jitter[k][1], a = 0.1)
                self.image.draw(320 + self.jitter[k][0], 240 + self.jitter[k][1], a = 0.5)
                k += 1

    def leave(self):
        print "Leave from python"

    def destroy(self):
        print "Destroy from python"

game = Game()

land.set_display_parameters(640, 480, 32, 100,
    land.display.WINDOWED | land.display.OPENGL)
land.set_frequency(100)
land.set_initial_runner(game)
land.main()

