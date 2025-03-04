#!/usr/bin/env python3

"""
Procedurally generated chettinad house with a central open courtyard in Minecraft using GDPC.
Labhesh Joshi MCGA ASsignment 1
"""

import logging
from random import randint, choice
import atexit

from gdpc import Block, Editor
from gdpc import geometry as geo
from gdpc import minecraft_tools as mt
from gdpc import editor_tools as et

import matplotlib.pyplot as plt

# Set up logging
logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s")

ED = Editor(buffering=True, bufferLimit=4096)
atexit.register(ED.flushBuffer)

# Get build area
BUILD_AREA = ED.getBuildArea()
STARTX, STARTY, STARTZ = BUILD_AREA.begin
LASTX, LASTY, LASTZ = BUILD_AREA.last

# Load world slice for terrain data
WORLDSLICE = ED.loadWorldSlice(BUILD_AREA.toRect(), cache=True)
HEIGHTS = WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

# Global variable for base height
HOUSE_Y = 0

def find_build_location():
    """Scan the build area to find a suitable spot for the house."""
    print("Scanning for a suitable build location.")
    suitable_spots = []
    min_size = 19

    for x in range(STARTX + min_size, LASTX - min_size):
        for z in range(STARTZ + min_size, LASTZ - min_size):
            heights = [HEIGHTS[(x - STARTX + dx, z - STARTZ + dz)] for dx in range(-min_size//2, min_size//2 + 1)
                       for dz in range(-min_size//2, min_size//2 + 1)]
            if max(heights) - min(heights) <= 1 and max(heights) < LASTY - 10:
                suitable_spots.append((x, z, min(heights)))

    if not suitable_spots:
        fallback_x, fallback_z = STARTX + (LASTX - STARTX) // 2, STARTZ + (LASTZ - STARTZ) // 2
        fallback_y = HEIGHTS[(LASTX - STARTX) // 2, (LASTZ - STARTZ) // 2]
        print(f"No suitable flat spot found. Using fallback location.")
        return (fallback_x, fallback_z, fallback_y)
    
    chosen_spot = choice(suitable_spots)
    return chosen_spot

def build_house(x, z, y):
    global HOUSE_Y
    HOUSE_Y = y
    width = randint(19, 23)
    length = randint(19, 23)
    height = randint(4, 6)
    orientation = choice(["north-south", "east-west"])

    print(f"Building house at ({x}, {y}, {z})")

    if orientation == "north-south":
        x_min, x_max = x - width // 2, x + width // 2
        z_min, z_max = z - length // 2, z + length // 2
        door_pos = (x, y + 1, z_min)
        door_facing = "north"
    else:
        x_min, x_max = x - length // 2, x + length // 2
        z_min, z_max = z - width // 2, z + width // 2
        door_pos = (x_max, y + 1, z)
        door_facing = "west"

    # Foundation
    geo.placeCuboid(ED, (x_min, y, z_min), (x_max, y, z_max), Block("stone"))

    # Supporting pillars at corners to adapt to terrain
    for px, pz in [(x_min, z_min), (x_min, z_max), (x_max, z_min), (x_max, z_max)]:
        terrain_height = HEIGHTS[(px - STARTX, pz - STARTZ)]
        if terrain_height < y:
            geo.placeCuboid(ED, (px, terrain_height, pz), (px, y - 1, pz), Block("dark_oak_log"))
        else:
            pass
    
    # Wall
    geo.placeCuboid(ED, (x_min, y + 1, z_min), (x_max, y + height, z_max), Block("cut_sandstone"))
    for corner in [(x_min, z_min), (x_min, z_max), (x_max, z_min), (x_max, z_max)]:
        geo.placeCuboid(ED, (corner[0], y + 1, corner[1]), (corner[0], y + height, corner[1]), Block("oak_log"))

    # Roof
    print("Constructing roof")
    for h in range(height + 1, height + 4):
        roof_min = (x_min - 1 + (h - height - 1), y + h, z_min - 1 + (h - height - 1))
        roof_max = (x_max + 1 - (h - height - 1), y + h, z_max + 1 - (h - height - 1))
        geo.placeCuboid(ED, roof_min, roof_max, Block("red_nether_brick_stairs"))
    geo.placeCuboid(ED, (x_min + 2, y + height + 4, z_min + 2), (x_max - 2, y + height + 4, z_max - 2), Block("red_nether_brick_slab"))
    

    # Door
    ED.placeBlock(door_pos, Block("oak_door", {"facing": door_facing}))

    # Windows
    glass_colors = [
        "orange_stained_glass_pane", "magenta_stained_glass_pane",
        "light_blue_stained_glass_pane", "yellow_stained_glass_pane", "lime_stained_glass_pane",
        "pink_stained_glass_pane", "gray_stained_glass_pane", "light_gray_stained_glass_pane",
        "cyan_stained_glass_pane", "purple_stained_glass_pane", "blue_stained_glass_pane",
        "brown_stained_glass_pane", "green_stained_glass_pane", "red_stained_glass_pane"
    ]

    window_color = choice(glass_colors)
         
    print("Adding windows")
    for wall_x in [x_min, x_max]:
        for win_z in [z_min + 4, z_max - 4]:
            geo.placeCuboid(ED, (wall_x, y + 2, win_z - 1), (wall_x, y + 3, win_z + 2), Block(window_color))

    for wall_z in [z_min, z_max]:
        for win_x in [x_min + 4, x_max - 4]: 
            geo.placeCuboid(ED, (win_x - 1, y + 2, wall_z), (win_x + 2, y + 3, wall_z), Block(window_color))

    for wall_x in [x_min, x_max]:
        for win_z in [z_min + 4, z_max - 4]:
            geo.placeCuboid(ED, (wall_x, y + 2, win_z - 1), (wall_x, y + 3, win_z + 2), Block(window_color))

    for wall_z in [z_min + 4, z_max - 4]:
        for win_x in [x_min + 4, x_max - 4]:
            geo.placeCuboid(ED, (win_x - 1, y + 2, wall_z), (win_x + 2, y + 3, wall_z), Block(window_color))


    # Courtyard
    courtyard_size = min(width, length) // 2 - 2
    cx_min, cx_max = x - courtyard_size // 2, x + courtyard_size // 2
    cz_min, cz_max = z - courtyard_size // 2, z + courtyard_size // 2

    geo.placeCuboid(ED, (cx_min, y + 1, cz_min), (cx_max, y + height + 4, cz_max), Block("air"))

    geo.placeCuboid(ED, (cx_min, y, cz_min), (cx_max, y, cz_max), Block("grass_block"))

    # Courtyard seating
    for cx in range(cx_min, cx_max + 1):
        ED.placeBlock((cx, y + 1, cz_min), Block("oak_stairs", {"facing": "north"}))
        ED.placeBlock((cx, y + 1, cz_max), Block("oak_stairs", {"facing": "south"}))
    for cz in range(cz_min + 1, cz_max):
        ED.placeBlock((cx_min, y + 1, cz), Block("oak_stairs", {"facing": "west"}))
        ED.placeBlock((cx_max, y + 1, cz), Block("oak_stairs", {"facing": "east"}))
        

    # Campfire in courtyard
    ED.placeBlock((x, y + 1, z), Block("campfire"))

    # Clear interior
    # west section
    geo.placeCuboid(ED, (x_min + 1, y + 1, z_min + 1), (cx_min - 1, y + height, z_max - 1), Block("air"))
    # east section
    geo.placeCuboid(ED, (cx_max + 1, y + 1, z_min + 1), (x_max - 1, y + height, z_max - 1), Block("air"))
    # south section
    geo.placeCuboid(ED, (cx_min, y + 1, z_min + 1), (cx_max, y + height, cz_min - 1), Block("air"))
    # north section
    geo.placeCuboid(ED, (cx_min, y + 1, cz_max + 1), (cx_max, y + height, z_max - 1), Block("air"))

    # Pillars at courtyard
    pillar_top = height  
    corner_positions = [
        (cx_min - 1, cz_min - 1),
        (cx_min - 1, cz_max + 1),
        (cx_max + 1, cz_min - 1),
        (cx_max + 1, cz_max + 1)
    ]
    midpoint_positions = [
        (cx_min - 1, (cz_min - 1 + cz_max + 1) // 2),
        ((cx_min - 1 + cx_max + 1) // 2, cz_min - 1),
        (cx_max + 1, (cz_min - 1 + cz_max + 1) // 2),
        ((cx_min - 1 + cx_max + 1) // 2, cz_max + 1)
    ]
    all_positions = corner_positions + midpoint_positions
    for px, pz in all_positions:
        terrain_height = HEIGHTS[(px - STARTX, pz - STARTZ)]
        pillar_base = min(terrain_height, y)
        geo.placeCuboid(ED, (px, pillar_base, pz), (px, y + pillar_top, pz), Block("dark_oak_log"))


def decorate_interior(x, z):
    width = randint(19, 23)
    length = randint(19, 23)
    x_min, x_max = x - width // 2, x + width // 2
    z_min, z_max = z - length // 2, z + length // 2 
    courtyard_size = min(width, length) // 2 - 2
    cx_min, cx_max = x - courtyard_size // 2, x + courtyard_size // 2
    cz_min, cz_max = z - courtyard_size // 2, z + courtyard_size // 2

    print("Generating interior")

    # Living room (south-west)
   
    ED.placeBlock((x_min + 3, HOUSE_Y + 1, z_min + 3), Block("oak_stairs", {"facing": "north"}))
    ED.placeBlock((x_min + 4, HOUSE_Y + 1, z_min + 3), Block("oak_stairs", {"facing": "north"}))



    # Bedroom (north-west) - Ensure bed area is clear and place both parts
    ED.placeBlock((x_min + 3, HOUSE_Y + 1, z_max - 3), Block("air"))
    ED.placeBlock((x_min + 3, HOUSE_Y + 1, z_max - 3), Block("cyan_bed", {"facing": "south"}))
    ED.placeBlock((x_min + 4, HOUSE_Y + 1, z_max - 2), Block("chest"))

    # Kitchen (east)
    ED.placeBlock((x_max - 3, HOUSE_Y + 1, cz_min + 2), Block("crafting_table"))
    ED.placeBlock((x_max - 3, HOUSE_Y + 1, cz_min + 3), Block("furnace"))
    ED.placeBlock((x_max - 2, HOUSE_Y + 1, cz_min + 2), Block("barrel",{"open":"true"}))

    # Cat in the house (near courtyard entrance)
    cat_variant = choice(["red", "siamese", "white", "jellie"])

    ED.runCommand(f"summon cat {cx_max + 2} {HOUSE_Y + 1} {z} {{CatType:{cat_variant}}}")

    # Carpet with random color (living room area)
    carpet_color = choice(["red", "blue", "yellow", "purple", "orange", "white", "black"])
    geo.placeCuboid(ED, (x_min + 3, HOUSE_Y + 1, z_min + 4), (x_min + 4, HOUSE_Y + 1, z_min + 5), Block(f"{carpet_color}_carpet"))

def decorate_exterior(x, z):
    width = randint(19, 23)
    length = randint(19, 23)
    x_min, x_max = x - width // 2, x + width // 2
    z_min, z_max = z - length // 2, z + length // 2

    print("Decorating exterior")

    # Garden area
    buffer = 5
    for dx in [-buffer, buffer]:
        for dz in [-buffer, buffer]:
            geo.placeCuboid(ED, (x_min + dx, HOUSE_Y, z_min + dz), (x_max - dx, HOUSE_Y, z_max - dz), Block("grass_block"))

    # More grass patches outside garden
    for _ in range(6):
        gx = randint(STARTX, LASTX) 
        gz = randint(STARTZ, LASTZ)
        if not (x_min <= gx <= x_max and z_min <= gz <= z_max): 
            geo.placeCuboid(ED, (gx - 1, HOUSE_Y, gz - 1), (gx + 1, HOUSE_Y, gz + 1), Block("grass"))

    for _ in range(20):
        fx = randint(STARTX, LASTX)
        fz = randint(STARTZ, LASTZ)
        flower = choice(["dandelion", "poppy", "azure_bluet", "oxeye_daisy", "lilac", "rose_bush", "peony"])
        if not (x_min <= fx <= x_max and z_min <= fz <= z_max):
            ED.placeBlock((fx, HOUSE_Y + 1, fz), Block(flower))

    # Trees at garden edges with pillars below
    tree_positions = [
        (x_min - buffer, z_min - buffer),  # Southwest edge
        (x_min - buffer, z_max + buffer),  # Northwest edge
        (x_max + buffer, z_min - buffer),  # Southeast edge
        (x_max + buffer, z_max + buffer)   # Northeast edge
    ]
    heightmap_width = LASTX - STARTX + 1  
    heightmap_height = LASTZ - STARTZ + 1
    for tx, tz in tree_positions:
        # Clamp coordinates to stay within heightmap bounds
        tx_clamped = max(STARTX, min(LASTX, tx))
        tz_clamped = max(STARTZ, min(LASTZ, tz))
        terrain_height = HEIGHTS[(tx_clamped - STARTX, tz_clamped - STARTZ)]  # Get terrain height at clamped position
        if terrain_height < HOUSE_Y:
            geo.placeCuboid(ED, (tx, terrain_height, tz), (tx, HOUSE_Y - 1, tz), Block("dark_oak_log"))
        tree_height = randint(4, 6)
        geo.placeCuboid(ED, (tx, HOUSE_Y + 1, tz), (tx, HOUSE_Y + tree_height, tz), Block("oak_log"))
        leaves_height = randint(tree_height, tree_height + 1)
        geo.placeCuboid(ED, (tx - 2, HOUSE_Y + leaves_height, tz - 2), (tx + 2, HOUSE_Y + leaves_height + 1, tz + 2), Block("oak_leaves"))
        for side in ["north", "south", "east", "west"]:
            cocoa_y = HOUSE_Y + randint(2, tree_height - 1)
            if side == "north":
                cocoa_pos = (tx, cocoa_y, tz - 1)
            elif side == "south":
                cocoa_pos = (tx, cocoa_y, tz + 1)
            elif side == "east":
                cocoa_pos = (tx + 1, cocoa_y, tz)
            else:  # west
                cocoa_pos = (tx - 1, cocoa_y, tz)
            ED.placeBlock(cocoa_pos, Block("cocoa", {"facing": side, "age": "2"}))


def plot_terrain_adaptability(x, z, y, x_min, x_max, z_min, z_max, cx_min, cx_max, cz_min, cz_max, tree_positions):

    # heatmap
    plt.figure(figsize=(10, 8))
    plt.imshow(HEIGHTS, cmap='terrain', interpolation='nearest', extent=[STARTX, LASTX, STARTZ, LASTZ])
    plt.colorbar(label='Terrain Height (Blocks)')

    # house footprint (rectangle)
    house_rect = plt.Rectangle((x_min, z_min), x_max - x_min, z_max - z_min, linewidth=2, edgecolor='black', facecolor='none', label='House Footprint')
    plt.gca().add_patch(house_rect)

    # courtyard footprint (rectangle)
    courtyard_rect = plt.Rectangle((cx_min, cz_min), cx_max - cx_min, cz_max - cz_min, linewidth=2, edgecolor='blue', facecolor='none', label='Courtyard')
    plt.gca().add_patch(courtyard_rect)

    # garden footprint (rectangle)
    buffer = 5
    garden_x_min, garden_x_max = x_min - buffer, x_max + buffer
    garden_z_min, garden_z_max = z_min - buffer, z_max + buffer
    garden_rect = plt.Rectangle((garden_x_min, garden_z_min), garden_x_max - garden_x_min, garden_z_max - garden_z_min, 
                               linewidth=2, edgecolor='yellow', facecolor='none', label='Garden')
    plt.gca().add_patch(garden_rect)

    # house edge pillars
    house_edge_pillars = [(x_min, z_min), (x_min, z_max), (x_max, z_min), (x_max, z_max)]
    for px, pz in house_edge_pillars:
        px_clamped = max(STARTX, min(LASTX, px))
        pz_clamped = max(STARTZ, min(LASTZ, pz))
        terrain_height = HEIGHTS[px_clamped - STARTX, pz_clamped - STARTZ]
        color = 'red' if terrain_height < y else 'green'
        plt.plot(px, pz, '^', color=color, markersize=8, label='House Edge Pillar')


    # garden tree pillars
    for tx, tz in tree_positions:
        tx_clamped = max(STARTX, min(LASTX, tx))
        tz_clamped = max(STARTZ, min(LASTZ, tz))
        terrain_height = HEIGHTS[tx_clamped - STARTX, tz_clamped - STARTZ]
        color = 'red' if terrain_height < y else 'green'
        plt.plot(tx, tz, 's', color=color, markersize=8, label='Garden Tree Pillar')

    plt.title('Terrain Adaptability: House and Pillar Placement', fontsize=14)
    plt.xlabel('X Coordinate', fontsize=12)
    plt.ylabel('Z Coordinate', fontsize=12)
    plt.legend(loc='upper right')
    plt.savefig('terrain_adaptability_plot.png', dpi=300, bbox_inches='tight')
    plt.close()

    
def main():
    try:
        print("Starting house generation process")
        x, z, y = find_build_location()
        build_house(x, z, y)
        decorate_interior(x, z)
        decorate_exterior(x, z)
        print("House generation complete!")

    except KeyboardInterrupt:
        print("Process interrupted with Ctrl-C.")

if __name__ == '__main__':
    main()