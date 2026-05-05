import random
from abc import ABC, abstractmethod
import agents
from agents import Agent, MirrorAgent, HumanAgent

# =========================
# Игра
# =========================
class Game:
    """
    Класс, реализующий логику аукционной игры.

    Игра проходит в несколько раундов, где два агента делают ставки
    на предмет со случайной стоимостью.

    Правила:
    - у каждого игрока изначально 200 очков
    - стоимость предмета: случайное число от 10 до 30
    - игрок с большей ставкой выигрывает
    - выигрыш: value - bid
    - проигрыш: 0
    - ничья: 0

    Параметры:
    ----------
    agent1 : Agent
        Первый игрок
    agent2 : Agent
        Второй игрок
    rounds : int
        Количество раундов
    """
    def __init__(self, agent1: Agent, agent2: Agent, rounds: int = 10):
        self.agent1 = agent1
        #self.agent1.name = "Agent1"
        self.agent2 = agent2
        #self.agent2.name = "Agent2"
        self.rounds = rounds

        if self.agent1.name == self.agent2.name:
            self.agent2.name += "_2"

        self.points = {
            self.agent1.name: 200,
            self.agent2.name: 200
        }

        self.history = []

    def _validate_bid(self, bid: int, max_points: int) -> int:
        """
        Проверяет корректность ставки.

        Правила:
        - ставка должна быть целым неотрицательным числом
        - ставка <= доступных очков

        Если ставка некорректна, она корректируется:
        - отрицательная или не целое → 0
        - слишком большая → обрезается до max_points

        Возвращает:
        -----------
        int
            Корректная ставка
        """

        if not isinstance(bid, int):
            print(" Некорректный тип ставки. Установлена 0.")
            return 0

        if bid < 0:
            print(" Ставка < 0. Установлена 0.")
            return 0

        if bid > max_points:
            print(f"Ставка превышает доступные очки ({max_points}). Обрезана.")
            return max_points

        return bid

    def _get_context(self, agent: Agent, opponent: Agent, round_number: int):
        """
    Формирует состояние игры (context), передаваемое агенту.

    Включает:
    - номер раунда
    - текущие очки агента
    - очки оппонента
    - историю предыдущих раундов

    История содержит:
    - свою ставку
    - ставку оппонента
    - стоимость предмета

    Возвращает:
    -----------
    dict
        Контекст для принятия решения агентом
    """
        return {
            'round': round_number,
            'my_points': self.points[agent.name],
            'opponent_points': self.points[opponent.name],
            'history': [
                {
                    'my_bid': h[agent.name]['bid'],
                    'opponent_bid': h[opponent.name]['bid'],
                    'value': h['value']
                }
                for h in self.history
            ]
        }

    def play(self):
        """
    Запускает игру.

    Для каждого раунда:
    - генерируется стоимость предмета
    - агенты делают ставки
    - ставки валидируются
    - определяется победитель
    - обновляются очки
    - сохраняется история

    После завершения:
    - выводится итоговый результат
    """
        for r in range(1, self.rounds + 1):
            print(f"\n=== Раунд {r} ===")

            value = random.randint(10, 30)

            # Получаем ставки
            bid1 = self.agent1.make_bid(
                self._get_context(self.agent1, self.agent2, r)
            )
            bid2 = self.agent2.make_bid(
                self._get_context(self.agent2, self.agent1, r)
            )

            # Валидация
            bid1 = self._validate_bid(bid1, self.points[self.agent1.name])
            bid2 = self._validate_bid(bid2, self.points[self.agent2.name])

            print(f"{self.agent1.name}: {bid1}")
            print(f"{self.agent2.name}: {bid2}")

            # Применение правил
            if bid1 > bid2:
                self.points[self.agent1.name] += (value - bid1)
                print(f"{self.agent1.name} выигрывает ({value})")

            elif bid2 > bid1:
                self.points[self.agent2.name] += (value - bid2)
                print(f"{self.agent2.name} выигрывает ({value})")

            else:
                print("Ничья")

            # запись истории
            self.history.append({
                self.agent1.name: {'bid': bid1},
                self.agent2.name: {'bid': bid2},
                'value': value
            })

            print(f"Очки: {self.points}")

        self._result()

    def _result(self):
        """
        Выводит итог игры.

        Показывает:
        - очки каждого игрока
        - победителя (или победителей при ничьей)
        """
        print("\n=== Итог ===")
        for name, pts in self.points.items():
            print(f"{name}: {pts}")
        
        winner = max(self.points, key=self.points.get)
        winners = [name for name, pts in self.points.items() if pts == self.points[winner]]
        
        print(f"Победители: {', '.join(winners)}")
       


# Пример игры
if __name__ == "__main__":
    agent1 =  agents.RandomAgent("RandomBot")#MirrorAgent("MirrorBot")
    agent2 = agents.MinimaxAgent("MinimaxBot")#HumanAgent("Player")
    agent3 = agents.PunisherAgent("PunisherBot")
    agent4 = agents.BayesianAgent("BayesianBot")
    #agent5 = agents.AdaptiveAgent("AdaptiveBot")
    agent6 = agents.MirrorAgent("MirrorBot")
    agent7 = agents.HumanAgent("HumanBot")

    agent8 = agents.DoNothingAgent("DoNothingBot")
    game = Game(agent2, agent7)
    game.play()        