import statistics
import math
import random
from abc import ABC, abstractmethod



class Agent(ABC):
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

# class QLearningAgent(Agent):
#     shared_q = {}

#     def __init__(self, name):
#         self.name = name
#         self.q = QLearningAgent.shared_q
#         self.alpha = 0.3  # Агрессивное обучение
#         self.gamma = 0.7  # Меньше смотрим в будущее (игра короткая)
#         self.epsilon = 0.2

#         # Сокращаем выбор до 7 вариантов (шаг 5)
#         self.possible_actions = [0, 5, 10, 15, 20, 25, 30]

#         self.last_state = None
#         self.last_action = None

#     def _get_state(self, context):
#         # Максимально простое состояние: только 3 фазы игры
#         # (начало, середина, конец)
#         return context['round'] // 17

#     def _compute_reward(self, context):
#         history = context['history']
#         if not history: return None
        
#         last = history[-1]
#         # Если выиграли, профит = цена - ставка. 
#         # Если проиграли, профит = 0 (мы ничего не потеряли)
#         if last['my_bid'] > last['opponent_bid']:
#             return last['value'] - last['my_bid']
#         else: return last['opponent_bid'] - last['value']
#         return 0

#     def make_bid(self, context: dict) -> int:
#         state = self._get_state(context)
#         reward = self._compute_reward(context)

#         # ОТЛАДКА: Проверяем, заходим ли мы в обновление
#         if reward is not None:
#             if self.last_state is not None:
#                 print(f"Updating Q for {self.last_state} with reward {reward}")
#                 self._update_q(self.last_state, self.last_action, reward, state)
#             else:
#                 print("First round: no last_state yet.")
#         else:
#             print("Warning: Reward is None! Check history keys.")

#         # ACTION SELECTION
#         qs = [self.q.get((state, a), 0) for a in self.possible_actions]
#         #print(qs)
#         # Если всё ещё нули, выведем состояние, чтобы понять почему
#         if all(v == 0 for v in qs):
#             pass
#            # print(f"State {state} is completely new or all Qs are 0")

#         if random.random() < self.epsilon:
#             action = random.choice(self.possible_actions)
#         else:
#             max_q = max(qs)
#             if max_q == 0:
#                 action = random.choice(self.possible_actions)
#             else:
#                 best_actions = [a for a, q in zip(self.possible_actions, qs) if q == max_q]
#                 action = random.choice(best_actions)

#         self.last_state = state
#         self.last_action = action
#         return min(action, context['my_points'])
    
#     def _update_q(self, state, action, reward, next_state):
#         old_q = self.q.get((state, action), 0)
#         max_future = max([self.q.get((next_state, a), 0) for a in self.possible_actions], default=0)
        
#         # Обновляем значение
#         self.q[(state, action)] = old_q + self.alpha * (reward + self.gamma * max_future - old_q)


# class QLearningAgent(Agent):
#     def __init__(self, name):
#         super().__init__(name)

#         self.q = {}
#         self.alpha = 0.1
#         self.gamma = 0.9
#         self.epsilon = 0.2

#         self.actions = list(range(0, 31))

#         self.last_state = None
#         self.last_action = None

#     def _get_state(self, context):
#         return (
#             context['my_points'] // 10,
#             context['opponent_points'] // 10
#         )

#     def _compute_reward(self, context):
#         """Восстанавливаем reward из последнего раунда"""
#         history = context['history']

#         if not history:
#             return None

#         last = history[-1]

#         my_bid = last['my_bid']
#         opp_bid = last['opponent_bid']
#         value = last['value']
        
#         if my_bid > opp_bid:
#             return value - my_bid
#         else:
#             return opp_bid - value

#     def make_bid(self, context: dict) -> int:
#         state = self._get_state(context)

#         # --- LEARNING STEP ---
#         reward = self._compute_reward(context)

#         if reward is not None and self.last_state is not None:
#             self._update_q(self.last_state, self.last_action, reward, state)

#         # --- ACTION SELECTION ---
#         if random.random() < self.epsilon:
#             action = random.choice(self.actions)
#         else:
#             qs = [self.q.get((state, a), 0) for a in self.actions]
#             max_q = max(qs)
#             best_actions = [a for a, q in zip(self.actions, qs) if q == max_q]
#             print(qs)
#             action = random.choice(best_actions)

#         self.last_state = state
#         self.last_action = action

#         return self.clip_bid(action, context['my_points'])

#     def _update_q(self, state, action, reward, next_state):
#         max_future = max(
#             [self.q.get((next_state, a), 0) for a in self.actions],
#             default=0
#         )

#         old = self.q.get((state, action), 0)

#         self.q[(state, action)] = (
#             old + self.alpha * (reward + self.gamma * max_future - old)
#         )        


class EVAgent(Agent):
    def make_bid(self, context: dict) -> int:
        my_points = context['my_points']

        # базовое EV-ограничение
        max_profitable_bid = 20

        # небольшая вариативность, чтобы не быть детерминированным
        bid = random.randint(10, max_profitable_bid)

        return self.clip_bid(bid, my_points)


class AdaptiveAgent(Agent):
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
    def make_bid(self, context: dict) -> int:
        if context['round'] == 1:
            return random.randint(1, context['my_points'])

        last_round = context['history'][-1]
        return self.clip_bid(last_round['opponent_bid'], context['my_points'])


class HumanAgent(Agent):
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
    def make_bid(self, context: dict) -> int:
        return self.clip_bid(random.randint(0, 30), context['my_points'])
    

class DoNothingAgent(Agent):
    def make_bid(self, context: dict) -> int:
        return 0    
    
    