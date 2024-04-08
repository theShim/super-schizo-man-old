class Tile:
    def __init__(self, type, variant, pos):
        self.type = type
        self.variant = variant
        self.pos = pos

def find_outline(tilemap, start_x, start_y):
    outline_tiles = set()
    stack = [(start_x, start_y)]
    
    while stack:
        x, y = stack.pop()
        if (x, y) not in outline_tiles:
            outline_tiles.add((x, y))
            # Check neighbors
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
            for nx, ny in neighbors:
                if (nx, ny) not in outline_tiles and tilemap.get(f"{nx};{ny}"):
                    stack.append((nx, ny))
    
    return outline_tiles

def find_tile_outlines(tilemap):
    outlines = []
    visited = set()
    for key in tilemap:
        x, y = map(int, key.split(';'))
        if (x, y) not in visited:
            outline = find_outline(tilemap, x, y)
            outlines.append(outline)
            visited.update(outline)
    return outlines

# Example usage:
tilemap = {
    "0;0": Tile("grass", "grass_8", (0, 0)),
    "0;3": Tile("grass", "grass_8", (0, 3)),
    "3;0": Tile("grass", "grass_8", (3, 0)),
    "2;3": Tile("rock", "rock_1", (2, 3)),
    "3;3": Tile("rock", "rock_1", (3, 3)),
    # Add more tiles as needed
}

tile_outlines = find_tile_outlines(tilemap)
for outline in tile_outlines:
    print(outline)
