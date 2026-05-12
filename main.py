# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ - РАНДОМН
import random
import copy

# Константы состояний клеток
WATER = 0
SHIP = 1
MISS = 2
HIT = 3

# Классический флот: 1х4, 2х3, 3х2, 4х1
REQUIRED_SHIPS = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
BOARD_SIZE = 10
def random_placement():
    """Создаёт валидное поле за одну итерацию без рекурсии."""
    while True:  # На практике цикл выполняется ровно 1 раз
        board = [[WATER] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        success = True
        
        for size in REQUIRED_SHIPS:
            # Генерируем все возможные позиции для корабля текущего размера
            candidates = []
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE - size + 1):
                    candidates.append((r, c, True))   # горизонтально
            for r in range(BOARD_SIZE - size + 1):
                for c in range(BOARD_SIZE):
                    candidates.append((r, c, False))  # вертикально
                    
            random.shuffle(candidates)
            
            placed = False
            for r, c, horizontal in candidates:
                # Проверка на пересечение и касание (включая диагонали)
                conflict = False
                for i in range(size):
                    cr = r if horizontal else r + i
                    cc = c if not horizontal else c + i
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            nr, nc = cr + dr, cc + dc
                            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == SHIP:
                                conflict = True
                                break
                        if conflict: break
                    if conflict: break
                    
                if not conflict:
                    # Ставим корабль
                    for i in range(size):
                        cr = r if horizontal else r + i
                        cc = c if not horizontal else c + i
                        board[cr][cc] = SHIP
                    placed = True
                    break
                    
            if not placed:
                success = False
                break  # Пересоздаём доску целиком
                
        if success:
            return board
def validate_board(board):
    """Возвращает (True, list_of_ships) или (False, [])"""
    if len(board) != BOARD_SIZE or any(len(row) != BOARD_SIZE for row in board):
        return False, []

    ship_cells = {(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == SHIP}
    if len(ship_cells) != sum(REQUIRED_SHIPS):
        return False, []

    # BFS для поиска связных компонентов (4 направления)
    visited = set()
    ships = []
    for r, c in ship_cells:
        if (r, c) in visited: continue
        component = set()
        stack = [(r, c)]
        visited.add((r, c))
        component.add((r, c))
        while stack:
            cr, cc = stack.pop()
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = cr+dr, cc+dc
                if (nr, nc) in ship_cells and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    component.add((nr, nc))
                    stack.append((nr, nc))
        ships.append(component)

    # Проверка размеров кораблей
    if sorted(len(s) for s in ships) != sorted(REQUIRED_SHIPS):
        return False, []

    # Проверка отсутствия касаний
    for i in range(len(ships)):
        for j in range(i+1, len(ships)):
            for r, c in ships[i]:
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0: continue
                        if (r+dr, c+dc) in ships[j]:
                            return False, []

    return True, [{'coords': s, 'hits': set()} for s in ships]
  def STAND(mode, turn_name, result, p1_state, p2_state):
    """Выводит результат полухода в консоль."""
    is_p1_turn = (turn_name == "Агент 1 (P1)")
    my_state = p1_state if is_p1_turn else p2_state
    opp_state = p2_state if is_p1_turn else p1_state

    print("\n" + "="*50)
    print(f"Ход {turn_name}")
    print(f"Результат: {result['status'].upper()} | Координаты: {result['coords']}")
    
    def draw_board(state, title, show_ships=True):
        sym = {WATER: '~', SHIP: 'S', MISS: '•', HIT: '*'}
        print(f"\n{title}")
        print("    " + "  ".join(str(i) for i in range(10)))
        for r in range(10):
            row_str = f"{r} | "
            for c in range(10):
                val = state['board'][r][c]
                if not show_ships and val == SHIP:
                    val = WATER  # Скрываем корабли в слепом режиме
                row_str += sym.get(val, '?') + "  "
            print(row_str)

    if mode == 'open':
        draw_board(my_state, "Поле этого агента", show_ships=True)
        draw_board(opp_state, "Поле другого агента", show_ships=True)
    else:
        draw_board(my_state, "Поле этого агента", show_ships=True)
        draw_board(opp_state, "Поле другого агента (корабли противника скрыты)", show_ships=False)
        
    print("="*50)
    def CTRL(P1, P2, STAND, mode='open'):
    """Управление игрой: расстановка, валидация, ходы, проверка победы."""
    p1_state = {'board': [[WATER]*10 for _ in range(10)], 'shots': set(), 'ships': [], 'phase': 'placement'}
    p2_state = {'board': [[WATER]*10 for _ in range(10)], 'shots': set(), 'ships': [], 'phase': 'placement'}
    agents = {0: (P1, p1_state, "Агент 1 (P1)"), 
              1: (P2, p2_state, "Агент 2 (P2)")}
    
    # --- ФАЗА 1: РАССТАНОВКА ---
    for agent_id in [0, 1]:
        func, state, name = agents[agent_id]
        print(f"\n{name} размещает корабли...")
        try:
            new_board = func(state, {'status': 'start', 'coords': None})
            is_valid, ships = validate_board(new_board)
            if not is_valid:
                raise ValueError(f"{name} предоставил некорректное поле!")
            state['board'] = new_board
            state['ships'] = ships
            state['phase'] = 'game'
        except Exception as e:
            print(f"❌ Ошибка расстановки {name}: {e}")
            return

    # --- ФАЗА 2: ИГРОВОЙ ЦИКЛ ---
    current = 0
    last_result = {'status': 'start', 'coords': None}
    
    while True:
        func, my_state, name = agents[current]
        opp_state = agents[1-current][1]
        
        # Получаем ход
        try:
            move = func(my_state, last_result)
            if not isinstance(move, (tuple, list)) or len(move) != 2:
                raise ValueError("Ход должен быть (row, col)")
            r, c = int(move[0]), int(move[1])
        except Exception as e:
            print(f"❌ {name} вернул ошибку: {e}")
            break

        # Валидация хода
        if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
            result = {'status': 'invalid', 'coords': (r, c)}
        elif (r, c) in my_state['shots']:
            result = {'status': 'repeat', 'coords': (r, c)}
        else:
            my_state['shots'].add((r, c))
            cell = opp_state['board'][r][c]
            
            if cell == WATER:
                opp_state['board'][r][c] = MISS
                result = {'status': 'miss', 'coords': (r, c)}
            elif cell == SHIP:
                opp_state['board'][r][c] = HIT
                result = {'status': 'hit', 'coords': (r, c)}
                
                # Проверка на потопление
                for ship in opp_state['ships']:
                    if (r, c) in ship['coords']:
                        ship['hits'].add((r, c))
                        if len(ship['hits']) == len(ship['coords']):
                            result['status'] = 'sunk'
                            # Авто-отметка промахов вокруг потопленного корабля
                            for sr, sc in ship['coords']:
                                for dr in [-1, 0, 1]:
                                    for dc in [-1, 0, 1]:
                                        nr, nc = sr+dr, sc+dc
                                        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                                            if opp_state['board'][nr][nc] == WATER:
                                                opp_state['board'][nr][nc] = MISS
                                                my_state['shots'].add((nr, nc))
                            break
                            
        STAND(mode, name, result, p1_state, p2_state)
        
        # Проверка победы
        if all(len(s['hits']) == len(s['coords']) for s in opp_state['ships']):
            print(f"\n🏆 {name} ПОБЕДИЛ! Все корабли противника потоплены.")
            break
            
        # Смена хода
        current = 1 - current
        last_result = result
      def Pexample(state, last_result):
    """ШАБЛОН АГЕНТА. Скопируйте и создайте своего агента"""
    if state['phase'] == 'placement':
        return random_placement()
    else:
        # TODO: Ваша логика стрельбы
        available = [(r,c) for r in range(10) for c in range(10) if (r,c) not in state['shots']]
        return random.choice(available)

def P1(state, last_result):
    """Простой агент: случайные выстрелы без приоритетов."""
    if state['phase'] == 'placement':
        return random_placement()
    available = [(r,c) for r in range(10) for c in range(10) if (r,c) not in state['shots']]
    return random.choice(available)

def P2(state, last_result):
    """Умный агент: режим 'поиск-охота'."""
    if state['phase'] == 'placement':
        return random_placement()
        
    if 'target_stack' not in state:
        state['target_stack'] = []
        
    # При попадании/потоплении добавляем соседей в очередь целей
    if last_result['status'] in ('hit', 'sunk') and last_result['coords']:
        r, c = last_result['coords']
        neighbors = [(r+dr, c+dc) for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]]
        random.shuffle(neighbors)
        for nr, nc in neighbors:
            if 0 <= nr < 10 and 0 <= nc < 10 and (nr, nc) not in state['shots']:
                if (nr, nc) not in state['target_stack']:
                    state['target_stack'].append((nr, nc))
                    
    # Стреляем по целям, если есть
    while state['target_stack']:
        target = state['target_stack'].pop(0)
        if target not in state['shots']:
            return target
            
    # Иначе случайный выстрел
    available = [(r,c) for r in range(10) for c in range(10) if (r,c) not in state['shots']]
    return random.choice(available)
def main():
    CTRL(P1, P2, STAND, mode='open')
if __name__ == "__main__":
    main()
