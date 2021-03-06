from sys import stderr
import re
import math

speaker_num_map = {
    '20 for barzani dialect': 20,
    '1? possibly extinct?': 0,
    'hundreds': 400,
    'very small group': 20,
    'unclear': 30,
    '97000 speakers in india. 100190 speakers worldwide.': 100190,
    'not known': 30,
    'approx. 30': 30,
    'only a handful of speakers': 5,
    '0 extinct?': 0,
    'extinct (possibly)': 0,
    'approximately 12000': 12000,
    'extinct. unlikely any speakers remain': 0,
    'no fully fluent speakers remaining': 0,
    'unknown may be dormant': 0,
    'the last fluent speakers passed away in 2004.': 0,
    '6000 4000': 4900,
    '18000 12000': 14700,
    '42000 30000': 35500,
    'unknown; possibly 0': 0,
    'approx 9500-10500 speakers in all countries': 10000,
    '230 in paraguay unknown in argentina': 300,
    'possibly extinct': 0,
    'fewer than 20': 5,
    'no known l1 speakers in italy': 0,
    '"unlikely any speakers remain"': 0,
    'approx. 50': 50,
    'none (second language only)': 0,
    '1300 in burkina faso': 1300,
    'up to 340': 340,
    'nearly extinct': 30,
    'last known speaker passed away in 2003': 0,
    '90 households': 200,
    '42100.': 42100,
    '"practically extinct" (omo-murle dialect only)': 0,
    'about 1000 quite possibly less': 1000,
    '15? or extinct?': 10,
    'fewer than 100': 60,
    'about 20': 20,
    '"extinct. unlikely any speakers remain"': 0,
    'some in tanzania': 30,
    '24 nearly extinct': 24,
    'fewer than 100 families': 200,
    '45 speakers and semispeakers?': 30,
    'nearly extinct': 5,
    'possibly 0': 0,
    'no known fluent speakers': 0,
    '200000 in namibia (2006). population total all countries: 251100': 251100,
    'not available': 30,
    '47800 in greenland (1995 m. krauss). 3000 east greenlandic 44000 west greenlandic 800 north greenlandic. population total all countries: 57800': 57800,
    '5800. 725 monolinguals (1990 census). ethnic population: 6300': 6300,
    'one or two thousand': 1500,
    'a couple hundred': 400,
    'only in the hundreds': 200,
    'language with less than ten speakers or only rememberers':8,
    'many adults': 50,
    '3.132': 3132

}
zeros = set([
    'no known l1 speakers',
    'no known speakers',
    'no known speakers.',
    'no known native speakers',
    'extinct',
    'extinct?',
    '"no remaining speakers"',
    'likely dormant',
    'unlikely any speakers remain',
    '"unlikely that any speakers remain."',
    '0 extinct',
    'no fully competent speakers.',
    'obsolescent',
    'obsolescent (i.e. no longer spoken' +\
    'as an everyday language but a few speakers remember it)'
])
unknown = set([
    'no estimate available',
    'number of speakers unknown',
    'unknown',
    '?',
])
few = set([
    'few',
    'few?',
    'a few',
    'very few',
    'a few users',
    'a handful',
    'some',
    'few signers',
    '? few',
    '"a few"'
])

interval_re = re.compile(ur'~?\s*(\d+)\s*[-\u2013~]\s*(\d+)', re.UNICODE)
date_after_re = re.compile(r'^(~|(>|<))?\s*(\d+)\s*\(', re.UNICODE)
num_re = re.compile(r'^(~|(>|<))?\s*(\d+)\??\+?$', re.UNICODE)
one_number_in_line_re = re.compile(
    r'^[^0-9]*?(~|(>|<))?\s*(\d+)\??\+?[^0-9]*$', re.UNICODE)
category_map = {
    'Safe': 8,
    'At risk': 6,
    'Vulnerable': 5,
    'Threatened': 4,
    'Endangered': 3,
    'Severely endangered': 2,
    'Critically endangered': 1,
    'Dormant': 0,
    'Awakening': 0,
}


def aggregate_category(fields):
    avg = 0
    not_zero = 0
    categories = list()
    for cat, conf in fields:
        categories.append((category_map[cat], int(conf)))
        avg += int(conf)
        if not int(conf) == 0:
            not_zero += 1
    if len(fields) == 0:
        return 'n/a', 'n/a'
    if not_zero == 0:
        return sum(i[0] for i in categories) / float(len(categories)), 0
    avg = float(avg) / not_zero
    score = 0.0
    weights = 0.0
    for cat, weight in categories:
        if weight == 0:
            weights += avg
            score += cat * avg
        else:
            weights += weight
            score += cat * weight
    return sum(i[0] for i in categories) / float(len(categories)), \
        weights / float(len(categories))


def aggregate_l1(fields_):
    fields = list(fields_)
    s = 0
    if len(fields) == 0:
        return 0
    for fd in fields:
        num = normalize_number(fd.strip().lower())
        if num == 0:
            num = 1
        s += math.log(num)
    s /= len(fields)
    return round(math.exp(s), 1)


def geometric_mean(numbers):
    if len(numbers) == 0:
        return 0
    s = 0
    for n in numbers:
        s += math.log(n)
    s /= len(numbers)
    return round(math.exp(s), 1)


def normalize_number(num):
    
    if num_re.match(num):
        g = num_re.match(num).groups()
        n = int(g[2])
        if g[0] in [None, '~']:
            return n if n > 0 else 1
        elif g[0] == '<':
            return math.floor(0.9 * n)
        elif g[0] == '>':
            return math.floor(1.1 * n)
    if num.strip().lower() in zeros:
        return 1
    elif num.strip().lower() in unknown:
        return 30
    elif num.strip().lower() in few:
        return 30
    elif interval_re.match(num):
        m = interval_re.match(num)
        return geometric_mean2(int(m.group(1)), int(m.group(2)))
    elif date_after_re.match(num):
        g = date_after_re.match(num).groups()
        n = int(g[2])
        if g[0] in [None, '~']:
            return n if n > 0 else 1
        elif g[0] == '<':
            return math.floor(0.9 * n)
        elif g[0] == '>':
            return math.floor(1.1 * n)
    elif 'few dozen' in num:
        return 30
    elif 'few hundred' in num:
        return 300
    elif 'few thousand' in num:
        return 3000
    elif 'several dozen' in num:
        return 60
    elif 'several hundred' in num:
        return 600
    elif 'several thousand' in num:
        return 6000
    elif 'elder' in num:
        return 5
    elif num in speaker_num_map:
        return speaker_num_map[num]
    elif one_number_in_line_re.match(num):
        g = one_number_in_line_re.match(num).groups()
        n = int(g[2])
        if g[0] in [None, '~']:
            return n if n > 0 else 1
        elif g[0] == '<':
            return math.floor(0.9 * n)
        elif g[0] == '>':
            return math.floor(1.1 * n)
    else:
        stderr.write('Unmatched {0}\n'.format(num.encode('utf8')))


def geometric_mean2(n1, n2):
    return math.sqrt(n1 * n2)

def main():
    import sys
    for l in open(sys.argv[1]):
        print '{}\t{}'.format(l.strip(), normalize_number(l.strip()))

if __name__ == '__main__':
            main()
