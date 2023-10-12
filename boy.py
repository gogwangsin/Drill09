# 이것은 각 상태들을 객체로 구현한 것임.
import math

from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDL_KEYUP, SDLK_RIGHT, SDLK_LEFT, SDLK_a


# true false 단위로 리턴 ==
def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def time_out(e):
    return e[0] == 'TIME_OUT'


def time_out_5(e):
    return e[0] == 'TIME_OUT' and e[1] == 5.0


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
            boy.action = 2 # 왼쪽 멈춤
        elif boy.action == 1:
            boy.action = 3 # 우측 멈춤
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
            boy.state_machine.handle_event(('TIME_OUT', 0))  # 타임아웃 이벤트 발생

        # print('Idle Do')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        # frame 가로 이미지, action 몇 층인지
        pass


class Sleep:

    @staticmethod
    def enter(boy, e):
        boy.frame = 0
        print('눕다')

    @staticmethod
    def exit(boy, e):
        print('일어서기')

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
        pass


class Run:

    @staticmethod
    def enter(boy, e):  # entry action - 어떤 키가 눌렸는지
        if right_down(e) or left_up(e):  # 오른쪽으로 run -> up: 둘다 눌렀을 때 안되도록 , 왼쪽부터 검사하잖음
            boy.dir, boy.action = 1, 1
        if left_down(e) or right_up(e):  # 왼쪽
            boy.dir, boy.action = -1, 0

        print('달리기 준비')

    @staticmethod
    def exit(boy, e):
        print('달리기 멈추기')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 5 # IDLE 0이면 정지 -> 양수면 우측
        print('달리기')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass



class AutoRun:

    @staticmethod
    def enter(boy, e):  # entry action - 어떤 키가 눌렸는지
        if boy.action == 2:
            boy.dir, boy.action = -1, 0
        elif boy.action == 3:
            boy.dir, boy.action = 1, 1

        boy.wait_time = get_time()  # 경과 시간 얻는법 -> pico2d 시작하면 0초고 게임 시작 시간부터 시간 잼
        boy.frame = 0
        print('몸집이 커지고 속도가 빨라진다')

    @staticmethod
    def exit(boy, e):
        print('무적 런이 꺼진다.')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * 0.1 # 속도 느리게 설정중
        if get_time() - boy.wait_time > 5:  # 경과시간에서 보이 시작 시간 빼기 - 차이가 3초가 넘으면
            boy.state_machine.handle_event(('TIME_OUT', 0))  # 타임아웃이 넘어감
        else:
            print('자동 무적 런 하는중')

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y + 40, 200, 200)




class StateMachine:
    def __init__(self, boy):
        self.boy = boy
        self.cur_state = Idle # 기본 idle 상태
        # 딕셔너리 -> Sleep상태에서 space 들어오면 idle상태가 된다.
        self.transitions = {
            # Idle에서 키 검사 +  time_out 검사
            Idle: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, time_out: Sleep, key_a_down: AutoRun},
            # 가만히 있는데 키를 떼면 run -> up은 있을 수 없음
            Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Idle},
            # 자고 있는중에 space
            Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle}, # value가 idle
            # 달리고 있는중 down키가 들어오면 idle화 -> 방향키 왼쪽 오른쪽 두번 들어온거
            # -> 달리고 있는 상태 Run에서 키 입력 들어오면 멈춤 idle
            # 달리고 있는중 떼면 idle화
            AutoRun: {time_out: Idle}
        }

    def start(self): # 시작 entry action 'key == START', event값 0 아직 안씀
        self.cur_state.enter(self.boy, ('START', 0))

    def handle_event(self, e):
        # 이벤트가 발생했을 때 상태를 바꿔주면 된다.
        # self table { dictionary } -> 현재 cur_state == sleep, 이놈의 items는 spacedown, idle
        for check_event, next_state in self.transitions[self.cur_state].items():
            # -> [Idle].items() : key = right_down부터 value = Run을 순서대로 불러와서 if(right_down)인지 검사하고
            # true면 상태 바꾸기
            if check_event(e):  # space_down이 true면
                self.cur_state.exit(self.boy, e)  # 상태 바뀌기 전에 Exit action, event정보를 e로 전달
                self.cur_state = next_state  # Idle 상태로 다음 과정으로 넘어간다.
                self.cur_state.enter(self.boy, e)  # 바뀐 상태일 때 entry action
                return True  # 상태변환 성공

        return False  # 위에가 실패하면 False -> 나중에 디버깅할 때 유리해진다.

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
        pass

    def draw(self):
        self.state_machine.draw()
