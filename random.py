import random
print(''.join(random.choices([digit for digit in range(10)] + [char for char in range(ord('a'), ord('z')+1)]), random.randint(10, 20)))