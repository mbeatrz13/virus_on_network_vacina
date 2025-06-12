from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import NetworkModule, ChartModule
from mesa.visualization.UserParam import Slider, NumberInput
from model import VirusModel, network_portrayal

network = NetworkModule(network_portrayal, 500, 500)

chart = ChartModule([
    {"Label": "Suscetivel", "Color": "#0080FF"},
    {"Label": "Infectado", "Color": "#FF0000"},
    {"Label": "Recuperado", "Color": "#00FF00"},
    {"Label": "Morte", "Color": "#000000"},
    {"Label": "Vacinado_Oxford", "Color": "#FFFF00"},
    {"Label": "Vacinado_Pfizer", "Color": "#FF00FF"}
])

model_params = {
    "num_nodes": NumberInput("Número de Agentes", value=100),
    "avg_node_degree": Slider("Grau Médio dos Nós", 4, 1, 10, 1),
    "initial_infected": Slider("Infectados Iniciais (%)", 0.05, 0.01, 1.0, 0.01),
    "virus_check_frequency": Slider("Frequência de Verificação do Vírus", 1, 1, 10, 1),
    "infection_chance": Slider("Probabilidade de Infecção", 0.3, 0.0, 1.0, 0.01),
    "recovery_chance": Slider("Probabilidade de Recuperação", 0.1, 0.0, 1.0, 0.01),
    "death_chance": Slider("Probabilidade de Morte", 0.002, 0.0, 0.05, 0.001),
    "percent_vacinado_oxford": Slider("Vacinação Oxford (1ª dose)", 0.0, 0.0, 1.0, 0.05),
    "percent_vacinado_pfizer": Slider("Vacinação Pfizer (1ª dose)", 0.0, 0.0, 1.0, 0.05),
    "oxford_efficacy": Slider("Eficácia da Oxford", 0.79, 0.0, 1.0, 0.01),
    "pfizer_efficacy": Slider("Eficácia da Pfizer", 0.95, 0.0, 1.0, 0.01)
}

server = ModularServer(
    VirusModel,
    [network, chart],
    "Disseminação Viral em Rede com Vacinação",
    model_params
)

server.port = 8521
server.launch()
