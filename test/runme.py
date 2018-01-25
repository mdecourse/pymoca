#!/usr/bin/env python
"""
Modelica parse Tree to AST tree.
"""
from __future__ import print_function, absolute_import, division, unicode_literals

import os
import glob
import unittest
import itertools

import casadi as ca
import numpy as np

import pymola.backends.casadi.generator as gen_casadi
from pymola.backends.casadi.alias_relation import AliasRelation
from pymola.backends.casadi.model import Model, Variable
from pymola.backends.casadi.api import transfer_model, CachedModel
from pymola import parser, ast


TEST_DIR = os.path.dirname(os.path.realpath(__file__))


# noinspection PyPep8Naming,PyUnresolvedReferences
class GenCasadiTest(unittest.TestCase):
    def assert_model_equivalent(self, A, B):
        def sstr(a): return set([str(e) for e in a])

        for l in ["states", "der_states", "inputs", "outputs", "constants", "parameters"]:
            self.assertEqual(sstr(getattr(A, l)), sstr(getattr(B, l)))

    def assert_model_equivalent_numeric(self, A, B, tol=1e-9):
        self.assertEqual(len(A.states), len(B.states))
        self.assertEqual(len(A.der_states), len(B.der_states))
        self.assertEqual(len(A.inputs), len(B.inputs))
        self.assertEqual(len(A.outputs), len(B.outputs))
        self.assertEqual(len(A.constants), len(B.constants))
        self.assertEqual(len(A.parameters), len(B.parameters))

        if not isinstance(A, CachedModel) and not isinstance(B, CachedModel):
            self.assertEqual(len(A.equations), len(B.equations))
            self.assertEqual(len(A.initial_equations), len(B.initial_equations))

        for f_name in ['dae_residual', 'initial_residual', 'variable_metadata']:
            this = getattr(A, f_name + '_function')
            that = getattr(B, f_name + '_function')

            np.random.seed(0)

            args_in = []
            for i in range(this.n_in()):
                sp = this.sparsity_in(0)
                r = ca.DM(sp, np.random.random(sp.nnz()))
                args_in.append(r)

            this_out = this.call(args_in)
            that_out = that.call(args_in)

            # N.B. Here we require that the order of the equations in the two models is identical.
            for i, (a, b) in enumerate(zip(this_out, that_out)):
                for j in range(a.size1()):
                    for k in range(a.size2()):
                        if a[j, k].is_regular() or b[j, k].is_regular():
                            test = float(ca.norm_2(ca.vec(a[j, k] - b[j, k]))) <= tol
                            if not test:
                                print(j)
                                print(k)
                                print(a[j,k])
                                print(b[j,k])
                                print(f_name)
                            self.assertTrue(test)

        return True

    def test_function_call(self):
        with open(os.path.join(TEST_DIR, 'FunctionCall.mo'), 'r') as f:
            txt = f.read()
        ast_tree = parser.parse(txt)
        casadi_model = gen_casadi.generate(ast_tree, 'FunctionCall')
        print("FunctionCall", casadi_model)
        ref_model = Model()

        radius = ca.MX.sym('radius')
        diameter = radius * 2
        circle_properties = ca.Function('circle_properties', [radius], [3.14159*diameter, 3.14159*radius**2, ca.if_else(3.14159*radius**2 > 10, 1, 2), ca.if_else(3.14159*radius**2 > 10, 10, 3.14159*radius**2), 8, 3, 12])

        c = ca.MX.sym("c")
        a = ca.MX.sym("a")
        d = ca.MX.sym("d")
        e = ca.MX.sym("e")
        S1 = ca.MX.sym("S1")
        S2 = ca.MX.sym("S2")
        r = ca.MX.sym("r")
        ref_model.alg_states = list(map(Variable, [c, a, d, e, S1, S2, r]))
        ref_model.outputs = list(map(Variable, [c, a, d, e, S1, S2]))
        ref_model.equations = [ca.vertcat(c, a, d, e, S1, S2) - ca.vertcat(*circle_properties.call([r])[0:-1])]

        self.assert_model_equivalent_numeric(ref_model, casadi_model)


c = GenCasadiTest()
c.test_function_call()
