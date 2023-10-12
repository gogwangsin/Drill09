# 이것은 각 상태들을 객체로 구현한 것임.
import math

from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDL_KEYUP, SDLK_RIGHT, SDLK_LEFT, SDLK_a


# true false 단위로 리턴 ==
def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def time_out(e):
    return e[0] == 'TIME_OUT'


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def key_a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a





class Idle:

    @staticmethod
    def enter(boy, e):  # idle상태가 시작됐을 때 시작을 세서 time_out 이벤트를 발생시켜야함
        if boy.action == 0:
            boy.action = 2
        elif boy.action == 1:
            boy.action = 3
        boy.dir = 0
        boy.wait_time = get_time()  # 경과 시간 얻는법 -> pico2d 시작하면 0초고 게임 시작 시간부터 시간 잼
        boy.frame = 0
        print('Idle Enter')

    @staticmethod
    def exit(boy, e):
        print('Idle Exit')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.wait_time > 3:  # 경과시간에서 보이 시작 시간 빼기 - 차이가 3초가 넘으면
            boy.state_machine.handle_event(('TIME_OUT', 0))  # 타임아웃이 넘어감

        # print('Idle Do')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        # frame 가로 이미지, action 몇 층인지


class Sleep:

    @staticmethod
    def enter(boy, e):
        boy.frame = 0
        print('눕다')

    @staticmethod
    def exit(boy, e):
        print('일어선다')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        print('드르렁')

    @staticmethod
    def draw(boy):

        if boy.action == 2:
            boy.image.clip_composite_draw(boy.frame * 100, 200, 100, 100,
                                          math.pi / 2, '', boy.x - 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(boy.frame * 100, 300, 100, 100,
                                          math.pi / 2, '', boy.x - 25, boy.y - 25, 100, 100)

            # 계산 하는 것 보다 누운 이미지를 갖고 있으면 그걸 쓰자 - 불필요한 계산
        # frame 가로 이미지, action 몇 층인지


class Run:

    @staticmethod
    def enter(boy, e):  # entry action - 어떤 키가 눌렸는지
        if right_down(e) or left_up(e):  # 오른쪽으로 run -> up: 둘다 눌렀을 때 안되도록 , 왼쪽부터 검사하잖음
            boy.dir, boy.action = 1, 1
        if left_down(e) or right_up(e):  # 왼쪽
            boy.dir, boy.action = -1, 0

        print('달린다')

    @staticmethod
    def exit(boy, e):
        print('멈춘다.')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5
        print('달린다')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)


class AutoRun:

    @staticmethod
    def enter(boy, e):  # entry action - 어떤 키가 눌렸는지
        if boy.action == 2:
            boy.dir, boy.action = -1, 0
        elif boy.action == 3:
            boy.dir, boy.action = 1, 1

        boy.wait_time = get_time()  # 경과 시간 얻는법 -> pico2d 시작하면 0초고 게임 시작 시간부터 시간 잼
        boy.frame = 0
        print('커지고 속도가 빨라진다')

    @staticmethod
    def exit(boy, e):
        print('무적 런이 꺼진다.')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 0.1
        if get_time() - boy.wait_time > 5:  # 경과시간에서 보이 시작 시간 빼기 - 차이가 3초가 넘으면
            boy.state_machine.handle_event(('TIME_OUT', 0))  # 타임아웃이 넘어감
        else:
            print('자동 무적 런 하는중')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)





class StateMachine:
    def __init__(self, boy):
        self.boy = boy
        self.cur_state = Idle # 기본 idle 상태
        self.transitions = {
            Idle: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, time_out: Sleep, key_a_down: AutoRun},
            # idle 상태에서 a키
            Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle},
            Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Idle},
            AutoRun: {time_out: Idle}
        }

    def start(self):
        self.cur_state.enter(self.boy, ('START', 0))

    def handle_event(self, e):
        for check_event, next_state in self.transitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.boy, e)
                self.cur_state = next_state
                self.cur_state.enter(self.boy, e)
                return True

        return False

    def update(self):
        self.cur_state.do(self.boy)

    def draw(self):
        self.cur_state.draw(self.boy)  # 소년 이미지, 소년 위치를 알아야 그리지요.


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)  # 소년객체 정보 주기
        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event): # 이벤트 받고
        print(event)
        self.state_machine.handle_event(('INPUT', event)) # input으로 들어가고

    def draw(self):
        self.state_machine.draw()
