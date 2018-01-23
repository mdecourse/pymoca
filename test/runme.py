import casadi as ca
import numpy as np

import os

import unittest
import pymola.backends.casadi.generator as gen_casadi
from pymola.backends.casadi.alias_relation import AliasRelation
from pymola.backends.casadi.model import Model, Variable
from pymola.backends.casadi.api import transfer_model, CachedModel
from pymola import parser, ast

TEST_DIR = os.path.dirname(os.path.realpath(__file__))

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


    def test_simple_array(self):
        with open(os.path.join(TEST_DIR, 'SimpleArray.mo'), 'r') as f:
            txt = f.read()
        ast_tree = parser.parse(txt)
        casadi_model = gen_casadi.generate(ast_tree, 'SimpleArray')

        casadi_model.simplify({})

        print(casadi_model)
        ref_model = Model()

        a_1 = ca.MX.sym("a[1]")
        a_2 = ca.MX.sym("a[2]")
        a_3 = ca.MX.sym("a[3]")
        b_1 = ca.MX.sym("b[1]")
        b_2 = ca.MX.sym("b[2]")
        b_3 = ca.MX.sym("b[3]")
        b_4 = ca.MX.sym("b[4]")
        c_1 = ca.MX.sym("c[1]")
        c_2 = ca.MX.sym("c[2]")
        c_3 = ca.MX.sym("c[3]")
        d_1 = ca.MX.sym("d[1]")
        d_2 = ca.MX.sym("d[2]")
        d_3 = ca.MX.sym("d[3]")
        e_1 = ca.MX.sym("e[1]")
        e_2 = ca.MX.sym("e[2]")
        e_3 = ca.MX.sym("e[3]")
        g = ca.MX.sym("g")
        h = ca.MX.sym("h")
        i_1_1 = ca.MX.sym('i[1,1]')
        i_1_2 = ca.MX.sym('i[1,2]')
        i_1_3 = ca.MX.sym('i[1,3]')
        i_2_1 = ca.MX.sym('i[2,1]')
        i_2_2 = ca.MX.sym('i[2,2]')
        i_2_3 = ca.MX.sym('i[2,3]')

        B_1 = ca.MX.sym("B[1]")
        B_2 = ca.MX.sym("B[2]")
        B_3 = ca.MX.sym("B[3]")
        C_1 = ca.MX.sym("C[1]")
        C_2 = ca.MX.sym("C[2]")
        D_1 = ca.MX.sym("D[1]")
        D_2 = ca.MX.sym("D[2]")
        D_3 = ca.MX.sym("D[3]")
        E_1 = ca.MX.sym("E[1]")
        E_2 = ca.MX.sym("E[2]")

        ar_x_1 = ca.MX.sym("ar.x[1]")
        ar_x_2 = ca.MX.sym("ar.x[2]")
        ar_x_3 = ca.MX.sym("ar.x[3]")
        arcy_1 = ca.MX.sym("arc.y[1]")
        arcy_2 = ca.MX.sym("arc.y[2]")
        arcw_1 = ca.MX.sym("arc.w[1]")
        arcw_2 = ca.MX.sym("arc.w[2]")
        nested1z_1 = ca.MX.sym('nested1.z[1]')
        nested1z_2 = ca.MX.sym('nested1.z[2]')
        nested1z_3 = ca.MX.sym('nested1.z[3]')
        nested2z_1_1 = ca.MX.sym('nested2.z[1,1]')
        nested2z_1_2 = ca.MX.sym('nested2.z[1,2]')
        nested2z_1_3 = ca.MX.sym('nested2.z[1,3]')
        nested2z_2_1 = ca.MX.sym('nested2.z[2,1]')
        nested2z_2_2 = ca.MX.sym('nested2.z[2,2]')
        nested2z_2_3 = ca.MX.sym('nested2.z[2,3]')
        nested1n = ca.MX.sym('nested1.n')
        nested2n_1 = ca.MX.sym('nested2.n[1]')
        nested2n_2 = ca.MX.sym('nested2.n[2]')

        scalar_f = ca.MX.sym("scalar_f")
        c_dim = ca.MX.sym("c_dim")
        d_dim = ca.MX.sym("d_dim")

        ref_model.alg_states = list(map(Variable, [ar_x_1, ar_x_2, ar_x_3, arcy_1, arcy_2, arcw_1, arcw_2, nested1z_1, nested1z_2, nested1z_3, nested2z_1_1, nested2z_1_2, nested2z_1_3, nested2z_2_1, nested2z_2_2, nested2z_2_3, a_1, a_2, a_3, c_1, c_2, c_3, d_1, d_2, d_3, e_1, e_2, e_3, scalar_f, g, h, i_1_1, i_1_2, i_1_3, i_2_1, i_2_2, i_2_3]))

        for i in range(19, 22):
            ref_model.alg_states[i].min = 0.0

        ref_model.parameters = list(map(Variable, [nested2n_1, nested2n_2, nested1n, d_dim]))
        parameter_values = [3, 3, 3, 3]
        for const, val in zip(ref_model.parameters, parameter_values):
            const.value = val
        ref_model.outputs = list(map(Variable, [h]))
        ref_model.constants = list(map(Variable, [b_1, b_2, b_3, b_4, c_dim, B_1, B_2, B_3, C_1, C_2, D_1, D_2, D_3, E_1, E_2]))
        constant_values = [2.7, 3.7, 4.7, 5.7, 2, 1.0, 1.5, 2.0, 1.7, 1.7, 0.0, 0.0, 0.0, 1.0, 1.0]
        for const, val in zip(ref_model.constants, constant_values):
            const.value = val

        ref_model.equations = [c_1 - (a_1 + b_1 * e_1),
                               c_2 - (a_2 + b_2 * e_2),
                               c_3 - (a_3 + b_3 * e_3),

                               d_1 - (ca.sin(a_1 / b_2)),
                               d_2 - (ca.sin(a_2 / b_3)),
                               d_3 - (ca.sin(a_3 / b_4)),

                               e_1 - (d_1 + scalar_f),
                               e_2 - (d_2 + scalar_f),
                               e_3 - (d_3 + scalar_f),

                               g - (c_1 + c_2 + c_3),

                               h - B_2,

                               ar_x_2 - scalar_f,

                               nested1z_1 - 1,
                               nested1z_2 - 1,
                               nested1z_3 - 1,
                               nested2z_1_1 - 4,
                               nested2z_1_2 - 5,
                               nested2z_1_3 - 6,
                               nested2z_2_1 - 3,
                               nested2z_2_2 - 2,
                               nested2z_2_3 - 1,

                               i_1_1 - 1,
                               i_1_2 - 1,
                               i_1_3 - 1,
                               i_2_1 - 1,
                               i_2_2 - 1,
                               i_2_3 - 1,

                               arcy_1 - arcy_2,
                               arcw_1 + arcw_2,

                               a_1 - 1,
                               a_2 - 2,
                               a_3 - 3,

                               scalar_f - 1.3]

        if not self.assert_model_equivalent_numeric(ref_model, casadi_model):
            raise Exception("Failed test")


c = GenCasadiTest()
c.test_simple_array()