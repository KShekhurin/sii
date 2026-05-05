import statistics
import math
import random
from abc import ABC, abstractmethod



class Agent(ABC):
    """
    Базовый абстрактный класс для всех агентов.

    Агент принимает решение о ставке на основе текущего состояния игры (context).
    Агент НЕ управляет очками и не изменяет состояние игры напрямую.

    Методы:
    -------
    make_bid(context: dict) -> int
        Должен быть реализован в наследниках. Возвращает ставку агента.

    clip_bid(bid: int, my_points: int) -> int
        Ограничивает ставку допустимыми значениями:
        - не меньше 0
        - не больше 30
        - не больше доступных очков
    """

    def __init__(self, name: str):
        self.name = name

    def clip_bid(self, bid: int, my_points: int) -> int:
        return max(0, min(int(bid), 30, my_points))
    

    @abstractmethod
    def make_bid(self, context: dict) -> int:
        """
        context:
        {
            'round': int,
            'my_points': int,
            'opponent_points': int,
            'history': list
        }
        """
        pass


class MinimaxAgent(Agent):
    """
    Агент, использующий стратегию minimax.

    Перебирает все возможные ставки и выбирает ту, которая максимизирует
    минимально возможный выигрыш (worst-case сценарий).

    Предположения:
    - стоимость предмета аппроксимируется как 20 (математическое ожидание)
    - оппонент может выбрать любую ставку

    Стратегия:
    - для каждой своей ставки оценивается худший исход
    - выбирается ставка с максимальным худшим результатом
    """
     
    def make_bid(self, context: dict) -> int:
        my_points = context['my_points']
        opponent_points = context['opponent_points']

        my_possible_bids = list(range(0, min(31, my_points + 1)))
        opponent_bids = list(range(0, min(31, opponent_points + 1)))
        def expected_value(my_bid, opp_bid):
            if my_bid > opp_bid:
                return 20 - my_bid
            elif my_bid < opp_bid:
                return -20 + opp_bid
            return 0

        best_bid = 0
        best_score = float('-inf')

        for my_bid in my_possible_bids:
            # worst-case (minimax)
            worst_case = float('inf')

            for opp_bid in opponent_bids:
                val = expected_value(my_bid, opp_bid)
                worst_case = min(worst_case, val)

            if worst_case > best_score:
                best_score = worst_case
                best_bid = my_bid

        return self.clip_bid(best_bid, my_points)
    

class BayesianAgent(Agent):
    """
    Агент, оценивающий поведение оппонента через статистику.

    Использует:
    - среднее значение ставок оппонента
    - стандартное отклонение

    Предполагает нормальное распределение ставок оппонента и оценивает
    вероятность выигрыша для разных ставок.

    Стратегия:
    - оценивает вероятность победы через CDF нормального распределения
    - выбирает ставку с максимальным ожидаемым выигрышем (EV)
    """
    def make_bid(self, context: dict) -> int:
        my_points = context['my_points']
        history = context['history']

        if not history:
            return random.randint(10, min(20, my_points))

        opp_bids = [h['opponent_bid'] for h in history]

        mu = statistics.mean(opp_bids)
        sigma = statistics.pstdev(opp_bids) or 1

        # пробуем несколько кандидатов
        candidates = range(0, min(31, my_points + 1), 3)

        best_bid = 0
        best_score = float('-inf')

        for bid in candidates:
            # вероятность выиграть (аппроксимация)
            z = (bid - mu) / sigma
            win_prob = 0.5 * (1 + math.erf(z / math.sqrt(2)))

            ev = win_prob * (20 - bid)

            if ev > best_score:
                best_score = ev
                best_bid = bid

        return self.clip_bid(best_bid, my_points)
    


class PunisherAgent(Agent):
    """
    Агент с реактивной и частично случайной стратегией.

    Поведение:
    - если оппонент делает агрессивную ставку (>15), агент отвечает ещё более высокой ставкой
    - в остальных случаях действует случайно

    Цель:
    - наказывать агрессивные стратегии
    - быть непредсказуемым
    """
    def make_bid(self, context: dict) -> int:
        my_points = context['my_points']
        history = context['history']

        if not history:
            return self.clip_bid(random.randint(0, 30), my_points)

        last_opp_bid = history[-1]['opponent_bid']

        # если оппонент агрессивен → punish
        if last_opp_bid > 15:
            return self.clip_bid(min(30, last_opp_bid + 5), my_points)

        # иначе — хаос
        if random.random() < 0.5:
            return self.clip_bid(random.randint(5, 15), my_points)
        else:
            return self.clip_bid(random.randint(15, 25), my_points)



class EVAgent(Agent):
    """
    Агент, ориентированный на ожидаемую ценность (Expected Value).

    Предполагает:
    - средняя стоимость предмета ≈ 20

    Стратегия:
    - выбирает случайную ставку в диапазоне [10, 20]
    - избегает переплаты (ставок > 20)

    Простой и стабильный baseline-агент.
    """
    def make_bid(self, context: dict) -> int:
        my_points = context['my_points']

        # базовое EV-ограничение
        max_profitable_bid = 20

        # небольшая вариативность, чтобы не быть детерминированным
        bid = random.randint(10, max_profitable_bid)

        return self.clip_bid(bid, my_points)


class AdaptiveAgent(Agent):
    """
    Адаптивный агент, изменяющий стратегию в зависимости от ситуации.

    Поведение:
    - если проигрывает по очкам → увеличивает ставки (агрессия)
    - если выигрывает → снижает ставки (осторожность)
    - в последних раундах → становится более агрессивным

    Учитывает:
    - текущий счёт
    - номер раунда
    """
    def make_bid(self, context: dict) -> int:
        my_points = context['my_points']
        opponent_points = context['opponent_points']
        round_number = context['round']

        # финальные раунды — агрессия
        if round_number >= 4:
            bid = int(max(0.6 * my_points, opponent_points + 5))

        # если отстаём — усиливаемся
        if my_points < opponent_points:
            bid = int(0.5 * my_points)

        # если ведём — играем осторожно
        else:
            bid = int(0.2 * my_points)

        return self.clip_bid(bid, my_points)
    

class MirrorAgent(Agent):
    """
    Агент, копирующий поведение оппонента.

    Поведение:
    - в первом раунде делает случайную ставку
    - далее повторяет ставку оппонента из предыдущего раунда

    """
    def make_bid(self, context: dict) -> int:
        if context['round'] == 1:
            return random.randint(1, context['my_points'])

        last_round = context['history'][-1]
        return self.clip_bid(last_round['opponent_bid'], context['my_points'])


class HumanAgent(Agent):
    """
    Агент для взаимодействия с человеком через консоль.

    Поведение:
    - запрашивает ставку у пользователя
    - валидирует ввод
    - не допускает отрицательные ставки или превышение доступных очков
    """
    def make_bid(self, context: dict) -> int:
        while True:
            try:
                bid = int(input(f"[{self.name}] Ставка (доступно {context['my_points']}): "))
                if bid > context['my_points']:
                    print(f"Ставка превышает доступные очки ({context['my_points']}). Попробуйте снова.")
                    continue
                if bid < 0:
                    print("Ставка не может быть отрицательной. Попробуйте снова.")
                    continue

                return bid
            except ValueError:
                print("Введите число.")

class RandomAgent(Agent):
    """
    Агент со случайной стратегией.

    Поведение:
    - выбирает случайную ставку в диапазоне [0, 30]
    """
    def make_bid(self, context: dict) -> int:
        return self.clip_bid(random.randint(0, 30), context['my_points'])
    

class DoNothingAgent(Agent):
    """
    Агент, который никогда не делает ставку.

    Всегда возвращает 0.
    """
    def make_bid(self, context: dict) -> int:
        return 0    
    
    