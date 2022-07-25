import argparse

parser= argparse.ArgumentParser(prog='Test', usage='%(prog)s -f Filename Option1 Option2 ')
parser.add_argument ('-c', '--cb_size', nargs=2, type=int, action = 'append')

checkerboardSize = parser.parse_args().cb_size

print(checkerboardSize)

print(tuple(checkerboardSize[0]))

for f in checkerboardSize:
    print(tuple(f))
