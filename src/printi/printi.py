import functools
import sys
from dataclasses import dataclass
from itertools import product
import math
import re
from fractions import Fraction as F


@dataclass
class Config:
    min_denominator: int
    max_denominator: int
    tol: float  # Passed to math.isclose()
    specials: dict[float, str]
    symbol: str


class Printi:
    # TODO (@davidgilbertson): these docs don't show up with `help(printi)`
    def __init__(self):
        self._conf = Config(
            min_denominator=3,
            max_denominator=100,
            tol=1e-9,
            specials={
                math.pi: 'π',
                math.tau: 'τ',
                math.e: 'e',
            },
            symbol='💡',
        )
        self.original_write = None

    # TODO (@davidgilbertson): how to inherit the type annotations of print?
    #  Must I extend print, oh but that's not a class.
    #  What does @wrapped do? The docs say:
    #      "Note that the current implementation only supports function attributes
    #       on user-defined functions. Function attributes on built-in functions
    #       may be supported in the future."
    def __call__(self, *args, **kwargs):
        print(*args, **kwargs)
        string = ' '.join(map(str, args))

        for rep in self.find_representations(string):
            print(rep)

    # TODO (@davidgilbertson): delete this set_config, better to do it directly setting attributes
    # def set_config(self, **new_opt):
    #     # TODO (@davidgilbertson): Explicit `None` resets to default?
    #     for key, val in new_opt.items():
    #         if hasattr(self._conf, key):
    #             setattr(self._conf, key, val)
    #         else:
    #             print(f'Unknown option {key!r}')

    def format_equation(
            self,
            const: float,
            add: int = 0,
            mult: int = 1,
            power: F | int = 1,
            div: int = 1,
            flip_sign: bool = False,
    ) -> str:
        # The base form is: add + mult * const ** power / div
        # The code below starts with const and appends/prepends the other parts
        # to build the return string
        assert div >= 1

        result = const

        const_on_top = power > 0
        power = abs(power)

        # TODO (@davidgilbertson): I don't love how this becomes a string so soon
        #  Is there a smarter way to do this, where I fill in slots? E.g. in a ± bc/cd
        if const in self._conf.specials:
            result = self._conf.specials[const]

        if power == F(1, 2):
            result = f'√{result}'
        elif power == F(1, 3):
            result = f'∛{result}'
        elif power == 2:
            result = f'{result}²'
        elif power == 3:
            result = f'{result}³'
        elif power == 4:
            result = f'{result}⁴'
        elif power != 1:
            result = f'{result}^{power}'

        sub_from = 0
        if add != 0 and mult < 0:
            sub_from = add
            add = 0
            mult *= -1

        if const_on_top:
            if mult != 1:
                if isinstance(result, float):
                    result *= mult
                elif power > 1 and isinstance(const, int):
                    result = f'{mult}×{result}'
                else:
                    result = f'{mult}{result}'

            if div != 1:
                result = f'{result}/{div}'
        else:  # const is on the bottom
            if div != 1:
                if isinstance(result, float):
                    result *= div
                elif power > 1 and isinstance(const, int):
                    result = f'({div}×{result})'  # e.g. 3×5²
                else:
                    result = f'{div}{result}'  # e.g. 3π

            result = f'{mult}/{result}'

        if add > 0:
            sign = '-' if flip_sign else '+'
            result = f'{add} {sign} {result}'
        elif add < 0:
            sign = '-' if flip_sign else ''
            result = f'{sign}{result} - {abs(add)}'
        elif sub_from != 0:
            # subtracting a negative is addition, so the sign is flipped here
            sign = '+' if flip_sign else '-'
            result = f'{sub_from} {sign} {result}'
        else:
            sign = '-' if flip_sign else ''
            result = f'{sign}{result}'

        return result

    @staticmethod
    def format_fraction(frac: F) -> str:
        n = frac.numerator
        d = frac.denominator

        if n > d:
            return f'{n // d} + {n % d}/{d}'

        return f'{n}/{d}'

    # TODO (@davidgilbertson): can I get autocomplete for these params
    #  Based on the Config type?
    def update_config(self, **new_config):
        for key, val in new_config.items():
            if key == 'specials':
                assert isinstance(val, dict)
                for s_key, s_val in val.items():
                    assert isinstance(s_key, float)
                    assert isinstance(s_val, str | None)
                    if s_val is None:
                        del self._conf.specials[s_key]
                    else:
                        self._conf.specials[s_key] = s_val
            elif hasattr(self._conf, key):
                setattr(self._conf, key, val)
            else:
                print(f'{key!r} is not a valid config option')

        # TODO (@davidgilbertson): write tests. Check cache clearing
        self.find_representation.cache_clear()
        self.find_representations.cache_clear()
        return self._conf

    @functools.lru_cache(maxsize=1000)
    def find_representation(self, num: float):
        last_resort = None

        # TODO (@davidgilbertson): perhaps track all matches, then pick the best representation
        #  e.g. prefer √2/2 over 1/√2
        fracs = [
            (1, 1),
            (1, 2),
            (1, 3), (2, 3),
            (1, 4), (3, 4),
            (1, 5), (2, 5), (3, 5), (4, 5),
            (1, 6), (5, 6),
            (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7),
            (1, 8), (3, 8), (5, 8), (7, 8),
            (1, 9), (2, 9), (4, 9), (5, 9), (7, 9), (8, 9),
        ]
        powers = [
            1, 2, 3, 4,
            F(1, 2), F(1, 3),
            -F(1, 2), -F(1, 3),
        ]
        constants = list(self._conf.specials.keys()) + list(range(1, 10))
        min_denominator = self._conf.min_denominator
        max_denominator = self._conf.max_denominator

        # Skip things like 0.99999999999999999 ≈ 1. Not helpful!
        # TODO (@davidgilbertson): is num %1 better than round()?
        if math.isclose(round(num), num, rel_tol=self._conf.tol):
            return

        # First test for plain fractions
        frac = F(num).limit_denominator()
        if min_denominator <= frac.denominator <= max_denominator:
            return self.format_fraction(frac)

        for constant, (mult, divisor), power in product(constants, fracs, powers):
            # if constant == math.pi and mult == 1 and divisor == 1 and power == 1:
            #     breakpoint()

            # Don't raise 1 to anything
            if constant == 1 and power != 1:
                continue

            # Avoid things like 2²
            if constant not in self._conf.specials and power > 1:
                continue

            #  To avoid things like √4, allow √3
            if power < 1 and constant ** power % 1 == 0:
                continue

            test = (mult * constant ** power) / divisor
            # All test values are positive, so we compare with an absolute value,
            # and flip the sign back later if required
            if math.isclose(abs(num), test, rel_tol=self._conf.tol):
                return self.format_equation(
                    # add=0,
                    mult=mult,
                    const=constant,
                    power=power,
                    div=divisor,
                    flip_sign=num < 0
                )

            # For the special constants, we check some other patterns
            if constant in self._conf.specials or power < 1:
                # Can we adjust by an integer? Includes subtraction I.e. π + -x is π - x
                # If we're off by a whole number, just add that number
                add_to = num - test
                if round(add_to) == add_to:
                    return self.format_equation(
                        add=int(add_to),
                        mult=mult,
                        const=constant,
                        power=power,
                        div=divisor,
                    )

                # Can we subtract from an integer? I.e. x - π
                sub_from = num + test
                if round(sub_from) == sub_from:
                    # TODO (@davidgilbertson): I should be able to use add_to and mult *= -1
                    return self.format_equation(
                        add=int(sub_from),
                        mult=mult * -1,
                        const=constant,
                        power=power,
                        div=divisor,
                    )

                # Can we multiply by an integer? E.g. 3π
                mult_by = num / test
                if round(mult_by) == mult_by:
                    return self.format_equation(
                        # add=0,
                        mult=mult * round(mult_by),
                        const=constant,
                        power=power,
                        div=divisor,
                    )

            # In addition to looping over mult/divisor, we also check if there's some big
            #  fraction we can mix in.
            # TODO (@davidgilbertson): it would be nice to combine big fractions with add/subtract
            if mult == 1 and divisor == 1 and constant in self._conf.specials:
                frac = F(num / test).limit_denominator()

                if frac and min_denominator <= frac.denominator <= max_denominator:
                    # This matches quite eagerly, but there could be cleaner results.
                    # So we store this and if nothing else returns a value, we'll return this.
                    last_resort = self.format_equation(
                        # add=0,
                        mult=mult * frac.numerator,
                        const=constant,
                        power=power,
                        div=divisor * frac.denominator,
                    )

        return last_resort

    @functools.lru_cache(maxsize=1000)
    def find_representations(self, string: str) -> list[str]:
        results = []
        # TODO (@davidgilbertson): make min_decimals an option
        # TODO (@davidgilbertson): add when min_decimals is 0, allow looking up
        #  ints in the specials list. I mean, meh, really? Nah, that's dumb.
        for num_string in re.findall(r'-?\d+\.\d{4,}', string):
            # This might be a duplicate, but the function is cached so this isn't
            # wasteful
            if rep := self.find_representation(float(num_string)):
                if (result := f'{self._conf.symbol} {num_string} ≈ {rep}') not in results:
                    results.append(result)

        return results

    def watch(self):
        std_write = sys.stdout.write
        self.original_write = std_write

        # TODO (@davidgilbertson): for something like this, it interrupts a lot
        #  for i in range(2, 29):
        #      print(f'{i=} {math.comb(i, 2) / 365 =}')
        #  Can I put all the 💡 things at the end? Can I batch? Must I use async?
        #  Maybe config log_location: Literal['replace', 'line_end', 'line_below', 'batch']

        def watched_write(value):
            std_write(value)

            # print() calls this with '\n' for every other write, skip those
            if value != '\n':
                for result in self.find_representations(value):
                    std_write('\n')
                    std_write(result)

        sys.stdout.write = watched_write

        print('Printi is watching. '
              f'Representations will be shown with a {self._conf.symbol}. '
              'Type `printi.unwatch()` to stop.')

    def unwatch(self):
        if self.original_write:
            sys.stdout.write = self.original_write

        print('Printi is no longer watching. Type `printi.watch()` to resume.')


printi = Printi()
watch = printi.watch
unwatch = printi.unwatch
update_config = printi.update_config


def main():
    print('Running printi.py')

    printi(0.7071067811865476)

    # printi(f'Hey this is {math.sin(math.pi / 4)=}')
    # printi(f'1. This is 1.2345678')
    # printi.update_config(specials={1.2345678: 'y'}, max_denominator=5)
    # printi(f'2. This is 1.2345678')
    # printi.update_config(specials={1.2345678: None})
    # printi(f'3. This is 1.2345678')
    # printi('What is this 1.2345678 thing?')


if __name__ == '__main__':
    main()
