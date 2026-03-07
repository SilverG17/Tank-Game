from entities.tree import Tree
from constants import TILE_SIZE

class WorldLoader:
    @staticmethod
    def spawn_objects_from_map(level_map, tree_img):
        trees = []

        for row_index, row in enumerate(level_map):
            for col_index, char in enumerate(row):

                if char == 'T':
                    trees.append(
                        Tree(
                            col_index,
                            row_index,
                            TILE_SIZE,
                            tree_img
                        )
                    )

        return trees