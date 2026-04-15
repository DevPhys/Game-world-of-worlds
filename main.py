import GC # Делаем обычный импорт для связи с переменными FPS
from GC import * # Импортируем собственную библиотеку
import pygame # Иногда пригождаеться
import numpy as np # Для более быстрых вычислений
import time # Нужно для загрузки

# Создаем окно на весь экран. Передаем True, чтобы узнать разрешение монитора
w, h = Screen.full_size(bl=True)

# Создаем класс Chunk для работы с чанками
class Chunk:
    # Подгатавливаем переменные
    def __init__(self, cx, cy, tile_images):
        self.cx = cx
        self.cy = cy
        self.CHUNK_SIZE = mn.gl.gm.CHUNK_SIZE

        # Заполняем сразу всё нулями (водой)
        self.np_types = np.zeros((self.CHUNK_SIZE, self.CHUNK_SIZE), dtype=np.int32)

        # Генерируем случайные вариации для всего чанка
        self.np_variants = np.random.randint(0, 3, size=(self.CHUNK_SIZE, self.CHUNK_SIZE), dtype=np.int32)

        # Генеринуем массив для самой верхней поверхности (деревья, кусты, камни и тд)
        self.objects = np.zeros((self.CHUNK_SIZE, self.CHUNK_SIZE), dtype=np.int32)

        # Графика
        size = self.CHUNK_SIZE * mn.gl.gm.TILE_SIZE
        self.surface = Hit_box.surface(size, size)
        self.tile_images = tile_images
        self.dirty = True # Перерисовываем

    # Перерисовка чанка
    def render(self):
        if self.dirty:
            # фиксим размер для внутренней прорисовки
            INTERNAL_TILE = 16
            size = self.CHUNK_SIZE * INTERNAL_TILE

            # Создаем поверхность один раз
            if self.surface.get_width() != size:
                self.surface = pygame.Surface((size, size)).convert()

            # Временный кэш для оригинальных размеров
            scaled_cache = {}

            for y in range(self.CHUNK_SIZE):
                for x in range(self.CHUNK_SIZE):
                    t_type = self.np_types[y, x]
                    t_var = self.np_variants[y, x]

                    cache_key = (t_type, t_var)
                    if cache_key not in scaled_cache:
                        orig_img = self.tile_images[t_type][t_var]
                        # Скейливаем к стандару (32х32
                        scaled_cache[cache_key] = pygame.transform.scale(orig_img, (INTERNAL_TILE, INTERNAL_TILE))

                    self.surface.blit(scaled_cache[cache_key], (x * INTERNAL_TILE, y * INTERNAL_TILE))

            self.dirty = False

    def draw_only_ground(self, cam_x, cam_y):
        # 1. Вызываем рендер, только если блоки реально изменились
        if self.dirty:
            self.render()

        tile_size = mn.gl.gm.TILE_SIZE

        # 2. Масштабируем ВСЮ поверхность чанка целиком ОДНИМ вызовом
        # Это в 256 раз быстрее, чем рисовать тайлы по отдельности!
        current_size = self.CHUNK_SIZE * tile_size
        scaled_surf = pygame.transform.scale(self.surface, (current_size, current_size))

        # 3. Считаем координаты и рисуем
        screen_x = int(self.cx * current_size + cam_x)
        screen_y = int(self.cy * current_size + cam_y)

        Interface.draw(scaled_surf, screen_x, screen_y)

    def draw_only_objects(self, cam_x, cam_y):
        tile_size = mn.gl.gm.TILE_SIZE
        if tile_size < 3:
            return

        # Находим координаты всех деревьев (ID 10) в массиве NumPy
        # Это заменяет двойной цикл for!
        rows, cols = np.where(self.objects == 10)
        if len(rows) == 0:
            return

        screen_x = self.cx * self.CHUNK_SIZE * tile_size + cam_x
        screen_y = self.cy * self.CHUNK_SIZE * tile_size + cam_y

        img = mn.gl.gm.scaled_tree
        s_w, s_h = img.get_size()

        # Смещения для центрирования дерева
        offset_x = -(s_w // 2) + (tile_size // 2)
        offset_y = -s_h + tile_size

        # Рисуем только найденные объекты
        for r, c in zip(rows, cols):
            target_x = screen_x + (c * tile_size) + offset_x
            target_y = screen_y + (r * tile_size) + offset_y

            # Проверка видимости (Culling)
            if -s_w < target_x < mn.gl.gm.w and -s_h < target_y < mn.gl.gm.h:
                Interface.draw(img, int(target_x), int(target_y))

class FileLoad:
    def __init__(self):
        global w, h

        self.base_path = "textures/"
        self.base_path_grass = "textures/grass/"
        self.base_path_dirt = "textures/dirt/"
        self.base_path_red_sand = "textures/red_sand/"
        self.base_path_sand = "textures/sand/"
        self.base_path_water = "textures/water/"

        self.base_path_buttons = "textures/buttons/"
        self.base_path_bg = "textures/bg/"

        self.w,self.h = w,h

    def load_tiles(self):
        return {
            0: [Load.load(self.base_path_water + "water_1.png").convert(),
                Load.load(self.base_path_water + "water_2.png").convert(),
                Load.load(self.base_path_water + "water_3.png").convert(),
                Load.load(self.base_path_water + "water_3.png").convert(),],
            1: [Load.load(self.base_path_dirt + "dirt_1.png").convert(),
                Load.load(self.base_path_dirt + "dirt_2.png").convert(),
                Load.load(self.base_path_dirt + "dirt_3.png").convert(),
                Load.load(self.base_path_dirt + "dirt_3.png").convert(),],
            2: [Load.load(self.base_path_grass + "grass_1.png").convert(),
                Load.load(self.base_path_grass + "grass_2.png").convert(),
                Load.load(self.base_path_grass + "grass_3.png").convert(),
                Load.load(self.base_path_grass + "grass_3.png").convert(),],
            3: [Load.load(self.base_path_red_sand + "sand_1.png").convert(),
                Load.load(self.base_path_red_sand + "sand_2.png").convert(),
                Load.load(self.base_path_red_sand + "sand_3.png").convert(),
                Load.load(self.base_path_red_sand + "sand_3.png").convert(),],
            4: [Load.load(self.base_path_sand + "sand_1.png").convert(),
                Load.load(self.base_path_sand + "sand_1.png").convert(),
                Load.load(self.base_path_sand + "sand_2.png").convert(),
                Load.load(self.base_path_sand + "sand_3.png").convert(),],
            10:[Load.load(self.base_path + "maple.png").convert_alpha()],
        }

    def load_buttons(self):
        return [
            Interface.transform(Load.load(self.base_path_buttons + "minus_button.png").convert_alpha(),(40,40)),
            Interface.transform(Load.load(self.base_path_buttons + "plus_button.png").convert_alpha(),(40,40)),
            Load.load(self.base_path_buttons + "button.png"),
        ]

    def load_sound(self):
        return [
            Load.load_sound("textures/sound/sound_bg_game.mp3")
        ]

    def load_bg(self):
        return {
            "bg_menu": Interface.transform(Load.load(self.base_path_bg + "bg_menu.png"), (self.w, self.h))
        }

class Game:
    def __init__(self,x_chunks=16, y_chunks=8):
        global w,h
        self.w, self.h = w,h

        # НАСТРОЙКИ
        self.TILE_SIZE = 1  # "зум", количество пикселей
        self.CHUNK_SIZE = 32  # 16x16 тайлов
        self.SCREEN_SIZE = 128
        self.brush_size = 1
        self.time = 0
        self.years = 0

        self.chunks = {}
        self.tree_cache = {}  # Здесь будем хранить дерево для каждого размера TILE_SIZE
        self.x_chunks, self.y_chunks = x_chunks, y_chunks  # Первое х второе у

        self.current_tile = 1  # Начинаем с земли

        self.fl = FileLoad()
        self.tiles = self.fl.load_tiles()
        self.buttons_list = self.fl.load_buttons()
        self.sound_bg = self.fl.load_sound()
        self.sound_bg = self.sound_bg[0]

        # Примерно так, чтобы центр сетки чанков совпал с центром экрана
        self.camera_x = self.w // 2 - (self.x_chunks * self.CHUNK_SIZE * self.TILE_SIZE) // 2
        self.camera_y = self.h // 2 - (self.y_chunks * self.CHUNK_SIZE * self.TILE_SIZE) // 2

        # В классе Game (метод scroll или __init__)
        # Мы берем оригинальную маленькую картинку и увеличиваем её ровно в TILE_SIZE раз
        self.scaled_tree = pygame.transform.scale(self.tiles[10][0],
                                                  (4 * self.TILE_SIZE, 8 * self.TILE_SIZE))

    def map(self): # Метод создания карты
        for cy in range(self.y_chunks):
            for cx in range(self.x_chunks):
                # Передаем tiles в чанк
                self.chunks[(cx, cy)] = Chunk(cx, cy, self.tiles)

    def scroll(self):
        scroll = Keyboard.get_scroll()
        if scroll != 0:
            # Берем центр экрана
            mx, my = self.w // 2, self.h // 2

            world_x_before = (mx - self.camera_x) / self.TILE_SIZE
            world_y_before = (my - self.camera_y) / self.TILE_SIZE

            old_size = self.TILE_SIZE
            if scroll == 1 and self.TILE_SIZE < 15: self.TILE_SIZE += 1
            elif scroll == -1 and self.TILE_SIZE > 1: self.TILE_SIZE -= 1

            if old_size != self.TILE_SIZE:
                # Проверяем, есть ли дерево такого размера в кэше
                if self.TILE_SIZE not in self.tree_cache:
                    img_idx = Random.random_number(0, len(self.tiles[10]) - 1)
                    original_img = self.tiles[10][img_idx]

                    # Масштабируем один раз и сохраняем
                    new_size = (8 * self.TILE_SIZE, 16 * self.TILE_SIZE)
                    self.tree_cache[self.TILE_SIZE] = pygame.transform.scale(original_img, new_size)

                # Просто берем готовую картинку из словаря
                self.scaled_tree = self.tree_cache[self.TILE_SIZE]

            if old_size != self.TILE_SIZE:
                # Корректируем камеру, чтобы точка в центре осталась на месте
                self.camera_x = mx - (world_x_before * self.TILE_SIZE)
                self.camera_y = my - (world_y_before * self.TILE_SIZE)

    def mouse_pressed(self):
        if Keyboard.mouse_pressed(1):
            rel_x, rel_y = pygame.mouse.get_rel()

            # Рассчитываем размер всего мира в пикселях
            world_w_px = self.x_chunks * self.CHUNK_SIZE * self.TILE_SIZE
            world_h_px = self.y_chunks * self.CHUNK_SIZE * self.TILE_SIZE

            # Новые потенциальные координаты
            new_x = self.camera_x + rel_x
            new_y = self.camera_y + rel_y

            # ОГРАНИЧЕНИЯ:
            self.camera_x = max(self.w - world_w_px - 800, min(800, new_x))
            self.camera_y = max(self.h - world_h_px - 800, min(800, new_y))
        else:
            pygame.mouse.get_rel()

    def draw_chanks_see(self):
        visible_chunks = []  # Список чанков, которые попали в кадр

        for chunk in self.chunks.values():
            screen_x = chunk.cx * self.CHUNK_SIZE * self.TILE_SIZE + self.camera_x
            screen_y = chunk.cy * self.CHUNK_SIZE * self.TILE_SIZE + self.camera_y
            p_size = self.CHUNK_SIZE * self.TILE_SIZE

            if (screen_x + p_size > 0 and screen_x < self.w and
                    screen_y + p_size > 0 and screen_y < self.h):
                chunk.draw_only_ground(self.camera_x, self.camera_y)
                visible_chunks.append(chunk)

        for chunk in visible_chunks:
            chunk.draw_only_objects(self.camera_x, self.camera_y)

    def handle_drawing(self):
        mx, my = Keyboard.coordinat_mouse()
        if my >= 690: return

        if Keyboard.mouse(0):
            world_mx = mx - self.camera_x
            world_my = my - self.camera_y

            # Переводим координаты мыши в координаты тайлов
            center_tx = world_mx // self.TILE_SIZE
            center_ty = world_my // self.TILE_SIZE

            # Радиус кисти в тайлах
            radius = self.brush_size // 2

            # Проходим по квадрату, внутри которого будем отсекать лишнее для круга
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):

                    # --- МАГИЯ КРУГА ---
                    # Считаем расстояние от центра (0,0) до текущей точки (dx, dy)
                    # Если оно больше радиуса — пропускаем этот тайл
                    if dx * dx + dy * dy > radius * radius:
                        continue

                    # Мировые координаты тайла
                    tx_world = center_tx + dx
                    ty_world = center_ty + dy

                    cx = int(tx_world // self.CHUNK_SIZE)
                    cy = int(ty_world // self.CHUNK_SIZE)
                    tx = int(tx_world % self.CHUNK_SIZE)
                    ty = int(ty_world % self.CHUNK_SIZE)

                    if (cx, cy) in self.chunks:
                        chunk = self.chunks[(cx, cy)]

                        # Меняем данные через NumPy
                        if chunk.np_types[ty, tx] != self.current_tile:
                            chunk.np_types[ty, tx] = self.current_tile
                            chunk.np_variants[ty, tx] = np.random.randint(0, 4)

                            if self.current_tile != 2:
                                chunk.objects[ty, tx] = 0

                            chunk.dirty = True

    def update(self):
        if Keyboard.event_once("1"): self.current_tile = 0
        if Keyboard.event_once("2"): self.current_tile = 1
        if Keyboard.event_once("3"): self.current_tile = 2
        if Keyboard.event_once("4"): self.current_tile = 3
        if Keyboard.event_once("5"): self.current_tile = 4

    def panel(self,speed_time):
        Figures.square((self.w,300),(0,690),color=(190,190,190))
        Figures.line((0, 690), (self.w, 690), 3, color=(50, 50, 50))

        Figures.square((100,50),(345,695),color=(70,70,70))

        Text.write(f"Размер кисти {int(self.brush_size / 5 + 1)}", 60, 10, 710)
        Text.write(f"Выбранный блок {self.current_tile + 1}", 60,10,760)
        Text.write(f"Текущая скорость {int(speed_time)}", 60, 10, 810)

        self.time += Screen.dt(0.1 + speed_time * 0.05)
        if self.time > 12:self.time, self.years = 0, self.years + 1

        Text.write(f"{int(self.time)} Месяцев",60, 1250,710)
        Text.write(f"{int(self.years)} Лет/Годов", 60, 1250, 760)

        Text.write(f"ФПС {round(GC.Screen.clock.get_fps(),2)}",30,self.w - 130,20)

        if (Interface.button(self.buttons_list[0],400,700,bl=True) or Keyboard.event_once("0")) and self.brush_size > 5:
            self.brush_size -= 5
        if (Interface.button(self.buttons_list[1],350,700,bl=True) or Keyboard.event_once("9")) and self.brush_size < 45:
            self.brush_size += 5

    def update_process_dirt_to_grass(self):
        # 1. Выбираем случайный чанк
        if not self.chunks: return
        cx, cy = np.random.randint(0, self.x_chunks), np.random.randint(0, self.y_chunks)

        if (cx, cy) in self.chunks:
            chunk = self.chunks[(cx, cy)]

            dirt_mask = (chunk.np_types == 1)

            has_grass_neighbor = (
                    (np.roll(chunk.np_types, 1, axis=0) == 2) |  # верх
                    (np.roll(chunk.np_types, -1, axis=0) == 2) |  # низ
                    (np.roll(chunk.np_types, 1, axis=1) == 2) |  # лево
                    (np.roll(chunk.np_types, -1, axis=1) == 2) |  # право
                    (np.roll(np.roll(chunk.np_types, 1, axis=0), 1, axis=1) == 2) |  # диагональ
                    (np.roll(np.roll(chunk.np_types, -1, axis=0), -1, axis=1) == 2)  # диагональ
            )

            spontaneous_growth = np.random.random(chunk.np_types.shape) < 0.0009  # 0.1% шанс сам по себе
            infect_chance = np.random.random(chunk.np_types.shape) < 0.9  # 10% шанс от соседа

            final_mask = dirt_mask & ((has_grass_neighbor & infect_chance) | spontaneous_growth)

            # 5. Превращаем в ТРАВУ (ID 2)
            if np.any(final_mask):
                chunk.np_types[final_mask] = 2
                # Случайные вариации для всех новых блоков травы
                chunk.np_variants[final_mask] = np.random.randint(0, 3)
                chunk.dirty = True

    def update_process_trees(self):
        if not self.chunks: return
        cx, cy = np.random.randint(0, self.x_chunks), np.random.randint(0, self.y_chunks)

        if (cx, cy) in self.chunks:
            chunk = self.chunks[(cx, cy)]

            # 1. Находим, где есть ТРАВА и НЕТ объектов
            # 2 - трава, 0 - пусто в объектах (теперь там числа)
            can_grow_here = (chunk.np_types == 2) & (chunk.objects == 0)

            # 2. ПРОВЕРКА ТЕСНОТЫ (Магия NumPy)
            # Мы проверяем, сколько деревьев (ID 10) в радиусе вокруг каждой клетки.
            # Для этого "сдвигаем" массив объектов и складываем результаты.
            neighbor_trees = np.zeros_like(chunk.objects)
            for dy in range(-2, 7):  # Проверяем радиус 2 клетки
                for dx in range(-2, 7):
                    if dx == 0 and dy == 0: continue
                    neighbor_trees += (np.roll(np.roll(chunk.objects, dy, axis=0), dx, axis=1) == 10)

            # 3. Условие: Трава И нет соседей-деревьев И случайный шанс
            growth_chance = np.random.random(chunk.objects.shape) < 0.001  # 1% шанс вырасти
            final_mask = can_grow_here & (neighbor_trees == 0) & growth_chance

            # 4. Сажаем деревья (ID 10)
            if np.any(final_mask):
                chunk.objects[final_mask] = 10
                chunk.dirty = True

    def update_process_erosion(self):
        if not self.chunks: return
        # 1. Выбираем случайный чанк для симуляции в этом кадре
        cx, cy = np.random.randint(0, self.x_chunks), np.random.randint(0, self.y_chunks)

        if (cx, cy) in self.chunks:
            chunk = self.chunks[(cx, cy)]

            # 2. Находим ТРАВУ (2) и ЗЕМЛЮ (3) — это наши цели для размытия
            target_mask = (chunk.np_types == 2) | (chunk.np_types == 3)

            # 3. Находим блоки, которые граничат с ВОДОЙ (0)
            # Используем сдвиги (roll), чтобы проверить соседей во всех направлениях
            has_water_neighbor = (
                    (np.roll(chunk.np_types, 1, axis=0) == 0) |  # вода сверху
                    (np.roll(chunk.np_types, -1, axis=0) == 0) |  # вода снизу
                    (np.roll(chunk.np_types, 1, axis=1) == 0) |  # вода слева
                    (np.roll(chunk.np_types, -1, axis=1) == 0)  # вода справа
            )

            # 4. Совмещаем: блок должен быть сушей И иметь соседа-воду
            erosion_zone = target_mask & has_water_neighbor

            # 5. Добавляем шанс (чтобы берег не исчез мгновенно)
            # 0.03 означает, что размоется примерно 3% подходящих блоков за раз
            chance_mask = np.random.random(chunk.np_types.shape) < 0.003
            final_erosion = erosion_zone & chance_mask

            # В эрозии, после создания final_erosion:
            # Убираем влияние "зацикливания" краев
            final_erosion[0, :] = False
            final_erosion[-1, :] = False
            final_erosion[:, 0] = False
            final_erosion[:, -1] = False

            # 6. Превращаем в ПЕСОК (4)
            if np.any(final_erosion):
                chunk.np_types[final_erosion] = 4
                # Обновляем текстурные вариации для песка
                chunk.np_variants[final_erosion] = np.random.randint(0, 4)
                chunk.dirty = True

class Menu:
    def __init__(self):
        self.fl = FileLoad()
        self.sm = SceneManager()

        self.bg_dict = self.fl.load_bg()
        self.buttons_list = self.fl.load_buttons()

        self.elements = [
            SceneElement(
                x=0,
                y=0,
                texture=self.bg_dict["bg_menu"],
                is_button=False,
                id="background"
            ),SceneElement(
                x=600,
                y=600,
                texture=self.buttons_list[2],
                is_button=True,
                effect = True,
                id="button_exit"
            ),SceneElement(
                x=600,
                y=300,
                texture=self.buttons_list[2],
                is_button=True,
                effect = True,
                id="button_start"
            ),SceneElement(
                x=600,
                y=450,
                texture=self.buttons_list[2],
                is_button=True,
                effect = True,
                id="button_sitting"
            )]

    def rendering(self):
        text = SceneManager.scene(elements=self.elements)

        Text.write("Играть",100,650,340)
        Text.write("Настройки",70,640,500)
        Text.write("Выход",100,650,640)

        if text == "button_start":return "world_setup"
        if text == "button_sitting": pass
        if text == "button_exit": return "exit"

        return "menu"

class WorldSetup:
    def __init__(self):
        pass

class AiGame:
    def __init__(self):
        pass

class Gameplay:
    def __init__(self):
        self.mn = Menu()
        self.gm = Game(y_chunks=16, x_chunks=16) # 20x20 - максимум

        self.speed_time = 1
        self.loading_start = 0

        self.phrases = ["Стрижка газонов...", "Наполнение океанов...", "Размещение песка...", "Отрисовка чанков..."]
        self.phrases_num = 0

    def menu(self):
        cmd = self.mn.rendering()

        if Keyboard.event_once("enter"):
            return "world_setup"
        if Keyboard.event_once("esc"): return "exit"
        return cmd

    def world_setup(self):
        self.loading_start = time.time()
        self.gm.TILE_SIZE = 1
        self.gm.camera_x = self.gm.w // 2 - (self.gm.x_chunks * self.gm.CHUNK_SIZE * self.gm.TILE_SIZE) // 2
        self.gm.camera_y = self.gm.h // 2 - (self.gm.y_chunks * self.gm.CHUNK_SIZE * self.gm.TILE_SIZE) // 2
        return "start"

    def preparation(self):
        self.gm.map()
        return "loading"

    def loading_screen(self):
        if Keyboard.event_once("esc"): return "menu"

        Interface.fill_color(120, 120, 120)
        Text.write("Загрузка...", 30, self.gm.w - 200, self.gm.h - 100)

        if Random.random_number(1,20) == 1: self.phrases_num = Random.random_number(0,len(self.phrases)-1)
        Text.write(f"{self.phrases[self.phrases_num]}", 30,20, self.gm.h - 100)

        # Ждем ровно 5 секунд
        if time.time() - self.loading_start > 5.0:
            Sound_mixer.sound_infinity(5, self.gm.sound_bg)
            return "game"

        return "loading"

    def game(self):
        Interface.fill_color(39,51,254)

        if Keyboard.event_once("esc"):
            Sound_mixer.sound_stop()
            return "menu"
        speed_time = Screen.dt(self.speed_time * 70)

        #print(int(speed_time))
        for _ in range(int(speed_time)):
            self.gm.update_process_dirt_to_grass()
            self.gm.update_process_trees()
            self.gm.update_process_erosion()

        self.gm.update()
        self.gm.mouse_pressed()
        self.gm.scroll()
        self.gm.handle_drawing()

        self.gm.draw_chanks_see()
        self.gm.panel(speed_time=self.speed_time)

        if Keyboard.event_once("d") and self.speed_time < 5: self.speed_time += 1
        if Keyboard.event_once("a") and self.speed_time > 1: self.speed_time -= 1

        return "game"

class Main:
    def __init__(self):
        self.status = "menu"
        self.gl = Gameplay()

        self.status_dict = {
            "menu": self.gl.menu,
            "world_setup": self.gl.world_setup,
            "start": self.gl.preparation,
            "loading": self.gl.loading_screen,
            "game": self.gl.game,
        }

    def main_loop(self):
        while True:
            Screen.FPS(60)

            text = self.status_dict[self.status]()

            if text == "exit": break
            if text != self.status: self.status = text

            Screen.update_dt()
            Screen.update()
        Screen.quit()

mn = Main()
mn.main_loop()



















