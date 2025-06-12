from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import networkx as nx
import random

class VirusAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.state = "S"  # S = Suscetível, I = Infectado, R = Recuperado, D = Morte
        self.days_infected = 0
        self.vacinado = False
        self.tipo_vacina = None

    def step(self):
        if self.state == "I":
            self.days_infected += 1

            # Definir chance de morte considerando vacinação
            death_chance = self.model.death_chance
            if self.vacinado:
                if self.tipo_vacina == "Oxford":
                    death_chance = 0.0
                elif self.tipo_vacina == "Pfizer":
                    death_chance = 0.005

            if random.random() < death_chance:
                self.state = "D"
                return

            if random.random() < self.model.recovery_chance:
                self.state = "R"
                return

            # Tentar infectar vizinhos
            neighbors = self.model.G.neighbors(self.unique_id)
            for n in neighbors:
                neighbor_agent = self.model.schedule.agents[n]
                if neighbor_agent.state == "S":
                    effective_chance = self.model.virus_spread_chance
                    if neighbor_agent.vacinado:
                        if neighbor_agent.tipo_vacina == "Oxford":
                            effective_chance *= (1 - self.model.oxford_efficacy)
                        elif neighbor_agent.tipo_vacina == "Pfizer":
                            effective_chance *= (1 - self.model.pfizer_efficacy)

                    if random.random() < effective_chance:
                        neighbor_agent.state = "I"

class VirusModel(Model):
    def __init__(self, num_nodes, avg_node_degree, initial_infected,
                 virus_check_frequency=1, infection_chance=0.3, recovery_chance=0.1, death_chance=0.002,
                 oxford_efficacy=0.79, pfizer_efficacy=0.95, percent_vacinado_oxford=0.0, percent_vacinado_pfizer=0.0):
        
        self.num_nodes = num_nodes
        self.G = nx.erdos_renyi_graph(n=self.num_nodes, p=avg_node_degree/self.num_nodes)
        self.schedule = RandomActivation(self)
        self.virus_spread_chance = infection_chance
        self.recovery_chance = recovery_chance
        self.death_chance = death_chance
        self.oxford_efficacy = oxford_efficacy
        self.pfizer_efficacy = pfizer_efficacy
        self.percent_vacinado_oxford = percent_vacinado_oxford
        self.percent_vacinado_pfizer = percent_vacinado_pfizer

        for i in range(self.num_nodes):
            a = VirusAgent(i, self)
            self.schedule.add(a)
            self.G.nodes[i]["agent"] = a

        initial_infected = int(initial_infected * self.num_nodes)
        infected_nodes = self.random.sample(range(self.num_nodes), initial_infected)
        for node in infected_nodes:
            self.schedule.agents[node].state = "I"

        # Vacinação Oxford
        num_oxford = int(self.percent_vacinado_oxford * self.num_nodes)
        oxford_agents = self.random.sample(self.schedule.agents, num_oxford)
        for agent in oxford_agents:
            agent.vacinado = True
            agent.tipo_vacina = "Oxford"

        # Vacinação Pfizer
        num_pfizer = int(self.percent_vacinado_pfizer * self.num_nodes)
        remaining_agents = [a for a in self.schedule.agents if not a.vacinado]
        pfizer_agents = self.random.sample(remaining_agents, min(num_pfizer, len(remaining_agents)))
        for agent in pfizer_agents:
            agent.vacinado = True
            agent.tipo_vacina = "Pfizer"

        self.datacollector = DataCollector(
            model_reporters={
                "Suscetivel": lambda m: sum(1 for a in m.schedule.agents if a.state == "S"),
                "Infectado": lambda m: sum(1 for a in m.schedule.agents if a.state == "I"),
                "Recuperado": lambda m: sum(1 for a in m.schedule.agents if a.state == "R"),
                "Morte": lambda m: sum(1 for a in m.schedule.agents if a.state == "D"),
                "Vacinado_Oxford": lambda m: sum(1 for a in m.schedule.agents if a.vacinado and a.tipo_vacina == "Oxford"),
                "Vacinado_Pfizer": lambda m: sum(1 for a in m.schedule.agents if a.vacinado and a.tipo_vacina == "Pfizer")
            }
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

def network_portrayal(G):
    portrayal = {"nodes": [], "edges": []}
    
    for node in G.nodes():
        agent = G.nodes[node].get("agent", None)
        color = "#808080"  # Default gray

        if agent:
            if agent.state == "D":
                color = "#000000"  
            elif agent.state == "I":
                color = "#FF0000"  
            elif agent.state == "R":
                color = "#00FF00"  
            elif agent.state == "S":
                color = "#0080FF"  

        if agent.state != "D" and agent.vacinado:
            if agent.tipo_vacina == "Oxford":
                color = "#FFFF00"
            elif agent.tipo_vacina == "Pfizer":
                color = "#FF00FF"

        portrayal["nodes"].append({
            "id": node,
            "color": color,
            "size": 6,
            "tooltip": f"State: {agent.state if agent else 'None'}"
        })

    for edge in G.edges():
        portrayal["edges"].append({
            "source": edge[0],
            "target": edge[1],
            "color": "#CCCCCC"
        })

    return portrayal
