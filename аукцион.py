# import random
# from abc import ABC, abstractmethod
# import agents
# from agents import Agent, MirrorAgent, HumanAgent

# # # =========================
# # # Интерфейс агента
# # # =========================
# # class Agent(ABC):
# #     def __init__(self, name: str):
# #         self.name = name

# #     @abstractmethod
# #     def make_bid(self, context: dict) -> int:
# #         """
# #         context:
# #         {
# #             'round': int,
# #             'my_points': int,
# #             'opponent_points': int,
# #             'history': list
# #         }
# #         """
# #         pass


# # # =========================
# # # Агент 1: случайный + зеркальный
# # # =========================
# # class MirrorAgent(Agent):
# #     def make_bid(self, context: dict) -> int:
# #         if context['round'] == 1:
# #             return random.randint(1, context['my_points'])

# #         last_round = context['history'][-1]
# #         return min(last_round['opponent_bid'], context['my_points'])


# # # =========================
# # # Агент 2: человек
# # # =========================
# # class HumanAgent(Agent):
# #     def make_bid(self, context: dict) -> int:
# #         while True:
# #             try:
# #                 bid = int(input(f"[{self.name}] Ставка (доступно {context['my_points']}): "))
# #                 return bid
# #             except ValueError:
# #                 print("Введите число.")


# # =========================
# # Игра
# # =========================
# class Game:
#     def __init__(self, agent1: Agent, agent2: Agent, rounds: int = 10):
#         self.agent1 = agent1
#         #self.agent1.name = "Agent1"
#         self.agent2 = agent2
#         #self.agent2.name = "Agent2"
#         self.rounds = rounds

#         if self.agent1.name == self.agent2.name:
#             self.agent2.name += "_2"

#         self.points = {
#             self.agent1.name: 200,
#             self.agent2.name: 200
#         }

#         self.history = []

#     def _validate_bid(self, bid: int, max_points: int) -> int:
#         if not isinstance(bid, int):
#             print(" Некорректный тип ставки. Установлена 0.")
#             return 0

#         if bid < 0:
#             print(" Ставка < 0. Установлена 0.")
#             return 0

#         if bid > max_points:
#             print(f"Ставка превышает доступные очки ({max_points}). Обрезана.")
#             return max_points

#         return bid

#     def _get_context(self, agent: Agent, opponent: Agent, round_number: int):
#         return {
#             'round': round_number,
#             'my_points': self.points[agent.name],
#             'opponent_points': self.points[opponent.name],
#             'history': [
#                 {
#                     'my_bid': h[agent.name]['bid'],
#                     'opponent_bid': h[opponent.name]['bid'],
#                     'value': h['value']
#                 }
#                 for h in self.history
#             ]
#         }

#     def play(self):
#         for r in range(1, self.rounds + 1):
#             print(f"\n=== Раунд {r} ===")

#             value = random.randint(10, 30)

#             # Получаем ставки
#             bid1 = self.agent1.make_bid(
#                 self._get_context(self.agent1, self.agent2, r)
#             )
#             bid2 = self.agent2.make_bid(
#                 self._get_context(self.agent2, self.agent1, r)
#             )

#             # Валидация
#             bid1 = self._validate_bid(bid1, self.points[self.agent1.name])
#             bid2 = self._validate_bid(bid2, self.points[self.agent2.name])

#             print(f"{self.agent1.name}: {bid1}")
#             print(f"{self.agent2.name}: {bid2}")

#             # Применение правил
#             if bid1 > bid2:
#                 self.points[self.agent1.name] += (value - bid1)
#                 print(f"{self.agent1.name} выигрывает ({value})")

#             elif bid2 > bid1:
#                 self.points[self.agent2.name] += (value - bid2)
#                 print(f"{self.agent2.name} выигрывает ({value})")

#             else:
#                 print("Ничья")

#             # запись истории
#             self.history.append({
#                 self.agent1.name: {'bid': bid1},
#                 self.agent2.name: {'bid': bid2},
#                 'value': value
#             })

#             print(f"Очки: {self.points}")

#         self._result()

#     def _result(self):
#         print("\n=== Итог ===")
#         for name, pts in self.points.items():
#             print(f"{name}: {pts}")
        
#         winner = max(self.points, key=self.points.get)
#         winners = [name for name, pts in self.points.items() if pts == self.points[winner]]
        
#         print(f"Победители: {', '.join(winners)}")
       



# if __name__ == "__main__":
#     agent1 =  agents.RandomAgent("RandomBot")#MirrorAgent("MirrorBot")
#     agent2 = agents.MinimaxAgent("MinimaxBot")#HumanAgent("Player")
#     agent3 = agents.PunisherAgent("PunisherBot")
#     agent4 = agents.BayesianAgent("BayesianBot")
#     #agent5 = agents.AdaptiveAgent("AdaptiveBot")
#     agent6 = agents.MirrorAgent("MirrorBot")
#     agent7 = agents.HumanAgent("HumanBot")

#     agent8 = agents.DoNothingAgent("DoNothingBot")
#     game = Game(agent2, agent7)
#     game.play()        
