def get_adjacent_tiles(pos, tiles):
    """
    Function to get adjacent tiles to a given position.
    """
    x, y = pos
    adjacent_tiles = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if (dx != dy) and (x + dx, y + dy) in tiles:
                adjacent_tiles.append((x + dx, y + dy))
    return adjacent_tiles

def dfs(start_pos, tiles, visited, group):
    """
    Depth-first search to find connected tiles.
    """
    visited.add(start_pos)
    group.append([start_pos, tiles[start_pos]])
    adjacent_tiles = get_adjacent_tiles(start_pos, tiles)
    for tile in adjacent_tiles:
        if tile not in visited:
            dfs(tile, tiles, visited, group)

def segment_tiles(tiles):
    """
    Segments tiles into groups of adjacent tiles.
    """
    groups = []
    visited = set()
    for pos in tiles:
        if pos not in visited:
            group = []
            dfs(pos, tiles, visited, group)
            groups.append(group)
    return groups

# Example usage:
tiles = {(0, 0): 1, (1, 0): 1, (1, 1): 1, (2, 1): 1, (3, 1): 1, (3, 0): 1, (10, 2):1, (3, 3):1}
groups = segment_tiles(tiles)
for g in groups:print(g)
