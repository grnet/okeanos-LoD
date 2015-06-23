#!/usr/bin/python
import random

""" Create a random message with 20 words and 5 tags.

	Create 2 lists, one for the message and one for the tags.
	Select 25 random numbers in range 1 - #number of file lines.
	Read the file and for each line selected, add it to the appropriate list.
	Finally print the message with the tags.
"""


def main():
	filename = '/usr/share/dict/american-english'
	lines = list()
	hashtags = list()
	message = ''
	tags = ''
	f = open(filename)

	for i in range(20):
		j = random.randrange(1, 99171)
		lines.append(j)

	for i in range(5):
		j = random.randrange(1, 99171)
		hashtags.append(j)

	i = 0
	for line in f:
		if i in lines:
			message = message + line.strip() + ' '
		if i in hashtags:
			tags = tags + '#' + line.strip() + ' '
		i += 1
	f.close()
	print message, tags

if __name__ == '__main__':
	main()
