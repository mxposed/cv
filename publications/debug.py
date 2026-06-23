import argparse
import sys
import json

import filter


def main():
    if sys.argv[1] == 'dump':
        data = json.load(open("filtered_publications.json", "r"))
        for item in data:
            print(item + "\n")
            for p in data[item]:
                print(p)

if __name__ == '__main__':
    main()
