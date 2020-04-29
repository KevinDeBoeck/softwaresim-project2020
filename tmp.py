from rectpack import newPacker

rectangles = [(250, 400)]
bins = [(300, 450)]

packer = newPacker()

# Add the rectangles to packing queue
for r in rectangles:
	packer.add_rect(*r)

# Add the bins where the rectangles will be placed
for b in bins:
	packer.add_bin(*b)

# Start packing
packer.pack()
rectangle = (50, 20)
rectangle2 = (150, 80)
print(len(packer[0]))
packer.add_rect(*rectangle2)
packer.pack()
print(len(packer[0]))
packer.add_rect(*rectangle)
packer.pack()
print(len(packer[0]))
