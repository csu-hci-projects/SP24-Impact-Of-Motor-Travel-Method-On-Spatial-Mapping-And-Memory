from PIL import Image, ImageDraw
import uuid
import json
import sys


def ind_to_abs_pos(ind: int, rel_len: int):
    return ind * rel_len


def load_json(file_path: str="map_output.json"):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


class Piece:
    wall_color: str = "black"

    def __init__(self, image_draw: ImageDraw, rotation_index: int, wall_width: int, **kwargs):
        self.img_draw = image_draw
        self.rot_ind = rotation_index
        self.wall_width = wall_width

        try:
            self.x_pad = kwargs["img_padding"][0]
            self.y_pad = kwargs["img_padding"][1]

        except KeyError:
            self.x_pad = 0
            self.y_pad = 0

    def get_bottom_wall(self, x: int, y: int, cell_width: int, cell_height: int) -> list:
        org_x = ind_to_abs_pos(x, cell_width) + self.x_pad
        org_y = ind_to_abs_pos(y, cell_height) + self.y_pad

        x1 = org_x
        y1 = org_y + cell_height - self.wall_width
        x2 = org_x + cell_width
        y2 = org_y + cell_height

        return [x1, y1, x2, y2]

    def get_left_wall(self, x: int, y: int, cell_width: int, cell_height: int) -> list:
        org_x = ind_to_abs_pos(x, cell_width) + self.x_pad
        org_y = ind_to_abs_pos(y, cell_height) + self.y_pad

        x1 = org_x
        y1 = org_y
        x2 = org_x + self.wall_width
        y2 = org_y + cell_height

        return [x1, y1, x2, y2]

    def get_top_wall(self, x: int, y: int, cell_width: int, cell_height: int) -> list:
        org_x = ind_to_abs_pos(x, cell_width) + self.x_pad
        org_y = ind_to_abs_pos(y, cell_height) + self.y_pad

        x1 = org_x
        y1 = org_y
        x2 = org_x + cell_width
        y2 = org_y + self.wall_width

        return [x1, y1, x2, y2]

    def get_right_wall(self, x: int, y: int, cell_width: int, cell_height: int) -> list:
        org_x = ind_to_abs_pos(x, cell_width) + self.x_pad
        org_y = ind_to_abs_pos(y, cell_height) + self.y_pad

        x1 = org_x + cell_width - self.wall_width
        y1 = org_y
        x2 = org_x + cell_width
        y2 = org_y + cell_height

        return [x1, y1, x2, y2]

    def get_sphere(self, x: int, y: int, cell_width: int, cell_height: int, radius: int) -> list:
        org_x = ind_to_abs_pos(x, cell_width) + self.x_pad
        org_y = ind_to_abs_pos(y, cell_height) + self.y_pad
        center = (org_x + (cell_width // 2), org_y + (cell_height // 2))

        x1 = center[0] - radius
        y1 = center[1] - radius
        x2 = center[0] + radius
        y2 = center[1] + radius

        return [x1, y1, x2, y2]

    def draw(self, x: int, y: int, cell_width: int, cell_height: int) -> None:
        pass


class CornerWall(Piece):
    def __init__(self, image_draw: ImageDraw, rotation_index: int, wall_width: int=5, **kwargs):
        super().__init__(image_draw, rotation_index, wall_width, **kwargs)

    def draw(self, x: int, y: int, cell_width: int, cell_height: int) -> None:
        if self.rot_ind == 3:
            W1 = self.get_left_wall(x, y, cell_width, cell_height)
            W2 = self.get_top_wall(x, y, cell_width, cell_height)

        elif self.rot_ind == 2:
            W1 = self.get_top_wall(x, y, cell_width, cell_height)
            W2 = self.get_right_wall(x, y, cell_width, cell_height)

        elif self.rot_ind == 1:
            W1 = self.get_right_wall(x, y, cell_width, cell_height)
            W2 = self.get_bottom_wall(x, y, cell_width, cell_height)

        else:
            W1 = self.get_bottom_wall(x, y, cell_width, cell_height)
            W2 = self.get_left_wall(x, y, cell_width, cell_height)

        self.img_draw.rectangle(W1, fill=self.wall_color)
        self.img_draw.rectangle(W2, fill=self.wall_color)


class SideWall(Piece):
    def __init__(self, image_draw: ImageDraw, rotation_index: int, wall_width: int=5, **kwargs):
        super().__init__(image_draw, rotation_index, wall_width, **kwargs)

    def draw(self, x: int, y: int, cell_width: int, cell_height: int) -> None:
        if self.rot_ind == 2:
            wall = self.get_top_wall(x, y, cell_width, cell_height)
        elif self.rot_ind == 1:
            wall = self.get_right_wall(x, y, cell_width, cell_height)
        elif self.rot_ind == 0:
            wall = self.get_bottom_wall(x, y, cell_width, cell_height)
        else:
            wall = self.get_left_wall(x, y, cell_width, cell_height)

        self.img_draw.rectangle(wall, fill=self.wall_color)


class GlowingSphere(Piece):
    def __init__(self, image_draw: ImageDraw, radius: int, color: str="red", **kwargs):
        super().__init__(image_draw, 0, 0, **kwargs)
        self.radius = radius
        self.color = color

    def draw(self, x: int, y: int, cell_width: int, cell_height: int) -> None:
        bounding_box = self.get_sphere(x, y, cell_width, cell_height, self.radius)
        self.img_draw.ellipse(bounding_box, fill=self.color)


class NoWalls(Piece):
    """ Needed due to standard instantiation model """
    def __init__(self, image_draw: ImageDraw, rotation_index: int, wall_width: int=5, **kwargs):
        pass

    def draw(self, x: int, y: int, cell_width: int, cell_height: int) -> None:
        return


class Grid:
    channel: str = "RGB"
    piece_dict: dict = {
        "no_walls": NoWalls,
        "corner_wall": CornerWall,
        "side_wall": SideWall,
    }

    def __init__(self, num_cells_row: int=10, num_cells_col: int=10, cell_width: int=10, cell_height: int=10,
                 background_color: str="white", wall_width: int=5, scale: int=1, padding: list=[0, 0, 0, 0],
                 draw_spheres: bool=True):
        self.num_cells_row = num_cells_row
        self.num_cells_col = num_cells_col
        self.org_cell_width = cell_width
        self.org_cell_height = cell_height
        self.cell_width = cell_width * scale
        self.cell_height = cell_height * scale
        self.wall_width = wall_width
        self.img_padding = [pad * scale for pad in padding]
        self.draw_spheres = draw_spheres

        self.grid = [[None for _ in range(num_cells_row)] for _ in range(num_cells_col)]
        self.ball_grid = [[None for _ in range(num_cells_row)] for _ in range(num_cells_col)]
        self.saved = False

        self.image = Image.new(self.channel,
                               (self.img_padding[0] + self.img_padding[2] + num_cells_row * self.cell_width,
                                self.img_padding[1] + self.img_padding[3] + num_cells_col * self.cell_height),
                               background_color)
        self.draw = ImageDraw.Draw(self.image)

    def set_piece_in_grid(self, piece_type: str, row: int, col: int, rotation_index: int):
        self.grid[row][col] = self.piece_dict[piece_type](self.draw, rotation_index, self.wall_width,
                                                          img_padding=self.img_padding)
        self.saved = False

    def add_colored_ball(self, color: str, row: int, col: int):
        self.ball_grid[row][col] = GlowingSphere(self.draw, int(self.cell_width // 2 * 0.35), color=color,
                                                 img_padding=self.img_padding)

    def draw_map(self):
        self.draw.rectangle([0, 0, self.cell_width * self.num_cells_row, self.cell_height * self.num_cells_col], fill="white")

        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] is None:
                    self.draw.rectangle([x * self.cell_width + self.img_padding[0], y * self.cell_height + self.img_padding[1], x * self.cell_width + self.cell_width + self.img_padding[0], y * self.cell_height + self.cell_height + self.img_padding[1]], fill="black")

                else: self.grid[y][x].draw(x, y, self.cell_width, self.cell_height)
                if self.ball_grid[y][x] is None or self.grid[y][x] is None or not self.draw_spheres: continue
                else: self.ball_grid[y][x].draw(x, y, self.cell_width, self.cell_height)

        self.saved = True

    def save(self, file_path: str=None, use_original_orientation=False):
        if not self.saved:
            self.draw_map()

        if not use_original_orientation:
            self.image = self.image.rotate(180)
            self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)

        if file_path is None:
            self.image.save(f"map_{self.num_cells_row}_{self.num_cells_col}_{uuid.uuid4()}.png")

        else:
            if "png" not in file_path:
                self.image.save(f"{file_path}.png")
            else:
                self.image.save(file_path)

        self.saved = True


class JsonGridLoader:
    name_to_module_index: dict = {
        0: "corner_wall",
        1: "no_walls",
        2: "side_wall",
    }
    detail_keys: list = ["offsets", "rowLength", "columnLength", "mapSeed"]

    def __init__(self, file_path: str="map_output.json", draw_spheres: bool=True):
        self.file_path = file_path
        self.draw_spheres = draw_spheres

    def json_to_image(self):
        all_map_info = load_json(self.file_path)
        grid = Grid(num_cells_row=all_map_info[self.detail_keys[1]], num_cells_col=all_map_info[self.detail_keys[2]],
                    scale=25, padding=[2, 2, 2, 2], draw_spheres=self.draw_spheres)
        all_cells = [item for key, item in all_map_info.items() if key not in self.detail_keys]
        for cell in all_cells:
            try:
                piece_type = self.name_to_module_index[cell["moduleIndex"]]
                row = cell["gridIndices"]["x"]
                col = cell["gridIndices"]["y"]
                grid.set_piece_in_grid(piece_type, row, col, cell["rotationIndex"])
            except KeyError:  # This should be a sphere
                grid.add_colored_ball(cell["color"].lower(), cell["gridIndices"]["x"], cell["gridIndices"]["y"])

        grid.save()


draw_spheres = sys.argv[1].lower() != "false"
j_loader = JsonGridLoader(draw_spheres=draw_spheres)
j_loader.json_to_image()

