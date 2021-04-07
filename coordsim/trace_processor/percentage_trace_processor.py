from coordsim.simulation.simulatorparams import SimulatorParams
from coordsim.simulation.flowsimulator import FlowSimulator
from simpy import Environment
import numpy as np
import logging
log = logging.getLogger(__name__)


class PercentageTraceProcessor():
    """
    Trace processor class
    """

    def __init__(self, params: SimulatorParams, env: Environment, trace: list):
        self.params = params
        self.env = env
        self.trace_index = 0
        self.percentage_trace = trace
        self.init()
        self.env.process(self.process_trace())

    def init(self):
        for idx,node in enumerate(self.params.ing_nodes):
            self.params.percentage[node[0]] = dict()
            for idx_key,key in enumerate(self.percentage_trace[idx].keys()):
                if idx_key > 1:
                    self.params.percentage[node[0]][key] = float(self.percentage_trace[idx][key])
            
        pass

    def process_trace(self):
        """
        Changes the inter arrival mean during simulation
        The initial time is read from the the config file, so if the inter_arrival_time set in the trace CSV
        file does not start from 0, then the simulator will use the value set in sim_config

        """
        self.timeout = float(self.percentage_trace[self.trace_index]['time']) - self.env.now - 1
        self.timeout = np.clip(self.timeout, 0, None)
        
        percent = list()

        for idx_key,key in enumerate(self.percentage_trace[self.trace_index].keys()):
            if idx_key > 1:
                percent.append(float(self.percentage_trace[self.trace_index][key]))

        yield self.env.timeout(self.timeout)
        node_id = self.percentage_trace[self.trace_index]['node']

        for idx_key,key in enumerate(self.percentage_trace[self.trace_index].keys()):
            if idx_key > 1:
                self.params.percentage[node_id][key] = percent[idx_key-2]

        if self.trace_index < len(self.percentage_trace) - 1:
            self.trace_index += 1
            self.env.process(self.process_trace())
