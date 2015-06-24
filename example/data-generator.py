#!/usr/bin/python
import random
import argparse

""" Create a random message with 20 words and 5 tags.

    Create 2 lists, one for the message and one for the tags.
    Select 25 random numbers in range 1 - #number of file lines.
    Read the file and for each line selected, add it to the appropriate list.
    Finally print the message with the tags.
"""


def create_random_message():
    # Parse arguments
    default_file = '/usr/share/dict/american-english'
    parser = argparse.ArgumentParser(description="Random data generator")
    parser.add_argument('--filename', type=str, default=default_file)
    parser.add_argument('--messages', type=int, default=20)
    parser.add_argument('--tags', type=int, default=5)
    args = parser.parse_args()

    with open(args.filename) as f:
        words = f.readlines()
        message = ' '.join(
            [random.choice(words).strip() for _ in range(args.messages)])
        tags = '#' + ' #'.join(
            [random.choice(words).strip() for _ in range(args.tags)])

    return ' '.join((message,tags))


if __name__ == '__main__':
    random_message = create_random_message()
    print random_message
