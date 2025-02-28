import random
import re
import importlib
from lib.helpers.city import city

def generate(template):
    """A really useful function.

        Returns None
        """
    if type(template) == dict:
        obj = {}
        for i in template.keys():
            regex = r"^.+\|optional$"
            matches = re.match(regex, i)
            if matches is not None:  # Optional
                si = i.split('|')
                if random.randint(0, 10) % 2 == 0:  # ToDo: Fixed probability (50%)
                    obj[si[0]] = generate(template[i])
            else:
                obj[i] = generate(template[i])
        return obj

    if type(template) == list:
        lst = []
        it = iter(template)
        while True:
            r = next(it, None)
            if r is None:
                break
            if type(r) == str:
                regex = r"^\{\{repeat\(\s*\d+\s*,{0,1}\s*\d*\s*\)\}\}$"
                matches = re.match(regex, r)
                if matches is not None:  # Repeat
                    s = template[0].find('(') + 1
                    e = template[0].find(')')
                    rng = template[0][s:e].replace(' ', '').split(',')
                    if len(rng) > 1:
                        repeat = random.randint(int(rng[0]), int(rng[1]))
                    else:
                        repeat = int(rng[0])
                    r = next(it, None)  # Repeat it
                    if r is None:
                        break
                    for i in range(0, repeat):
                        lst.append(generate(r))
                else:
                    lst.append(generate(r))
            else:
                lst.append(generate(r))
        return lst

    if type(template) == str:
        regex = r"^\{{2}.+\(.*\)\}{2}$"
        matches = re.match(regex, template)
        if matches is not None:
            k = template.find('(')
            method = 'lib.helpers.' + template[2:k]
            mod = importlib.import_module(method)
            call = 'mod.{}'.format(template[2:-2])
            return eval(call)
        else:
            return template
