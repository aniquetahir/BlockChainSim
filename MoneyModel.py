from mesa import Model, Agent
# from typing import Dict, ClassVar
from mesa.time import RandomActivation
import matplotlib.pyplot as plt

class MoneyModel(Model):
    def __init__(self, N: int):
        self.num_agents = N
        self.schedule = RandomActivation(self)
        # Create Agents
        for i in range(self.num_agents):
            a = MoneyAgent(i, self)
            self.schedule.add(a)

    def step(self):
        self.schedule.step()


class MoneyAgent(Agent):
    def __init__(self, uid: int, model: MoneyModel):
        super().__init__(uid, model)
        self.wealth = 1

    def step(self):
        if self.wealth == 0:
            return
        other_agent = self.random.choice(self.model.schedule.agents)
        other_agent.wealth += 1
        self.wealth -= 1

if __name__ == "__main__":
    model = MoneyModel(10)
    for i in range(10):
        model.step()

    agent_wealth = [a.wealth for a in model.schedule.agents]
    plt.hist(agent_wealth)
    plt.show()


