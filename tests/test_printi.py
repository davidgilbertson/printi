import math
import random
import unittest
from fractions import Fraction as F
from math import pi, e, tau
from unittest.mock import patch, call

from src.printi import printi


class TestPrinti(unittest.TestCase):
    def test_printi(self):
        # This tests calling printi() directly as a function
        with patch('sys.stdout.write') as mock_write:
            printi(f'The numbers are {math.sin(math.pi / 4)} and {math.e ** 2}!')

            mock_write.assert_has_calls([
                call('The numbers are 0.7071067811865476 and 7.3890560989306495!'),
                call('\n'),
                call('💡 0.7071067811865476 ≈ 1/√2'),
                call('\n'),
                call('💡 7.3890560989306495 ≈ e²'),
                call('\n'),
            ])
            self.assertEqual(mock_write.call_count, 6)

    def test_printi_watch(self):
        # This tests using print() in watch mode
        with patch('sys.stdout.write') as mock_write:
            printi.watch()
            mock_write.reset_mock()  # calling watch() prints, clear that.

            print(f'The numbers are {math.sin(math.pi / 4)} and {math.e ** 2}!')

            mock_write.assert_has_calls([
                call('The numbers are 0.7071067811865476 and 7.3890560989306495!'),
                call('\n'),
                call('💡 0.7071067811865476 ≈ 1/√2'),
                call('\n'),
                call('💡 7.3890560989306495 ≈ e²'),
                call('\n'),
            ])
            self.assertEqual(mock_write.call_count, 6)

            printi.unwatch()

    def test_printi_no_op(self):
        with patch('sys.stdout.write') as mock_write:
            printi('This text contains nothing special')

            mock_write.assert_has_calls([
                call('This text contains nothing special'),
                call('\n'),
            ])
            self.assertEqual(mock_write.call_count, 2)

    def test_format_equation(self):
        self.assertEqual('2π/3', printi.format_equation(
            add=0,
            mult=2,
            const=pi,
            power=1,
            div=3
        ))
        self.assertEqual('2π²/3', printi.format_equation(
            add=0,
            mult=2,
            const=pi,
            power=2,
            div=3
        ))
        self.assertEqual('π⁴', printi.format_equation(
            add=0,
            mult=1,
            const=pi,
            power=4
        ))
        self.assertEqual('1 + π⁴', printi.format_equation(
            add=1,
            mult=1,
            const=pi,
            power=4
        ))
        self.assertEqual('π⁴ - 1', printi.format_equation(
            add=-1,
            mult=1,
            const=pi,
            power=4
        ))
        self.assertEqual('1 - π⁴', printi.format_equation(
            add=1,
            mult=-1,
            const=pi,
            power=4
        ))
        self.assertEqual('1 - √π/3', printi.format_equation(
            add=1,
            mult=-1,
            const=pi,
            div=3,
            power=F(1, 2)
        ))
        self.assertEqual('2/π', printi.format_equation(
            mult=2,
            const=pi,
            power=-1
        ))
        self.assertEqual('2/3√π', printi.format_equation(
            mult=2,
            const=pi,
            div=3,
            power=-F(1, 2)
        ))
        self.assertEqual('2/(3×5²)', printi.format_equation(
            mult=2,
            const=5,
            div=3,
            power=-2
        ))

    def test_find_representation(self):
        # TODO (@davidgilbertson): a normal dist with σ=0.3989422804014327
        #  has a E[0] of exactly one. This value is math.sqrt(1 / math.tau)
        #  I wish printi would have caught that. This is actually math.tau ** (-1/2), so negative
        #  fraction exponents should do the trick
        tests = [
            (1 - math.pi, '1 - π'),
            (0.5641895835477563, '1/√π'),
            (0.3989422804014327, '1/√τ'),

            # Plain fractions
            (2.3333333333333335, '2 + 1/3'),
            (0.30000000000000004, '3/10'),
            (0.49999999999999994, '1/2'),
            (1.1666666666666665, '1 + 1/6'),
            (2.3999999603083877, '2 + 2/5'),
            (0.0625, '1/16'),
            (4 / 3, '1 + 1/3'),
            (1.33333333333333333, '1 + 1/3'),
            (22 / 7, '3 + 1/7'),
            (1 / 3, '1/3'),
            (12 / 45, '4/15'),

            # Special constants
            (pi, 'π'),
            (e, 'e'),
            (2 * pi, '2π'),
            (2 * e, '2e'),

            # Roots and powers
            (math.sqrt(5) / 2, '√5/2'),
            (0.8660254037844386, '√3/2'),
            (9.869604401089358, 'π²'),
            (pi ** 3, 'π³'),
            (e ** 2, 'e²'),
            (2.0943951023931953, '2π/3'),
            (1.0471975511965976, 'π/3'),
            (0.8862269254527579, '√π/2'),
            (1.6487212707001282, '√e'),
            (0.6523876388301708, '6e/25'),

            # Additions/subtractions
            (866.8660254037844386, '866 + √3/2'),
            (0.0943951023931953, '2π/3 - 2'),
            (-9.905604897606805, '2π/3 - 12'),
            (7.905604897606805, '10 - 2π/3'),
            (-2.0943951023931953, '-2π/3'),

            # Large multipliers/divisors
            (36.075979777132, '83e²/17'),

            # Negatives
            (123 - 3 * pi ** 4 / 5, '123 - 3π⁴/5'),
            (123 - 3 * pi / -5, '123 + 3π/5'),  # Double negative
            (3 * pi / 5 - 123, '3π/5 - 123'),
            (-3 * pi / 5 - 123, '-123 - 3π/5'),
            (-36.075979777132, '-83e²/17'),

            # Close, but should be None
            (0.99999999999999999, None),
            (-240187.4999999999, None),
            (1.0000001, None),
        ]

        for test in tests:
            with self.subTest(msg=f'{test[0]} => {test[1]}'):
                self.assertEqual(test[1], printi.find_representation(test[0]))

        # TODO (@davidgilbertson): I should take the response, replace some characters,
        #  eval() it and check it's right

    def test_specials(self):
        printi.find_representation.cache_clear()
        self.assertEqual('π', printi.find_representation(pi))
        self.assertEqual('2π', printi.find_representation(tau))
        self.assertEqual(printi.find_representation.cache_info().currsize, 2)

        # Now remove pi and add tau
        printi.update_config(specials={
            math.pi: None,
            math.tau: 'τ',
        })

        # Updating config should clear cache
        self.assertEqual(printi.find_representation.cache_info().currsize, 0)

        self.assertEqual('τ/2', printi.find_representation(pi))
        self.assertEqual('τ', printi.find_representation(tau))

        # Now add some other constant (Laplace limit)
        printi.update_config(specials={0.66274341934918158097: 'λ'})
        self.assertEqual('λ', printi.find_representation(0.662743419349181))

    def test_false_positives(self):
        # Random troublemakers...
        self.assertEqual(None, printi.find_representation(0.10294784944315827))
        self.assertEqual(None, printi.find_representation(0.01267735773951350))
        self.assertEqual(None, printi.find_representation(0.06309446502889374))

        # Use this to fine tune the module options
        for _ in range(10):
            rand = random.random()
            with self.subTest(args=rand, msg=f'{rand} should be None'):
                self.assertEqual(None, printi.find_representation(rand))


if __name__ == '__main__':
    unittest.main()
