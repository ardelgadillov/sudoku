import pyomo.environ as pyo
from pyomo.core.util import quicksum
from pyomo.opt import SolverFactory
import pandas as pd
import requests
from itertools import islice
import os
import logging.config

# open logging configuration file
logging.config.fileConfig('sudoku_log.config')
# create logger
logger = logging.getLogger('Sudoku')


# 'application' code
class Sudoku:
    def __init__(self, fixed):
        # logger.debug('debug message')
        # logger.info('info message')
        # logger.warning('warn message')
        # logger.error('error message')
        # logger.critical('critical message')
        logger.info('Sudoku constructor')
        self.fixed = fixed
        self.solution = [[0] * 9 for i in range(9)]
        self.model = self.sudoku_model()
        self.solve()

    @staticmethod
    def sudoku_model():
        """ define the optimization model

        Args:
            fixed: fixed values
        """

        logger.info('Create optimization model')

        model = pyo.ConcreteModel()

        """Sets"""
        model.i = pyo.RangeSet(1, 9)  # rows - 1 to 9
        model.j = pyo.RangeSet(1, 9)  # columns - 1 to 9
        model.k = pyo.RangeSet(1, 9)  # digits - 1 to 9

        model.p = pyo.RangeSet(1, 3)  # boxes - 1 to 3
        model.q = pyo.RangeSet(1, 3)  # boxes - 1 to 3

        """Variables"""
        model.x = pyo.Var(model.i, model.j, model.k, domain=pyo.Binary)

        """Objective Function"""

        def obj_expression(m):
            return quicksum(m.x[i, j, k] for i in m.i for j in m.j for k in m.k)

        """Constraints"""

        # Unique digits
        def c_digits(m, i, j):
            return quicksum(m.x[i, j, k] for k in m.k) == 1

        # Unique in rows
        def c_rows(m, j, k):
            return quicksum(m.x[i, j, k] for i in m.i) == 1

        # Unique in columns
        def c_columns(m, i, k):
            return quicksum(m.x[i, j, k] for j in m.j) == 1

        # Unique in boxes
        def c_boxes(m, k, p, q):
            return quicksum(m.x[i, j, k] for i in range(3 * p - 2, 3 * p + 1) for j in range(3 * q - 2, 3 * q + 1)) == 1

        """Define optimization problem"""
        model.obj = pyo.Objective(rule=obj_expression, sense=pyo.maximize)
        """Add constraints to optimization model"""
        model.c_digits = pyo.Constraint(model.i, model.j, rule=c_digits)
        model.c_rows = pyo.Constraint(model.j, model.k, rule=c_rows)
        model.c_columns = pyo.Constraint(model.i, model.k, rule=c_columns)
        model.c_boxes = pyo.Constraint(model.k, model.p, model.q, rule=c_boxes)

        # return model
        return model

    @classmethod
    def from_rapidapi(cls, difficulty="easy"):
        logger.info('Reading Sudoku puzzle from rapidapi')

        url = 'https://sudoku-generator1.p.rapidapi.com/sudoku/generate'
        querystring = {"difficulty": difficulty}
        headers = {
            'x-rapidapi-host': 'sudoku-generator1.p.rapidapi.com',
            'x-rapidapi-key': os.getenv('rapidapi_key')
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        output = response.json()
        str_sudoku = output['puzzle']
        str_sudoku = str_sudoku.replace('.', '0')
        list_sudoku = list(str_sudoku)
        list_sudoku = [int(i) for i in list_sudoku]

        # Length of 2D lists needed
        len_2d = [9] * 9

        # Use islice
        def convert(list_a, len_2d):
            res = iter(list_a)
            return [list(islice(res, i)) for i in len_2d]

        fixed = convert(list_sudoku, len_2d)
        print(pd.DataFrame(fixed))
        return cls(fixed)

    def decode(self):
        dec = [(i + 1, j + 1, self.fixed[i][j]) for i in range(9)
               for j in range(9)
               if ((self.fixed[i][j] >= 1) and (self.fixed[i][j] <= 9))]
        for i in dec:
            self.model.x[i].fix(1)

    def encode(self):
        for (i, j, k), v in self.model.x.items():
            if pyo.value(v) == 1:
                self.solution[i - 1][j - 1] = k

    def solve(self):
        logger.info('Solving sudoku')

        self.decode()
        opt = SolverFactory('cbc', executable='cbc')
        opt.solve(self.model)
        self.encode()

        logger.info('Sudoku solution')
        print(pd.DataFrame(self.solution))
