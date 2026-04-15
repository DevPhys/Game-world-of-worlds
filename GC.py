import pygame, os, json, random
from dataclasses import dataclass
from typing import Optional, Callable

errors_log = set()
print("Оболочка Game cover (GC) (версия 1.0.0)")

def safe_call(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"Error -> {func.__name__}: {e}"
            if error_msg not in errors_log:
                print(error_msg)
                errors_log.add(error_msg)
    return wrapper

class Screen:
        display = None
        clock = None
        dt_value = 0
        fps = 45

        @staticmethod
        @safe_call
        def update_dt():
            Screen.dt_value = Screen.clock.tick(Screen.fps) / 1000
            return Screen.dt_value

        @staticmethod
        @safe_call
        def dt(num):
            return num * Screen.dt_value

        @staticmethod
        @safe_call
        def scene(list_x, list_y, list_textures, list_bl, list_eff, sound_list):
            # Упаковываем списки в один итерируемый объект
            data = zip(list_x, list_y, list_textures, list_bl, list_eff, sound_list)

            for i, (x, y, tex, is_btn, eff, snd) in enumerate(data):
                if not is_btn:
                    Interface.draw(tex, x, y)
                elif Interface.button(tex, x, y, eff, snd):
                    return f"click{i}"
            return ""

        @staticmethod
        @safe_call
        def size(width, height):
            pygame.init()
            pygame.mixer.init()

            Screen.display = pygame.display.set_mode((width, height))
            Screen.clock = pygame.time.Clock()

        @staticmethod
        @safe_call
        def full_size(bl):
            pygame.init()
            pygame.mixer.init()

            info = pygame.display.Info()
            screen_width = info.current_w
            screen_height = info.current_h

            Screen.display = pygame.display.set_mode((screen_width, screen_height),
                                                     pygame.FULLSCREEN | pygame.DOUBLEBUF)
            Screen.clock = pygame.time.Clock()

            if bl:
                return screen_width,screen_height

        @staticmethod
        @safe_call
        def FPS(fps):
            Screen.fps = fps
            if Screen.clock:
                Screen.clock.tick(Screen.fps)

        @staticmethod
        @safe_call
        def update():
            pygame.display.update()

        @staticmethod
        @safe_call
        def quit():
            pygame.quit()

        @staticmethod
        @safe_call
        def fade_in_out(width, height, start_alpha, end_alpha, step=5):
            fade = pygame.Surface((width, height))
            fade.fill((0, 0, 0))
            # Если start_alpha 255, а end_alpha 0 — будет появление из темноты
            for alpha in range(start_alpha, end_alpha, step if start_alpha < end_alpha else -step):
                fade.set_alpha(alpha)
                Screen.display.blit(fade, (0, 0))
                pygame.display.update()
                pygame.time.delay(20)

        @staticmethod
        @safe_call
        def shaking(bg):

            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            Interface.draw(bg, offset_x, offset_y)

@dataclass
class SceneElement:
    x: int
    y: int
    texture: any
    is_button: bool = False
    effect: bool = False
    sound: bool = None
    id: str = ""

class SceneManager:

    @staticmethod
    @safe_call
    def scene(elements: list[SceneElement]) -> str:
        for i, el in enumerate(elements):
            if not el.is_button:
                Interface.draw(el.texture, el.x, el.y)
            else:
                # Передаем параметры объекта
                clicked = Interface.button(
                    el.texture, el.x, el.y, el.effect, el.sound
                )
                if clicked:
                    return el.id or f"click{i}"
        return ""

class Keyboard:
        mx = 0
        my = 0

        last_key = None  # ОБЯЗАТЕЛЬНО добавь эту строчку здесь!
        # Словарь для хранения времени начала отсчета для разных комбинаций
        _timers = {}
        keys_map = {
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "space": pygame.K_SPACE,
            "esc": pygame.K_ESCAPE,
            "enter": pygame.K_RETURN,
            "a": pygame.K_a,
            "d": pygame.K_d,
            "w": pygame.K_w,
            "s": pygame.K_s,
            "num8": pygame.K_KP8,
            "num4": pygame.K_KP4,
            "num6": pygame.K_KP6,
            "num5": pygame.K_KP5,
            "num2": pygame.K_KP2,
            "num9": pygame.K_KP9,
            "num7": pygame.K_KP7,
            "num1": pygame.K_KP1,
            "num3": pygame.K_KP3,
            "1": pygame.K_1,
            "2": pygame.K_2,
            "3": pygame.K_3,
            "4": pygame.K_4,
            "5": pygame.K_5,
            "6": pygame.K_6,
            "7": pygame.K_7,
            "8": pygame.K_8,
            "9": pygame.K_9,
            "0": pygame.K_0,
        }

        @staticmethod
        @safe_call
        def get_scroll():
            if pygame.event.peek(pygame.MOUSEBUTTONDOWN):

                for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
                    if event.button == 4: return 1  # Скролл вверх
                    if event.button == 5: return -1 # Скролл вниз
            return 0

        @staticmethod
        @safe_call
        def mouse_pressed(button_index):
            # button_index: 0 - левая, 1 - средняя (колесико), 2 - правая
            return pygame.mouse.get_pressed()[button_index]

        @staticmethod
        @safe_call
        def event_sequence(key1, key2, timeout=1000):
            """
            Проверяет нажатие key1, а затем key2 в течение timeout (мс).
            Возвращает: True (успех), False (не успели), None (в процессе или ничего).
            """
            now = pygame.time.get_ticks()
            combo_id = f"{key1}_{key2}"  # Уникальный ключ для этой пары кнопок

            first_pressed = Keyboard.event_once(key1)
            second_pressed = Keyboard.event_once(key2)

            # 1. Если нажали первую кнопку — запускаем таймер
            if first_pressed:
                Keyboard._timers[combo_id] = now
                return None

            # 2. Если таймер запущен, проверяем вторую кнопку и время
            if combo_id in Keyboard._timers:
                start_time = Keyboard._timers[combo_id]

                # Если превысили время
                if now - start_time > timeout:
                    del Keyboard._timers[combo_id]
                    return False

                # Если нажали вторую кнопку вовремя
                if second_pressed:
                    del Keyboard._timers[combo_id]
                    return True

            return None

        @staticmethod
        @safe_call
        def event(key_name):
            pygame.event.pump()

            all_keys = pygame.key.get_pressed()
            pygame_key = Keyboard.keys_map.get(key_name.lower())

            if pygame_key and all_keys[pygame_key]:
                return True

            return False

        @staticmethod
        @safe_call
        def event_once(key_name):
            is_down = Keyboard.event(key_name)

            if is_down and Keyboard.last_key != key_name:
                Keyboard.last_key = key_name
                return True

            if not is_down and Keyboard.last_key == key_name:
                Keyboard.last_key = None

            return False

        @staticmethod
        @safe_call
        def mouse(num,bl=False):
            if pygame.mouse.get_pressed()[num]:  # Левая кнопка мыши
                Interface.mx, Interface.my = pygame.mouse.get_pos()
                return True

        @staticmethod
        @safe_call
        def coordinat_mouse():
            Interface.mx, Interface.my = pygame.mouse.get_pos()
            return Interface.mx, Interface.my

class Interface:
        was_pressed = False
        hover_cache = {}  # Кэш для хранения уже готовых подсвеченных кнопок
        x = 0

        @staticmethod
        @safe_call
        def sprit(sheet, padding=1, min_size=10):
            # 1. Создаем маску
            mask = pygame.mask.from_surface(sheet)

            # 2. ВАЖНО: Заполняем "дырки" внутри кнопок.
            # Это заставит маску считать полые прямоугольники цельными объектами.
            mask.convolve(pygame.mask.Mask((3, 3), fill=True))

            # 3. Получаем области
            raw_rects = mask.get_bounding_rects()

            # 4. Алгоритм склейки (теперь работает до победного)
            merged = True
            while merged:
                merged = False
                new_rects = []
                while raw_rects:
                    curr = raw_rects.pop(0)
                    found = False
                    for i, r in enumerate(new_rects):
                        # Для кнопок padding можно сделать чуть больше
                        if r.inflate(padding * 2, padding * 2).colliderect(curr):
                            new_rects[i] = r.union(curr)
                            found = True
                            merged = True
                            break
                    if not found:
                        new_rects.append(curr)
                raw_rects = new_rects

            # 5. Сортируем кнопки сверху вниз, слева направо
            raw_rects.sort(key=lambda r: (r.y, r.x))

            buttons = []
            for r in raw_rects:
                if r.width >= min_size and r.height >= min_size:
                    # Вырезаем кнопку именно по её РЕАЛЬНОМУ размеру,
                    # не вписывая в квадрат 64x64, чтобы не портить пропорции
                    btn_surf = pygame.Surface(r.size, pygame.SRCALPHA)
                    btn_surf.blit(sheet, (0, 0), r)
                    buttons.append(btn_surf)

            return buttons

        @staticmethod
        @safe_call
        def button_sound(list_texture,x,y,i,bl_sound):
            if bl_sound:
                if Interface.button( list_texture[i], x, y, True):
                    Sound_mixer.sound_stop()
                    return False

            elif not bl_sound:
                if Interface.button( list_texture[i], x, y,True):
                    Sound_mixer.sound_renewal()

            return True

        @staticmethod
        @safe_call
        def button(texture, x, y, bl, sound=None):
            # Получаем ID объекта, чтобы использовать его как ключ в кэше
            texture_id = id(texture)
            rect = texture.get_rect(topleft=(x, y))
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()[0]

            # Если мышка над кнопкой
            if rect.collidepoint(mouse_pos):
                if bl:
                    # ПРОВЕРКА КЭША: создаем подсветку, только если её еще нет
                    if texture_id not in Interface.hover_cache:
                        hover_img = texture.copy().convert_alpha()  # Не забываем конвертацию!
                        hover_img.fill((60, 60, 60), special_flags=pygame.BLEND_RGB_ADD)
                        Interface.hover_cache[texture_id] = hover_img

                    # Рисуем готовую картинку из кэша (0% нагрузки на расчеты)
                    Screen.display.blit(Interface.hover_cache[texture_id], rect)
                else:
                    Screen.display.blit(texture, rect)

                # Логика клика
                if mouse_click:
                    if not Interface.was_pressed:
                        Interface.was_pressed = True
                        if sound is not None:
                            Sound_mixer.sound_effect(5, sound)
                        return True
                else:
                    Interface.was_pressed = False
            else:
                # Мышка не на кнопке — просто рисуем оригинал
                Screen.display.blit(texture, rect)
                # Сбрасываем флаг нажатия, если мышка ушла с кнопки
                if not mouse_click:
                    Interface.was_pressed = False

            return False

        @staticmethod
        @safe_call
        def fill_color(a,d,c):
            Screen.display.fill((a,d,c))

        @staticmethod
        @safe_call
        def mixing_color(list_1, list_2):
            a = min(255, int(list_1[0]) + int(list_2[0]))
            b = min(255, int(list_1[1]) + int(list_2[1]))
            c = min(255, int(list_1[2]) + int(list_2[2]))

            Screen.display.fill((a,b,c))

        @staticmethod
        @safe_call
        def draw(texture_name, x, y):
            Screen.display.blit(texture_name,(x,y))

        @staticmethod
        @safe_call
        def transform(texture_name, size):
            return pygame.transform.scale(texture_name, size)

        @staticmethod
        @safe_call
        def transform_flip(texture_name,flip_x,flip_y):
            return pygame.transform.flip(texture_name, flip_x, flip_y)

        @staticmethod
        @safe_call
        def bg_infinity_forward(bg,speed,bl):
            bg_width = bg.get_width()

            if bl:
                Interface.x -= speed

            if Interface.x <= -bg_width:
                Interface.x = 0

            Interface.draw(bg,Interface.x,0)
            Interface.draw(bg,(Interface.x + bg_width),0)

        @staticmethod
        @safe_call
        def bg_infinity_back(bg,speed,bl):
            bg_width = bg.get_width()

            if bl:
                Interface.x += speed

            if Interface.x >= bg_width:
                Interface.x = 0

            Interface.draw(bg,Interface.x,0)
            Interface.draw(bg,(Interface.x - bg_width),0)

class Sound_mixer:

        @staticmethod
        @safe_call
        def sound_effect(volume,effect):    #volume принимается от 1 до 10
            effect.set_volume(volume / 10)
            effect.play()

        @staticmethod
        @safe_call
        def sound_infinity(volume,sound):    #volume принимается от 1 до 10
            sound.set_volume(volume / 10)
            sound.play(loops=-1)

        @staticmethod
        @safe_call
        def sound_pause():
            pygame.mixer.pause()

        @staticmethod
        @safe_call
        def sound_renewal():
            pygame.mixer.unpause()

        @staticmethod
        @safe_call
        def sound_stop():
            pygame.mixer.stop()

class Font:

        @staticmethod
        @safe_call
        def text_sitting(font,size):
            return pygame.font.Font(font,size)

class Text:
    rendered_cache = {}  # Здесь будем хранить готовые картинки
    cache = {}

    @staticmethod
    @safe_call
    def write(text_write, size, x, y, color=(0, 0, 0)):
        # Создаем уникальный ключ для конкретной строки и её параметров
        content_key = f"{text_write}_{size}_{color}"

        if content_key not in Text.rendered_cache:
            # Если такой картинки еще нет в кэше — создаем её
            font_key = f"default_{size}"
            if font_key not in Text.cache:
                Text.cache[font_key] = Font.text_sitting(None, size)

            # Рендерим и СРАЗУ конвертируем для GPU
            img = Text.cache[font_key].render(str(text_write), True, color).convert_alpha()
            Text.rendered_cache[content_key] = img

        # Рисуем уже готовую картинку из кэша
        Interface.draw(Text.rendered_cache[content_key], x, y)

        @staticmethod
        @safe_call
        def write_font(font_path, text_write, size, x, y, color=(0, 0, 0)):
            key = f"{font_path}_{size}"

            if key not in Text.cache:
                Text.cache[key] = Font.text_sitting(font_path, size)

            text_draw = Text.cache[key].render(str(text_write), True, color)
            Interface.draw(text_draw, x, y)

class Load:

        @staticmethod
        @safe_call
        def load_images_to_dict(folder_name):
            images = {}
            for filename in os.listdir(folder_name):
                if filename.endswith((".png", ".jpg", ".jpeg")):
                    name = os.path.splitext(filename)[0]
                    path = os.path.join(folder_name, filename)
                    images[name] = pygame.image.load(path).convert_alpha()
            return images

        @staticmethod
        @safe_call
        def load_sounds_to_dict(folder_name):
            sounds = {}
            # Проверяем, существует ли папка
            if not os.path.exists(folder_name):
                print(f"Папка {folder_name} не найдена!")
                return sounds

            for filename in os.listdir(folder_name):
                # Поддерживаемые форматы звуков в pygame
                if filename.endswith((".wav", ".mp3", ".ogg")):
                    # Получаем имя файла без расширения (например, 'hit' вместо 'hit.wav')
                    name = os.path.splitext(filename)[0]
                    path = os.path.join(folder_name, filename)

                    # Загружаем звук
                    sounds[name] = pygame.mixer.Sound(path)

            return sounds

        @staticmethod
        @safe_call
        def load(filename):
            return pygame.image.load(filename)

        @staticmethod
        @safe_call
        def load_sound(filename):
            return pygame.mixer.Sound(filename)

class File:

    @staticmethod
    @safe_call
    def save(save_dict, file_name):
        with open(file_name, 'w', encoding='utf-8') as json_file:
            json.dump(save_dict, json_file, ensure_ascii=False, indent=4)

        print(f"Данные успешно сохранены в файл '{file_name}'")

    @staticmethod
    @safe_call
    def read(file_name):
        if not os.path.exists(file_name):
            return {}

        with open(file_name, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)

class Figures:

        @staticmethod
        @safe_call
        def square(size,coordinates,color=(255,0,0)):
            surface = pygame.Surface(size)
            surface.fill(color)
            Screen.display.blit(surface, coordinates)

        @staticmethod
        @safe_call
        def circle(r,coordinates,color=(0,255,0)):
            # pygame.draw.circle(поверхность, цвет, центр, радиус)
            pygame.draw.circle(Screen.display, color, coordinates, r)

        @staticmethod
        @safe_call
        def triangle(angles,color=(0,0,255)):
            # pygame.draw.polygon(где, цвет, [точка1, точка2, точка3])
            pygame.draw.polygon(Screen.display, color, [angles[0],angles[1],angles[2]])

        @staticmethod
        @safe_call
        def line(start_pos,end_pos,width,color=(225,225,225)):
            # pygame.draw.line(где, цвет, старт, финиш, толщина)
            pygame.draw.line(Screen.display, color, start_pos, end_pos, width)

class Hit_box:

        @staticmethod
        @safe_call
        def surface(x,y):
            return pygame.Surface((x,y))

        @staticmethod
        @safe_call
        def rect(x,y,w,h):
            return pygame.Rect(x, y, w, h)

        @staticmethod
        @safe_call
        def touch(rect1, rect2):
            # Магический метод colliderect проверяет касание
            if rect1.colliderect(rect2):
                return True
            return False

        @staticmethod
        @safe_call
        def mask_map(bg):
            bg = bg.convert()

            bg_color = bg.get_at((1, 1))
            bg.set_colorkey(bg_color)

            walk_map = pygame.mask.from_surface(bg)

            if walk_map.count() > (bg.get_width() * bg.get_height() * 0.9):
                walk_map.invert()

            return walk_map

        @staticmethod
        @safe_call
        def draw_rect(rect, color=(255, 0, 0), width=2):    #Рисует тонкую рамку вокруг хитбокса
            pygame.draw.rect(Screen.display, color, rect, width)

        @staticmethod
        @safe_call
        def follow(rect, x, y):     #функция «приклеивает» хитбокс к персонажу
            rect.topleft = (x, y)

        @staticmethod
        @safe_call
        def check_list(player_rect, list_of_rects):     #функция сразу говорит: «Соник коснулся кольца номер 5».
            # Возвращает индекс первого коснувшегося объекта (удобно для колец)
            return player_rect.collidelist(list_of_rects)

        @staticmethod
        @safe_call
        def side_touch(rect1, rect2):       #Определяет, какой стороной произошло столкновение
            if rect1.colliderect(rect2):
                if rect1.bottom <= rect2.centery: return "top"
                if rect1.top >= rect2.centery: return "bottom"
                if rect1.centerx < rect2.centerx: return "right"
                return "left"

        @staticmethod
        @safe_call
        def resize(rect, scale_w, scale_h):     #Раздувает или сжимает хитбокс
            # Делает хитбокс чуть меньше/больше оригинала
            return rect.inflate(scale_w, scale_h)

        @staticmethod
        @safe_call
        def distance(rect1, rect2):     #Считает расстояние между двумя объектами
                # Расстояние между центрами (для логики врагов)
                p1 = pygame.math.Vector2(rect1.center)
                p2 = pygame.math.Vector2(rect2.center)
                return p1.distance_to(p2)

        @staticmethod
        @safe_call
        def is_out(rect):       #Проверяет, не вылетел ли объект за границы экрана
            sw, sh = Screen.display.get_size()
            return rect.right < 0 or rect.left > sw or rect.bottom < 0 or rect.top > sh

        @staticmethod
        @safe_call
        def stick(rect1, rect2, side):      #«Приклеивает» игрока к платформе.
                # "Прилипание" к платформе, чтобы не проваливаться
                if side == "top": rect1.bottom = rect2.top
                if side == "bottom": rect1.top = rect2.bottom

        @staticmethod
        @safe_call
        def mouse_hover(rect):      #Проверяет, наведена ли мышка на объект
            return rect.collidepoint(pygame.mouse.get_pos())

        @staticmethod
        @safe_call
        def checking_masks(mask1, x1, y1, mask2, x2, y2):        #проверка масок
            # Упрощенная проверка масок без мучений с offset
            offset = (x2 - x1, y2 - y1)
            return mask1.overlap(mask2, offset)

class Time:
    wait_until = pygame.time.get_ticks()
    main = True

    @staticmethod
    @safe_call
    def timer(t):
        if Time.main:
            Time.wait_until = pygame.time.get_ticks()
            Time.main = False

        if pygame.time.get_ticks() >= int(Time.wait_until + int(float(t) * 1000)):
            Time.main = True
            return True
        return False

class Random:

    @staticmethod
    @safe_call
    def random_symbols(n):
        symbols = "!@#$%^&*()_+1234567890-=!№;%:?*()/,~{><}[]':;"

        new = ""

        n2 = 0
        while n2 <= n:
            i = Random.random_number(0,len(symbols)-1)
            new += symbols[i]

            n2 += 1
        return new

    @staticmethod
    @safe_call
    def random_number(a,b):
        return random.randint(a,b)

    @staticmethod
    @safe_call
    def random():
        return random.random()

    @staticmethod
    @safe_call
    def randrange(start,stop,step):
        return random.randrange(start,stop,step)

    @staticmethod
    @safe_call
    def uniform(a, b):
        return random.uniform(a, b)

    @staticmethod
    @safe_call
    def choice(sequence):
        return random.choice(sequence)