import random
from pico2d import load_image
from pico2d import *

from state_machine import (StateMachine, time_out, space_down, right_up, left_down, right_down, left_up, \
    start_event, a_down)


class Idle:
    @staticmethod
    def enter(boy, e):
        if left_up(e) or right_down(e):
            boy.action = 2
            boy.face_dir = -1
        elif right_up(e) or left_down(e) or start_event(e):
            boy.action = 3
            boy.face_dir = 1

        boy.frame = 0
        boy.dir = 0
        boy.start_time = get_time()

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.start_time > 1:
            boy.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)


class Sleep:
    @staticmethod
    def enter(boy, e):
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:
            boy.image.clip_composite_draw(
                boy.frame * 100, 300, 100, 100,
                3.141592 / 2, ' ', boy.x - 25, boy.y - 25, 100, 100
            )
        elif boy.face_dir == -1:
            boy.image.clip_composite_draw(
                boy.frame * 100, 200, 100, 100,
                -3.141592 / 2, ' ', boy.x + 25, boy.y - 25, 100, 100
            )


class Run:
    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e):
            boy.action = 1
            boy.dir = 1
        elif left_down(e) or right_up(e):
            boy.action = 0
            boy.dir = -1

        boy.frame = 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 3

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(
            boy.frame * 100, boy.action * 100, 100, 100,
            boy.x, boy.y
        )


class AutoRun:
    @staticmethod
    def enter(boy, e):
        boy.frame = 0
        boy.start_time = get_time()
        boy.auto_speed = 6
        boy.auto_dir = random.choice([-1, 1])
        boy.size = 200

    @staticmethod
    def exit(boy, e):
        boy.size = 100
        boy.auto_speed = 3
        if boy.auto_dir == 1:
            boy.dir = 1
        elif boy.auto_dir == -1:
            boy.dir = -1

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        screen_wid = 800
        boy.x += boy.auto_dir * boy.auto_speed

        if boy.x < 0:
            boy.x = 0
            boy.auto_dir = 1
        elif boy.x > screen_wid:
            boy.x = screen_wid
            boy.auto_dir = -1

        if get_time() - boy.start_time > 5:
            boy.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(boy):
        if boy.auto_dir == - 1:
            boy.image.clip_draw(
            boy.frame * 100, 0, 100, 100,
            boy.x, boy.y + 25, boy.size, boy.size
            )
        elif boy.auto_dir == 1:
            boy.image.clip_draw(
                boy.frame * 100, 100, 100, 100,
                boy.x, boy.y + 25, boy.size, boy.size
            )


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start(Idle)
        self.size = 100
        self.state_machine.set_transitions(
            {
                Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep, a_down: AutoRun},
                Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle, a_down: AutoRun},
                Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Idle},
                AutoRun: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle, time_out: Idle}
            }
        )

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.add_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
