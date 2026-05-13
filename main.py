import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

# ===========================
# Базовый каркас для игр
# ===========================

class Player(ABC):
    """Абстрактный игрок (бот или человек)."""
    @abstractmethod
    def make_decision(self, state: Dict[str, Any]) -> Any:
        """
        Принимает решение на основе состояния игры.
        state содержит всю доступную игроку информацию.
        """
        pass

    def reset(self) -> None:
        """Сброс внутреннего состояния перед новой игрой (опционально)."""
        pass


class Game(ABC):
    """Абстрактная игра. Реализуйте run() для конкретной механики."""
    def __init__(self, players: List[Player]):
        self.players = players
        self.winner: Optional[int] = None  # индекс победителя или -1 для ничьей

    @abstractmethod
    def run(self) -> int:
        """
        Запускает игру и возвращает индекс победителя (0 или 1) или -1 при ничьей.
        """
        pass

    def get_winner(self) -> Optional[int]:
        return self.winner


# ===========================
# Конкретная игра: Аукцион
# ===========================

class AuctionGame(Game):
    """
    Игра "Аукцион" с одновременными ставками в каждом подраунде.

    Параметры:
        a, b : границы случайного секретного числа (включая обе)
        n    : количество раундов
        m    : количество подраундов (ставок каждого игрока за раунд)
        s    : начальный баланс
    """
    def __init__(self, players: List[Player], a: int, b: int, n: int, m: int, s: int):
        super().__init__(players)
        self.a = a
        self.b = b
        self.n = n
        self.m = m
        self.initial_balance = s
        self.balances = [s, s]
        self.current_round = 0
        self.bids: List[tuple] = []   # (player_idx, bid) – накапливаются все ставки раунда
        self.current_subround = 0     # номер текущего подраунда (0..m-1)
        self.secret = 0

    def _get_state(self, player_idx: int) -> Dict[str, Any]:
        """Формирует словарь с информацией, доступной игроку перед ходом."""
        return {
            'round': self.current_round,
            'subround': self.current_subround,    # 0 .. m-1
            'bids': list(self.bids),              # ставки предыдущих подраундов (и только они!)
            'my_balance': self.balances[player_idx],
            'opponent_balance': self.balances[1 - player_idx],
            'my_id': player_idx,
            'params': {
                'a': self.a,
                'b': self.b,
                'n': self.n,
                'm': self.m,
                'initial_balance': self.initial_balance
            }
        }

    def run(self) -> int:
        """Основной цикл игры."""
        # Сброс внутренних состояний игроков
        for p in self.players:
            p.reset()

        # n раундов
        for rnd in range(self.n):
            self.current_round = rnd
            self.secret = random.randint(self.a, self.b)
            self.bids = []

            # m подраундов с одновременными ставками
            for sub in range(self.m):
                self.current_subround = sub

                # Состояние для обоих игроков одинаковое (не содержит ставок текущего подраунда)
                state_p0 = self._get_state(0)
                state_p1 = self._get_state(1)

                # Игроки принимают решения "в закрытую"
                action0 = self.players[0].make_decision(state_p0)
                action1 = self.players[1].make_decision(state_p1)

                # Валидация и ограничение балансом
                bid0 = max(0, min(action0, self.balances[0]))
                bid1 = max(0, min(action1, self.balances[1]))

                # Добавляем обе ставки в историю (порядок фиксирован, но это не даёт преимущества)
                self.bids.append((0, bid0))
                self.bids.append((1, bid1))

            # --- Обработка результатов раунда (после ВСЕХ m подраундов) ---
            # Определяем максимальную ставку в раунде
            max_bid = max(bid for _, bid in self.bids)

            # Каждый игрок, который хотя бы раз поставил максимальную ставку,
            # платит её (один раз) и получает секретное число
            for i in range(2):
                if any(pid == i and bid == max_bid for pid, bid in self.bids):
                    self.balances[i] -= max_bid
                    self.balances[i] += self.secret

            # Опциональный вывод лога раунда
            print(f"Раунд {rnd+1}: секретное число = {self.secret}, "
                  f"ставки = {self.bids}, "
                  f"балансы = {self.balances}")

        # Определение победителя
        if self.balances[0] > self.balances[1]:
            self.winner = 0
        elif self.balances[1] > self.balances[0]:
            self.winner = 1
        else:
            self.winner = -1
        return self.winner


# ===========================
# Готовые боты
# ===========================

class RandomBot(Player):
    """Ставит случайную сумму от 0 до b."""
    def make_decision(self, state: Dict[str, Any]) -> int:
        return random.randint(0, state['params']['b'])


class ConstantBot(Player):
    """Всегда пытается поставить одно и то же число (ограничивается балансом)."""
    def __init__(self, constant: int = 10):
        self.constant = constant

    def make_decision(self, state: Dict[str, Any]) -> int:
        return min(self.constant, state['my_balance'])


class AverageBot(Player):
    """Ставит ожидаемое значение секретного числа (среднее между a и b)."""
    def make_decision(self, state: Dict[str, Any]) -> int:
        a = state['params']['a']
        b = state['params']['b']
        expected = (a + b) // 2
        return min(expected, state['my_balance'])


class LastBidBot(Player):
    """
    Повторяет последнюю ставку противника (из уже известных).
    Поскольку ходы одновременные, он использует ставку из предыдущего подраунда.
    Если истории ещё нет, ставит 0.
    """
    def make_decision(self, state: Dict[str, Any]) -> int:
        bids = state['bids']
        # Ищем последнюю ставку соперника в уже раскрытых данных
        opponent_bid = 0
        for pid, bid in reversed(bids):
            if pid != state['my_id']:
                opponent_bid = bid
                break
        return min(opponent_bid, state['my_balance'])


class HumanPlayer(Player):
    """Человек вводит ставку с клавиатуры."""
    def make_decision(self, state: Dict[str, Any]) -> int:
        print(f"\nВаш ход (игрок {state['my_id']}). Раунд {state['round']+1}, "
              f"подраунд {state['subround']+1}/{state['params']['m']}")
        print(f"Ваш баланс: {state['my_balance']}, баланс соперника: {state['opponent_balance']}")
        print(f"История ставок в этом раунде: {state['bids']}")
        while True:
            try:
                bid = int(input("Введите ставку: "))
                if 0 <= bid <= state['my_balance']:
                    return bid
                print(f"Ставка должна быть от 0 до {state['my_balance']}.")
            except ValueError:
                print("Введите целое число.")

class StrategicBot(Player):
    """
    Бот, использующий отложенную стратегию:
    - В первых m-1 своих ходах ставит 0, собирая информацию.
    - На последнем ходу вычисляет «справедливую цену» (ожидаемое секретное число минус 1)
      и перебивает текущую максимальную ставку, только если это выгодно и позволяет баланс.
    """
    def make_decision(self, state: Dict[str, Any]) -> int:
        my_id = state['my_id']
        bids = state['bids']
        m = state['params']['m']
        balance = state['my_balance']
        a = state['params']['a']
        b = state['params']['b']

        # Сколько своих ставок уже сделано (не считая текущую)
        my_bids_count = sum(1 for pid, _ in bids if pid == my_id)
        remaining = m - my_bids_count - 1  # осталось ходов после этого
        # Если это не последний ход – ставим 0
        if remaining > 0:
            return 0

        # Последний ход
        secret = (a + b) // 2
        fair_price = max(0, secret)

        # Текущий максимум среди всех ставок раунда
        max_bid = max((bid for _, bid in bids), default=0)

        # Если текущий максимум уже не ниже нашей справедливой цены, не перебиваем
        if max_bid >= fair_price:
            return 1

        # Целевая ставка: перебить на 1, но не выше fair_price
        target = min(max_bid + 1, fair_price)

        # Не можем позволить себе больше баланса
        if target > balance:
            return balance

        return target
# ===========================
# Реестр ботов и запуск
# ===========================

BOTS_REGISTRY = {
    "random": RandomBot,
    "constant": ConstantBot,
    "average": AverageBot,
    "lastbid": LastBidBot,
    "human": HumanPlayer,
    "strategic": StrategicBot
}

def choose_bot(player_num: int) -> Player:
    """Позволяет выбрать бота из реестра или создать с параметрами."""
    print(f"\nВыберите тип игрока {player_num}:")
    for name in BOTS_REGISTRY:
        print(f"  {name}")
    choice = input("Введите название: ").strip().lower()
    if choice not in BOTS_REGISTRY:
        print("Неизвестный тип, выбран RandomBot.")
        return RandomBot()
    bot_class = BOTS_REGISTRY[choice]
    if choice == "constant":
        c = int(input("Введите константу для ConstantBot: "))
        return bot_class(constant=c)
    return bot_class()


def main():
    print("=== Игра Аукцион с одновременными ставками ===")
    a = int(input("Нижняя граница секретного числа (a): "))
    b = int(input("Верхняя граница секретного числа (b): "))
    n = int(input("Количество раундов (n): "))
    m = int(input("Количество подраундов на игрока (m): "))
    s = int(input("Начальный баланс (s): "))

    player1 = choose_bot(1)
    player2 = choose_bot(2)

    game = AuctionGame([player1, player2], a, b, n, m, s)
    winner = game.run()

    print("\n=== Игра завершена ===")
    print(f"Итоговый баланс: Игрок 0 = {game.balances[0]}, Игрок 1 = {game.balances[1]}")
    if winner == -1:
        print("Ничья!")
    else:
        print(f"Победил Игрок {winner}!")


if __name__ == "__main__":
    main()
