import turtle as tt
import random
from abc import ABC, abstractmethod
from enum import Enum, auto


class Color:
    """
    Class containing constant colors or random generators for colors used in program.
    """
    cellar_background_color = (0xD3, 0xD3, 0xD3)
    white = (0xFF, 0xFF, 0xFF)
    black = (0, 0, 0)
    dark_gray = (0xA2, 0xA2, 0xA2)
    yellow = (0xFF, 0xE5, 0x7C)

    @staticmethod
    def random_color():
        """
        Picks random color from whole RGB palette.
        Return:
            tuple[int]: R, G and B chanel
        """

        return random.randint(0, 0xFF), random.randint(0, 0xFF), random.randint(0, 0xFF)

    @staticmethod
    def random_gray():
        """
        Picks randomly gray color with every chanel having the same value from <0xCC, 0xFF>
        Return:
            tuple[int]: R, G and B chanel
        """
        value = random.randint(0xCC, 0xFF)
        return value, value, value

    @staticmethod
    def random_beer_color():
        """
        Picks color for the beer's bottle.
        It returns in 50% slightly random variation of dark green,
        and in 50% slightly random variation of brown.
        Return:
            tuple[int]: R, G and B chanel
        """
        coin = random.randint(0, 1)
        if coin == 0:
            return random.randint(0, 0x10), random.randint(0x70, 0x90), random.randint(0, 0x10)
        return random.randint(0x49, 0x69), random.randint(0x2C, 0x4C), random.randint(0, 0x2F)


class GlobalSetup:
    """
    Class containing global constants.
    """

    # angles used to correctly position the turtle during drawing.
    up_angle = 0
    down_angle = 180
    left_angle = 90
    right_angle = 270
    window_shape = (1600, 900)  # (width, height)
    w, h = window_shape

    padding = {
        "left": int(.15 * w),
        "right": int(.15 * w),
        "top": int(.15 * h),
        "bottom": int(.15 * h)
    }

    rack_thickness = 5
    real_h = h - padding["top"] - padding["bottom"]
    real_w = w - padding["left"] - padding["right"]
    # values based on pure empirical experience gain during testing
    min_number_of_shelves = max(real_h//90, 3)
    max_number_of_shelves = max(real_h//40, 3)
    min_number_of_racks = max(real_w//250, 2)
    max_number_of_racks = max(real_w//100, 2)
    n_racks_threshold = (min_number_of_racks + max_number_of_racks)//2
    n_racks = random.randint(min_number_of_racks, max_number_of_racks)

    # if there are more than some racks (denoted as n_racks_threshold) racks, items on the shelves appears too small,
    # and i there are less than some racks, small items look great, so item's size
    # is picked conditionally.
    # values based on pure empirical experience gain during testing

    if n_racks < n_racks_threshold:
        max_item_width = .18
        min_item_width = .08
    else:
        max_item_width = .27
        min_item_width = .12

    def __init__(self):
        """
        Getting screen resolution.
        First method with PIL works only on Windows and MacOS. It wasn't tested, cause I work on Linux.
        Second method works on Linux only. It was tested and worked on my Fedora 31.
        Solutions are based on code from StackOverflow and blog.pythonlibrary.org with some modifications
        """
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            self.screen_width, self.screen_height = img.size
        except:
            try:
                import subprocess
                cmd = ['xrandr']
                cmd2 = ['grep', '*']
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                p2 = subprocess.Popen(cmd2, stdin=p.stdout, stdout=subprocess.PIPE)
                p.stdout.close()
                resolution_string, junk = p2.communicate()
                resolution = resolution_string.split()[0]
                width, height = str(resolution).split('x')
                self.screen_width = int(width[2:])
                self.screen_height = int(height[:-1])
            except:
                self.screen_height = None
                self.screen_width = None


class Coords:
    """
    Class managing coordinates and changing them from middle screen to left bottom corner
    Attributes:
        coords (tuple[int]): coordinates from left-bottom corner
        x (int): x coordinate
        y (int): y coordinate
    """

    def __init__(self, x, y):
        """
        Args:
            x (int): width, x
            y (int): height, y
        """

        self.coords = (x - GlobalSetup.window_shape[0] // 2, y - GlobalSetup.window_shape[1] // 2)
        self.x = self.coords[0]
        self.y = self.coords[1]

    def undo_shift(self):
        """
        In case of adding coordinates, double shift from the centered is created.
        This method deletes it.
        Should be used in every case of adding two Coords objects.
        """
        self.coords = (self.coords[0] + GlobalSetup.window_shape[0] // 2,
                       self.coords[1] + GlobalSetup.window_shape[1] // 2)
        self.x = self.coords[0]
        self.y = self.coords[1]
        return self

    def __add__(self, other):
        """
        Args:
            other (Coords): coordinate to add stored as Coords object.
        Return:
            Coords: Coords object after adding. Requires shifting before using!!
        """
        return Coords(self.x + other.x, self.y + other.y)

    def add_unbiased(self, other):
        """
        Args:
            other (tuple[int]): coordinate to add stored as tuple[int].
        Return:
            Coords: Coords object after adding. Requires shifting before using!!
        """
        return Coords(self.x + other[0], self.y + other[1])


class DrawingMethods:
    """
    Set of methods drawing different shapes.
    """
    @staticmethod
    def draw_rectangle(starting_coords: Coords, shape, bg_color, pen_color):
        """
        Args:
            starting_coords (tuple of int): coords of left-bottom coords
            shape (tuple of int): tuple of width and height (width, height)
            bg_color: background color
            pen_color: pen color

        Warning: this method is not changing the turtle's settings to original (angle, color etc.)
        Using method from this class after performing this operation is perfectly fine.
        Using other drawing methods may require additional setting the turtle at the beginning.
        """
        tt.up()
        tt.setpos(starting_coords.coords)
        tt.setheading(GlobalSetup.up_angle)
        tt.fillcolor(bg_color)
        tt.pencolor(pen_color)
        tt.begin_fill()
        tt.down()
        w, h = shape
        tt.forward(h)
        tt.right(90)
        tt.forward(w)
        tt.right(90)
        tt.forward(h)
        tt.setpos(starting_coords.coords)
        tt.end_fill()
        tt.update()

    @staticmethod
    def draw_triangle(starting_coords, length, bg_color, pen_color):
        """
        This method perform drawing the equilateral triangle staying at the ground.

        Args:
            starting_coords (tuple of int): coords of left-bottom coords
            length (int): length of one side.
            bg_color: background color
            pen_color: pen color

        Warning: this method is not changing the turtle's settings to original (angle, color etc.)
        Using method from this class after performing this operation is perfectly fine.
        Using other drawing methods may require additional setting the turtle at the beginning.
        """
        tt.up()
        tt.setpos(starting_coords.coords)
        tt.setheading(30)
        tt.fillcolor(bg_color)
        tt.pencolor(pen_color)
        tt.begin_fill()
        tt.down()
        tt.forward(length)
        tt.right(120)
        tt.forward(length)
        tt.right(120)
        tt.forward(length)
        tt.end_fill()
        tt.update()

    @staticmethod
    def draw_bottle(starting_coords, w, h, bg_color, pen_color):
        """
        This method is drawing the bottle shape.
        Args:
            starting_coords (tuple of int): coords of left-bottom coords
            w (int): width
            h (int): height
            bg_color: background color
            pen_color: pen color

        Warning: this method is not changing the turtle's settings to original (angle, color etc.)
        Using method from this class after performing this operation is perfectly fine.
        Using other drawing methods may require additional setting the turtle at the beginning.
        """
        tt.up()
        start_x, start_y = starting_coords.coords
        tt.setpos(starting_coords.coords)
        tt.setheading(GlobalSetup.up_angle)
        tt.fillcolor(bg_color)
        tt.pencolor(pen_color)
        tt.begin_fill()
        tt.down()
        tt.setpos(start_x, start_y + h//2)
        tt.setpos(start_x + w//3, start_y + h//2 + w//3)
        tt.setpos(start_x + w//3, start_y + 11 * h//12)
        tt.setpos(start_x + 2 * w//3, start_y + 11 * h//12)
        tt.setpos(start_x + 2 * w//3, start_y + h//2 + w//3)
        tt.setpos(start_x + w, start_y + h//2)
        tt.setpos(start_x + w, start_y)
        tt.setpos(starting_coords.coords)
        tt.end_fill()
        tt.update()


class Screen:
    """
    Describe basic image parameters.

    Attributes:
        pad (dict): Padding in pixels (keys: "left", "right", "top", "bottom")
        n_racks (int): Number of racks.
        racks (list of Rack objects): Racks on the picture.
        joint_rack_w (int): width of drawn image (joint width of all racks)
    """

    def __init__(self, pad=GlobalSetup.padding):
        """
        Args:
            pad (dict or None): List of padding values. If None,
                padding being 15% of w/h each side is created.
                Argument is optional (None by default).

        Raises:
            ValueError: width or height are bigger than screen resolution or less than 1.
            ValueError: padding values are to high and there is no space for racks
            TypeError: width or height are not integers
        """

        gs = GlobalSetup()
        w, h = GlobalSetup.window_shape
        if not isinstance(h, int) or not isinstance(w, int):
            raise TypeError("Width and height must be integers.")

        if gs.screen_width is not None and gs.screen_height is not None:
            if h > gs.screen_height or w > gs.screen_width:
                raise ValueError("Window resolution cannot be bigger than screen resolution")

        self.height = h
        self.width = w
        self.n_racks = GlobalSetup.n_racks

        if pad is None:     # creating default padding from 15% of w/h each side
            self.pad = {
                "left": int(.15 * w),
                "right": int(.15 * w),
                "top": int(.15 * h),
                "bottom": int(.15 * h)
            }
        else:
            self.pad = pad

        self.joint_rack_w = w - self.pad["left"] - self.pad["right"]     # width of whole block of racks
        rack_w = self.joint_rack_w // self.n_racks                            # width of one rack
        self.rack_h = h - self.pad["top"] - self.pad["bottom"]           # height of one rack
        if rack_w < 1 or self.rack_h < 1:
            raise ValueError("Paddings are too big.")

        # generating racks
        self.racks = []
        coords = [self.pad["left"], self.pad["bottom"]]
        for _ in range(self.n_racks):
            self.racks.append(Rack(w=rack_w, h=self.rack_h, coords=coords))
            coords = (coords[0] + rack_w, coords[1])

    def setup(self):
        """
        Basic initial setting
        """
        tt.setup(self.width, self.height)
        tt.title("Dreamy cellar during pandemic")
        # tt.tracer(0, 0)
        tt.mode("logo")
        tt.colormode(255)
        tt.speed(10)

    def draw(self):
        """
        Draw background and all racks on the screen.
        """
        tt.hideturtle()  # For some reason hideturtle() doesn't work when placed in setup method, but works here.
        DrawingMethods.draw_rectangle(Coords(self.pad["left"], self.pad["bottom"]),
                                      shape=(self.joint_rack_w, self.rack_h),
                                      bg_color=Color.cellar_background_color,
                                      pen_color=Color.cellar_background_color)

        for rack in self.racks:
            rack.draw()
        tt.update()


class Rack:
    """
    Describes a rack.

    Attributes:
        width (int): width of rack in pixels
        height (int): height of rack in pixels
        n_shelves (int): number of shelfs
        lb_coords (list of ints): coordinates of the left-bottom corner
        shelves (list of Shelf): list of shelves
        color (tuple of int): color in RGB
    """
    def __init__(self, w, h, coords):
        """
        Args:
            w (int): width in pixels
            h (int): height in pixels
            coords (tuple of int): coordinates of the left-bottom corner
        """

        self.width = w
        self.height = h
        self.lb_coords = coords
        self.n_shelves = random.randint(GlobalSetup.min_number_of_shelves, GlobalSetup.max_number_of_shelves)
        self.color = Color.random_color()

        # Generating shelves
        self.shelves = []
        shelf_w = self.width - 2 * GlobalSetup.rack_thickness
        shelf_h = self.height//self.n_shelves
        s_coords = [self.lb_coords[0] + GlobalSetup.rack_thickness,
                    self.lb_coords[1] + shelf_h // 2 - GlobalSetup.rack_thickness // 2]
        if self.n_shelves > 1:
            for _ in range(self.n_shelves - 1):
                self.shelves.append(Shelf(shelf_w, shelf_h, s_coords, self.color))
                s_coords = (s_coords[0], s_coords[1] + shelf_h)
        self.shelves.append(Shelf(shelf_w, shelf_h // 2, s_coords, self.color))

    def draw_rack_alone(self):
        """
        Method drawing the rack.
        This is divided into separate method due to drawing it twice (more on it in draw method)
        """
        DrawingMethods.draw_rectangle(Coords(*self.lb_coords),
                                      shape=(GlobalSetup.rack_thickness, self.height),
                                      bg_color=self.color,
                                      pen_color=self.color)
        DrawingMethods.draw_rectangle(
                                Coords(self.lb_coords[0] + self.width - GlobalSetup.rack_thickness, self.lb_coords[1]),
                                shape=(GlobalSetup.rack_thickness, self.height),
                                bg_color=self.color,
                                pen_color=self.color)

    def draw(self):
        """
        Draw the rack and all its components
        """

        self.draw_rack_alone()
        for shelf in self.shelves:
            shelf.draw()

        # This repetition prevent sum issues with item's border overlapping rack.
        # This solution isn't efficient, cause rack can be drawn just after shelves,
        # however it just look fancier during drawing with rack goes first.
        self.draw_rack_alone()


class Shelf:
    """
    Attributes:
        width (int): width
        height (int): possible height of all objects on shelf (not the thickness!)
        lb_coords (tuple[int]): left-bottom corner coordinates
        items (list[Item]): list of items on the shelf
        color (list[int]): color
    """

    def __init__(self, w, h, coords, color):
        """
        Args:
            w (int): width in pixels
            h (int): height in pixels
            coords (tuple[int]): left-bottom corner coordinates
            color (tuple[int]): color
        """

        self.width = w
        self.height = h
        self.lb_coords = coords
        self.color = color
        end_item_coords = []
        self.divide(end_item_coords)
        item_widths = (c[1] - c[0] for c in end_item_coords)
        self.items = []

        # Quite primitive method of randomly choosing the item. To be changed.
        item_lb_coords = (self.lb_coords[0], self.lb_coords[1] + GlobalSetup.rack_thickness)
        choice_dict = {
            ItemType.JAR: Jar,
            ItemType.JAR2: Jar,
            ItemType.SALT: Salt,
            ItemType.BEER: Beer,
            ItemType.BEER2: Beer
        }
        for length in item_widths:
            random_item_type = random.choice(list(ItemType))
            self.items.append(choice_dict[random_item_type](Coords(*item_lb_coords),
                                   int(length * self.width),
                                   self.height - GlobalSetup.rack_thickness))
            item_lb_coords = (item_lb_coords[0] + length * self.width, item_lb_coords[1])

    @staticmethod
    def divide(store, begin=0., end=1.):
        """
        This method randomly divides the unit section into parts, such that every part
        belongs to the range <GlobalSetup.min_item_width, GlobalSetup.max_item_width>.

        The algorithm recursively divides the section if the length if bigger than maximal.

        Assumptions: The max value must be at least 2 times higher than the min value.

        Warning: This algorithm isn't uniformly random. Not every state of divisions is equally probable.
        Also not every state is even possible. But in this case I think it works perfectly fine.

        Args:
            store (list): list to store tuples of begin and end of the section.
            begin (float): coordinate of the beginning of the section
            end (float): coordinate of the ending of the section
        """
        if end - begin > GlobalSetup.max_item_width:
            div_point = random.uniform(begin + GlobalSetup.min_item_width, end - GlobalSetup.min_item_width)
            Shelf.divide(store, begin, div_point)
            Shelf.divide(store, div_point, end)
        else:
            store.append((begin, end))

    def draw(self):
        """
        Draw shelf with all its items.
        """

        DrawingMethods.draw_rectangle(
            Coords(*self.lb_coords),
            shape=(self.width, GlobalSetup.rack_thickness),
            bg_color=self.color,
            pen_color=self.color)

        for item in self.items:
            item.draw()


class ItemType(Enum):
    """
    Enum of item types. For primitive randomising some of them are doubled.
    """
    JAR = auto()
    JAR2 = auto()
    SALT = auto()
    BEER = auto()
    BEER2 = auto()


class AbstractItem(ABC):
    """
    Item lying on the shelf.
    Attributes:
        lb_coords (Coords): left-bottom corner coordinates
        w (int): width
        h (int): height
        color (tuple[int]): item's color
    """

    def __init__(self, lb_coords, w, h):
        """
        Generates color randomly with algorithm specified in GlobalSetup

        Args:
            lb_coords (Coords): left-bottom corner coordinates
            w (int): maximal width
            h (int): maximal height

        """
        self.lb_coords = lb_coords
        self.w = w
        self.h = h
        self.color = Color.random_color()

    @abstractmethod
    def draw(self):
        """
        Every item have different drawing sequence, so this method must be implemented in child classes.
        """
        pass


class Jar(AbstractItem):
    """
    Jar item (default item from the exercise)
    """

    def __init__(self, lb_coords, w, h):
        super().__init__(lb_coords, w, h)
        self.h = random.randint(self.h//2, self.h)

    def draw(self):

        # jar
        DrawingMethods.draw_rectangle(self.lb_coords, (self.w, int(self.h * 6/7)), Color.white, Color.black)

        # lid
        DrawingMethods.draw_rectangle(self.lb_coords.add_unbiased((self.w // 10, 6 * self.h // 7)).undo_shift(),
                                      (4 * self.w // 5, max(3, self.h // 7)),
                                      Color.dark_gray, Color.dark_gray)

        # content
        DrawingMethods.draw_rectangle(self.lb_coords, (self.w, 54 * self.h // 70), self.color, Color.black)

        # label
        DrawingMethods.draw_rectangle(self.lb_coords.add_unbiased((self.w // 4, 3 * self.h // 14)).undo_shift(),
                                      (self.w // 2, 3 * self.h // 7),
                                      Color.yellow, Color.black)


class Salt(AbstractItem):
    """
    Salt class.
    """

    def __init__(self, lb_coords, w, h):
        super().__init__(lb_coords, w, h)
        self.color = Color.random_gray()
        if 3**(1/2) * self.w//2 > self.h:
            new_w = self.h//(3**(1/2)/2)
            delta_x = (self.w - new_w)//2
            self.lb_coords = self.lb_coords.add_unbiased((delta_x, 0)).undo_shift()
            self.w = new_w

    def draw(self):
        DrawingMethods.draw_triangle(self.lb_coords, self.w, self.color, Color.black)


class Beer(AbstractItem):
    def __init__(self, lb_coords, w, h):
        super().__init__(lb_coords, w, h)
        self.beer_color = Color.random_beer_color()
        self.label_color = Color.random_color()
        self.cap_color = Color.random_color()
        if self.h > 2 * self.w:
            self.h = random.randint(2 * self.w, self.h)
        else:
            new_w = self.h//2
            self.lb_coords = self.lb_coords.add_unbiased((((self.w-new_w)//2), 0)).undo_shift()
            self.w = new_w

    def draw(self):
        # bottle
        DrawingMethods.draw_bottle(self.lb_coords, self.w, self.h, self.beer_color, Color.black)

        # label
        DrawingMethods.draw_rectangle(self.lb_coords.add_unbiased((0, self.h//6)).undo_shift(),
                                      (self.w, self.h//4), self.label_color, Color.black)

        # Cap. In 10% cases the cap color will be different than label color. When all the time the color is different,
        # image is becoming a mess, so i have changed that.
        ran = random.randint(0, 10)
        if ran == 0:
            DrawingMethods.draw_rectangle(self.lb_coords.add_unbiased((self.w//3, 11 * self.h//12)).undo_shift(),
                                      (self.w//3, self.h//12), self.cap_color, self.cap_color)
        else:
            DrawingMethods.draw_rectangle(self.lb_coords.add_unbiased((self.w // 3, 11 * self.h // 12)).undo_shift(),
                                          (self.w // 3, self.h // 12), self.label_color, self.label_color)


def main():
    """
    Main function, calling all necessary methods to draw the image
    """
    random.seed(677)
    window = Screen()
    window.setup()
    window.draw()


def test():
    """
    Function created only for testing reasons. Can be completely ignored.
    """
    # w_shape = GlobalSetup.window_shape
    screen = Screen()
    screen.setup()
    # tt.setup(640, 480, 1, 1)
    # tt.title("Zapasy")
    # tt.hideturtle()
    # tt.tracer(0, 0)
    # tt.mode("logo")
    tt.colormode(255)
    DrawingMethods.draw_rectangle(Coords(0, 0), (100, 100), GlobalSetup.background_color)
    tt.exitonclick()


if __name__ == "__main__":
    main()




