from __future__ import annotations
import pygame
from dataclasses import dataclass, field
from collections.abc import Callable, Sequence, Iterable, MutableSequence, Mapping, MutableMapping, Hashable
from typing import ClassVar, Protocol, runtime_checkable

pygame.font.init()

type T_COLOR = tuple[int, int, int] | tuple[int, int, int, int]
"""type: Type definition of colors allowing 3 rgb channels and an optional 4th alpha channel."""


@runtime_checkable
class DisplayObject(Protocol):
    """Protocol to identify objects based on a 'render' function."""
    def render(self, display) -> None: ...


class Placement:
    """Predefined placements for easy positioning of objects.

    Attributes:
        CENTER (ClassVar[int]): Constant set to 0.
        LEFT (ClassVar[int]): Constant set to 1.
        RIGHT (ClassVar[int]): Constant set to 2.
        TOP (ClassVar[int]): Constant set to 3.
        BOTTOM (ClassVar[int]): Constant set to 4.
        LEFT_OUT (ClassVar[int]): Constant set to 5.
        RIGHT_OUT (ClassVar[int]): Constant set to 6.
        TOP_OUT (ClassVar[int]): Constant set to 7.
        BOTTOM_OUT (ClassVar[int]): Constant set to 8.
        TOP_LEFT (ClassVar[int]): Constant set to 9.
        TOP_RIGHT (ClassVar[int]): Constant set to 10.
        BOTTOM_LEFT (ClassVar[int]): Constant set to 11.
        BOTTOM_RIGHT (ClassVar[int]): Constant set to 12.
    """
    CENTER: ClassVar[int] = 0
    LEFT: ClassVar[int] = 1
    RIGHT: ClassVar[int] = 2
    TOP: ClassVar[int] = 3
    BOTTOM: ClassVar[int] = 4
    LEFT_OUT: ClassVar[int] = 5
    RIGHT_OUT: ClassVar[int] = 6
    TOP_OUT: ClassVar[int] = 7
    BOTTOM_OUT: ClassVar[int] = 8
    TOP_LEFT: ClassVar[int] = 9
    TOP_RIGHT: ClassVar[int] = 10
    BOTTOM_LEFT: ClassVar[int] = 11
    BOTTOM_RIGHT: ClassVar[int] = 12

    _INDICES = list(range(13))

    @classmethod
    def real_placement(cls, placement: int) -> bool:
        """
        Checks if a given Placement is predefined.

        Args:
            placement (int): Placement to check.

        Returns:
            bool: True if the given Placement is predefined, False otherwise.
        """
        return placement in cls._INDICES

    @classmethod
    def double_placement(cls, placement: int) -> bool:
        """
        Checks if a given Placement defines positioning on 2 axes.

        Args:
            placement (int): Placement to check.

        Returns:
            bool: True if placement defines 2 axes, False otherwise.
        """
        if not cls.real_placement(placement):
            raise ValueError('Not a valid Placement')

        return placement in (cls.TOP_LEFT, cls.TOP_RIGHT, cls.BOTTOM_LEFT, cls.BOTTOM_RIGHT, cls.CENTER)

    @classmethod
    def split(cls, placement: int) -> tuple[int, int]:
        """
        Splits a Placement that defines positioning on 2 axes to their single axis Placements.

        Args:
            placement (int): Placement that defines positioning on 2 axes.

        Returns:
            tuple[int, int]: Separate Placements for the horizontal and vertical axis.
        """
        if not cls.real_placement(placement):
            raise ValueError('Not a valid Placement')

        if not cls.double_placement(placement):
            if placement in (cls.TOP, cls.BOTTOM, cls.TOP_OUT, cls.BOTTOM_OUT):
                return cls.CENTER, placement
            else:
                return placement, cls.CENTER
        else:
            if placement == cls.CENTER:
                return cls.CENTER, cls.CENTER

            if placement in (cls.TOP_LEFT, cls.TOP_RIGHT):
                vert_direction = cls.TOP
            else:
                vert_direction = cls.BOTTOM

            if placement in (cls.TOP_LEFT, cls.BOTTOM_LEFT):
                hor_direction = cls.LEFT
            else:
                hor_direction = cls.RIGHT

            return hor_direction, vert_direction


class Frame:
    """Frame counter."""
    _frame: int = 0

    @classmethod
    def increase(cls, amount: int = 1) -> int:
        """
        Increases the frame by the given amount.

        Args:
            amount (int): Amount to increase the frame counter by.

        Returns:
            int: The new current frame number.
        """
        if isinstance(amount, int):
            cls._frame += amount
            return cls._frame
        else:
            return NotImplemented("Frame can only increase using intergers")

    @classmethod
    def set(cls, amount: int = 0) -> int:
        """
        Sets the frame to the given amount.

        Returns:
            int: The new current frame number.
        """
        if isinstance(amount, int):
            cls._frame = amount
            return cls._frame
        else:
            return NotImplemented("Frame can only be set to an integer")

    @classmethod
    def get(cls) -> int:
        """
        Gets the current frame.

        Returns:
            int: Current frame.
        """
        return cls._frame

    @classmethod
    def get_delta(cls, value: int) -> int:
        """
        Gets the delta between current frame and given value.

        Args:
            value (int): The value to get the delta for.

        Returns:
            int: The delta between the current frame and the given value.
        """
        if not isinstance(value, int):
            return NotImplemented
        return cls.get() - value

    def __repr__(self) -> str:
        """
        Represents the current frame as a string.

        Returns:
            str: The current frame as a string.
        """
        return f'Frame: {Frame.get()}'


class Display:
    """
    Access to display functions and reduces display parsing necessity for all DisplayObjects.

    Attributes:
        fps (ClassVar[int]): Frames per Second of the display.
        size (tuple): Size of the display.
        title (str): Title of the display.
        flags (tuple): Additional arguments for display configuration.
        display (pygame.Surface): Display surface.
    """
    _CLOCK: ClassVar[pygame.time.Clock] = pygame.time.Clock()
    fps: ClassVar[int] = 60
    _win: pygame.Surface | None = None

    @classmethod
    def window(cls) -> pygame.Surface | None:
        """
        Return the display surface.

        Returns:
            pygamme.Surface | None: Display surface.
        """
        return cls._win

    def __init__(self, size: tuple[int, int], title: str | None = None, *args) -> None:
        self.size = size
        self.title = title
        self.flags = args

        self.display = pygame.display.set_mode(self.size, *self.flags)
        pygame.display.set_caption(self.title)

        Display._win = self.display

    @property
    def width(self) -> int:
        """
        Width of the display.

        Returns:
            int: Width of the display.
        """
        return self.display.get_width()

    @property
    def height(self) -> int:
        """
        Height of the display.

        Returns:
             int: Height of the display.
        """
        return self.display.get_height()

    def fill(self, color: T_COLOR) -> None:
        """
        Fills the display.

        Args:
            color (T_COLOR): Color used to fill the display.
        """
        self.display.fill(color)

    @staticmethod
    def update() -> None:
        """
        Updates the display.
        """
        pygame.display.update()

    @classmethod
    def tick_frame(cls, increase_frame: int = 1) -> None:
        """
        Ticks the frame counter.

        Args:
            increase_frame (int): Amount to increase the frame counter by.
        """
        cls._CLOCK.tick(cls.fps)
        Frame.increase(increase_frame)


class Group:
    """
    Groups DisplayObjects together to be manipulated simulatiously.

    Attributes:
        objects (Iterable[DisplayObjects]): List of DisplayObjects to be added to the group.
    """

    def __init__(self, group_objects: Iterable[DisplayObject]) -> None:
        self.objects = group_objects

    def render(self, display: pygame.Surface | None = None) -> None:
        """
        Renders all DisplayObjects in the Group.

        Args:
            display (pygame.Surface | None): Display surface, automatically uses the Display object if one is defined.
        """
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        if isinstance(self.objects, Iterable):
            for obj in self.objects:
                if isinstance(obj, DisplayObject):
                    obj.render(display)

        else:
            raise TypeError('Objects should be an Iterable containing DispayObjects')

    def __setattr__(self, key, value) -> None:
        """
        Sets an attribute for all objects within the group when all of them have the attribute.

        Args:
             key (str): Attribute name.
             value (Any): Attribute value.
        """
        if key == 'objects':
            super().__setattr__(key, value)
        else:
            if all(hasattr(obj, key) for obj in self.objects):
                for obj in self.objects:
                    obj.key = value


@dataclass(kw_only=True)
class Shape:
    """
    Parent class for shapes.

    Attributes:
        color (T_COLOR): Color used to draw the shape.
        border (int): Border width of the shape.
    """
    color: T_COLOR = (0, 0, 0)
    border: int = 0


@dataclass
class Rect(Shape):
    """
    Rectangle shape.

    Attributes:
        x (int): X coordinate of the rectangle top-left corner.
        y (int): Y coordinate of the rectangle top-left corner.
        width (int): Width of the rectangle.
        height (int): Height of the rectangle.
        corner_radius_all (int): Radius of all rectangle corners.
        corner_radius_specific (dict[int, int]): Radius of specific Rectangle corners.
    """
    _CORNER_PLACEMENT_NAMES: ClassVar[dict[int, str]] = {
        Placement.TOP_LEFT: 'border_top_left_radius',
        Placement.TOP_RIGHT: 'border_top_right_radius',
        Placement.BOTTOM_LEFT: 'border_bottom_left_radius',
        Placement.BOTTOM_RIGHT: 'border_bottom_right_radius'
    }
    _rect: pygame.Rect = field(default=None, kw_only=True)
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    corner_radius_all: int = 0
    corner_radius_specific: dict[int, int] | None = None

    def __post_init__(self) -> None:
        self._rect = pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def rect(self) -> pygame.Rect:
        """
        Returns the rectangle.

        Returns:
             pygaem.Rect: The rectangle.
        """
        return self._rect

    def __setattr__(self, key, value) -> None:
        """
        Set an attribute of the rectangle and redefine the rectangle when position or size is changed.

        Args:
            key (str): Attribute name.
            value (Any): Attribute value.
        """
        super().__setattr__(key, value)
        if key in ['x', 'y', 'width', 'height'] and self._rect is not None:
            self._rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def render(self, display: pygame.Surface | None = None) -> None:
        """
        Renders the Rectangle.

        Args:
            display (pygame.Surface | None): Display surface, automatically uses the Display object if one is defined.
        """
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        if self.corner_radius_specific is None:
            pygame.draw.rect(display, self.color, self.rect, self.border, self.corner_radius_all)
        else:
            corner_radius = {Rect._CORNER_PLACEMENT_NAMES[key]: value for key, value in
                             self.corner_radius_specific.items()}
            pygame.draw.rect(display, self.color, self.rect, self.border, self.corner_radius_all,
                             **corner_radius)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Rectangle.

        Returns:
            str: The string representation of the Rectangle.
        """
        return f'Rect: ({self.x}, {self.y}) - ({self.width}, {self.height})'


@dataclass
class Circle(Shape):
    """
    Circle shape.

    Attributes:
        x (int): X coordinate of the Circle center.
        y (int): Y coordinate of the Circle center.
        radius (int): Radius of the Circle.
        enabled_corners (dict[int, bool] | None): Enabled corners of the Circle, if None the complete Circle is drawn.
    """
    _CORNER_PLACEMENT_NAMES: ClassVar[dict[int, str]] = {
        Placement.TOP_LEFT: 'draw_top_left',
        Placement.TOP_RIGHT: 'draw_top_right',
        Placement.BOTTOM_LEFT: 'draw_bottom_left',
        Placement.BOTTOM_RIGHT: 'draw_bottom_right'
    }
    _circle: tuple[int, int, int] = field(default=None, kw_only=True)
    x: int = 0
    y: int = 0
    _radius: int = 0
    enabled_corners: dict[int, bool] | None = None

    def __post_init__(self):
        self._circle = (self.x, self.y, self._radius)

    @property
    def circle(self) -> tuple[int, int, int]:
        """
        Returns the circle.

        Returns:
            tuple[int, int, int]: The Circle.
        """
        return self._circle

    @property
    def center(self) -> tuple[int, int]:
        """
        Returns the center of the Circle.

        Returns:
            tuple[int, int]: The center of the Circle.
        """
        return self.circle[0], self.circle[1]

    @property
    def radius(self) -> int:
        """
        Returns the radius of the Circle.

        Returns:
            int: The radius of the Circle.
        """
        return self.circle[2]

    @radius.setter
    def radius(self, value: object) -> None:
        if isinstance(value, int | float):
            self._radius = value
        else:
            raise NotImplemented

    @property
    def diameter(self) -> int:
        """
        Returns the diameter of the Circle.

        Returns:
            int: The diameter of the Circle.
        """
        return self.radius * 2

    @diameter.setter
    def diameter(self, value: object) -> None:
        if isinstance(value, int | float):
            self.radius = 0.5 * value

    @property
    def width(self) -> int:
        """
        Returns the width of the Circle.

        Returns:
            int: The width of the Circle.
        """
        return self.diameter

    @width.setter
    def width(self, value: object) -> None:
        self.diameter = value

    @property
    def height(self) -> int:
        """
        Returns the height of the Circle.

        Returns:
            int: The height of the Circle.
        """
        return self.diameter

    @height.setter
    def height(self, value: object) -> None:
        self.diameter = value

    def __setattr__(self, key, value) -> None:
        """
        Sets an attribute of the circle and redefine the Circle when position or radius is changed.

        Args:
             key (str): Attribute name.
             value (Any): Attribute value.
        """
        super().__setattr__(key, value)
        if key in ['x', 'y', '_radius'] and self._circle is not None:
            self._circle = (self.x, self.y, self._radius)

    def render(self, display: pygame.Surface | None = None) -> None:
        """
        Renders the Circle.

        Args:
            display (pygame.Surface | None): Display surface, automatically uses the Display object if one is defined.
        """
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        if self.enabled_corners is None:
            pygame.draw.circle(display, self.color, self.center, self.radius, self.border)
        else:
            draw_corner_strings = {value: self.enabled_corners[key] if key in self.enabled_corners.keys() else False for
                                   key, value in Circle._CORNER_PLACEMENT_NAMES.items()}
            pygame.draw.circle(display, self.color, self.center, self.radius, self.border, **draw_corner_strings)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Circle.

        Returns:
            str: The string representation of the Circle.
        """
        return f'Circle: ({self.center}) - ({self.radius})'


@dataclass
class Polygon(Shape):
    """
    Polygon shape.

    Attributes:
        polygon_points (MutableSequence[tuple[int, int]]): The points of the Polygon in clockwise order.
    """
    polygon_points: MutableSequence[tuple[int, int]] | None = None

    def __post_init__(self) -> None:
        self.polygon_points = self.polygon_points if self.polygon_points is not None else [(0, 0), (0, 0), (0, 0)]

    def insert_point(self, coordinate: tuple[int, int], point_index: int = -1) -> None:
        """
        Insert a point in the Polygon.

        Args:
            coordinate (tuple[int, int]): The coordinate of the inserted point.
            point_index (int): the index of the place where to insert into the point order.
        """
        if not isinstance(self.polygon_points, MutableSequence):
            raise TypeError('Polygon point insertion only possible on MutableSequence')
        elif not isinstance(coordinate, Sequence):
            raise TypeError('Polygon points must be Sequence[int, int] type')

        if coordinate not in self.polygon_points:
            self.polygon_points.insert(point_index, coordinate)

    def remove_point(self, coordinate: tuple[int, int] = (0, 0)) -> int | None:
        """
        Removes a point in the Polygon.

        Args:
            coordinate (tuple[int, int]): The coordinate of the point to remove.
        """
        if not isinstance(self.polygon_points, MutableSequence):
            raise TypeError('Polygon point removal only possible on MutableSequence')
        if not isinstance(coordinate, Sequence):
            raise TypeError('Polygon points must be Sequence[int, int] type')

        if coordinate in self.polygon_points:
            point_index = self.polygon_points.index(coordinate)
            self.polygon_points.remove(coordinate)
            return point_index
        else:
            return None

    def render(self, display: pygame.Surface | None = None) -> None:
        """
        Renders the Polygon.

        Args:
            display (pygame.Surface | None): Display surface, automatically uses the Display object if one is defined.
        """
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        pygame.draw.polygon(display, self.color, self.polygon_points, self.border)

    def __repr__(self) -> str:
        return f'Polygon: ({len(self.polygon_points)} - {self.polygon_points})'


@dataclass
class Ellipse(Shape):
    """
    Ellipse shape.

    Attributes:
        x (int): X coordinate of the ellipse's bounding box.
        y (int): Y coordinate of the ellipse's bounding box.
        width (int): Width of the ellipse's bounding box.
        height (int): Height of the ellipse's bounding box.
    """
    _ellipse: pygame.Rect = field(default=None, kw_only=True)
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    def __post_init__(self) -> None:
        self._ellipse: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def ellipse(self) -> pygame.Rect:
        """
        Returns the Ellipse bounding box.

        Returns:
            pygame.Rect: The Ellipse bounding box.
        """
        return self._ellipse

    def __setattr__(self, key, value) -> None:
        """
        Set an attribute of the Ellipse and redefine the bounding box when position or size is changed.

        Args:
            key (str): Attribute name.
            value (Any): Attribute value.
        """
        super().__setattr__(key, value)
        if key in ['x', 'y', 'width', 'height'] and self._ellipse is not None:
            self._ellipse = pygame.Rect(self.x, self.y, self.width, self.height)

    def render(self, display: pygame.Surface | None = None) -> None:
        """
        Renders the Ellipse.

        Args:
            display (pygame.Surface | None): Display surface, automatically uses the Display object if one is defined.
        """
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        pygame.draw.ellipse(display, self.color, self.ellipse, self.border)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Ellipse.

        Returns:
            str: The string representation of the Ellipse.
        """
        return f'Ellipse: ({self.x}, {self.y}) - ({self.width}, {self.height})'


@dataclass
class Text:
    """
    Text displays and base for objects with access to text functionality.

    Attributes:
        x (int): X coordinate of the text.
        y (int): Y coordinate of the text.
        color (T_COLOR): Text color.
        font (str): Text font name.
        font_size (int | None): Text font size, use None for auto-sizing text.
        bold (bool): Bold text.
        italic (bool): Italic text.
        alignment (int): Text alignment compared to given x/y coordinate.
        resize_max_width (int | None): Bounding box width for automatic resizing texts and multiline.
        resize_max_height (int | None): Bounding box height for automatic resizing texts and multiline.
        margin (int): Margins inside the bounding box.
        dynamic_multi_line (bool): Display multiline text with autoscaling.
        multi_line_height_factor (float): Multiline font letter height factor.
        multi_line_spacing_factor (float): Multiline line spacing.
    """
    text: str = ''
    x: int = 0
    y: int = 0
    color: T_COLOR = (0, 0, 0)
    font: str = 'helvetica'
    font_size: int | None = None
    bold: bool = False
    italic: bool = False
    alignment: int = Placement.CENTER
    _text_font_processed: pygame.font.Font | None = None
    resize_max_width: int | None = None
    resize_max_height: int | None = None
    margin: int = 20

    dynamic_multi_line: bool = False
    _multi_line_splitted: MutableSequence[Text] | None = None
    multi_line_height_factor: float = 0.75
    multi_line_spacing_factor: float = 1.4

    def __post_init__(self) -> None:
        if self.dynamic_multi_line:
            if None in [self.resize_max_width, self.resize_max_height]:
                raise ValueError('Provide resize_max_width and resize_max_height arguments to use dynamic multilines')

            self._multi_line_splitted = []
            lines = self.text.splitlines(False)

            longest_line = max(lines, key=lambda text: len(text))
            test_for_resize = Text(longest_line, font=self.font, bold=self.bold, italic=self.italic,
                                   resize_max_width=self.resize_max_width, resize_max_height=self.resize_max_height,
                                   margin=self.margin)
            max_font_size = min(test_for_resize.font_size,
                                int(self.resize_max_height / len(lines) * Text.multi_line_height_factor))
            line_size = int(max_font_size * Text.multi_line_spacing_factor)

            for n_line, line in enumerate(lines):
                line_text_obj = Text(line, self.x, self.y + n_line * line_size, self.color, self.font, bold=self.bold,
                                     italic=self.italic, alignment=self.alignment, font_size=max_font_size,
                                     margin=self.margin)
                self._multi_line_splitted.append(line_text_obj)

        else:
            if self.font_size is None:
                self.font_size = 300
                self.update_font()
                self.auto_size_font()
            self.update_font()

    def auto_size_font(self, resize: bool = True) -> int:
        """
        Calculates maximum font size within boundries.

        Args:
            resize (bool): Apply calculated font size.

        Returns:
            int: Maximum font size within boundries.
        """
        temp_text = self._text_font_processed.render(self.text, True, self.color)

        size_factor_w = size_factor_h = 1
        if self.resize_max_width is not None and temp_text.get_width() != 0:
            size_factor_w = (self.resize_max_width - self.margin) / temp_text.get_width()
        if self.resize_max_height is not None and temp_text.get_height() != 0:
            size_factor_h = (self.resize_max_height - self.margin) / temp_text.get_height()

        font_size = int(self.font_size * min(size_factor_w, size_factor_h))
        if resize:
            self.font_size = font_size
            self.update_font()
        return font_size

    def update_font(self) -> None:
        """
        Updates font setup.
        """
        self._text_font_processed = pygame.font.SysFont(self.font, self.font_size, self.bold, self.italic)

    def __setattr__(self, key, value) -> None:
        """
        Set an attribute of the Text object and resizes when the text is changed.

        Args:
            key (str): Attribute name.
            value (Any): Attribute value.
        """
        super().__setattr__(key, value)
        if key == 'text' and self.text is not None:
            if self.resize_max_width is not None or self.resize_max_height is not None:
                self.auto_size_font()

    @property
    def text_size_rect(self) -> Rect:
        """
        Returns text bounding box.

        Returns:
            Rect: Text bounding box.
        """
        return Rect(self.x, self.y, self.resize_max_width, self.resize_max_height)

    def render(self, display: pygame.Surface | None = None) -> None:
        """
        Renders the Text.

        Args:
            display (pygame.Surface | None): Display surface, automatically uses the Display object if one is defined.
        """
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        if self.dynamic_multi_line:
            for text_obj in self._multi_line_splitted:
                text_obj.render(display)

        else:
            text_render = self._text_font_processed.render(self.text, True, self.color)
            x_align, y_align = Placement.split(self.alignment)

            if y_align not in (Placement.TOP, Placement.TOP_OUT) and self.resize_max_height is None:
                y_align = Placement.TOP

            # noinspection PyUnreachableCode
            match y_align:
                case Placement.CENTER:
                    text_y = self.y + (self.resize_max_height - text_render.get_height()) // 2
                case Placement.TOP:
                    text_y = self.y + self.margin // 2
                case Placement.BOTTOM:
                    text_y = self.y + self.resize_max_height - text_render.get_height() - self.margin // 2
                case Placement.TOP_OUT:
                    text_y = self.y - text_render.get_height() - self.margin // 2
                case Placement.BOTTOM_OUT:
                    text_y = self.y + self.resize_max_height + text_render.get_height() + self.margin // 2
                case _:
                    raise NotImplementedError("Unusable text alignment")

            if x_align not in (Placement.LEFT, Placement.LEFT_OUT) and self.resize_max_width is None:
                x_align = Placement.LEFT

            # noinspection PyUnreachableCode
            match x_align:
                case Placement.CENTER:
                    text_x = self.x + (self.resize_max_width - text_render.get_width()) // 2
                case Placement.LEFT:
                    text_x = self.x + self.margin // 2
                case Placement.RIGHT:
                    text_x = self.x + self.resize_max_width - text_render.get_width() - self.margin // 2
                case Placement.LEFT_OUT:
                    text_x = self.x - text_render.get_width() - self.margin // 2
                case Placement.RIGHT_OUT:
                    text_x = self.x + self.resize_max_width + text_render.get_width() + self.margin // 2
                case _:
                    raise NotImplementedError("Unusable text alignment")

            display.blit(text_render, (text_x, text_y))

    def __repr__(self) -> str:
        """
        Returns string representation of the Text object.

        Returns:
             str: String representation of the Text object.
        """
        return f'"{self.text}", ({self.x}, {self.y}), {self.color}, size={self.font_size}'


@dataclass
class InputField:
    """
    Text input fields.

    Attributes:
        active_input_fields (ClassVar[list[InputField]]): List of active InputFields.
        active_input (ClassVar[InputField]): Active InputField where typing and returning are possible.
        input_rect (tuple[int, int, int, int, T_COLOR] | Rect): InputField box.
        rect_active_color (T_COLOR): InputField color when inputField is selected.
        rect_not_active_color (T_COLOR): InputField color when inputField is not selected.
        text (Text | str): Text object inside the InputField
        empty_text (Text | str): Text object inside the InputField to show when the InputField is empty.
        replace_text_char (str | None): If value is not None, replace all characters with value.
        character_max (int | None): Used to set a maximum number of characters within the InputField.
        restricted_characters (str): characters within this string are not ignored when entered into the InputField.
        allow_letters (bool): Used to restrict all alphabetical characters at once.
        allow_numbers (bool): Used to restrict all numeric characters at once.
        allow_spaces (bool): Used to restrict spaces.
        allow_special (str): Used to allow special characters into the InputField.
        exit_esc (bool): Deselect InputField when 'escape' is pressed.
        submit_return (bool): Returns text content upon pressing 'return'.
        clear_on_submit (bool): Clears the InputField upon pressing 'return'.
        can_del (bool): Allow deletion of characters upon pressing 'backspace'.
        select_on_init (bool): immediately select the InputField upon creation.
    """
    active_input_fields: ClassVar[list[InputField]] = []
    active_input: ClassVar[InputField | None] = None

    input_rect: tuple[int, int, int, int, T_COLOR] | Rect = (0, 0, 0, 0, (0, 0, 0))
    rect_active_color: T_COLOR | None = None
    rect_not_active_color: T_COLOR = field(default=None, kw_only=True)

    text: Text | str = ''
    empty_text: Text | str = ''
    replace_text_char: str | None = None
    _hidden_text: str = ''

    character_max: int | None = None
    restricted_characters: str = ''
    allow_letters: bool = True
    allow_numbers: bool = True
    allow_spaces: bool = True
    allow_special: str = ''

    exit_esc: bool = True
    submit_return: bool = True
    clear_on_submit: bool = True
    can_del: bool = True
    select_on_init: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.input_rect, Sequence):
            self.input_rect = Rect(*self.input_rect[:4], color=self.input_rect[4])

        self.rect_not_active_color = self.input_rect.color
        if self.select_on_init and self.rect_active_color is not None:
            self.input_rect.color = self.rect_active_color

        if self.select_on_init:
            InputField.active_input = self

        if isinstance(self.text, str):
            self.text = Text(text=self.text, x=self.input_rect.x, y=self.input_rect.y,
                             resize_max_width=self.input_rect.width, resize_max_height=self.input_rect.height,
                             font='monospace')
        if isinstance(self.text, str):
            self.empty_text = Text(text=self.empty_text, x=self.input_rect.x, y=self.input_rect.y,
                                   resize_max_width=self.input_rect.width, resize_max_height=self.input_rect.height,
                                   font='monospace')

        if self.empty_text.resize_max_width is None:
            self.empty_text.resize_max_width = self.input_rect.width
        if self.empty_text.resize_max_height is None:
            self.empty_text.resize_max_height = self.input_rect.height

        self.text.auto_size_font()
        self.empty_text.auto_size_font()

        InputField.active_input_fields.append(self)

    @property
    def text_str(self) -> str:
        """
        Returns the content inside the InputField.

        Replaces all characters when the text should be hidden

        Returns:
            str: Content inside the InputField.
        """
        return self.text.text

    @text_str.setter
    def text_str(self, value) -> None:
        if isinstance(value, str):
            if self.replace_text_char is not None:
                self.text.text = len(value) * self.replace_text_char
                self._hidden_text = value
            else:
                self.text.text = value
        else:
            raise NotImplemented

    @property
    def text_hidden(self) -> str:
        """
        Returns the text contents, even if the text is hidden.
        """
        if self.replace_text_char is not None:
            return self._hidden_text
        else:
            return self.text_str

    @property
    def empty_text_str(self) -> str:
        """
        Returns the text string of the empty_field Text object.

        Returns:
            str: Text string of the empty_field Text object.
        """
        return self.empty_text.text

    @empty_text_str.setter
    def empty_text_str(self, value) -> None:
        if isinstance(value, str):
            self.empty_text.text = value
        else:
            raise NotImplemented

    @property
    def rect_color(self) -> T_COLOR:
        """
        Returns the InputField color.

        Returns:
            T_COLOR: InputField color.
        """
        return self.input_rect.color

    def is_allowed(self, char: str) -> bool:
        """
        Used to check if a character is allowed in the InputField.

        Args:
            char (str): Character to check.

        Returns:
            bool: True if the character is allowed in the InputField, else False.
        """
        if char in self.restricted_characters:
            return False
        if not self.allow_numbers and not self.allow_letters and self.allow_special == '':
            return True

        if self.allow_numbers and char.isnumeric():
            return True
        if self.allow_letters and char.isalpha():
            return True
        if self.allow_spaces and char.isspace():
            return True
        if char in self.allow_special:
            return True
        return False

    def render(self, display: pygame.Surface | None = None) -> None:
        """
        Renders the InputField.

        Args:
            display (pygame.Surface | None): Display surface, automatically uses the Display object if one is defined.
        """
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        self.input_rect.render(display)

        text_x, text_y = self.input_rect.x, self.input_rect.y
        if self.text_str == '' and not self == InputField.active_input:
            self.empty_text.x, self.empty_text.y = text_x, text_y
            self.empty_text.render(display)
        else:
            self.text.x, self.text.y = text_x, text_y
            self.text.render(display)

    @classmethod
    def activate(cls, input_field: InputField) -> None:
        """
        Activates a given InputField and switches its color when a 'rect_active_color' is provided.

        Args:
            input_field (InputField): InputField object to activate.
        """
        if cls.active_input is not None:
            cls.active_input.input_rect.color = input_field.rect_not_active_color

        cls.active_input = input_field
        if input_field is not None and input_field.rect_active_color is not None:
            input_field.input_rect.color = input_field.rect_active_color

    @classmethod
    def deactivate(cls) -> None:
        """
        Deactivates the current active InputField.
        """
        if cls.active_input is not None:
            cls.active_input.input_rect.color = cls.active_input.rect_not_active_color
            cls.active_input = None

    @classmethod
    def process_input(cls, event: pygame.event.Event) -> str | None:
        """
        Processes the given event.

        Args:
            event (pygame.event.Event): Event to process.

        Returns:
            str | None: Return text if 'return' is pressed and 'submit_return' is set to True.
        """
        if cls.active_input is None:
            return None
        active_field = cls.active_input

        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_BACKSPACE):
            if event.key == pygame.K_ESCAPE and active_field.exit_esc:
                cls.deactivate()
                return None

            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return_text = None

                if active_field.submit_return:
                    return_text = active_field.text_hidden

                if active_field.clear_on_submit:
                    active_field.text_str = ''

                return return_text

            elif event.key == pygame.K_BACKSPACE and active_field.can_del:
                if len(active_field.text_str) >= 1:
                    active_field.text_str = active_field.text_str[:-1]
                return None

        elif active_field.is_allowed(event.unicode):
            if active_field.character_max is not None and len(active_field.text_str) < active_field.character_max:
                active_field.text_str += event.unicode
            elif active_field.character_max is None:
                active_field.text_str += event.unicode
            return None

        print(f'Input processing is not implemented for {event.unicode}')
        return None

    def check_collision(self, event_pos: tuple[int, int] | None = None) -> bool:
        """
        Checks for an event position on top of the InputField to select that field.

        Args:
            event_pos (tuple[int, int] | None): Event position or position of the mouse if None.

        Returns:
            bool: True if the mouse position collides with the InputField, else False.
        """
        event_pos = pygame.mouse.get_pos() if event_pos is None else event_pos

        if self.input_rect.rect.collidepoint(event_pos):
            InputField.activate(self)
            return True
        else:
            if InputField.active_input == self:
                InputField.deactivate()
        return False

    @classmethod
    def check_all_collisions(cls):
        """
        Checks for a mouse position on top of an InputField to select that field.
        """
        mouse_position = pygame.mouse.get_pos()

        for input_field in cls.active_input_fields:
            input_field.check_collision(mouse_position)

    def __repr__(self) -> str:
        """
        Returns a string representation of the InputField.

        Returns:
            str: String representation of the InputField.
        """
        return f'pos: ({self.input_rect.x}, {self.input_rect.y}) - text: {self.text_str}'


@dataclass
class Image:
    """
    Sprite displays and base for objects with access to image functionality.

    Attributes:
        assets_folder_path (ClassVar[str | None]): Path to the assets' folder.
        image (pygame.Surface): Image surface.
        border_rect (pygame.Rect): Rectangle that acts as a border around the sprite.
        path (str): Path to the sprite.
        x (int): X position of the sprite top-left corner.
        y (int): Y position of the sprite top-left corner.
        resize_to (Sequence[int | None, int | None]): If any or both values are given, the sprite is resized to the
            specified size. If only one of the values is given, the other is scaled to preserve the aspect ratio.
        direct_path (bool): Ignore assets_folder_path and use the given path without changes.
        border (int): Border size around the spirte.
        border_color (T_COLOR): Border color.
    """
    assets_folder_path: ClassVar[str | None] = None
    image: pygame.Surface = field(default=None, kw_only=True)
    border_rect: Rect = field(default=None, kw_only=True)

    path: str = ''
    x: int = 0
    y: int = 0
    resize_to: tuple[int | None, int | None] = (None, None)

    direct_path: bool = False

    border: int = 0
    border_color: T_COLOR = (0, 0, 0)

    def __post_init__(self) -> None:
        if Image.assets_folder_path is not None and not self.direct_path:
            if Image.assets_folder_path[-1] != '\\':
                self.path = Image.assets_folder_path + '\\' + self.path
            else:
                self.path = Image.assets_folder_path + self.path

        self.image = pygame.image.load(self.path)

        if self.resize_to is not (None, None):
            self.resize(self.resize_to)

        self.set_border()

    @property
    def width(self) -> int:
        """
        Returns the width of the sprite.

        Returns:
            int: Width of the sprite.
        """
        if self.image is not None:
            return self.image.get_width()
        return 0

    @width.setter
    def width(self, value: object) -> None:
        if isinstance(value, int) and self.image is not None:
            self.image.width = value

    @property
    def height(self) -> int:
        """
        Returns the height of the sprite.

        Returns:
            int: Height of the sprite.
        """
        if self.image is not None:
            return self.image.get_height()
        return 0

    @height.setter
    def height(self, value: object) -> None:
        if isinstance(value, int) and self.image is not None:
            self.image.height = value

    def set_border(self, border_size: int = None, border_color: T_COLOR = None) -> None:
        """
        Sets the border of the sprite.
        """
        if border_size is not None:
            self.border = border_size
        if border_color is not None:
            self.border_color = border_color

        if self.border > 0:
            self.border_rect = Rect(self.x - self.border, self.y - self.border, self.width + 2 * self.border,
                                    self.height + 2 * self.border, color=self.border_color, border=self.border)

    def resize(self, size: tuple[int | None, int | None] = None) -> None:
        """
        Resizes the sprite to the given size. If only one size is given, it scales to keep the aspect ratio the same.

        Args:
            size (Sequence[int | None, int | None]): New size of the sprite.
        """
        size = size if size is not None else self.resize

        if None not in size:
            size = (max(0, size[0]), max(0, size[1]))
            self.image = pygame.transform.scale(self.image, size)
        elif size[1] is None:
            factor = size[0] / self.width
            self.image = pygame.transform.scale_by(self.image, factor)
        elif size[0] is None:
            factor = size[1] / self.height
            self.image = pygame.transform.scale_by(self.image, factor)

        self.set_border()

    def render(self, display: pygame.Surface | None = None) -> None:
        """
        Renders the Image.

        Args:
            display (pygame.Surface | None): Display surface, automatically uses the Display object if one is defined.
        """
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        display.blit(self.image, (self.x, self.y))
        if self.border > 0:
            self.border_rect.render(display)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Image.

        Returns:
            str: String representation of the Image.
        """
        return f'pos: ({self.x}, {self.y}) - src: {self.path}'


class ObjectAnimation:
    """
    Saves animations and links them to Objects to be used later.

    Attributes:
        running_animations (ClassVar[MutableSequence['ObjectAnimation' | None]]): List of running animations.
        action_sequence (MutableSequence[Sequence[int, dict[str, int]]]): A sequence of Actions.
        animation_objects (Sequence[DisplayObject]): A sequence of DisplayObjects to perform the actions on.
        started_move (bool): Indicates if animation is active.
        action_index (int): Index of the Action to perform.
        object_index (int): Index of the object to perform the Action on.
        start_action_frame (int): Frame number on which the Action started.
        next_frame (int): Frame number on which the Action should move to the next animation step.
        stop_reset (bool): Used to indicate if the ObjectAnimation should reset to the starting position after being
            done.
    """
    @dataclass
    class Action:
        """
        Saves actions to perform during an animation.

        Attributes:
            SCALE (ClassVar[int]): Constant set to 0.
            SCALE_TO (ClassVar[int]): Constant set to 1.
            MOVE (ClassVar[int]): Constant set to 2.
            MOVE_TO (ClassVar[int]): Constant set to 3.
            CHANGE_CORNER_RADIUS (ClassVar[int]): Constant set to 4.
            CHANGE_CORNER_RADIUS_TO (ClassVar[int]): Constant set to 5.
            SET_COLOR_TO (ClassVar[int]): Constant set to 6.
            CHANGE_BORDER_WIDTH_TO (ClassVar[int]): Constant set to 7.
        """
        _display_fps: ClassVar[int] = Display.fps if Display.fps is not None else 60

        SCALE: ClassVar[int] = 0
        SCALE_TO: ClassVar[int] = 1
        MOVE: ClassVar[int] = 2
        MOVE_TO: ClassVar[int] = 3
        CHANGE_CORNER_RADIUS: ClassVar[int] = 4
        CHANGE_CORNER_RADIUS_TO: ClassVar[int] = 5
        SET_COLOR_TO: ClassVar[int] = 6
        CHANGE_BORDER_WIDTH_TO: ClassVar[int] = 7

        def __init__(self, indicator: int, changes: dict[str, int | T_COLOR]):
            self.indicator = indicator
            self.changes = changes

        @classmethod
        def execute(cls, objects: Sequence, cur_object_index: int, start_action_time: int,
                    action: ObjectAnimation.Action) -> tuple[int, int | None]:
            """
            Executes an Action.

            Args:
                objects (Sequence): The objects to perform the Action on.
                cur_object_index (int): Index of the current object to perform the Action on.
                start_action_time (int): Frame at which the Action started.
                action (ObjectAnimation.Action): Action to perform.
            """
            wait_time = 0
            object_index = None
            cur_object = objects[cur_object_index]

            if action.indicator is None:
                return wait_time, object_index

            if 'time' in action.changes.keys():
                if action.indicator in (cls.SCALE_TO, cls.MOVE_TO, cls.CHANGE_CORNER_RADIUS_TO,
                                        cls.CHANGE_BORDER_WIDTH_TO):
                    wait_time = start_action_time - Frame.get() + action.changes['time']
                else:
                    wait_time = action.changes['time']
                transform_factor = 1 / max(wait_time, 1)
            else:
                transform_factor = 1

            try:
                # noinspection PyUnreachableCode
                match action.indicator:
                    case cls.SCALE:
                        if 'width' in action.changes.keys():
                            step_size = int(action.changes['width'] * transform_factor)
                            cur_object.width += step_size
                        if 'height' in action.changes.keys():
                            step_size = int(action.changes['height'] * transform_factor)
                            cur_object.height += step_size

                        if 'width' not in action.changes.keys() and 'height' not in action.changes.keys():
                            raise KeyError('width and/or height key should be given to use SCALE action')

                    case cls.SCALE_TO:
                        if 'width' in action.changes.keys():
                            delta_w = action.changes['width'] - cur_object.width
                            step_size = int(delta_w * transform_factor)
                            cur_object.width += step_size
                        if 'height' in action.changes.keys():
                            delta_h = action.changes['height'] - cur_object.height
                            step_size = int(delta_h * transform_factor)
                            cur_object.height += step_size

                        if 'width' not in action.changes.keys() and 'height' not in action.changes.keys():
                            raise KeyError('width and/or height key should be given to use SCALE_TO action')

                    case cls.MOVE:
                        if 'x' in action.changes.keys():
                            step_size = int(action.changes['x'] * transform_factor)
                            cur_object.x += step_size
                        if 'y' in action.changes.keys():
                            step_size = int(action.changes['y'] * transform_factor)
                            cur_object.y += step_size

                        if 'x' not in action.changes.keys() and 'y' not in action.changes.keys():
                            raise KeyError('x and/or y key should be given to use MOVE action')

                    case cls.MOVE_TO:
                        if 'x' in action.changes.keys():
                            delta_x = action.changes['x'] - cur_object.x
                            step_size = int(delta_x * transform_factor)
                            cur_object.x += step_size
                        if 'y' in action.changes.keys():
                            delta_y = action.changes['y'] - cur_object.y
                            step_size = int(delta_y * transform_factor)
                            cur_object.y += step_size

                        if 'x' not in action.changes.keys() and 'y' not in action.changes.keys():
                            raise KeyError('x and/or y key should be given to use MOVE_TO action')

                    case cls.CHANGE_CORNER_RADIUS:
                        if 'radius' in action.changes.keys():
                            step_size = int(action.changes['radius'] * transform_factor)
                            cur_object.corner_radius_all += step_size
                        else:
                            raise KeyError('radius key should be given to use CHANGE_CORNER_RADIUS action')

                    case cls.CHANGE_CORNER_RADIUS_TO:
                        if 'radius' in action.changes.keys():
                            delta_r = action.changes['radius'] - cur_object.corner_radius_all
                            step_size = int(delta_r * transform_factor)
                            cur_object.corner_radius_all += step_size
                        else:
                            raise KeyError('radius key should be given to use CHANGE_CORNER_RADIUS_TO action')

                    case cls.SET_COLOR_TO:
                        if 'color' in action.changes.keys():
                            cur_object.color = action.changes['color']
                        else:
                            raise KeyError('color key should be given to use SET_COLOR_TO action')

                    case cls.CHANGE_BORDER_WIDTH_TO:
                        if 'border' in action.changes.keys():
                            delta_b = action.changes['border'] - cur_object.border
                            step_size = int(delta_b * transform_factor)
                            cur_object.border += step_size
                        else:
                            raise KeyError('border key should be given to use CHANGE_BORDER_WIDTH_TO action')

                    case _:
                        raise ValueError('Invalid Action value')

            except AttributeError:
                raise AttributeError('The animation object misses attributes to be compatible with this Action')

            return wait_time, object_index

    running_animations: ClassVar[MutableSequence[ObjectAnimation | None]] = []

    def __init__(self, action_sequence: MutableSequence[Action],
                 animation_objects: tuple[DisplayObject, ...], stop_reset: bool = True):
        self.action_sequence = action_sequence
        self.animation_objects = animation_objects
        self._start_object_setting = animation_objects[:]
        self.started_move = False
        self.action_index = 0
        self.object_index = 0
        self.start_action_frame = 0
        self.next_frame = 0
        self.stop_reset = stop_reset

    def start(self):
        """
        Start the ObjectAnimation.
        """
        if self not in ObjectAnimation.running_animations:
            self.start_action_frame = Frame.get()
            ObjectAnimation.running_animations.append(self)
        else:
            print('Animation already running')

    def stop(self):
        """
        Stop the ObjectAnimation and reset the ObjectAnimation if 'stop_reset' is True.
        """
        if self in ObjectAnimation.running_animations:
            ObjectAnimation.running_animations[ObjectAnimation.running_animations.index(self)] = None

        if self.stop_reset:
            self.reset()

    def reset(self):
        """
        Reset the ObjectAnimation to the starting position.
        """
        if not self.stop_reset:
            self.stop()
        else:
            if self in ObjectAnimation.running_animations:
                ObjectAnimation.running_animations.remove(self)
        self.action_index = 0
        self.object_index = 0
        self.start_action_frame = 0
        self.next_frame = 0
        self.started_move = False
        self.animation_objects = self._start_object_setting

    def render(self, display: pygame.Surface | None = None) -> None:
        """
        Renders the ObjectsAnimation.

        Args:
            display (pygame.Surface | None): Display surface, automatically uses the Display object if one is defined.
        """
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        self.animation_objects[self.object_index].render()

    def process_animation(self):
        """
        Processes the Animation object and performs Actions.
        """
        current_action = self.action_sequence[self.action_index]

        wait_time, object_index = ObjectAnimation.Action.execute(self.animation_objects, self.object_index,
                                                                 self.start_action_frame, current_action)

        if object_index is not None:
            self.object_index = object_index

        if Frame.get() >= self.next_frame:
            self.start_action_frame = Frame.get()
            self.next_frame = self.start_action_frame + wait_time - 1
            if self.started_move or wait_time <= 0:
                self.action_index += 1
                self.started_move = False
            else:
                self.started_move = True

            if self.action_index >= len(self.action_sequence):
                self.stop()
                return

            if wait_time <= 0:
                self.process_animation()

    @classmethod
    def update_animations(cls):
        """
        Processes all the active ObjectAnimations.
        """
        for animation in cls.running_animations:
            if animation is not None:
                animation.process_animation()

        cls.running_animations = [a for a in cls.running_animations if a is not None]


@dataclass
class Button:
    """
    Creates buttons to detect and save onclick behavior.

    Attributes:
        active_buttons (ClassVar[list[Button]]): List of active Buttons.
        rect (tuple[int, int, int, int, T_COLOR] | Rect): Button shape and hitbox.
        pressed_color (T_COLOR | None): Color of the Button when pressed, if None there is no color change.
        unpressed_color (T_COLOR): Color of the Button when unpressed.
        text (Text | None): Button text.
        fit_text (bool): Used to overwrite automatic text fit to the Button size.
        img (Image | None): Image to display within the Button.
        img_margin (int): Margin between the Image and Button edges.
        img_fill_button (bool): Determines if the Image should resize to fill the entire Button shape.
        img_alignment (int): Use Placement to align the image within the Button.
        pressed (bool): Boolean to set the pressed state on initialization.
        button_type (str): Classifies the Button as a 'switch' or 'push' button. Switch buttons switch state when
            pressed, push buttons are unpressed automatically directly after being pressed.
        target_scene_on_press (str | None): Switch to a given Scene when the Button is pressed.
        call_on_press (Callable | list[Callable]): Call all the given Callables upon the Button being pressed.
        call_on_press_kwargs (dict | list[dict]): Save Callable kwargs for the call_on_press Callables. These are
            automatically used when executing the call_on_press Callables.
    """
    _BUTTON_TYPES: ClassVar[tuple[str, ...]] = ('switch', 'push')

    active_buttons: ClassVar[list[Button]] = []

    rect: tuple[int, int, int, int, T_COLOR] | Rect = (0, 0, 0, 0, (0, 0, 0))
    pressed_color: T_COLOR | None = None

    text: Text | None = None
    fit_text: bool = True

    img: Image | None = None
    img_margin: int = 0
    img_fill_button: bool = True
    img_alignment: int = Placement.CENTER

    pressed: bool = False
    button_type: str = 'switch'
    target_scene_on_press: str | None = None
    call_on_press: Callable | list[Callable] | None = None
    call_on_press_kwargs: dict | list[dict] | None = None

    def __post_init__(self) -> None:
        if isinstance(self.rect, Sequence):
            self.rect = Rect(*self.rect[:4], color=self.rect[4])

        self.unpressed_color = self.rect.color
        if self.pressed_color is not None and self.pressed:
            self.rect.color = self.pressed_color

        if self.fit_text and self.text is not None:
            self.text.x = self.rect.x
            self.text.y = self.rect.y
            self.text.resize_max_width = self.rect.width
            self.text.resize_max_height = self.rect.height
            self.text.auto_size_font()

        if self.img is not None:
            if self.img_fill_button:
                self.img.x, self.img.y = self.rect.x + self.img_margin, self.rect.y + self.img_margin
                self.img.resize((self.rect.width - 2 * self.img_margin, self.rect.height - 2 * self.img_margin))

            else:
                if self.img_alignment in (Placement.LEFT, Placement.TOP_LEFT, Placement.BOTTOM_LEFT):
                    self.img.x = self.rect.x + self.img_margin
                elif self.img_alignment in (Placement.RIGHT, Placement.TOP_RIGHT, Placement.BOTTOM_RIGHT):
                    self.img.x = self.rect.x + self.rect.width - self.img.width - self.img_margin
                else:
                    self.img.x = self.rect.x + (self.rect.width - self.img.width) // 2

                if self.img_alignment in (Placement.TOP, Placement.TOP_LEFT, Placement.TOP_RIGHT):
                    self.img.y = self.rect.y + self.img_margin
                elif self.img_alignment in (Placement.BOTTOM, Placement.BOTTOM_LEFT, Placement.BOTTOM_RIGHT):
                    self.img.y = self.rect.y + self.rect.height - self.img.height - self.img_margin
                else:
                    self.img.y = self.rect.y + (self.rect.height - self.img.height) // 2

        Button.active_buttons.append(self)

    @property
    def text_str(self) -> str:
        """
        Returns the text of the Button.

        Returns:
            str: The text of the Button.
        """
        return self.text.text

    @text_str.setter
    def text_str(self, value) -> None:
        if isinstance(value, str):
            self.text.text = value
        else:
            raise NotImplemented

    def call_func(self, kwargs_list: list[dict] = None, **kwargs) -> None:
        """
        Call all associated functions upon the Button being pressed.

        Args:
            kwargs_list (list[dict] | None): List of keyword arguments to overwrite the defaulted keyword arguments
                within 'call_on_press_kwargs', used when keywords need to be overwritten and multiple 'call_on_press'
                Callables are saved.
            **kwargs (dict): Additional keyword arguments to overwrite the defaulted keyword arguments, used when only
                one 'call_on_press' Callable is saved.
        """
        if self.call_on_press is not None:
            if isinstance(self.call_on_press, Callable):
                call_kwargs = {} if self.call_on_press_kwargs is None else self.call_on_press_kwargs
                call_kwargs.update(**kwargs)
                self.call_on_press(**call_kwargs)
            elif isinstance(self.call_on_press, list):
                for index, func in enumerate(self.call_on_press):
                    if isinstance(func, Callable):
                        if isinstance(self.call_on_press_kwargs, list) and len(self.call_on_press_kwargs) > index:
                            callable_kwargs = self.call_on_press_kwargs[index]
                        else:
                            callable_kwargs = {}

                        if kwargs_list is not None and len(kwargs_list) > index:
                            callable_kwargs.update(**kwargs_list[index])

                        func(**callable_kwargs)

    def render(self, display: pygame.Surface | None = None) -> None:
        """
        Renders the Button.

        Args:
            display (pygame.Surface | None): Display surface, automatically uses the Display object if one is defined.
        """
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        self.rect.render(display)
        if self.img is not None:
            self.img.render(display)
        if self.text is not None:
            self.text.render(display)

    def check_collision(self, event_pos: tuple[int, int] | None = None, kwargs_list: list[dict] = None,
                        **func_kwargs) -> bool:
        """
        Checks collision for a position and executes all actions when pressed.

        Args:
            event_pos (tuple[int, int] | None): Position to check for collision, if None the position of the mouse is
                used.
            kwargs_list (list[dict] | None): List of keyword arguments to overwrite the defaulted keyword arguments
                within 'call_on_press_kwargs', used when keywords need to be overwritten and multiple 'call_on_press'
                Callables are saved.
            **func_kwargs (dict): Additional keyword arguments to overwrite the defaulted keyword arguments, used when
                only one 'call_on_press' Callable is saved.

        Returns:
            bool: True if collision was found, False otherwise.
        """
        event_pos = pygame.mouse.get_pos() if event_pos is None else event_pos

        if self.rect.rect.collidepoint(event_pos):
            if self.pressed:
                self.pressed = False
                return False
            self.pressed = not self.pressed
            if kwargs_list is None:
                self.call_func(**func_kwargs)
            else:
                self.call_func(kwargs_list=kwargs_list)

            return True

        return False

    @classmethod
    def check_all_collisions(cls) -> None:
        """
        Checks collisions for all active buttons using the mouse position.
        """
        mouse_position = pygame.mouse.get_pos()

        for button in cls.active_buttons:
            button.check_collision(mouse_position)

    @classmethod
    def release_push_buttons(cls) -> None:
        """
        Function used to unpress all Buttons classified as a 'push' Button.
        """
        for button in cls.active_buttons:
            if button.button_type == 'push' and button.pressed is True:
                button.pressed = False

    def __repr__(self) -> str:
        """
        Returns a string representation of the Button.

        Returns:
            str: String representation of the Button.
        """
        return f'Button: ({self.rect.x}, {self.rect.y}) - target: {self.target_scene_on_press}'


@dataclass
class Bar:
    """
    Creates a bar that can display a value compared to a maximum.

    Attributes:
        active_bars (ClassVar[list[Bar]]): List of active bars.
        rect (tuple[int, int, int, int, T_COLOR] | Rect): Containment rectangle for the bounds of the Bar.
        max_value_range (list[float]): List containing the minimum and maximum values of the Bar.
        bar_border_width (int): Border around the Bar rect.
        bar_color (T_COLOR): Color of the Bar.
        text (Text): Text object for information about the Bar.
        fit_text (bool): Used to overwrite automatic text fit to the Bar size.
        bar_bg_img (Image): Image used for the Bar background.
        bar_closed (bool): Close of bar inside using a line with the same width as the 'bar_border_width'.
        allow_inverse (bool): Allows the bottom value to rise above the upper value and the other way around.
        bar_inverse_color (T_COLOR): Color of the Bar when the bottom value is above the upper value.
        start_fill_side (int): Sets the side of the bar which is considered the bottom.
        bar_speed (float): Speed with which the Bar moves to its target values.
    """
    _display_fps: ClassVar[int] = Display.fps if Display.fps is not None else 60
    _moving_bars: ClassVar[list[Bar]] = []
    active_bars: ClassVar[list[Bar]] = []

    rect: tuple[int, int, int, int, T_COLOR] | Rect = (0, 0, 0, 0, (0, 0, 0))
    max_value_range: list[float] | None = None
    _goal_value_range: list[float] | None = field(default=None, kw_only=True)
    _display_range: list[float] | None = field(default=None, kw_only=True)

    bar_border_width: int = 2

    bar_color: T_COLOR = None
    text: Text | None = None
    fit_text: bool = True
    bar_bg_img: Image | None = None

    bar_closed: bool = False

    allow_inverse: bool = True
    bar_inverse_color: T_COLOR = None

    start_fill_side: int = Placement.LEFT
    bar_speed: float = 3.0
    _starting_frame: int = Frame.get()

    def __post_init__(self) -> None:
        Bar.active_bars.append(self)

        if isinstance(self.rect, Sequence):
            self.rect = Rect(*self.rect[:4], color=self.rect[4], border=self.bar_border_width)
        elif isinstance(self.rect, Rect):
            if self.rect.border == 0:
                self.rect.border = self.bar_border_width
            else:
                self.bar_border_width = self.rect.border

        if self.bar_color is None:
            # noinspection PyTypeChecker
            self.bar_color = tuple(255 - self.rect.color[c] for c in self.rect.color)

        self.max_value_range = [0.0, 100.0] if self.max_value_range is None else self.max_value_range
        self._goal_value_range = self.max_value_range[:]
        self._display_range = self.max_value_range[:]

        if self.start_fill_side not in (Placement.LEFT, Placement.BOTTOM):
            self.start_fill_side = Placement.LEFT

        if self.text is not None:
            self.text.x = self.rect.x
            self.text.y = self.rect.y
            self.text.resize_max_width = self.rect.width
            self.text.resize_max_height = self.rect.height
            if self.fit_text:
                self.text.auto_size_font()

        if self.bar_bg_img is not None:
            self.bar_bg_img.x, self.bar_bg_img.y = self.rect.x + self.rect.border, self.rect.y + self.rect.border
            self.bar_bg_img.resize((self.rect.width - 2 * self.bar_border_width,
                                    self.rect.height - 2 * self.bar_border_width))

    @property
    def text_str(self) -> str:
        """
        Returns the text of the Button.

        Returns:
            str: The text of the Button.
        """
        return self.text.text

    @text_str.setter
    def text_str(self, value: object) -> None:
        if isinstance(value, str):
            self.text.text = value
        else:
            raise NotImplemented

    @property
    def percentage(self) -> tuple[float, ...]:
        """
        Returns the percentages of the Bar's current value for the upper and lower values.
        """
        return tuple(round(self._goal_value_range[i] / self.max_value_range[1] * 100, 1) for i in range(2))

    def set_value(self, value: float, set_bottom: bool = False) -> None:
        """
        Sets the Bar to a new value.

        Args:
            value (float): New value for the Bar.
            set_bottom (bool): Set the new value to the bottom of the Bar instead of the top.
        """
        if self.allow_inverse:
            set_value = min(max(value, self.max_value_range[0]), self.max_value_range[1])
        else:
            if not set_bottom:
                set_value = min(max(value, self._goal_value_range[0]), self.max_value_range[1])
            else:
                set_value = min(max(value, self.max_value_range[0]), self._goal_value_range[1])

        target_index = 1 if not set_bottom else 0

        self._goal_value_range[target_index] = set_value

        if self not in Bar._moving_bars:
            Bar._moving_bars.append(self)

    def modify_value(self, value: float, set_bottom: bool = False) -> None:
        """
        Increase the Bar's current value by the given value.

        Args:
            value (float): Value that should be added to the current value of the Bar.
            set_bottom (bool): Set the new value to the bottom of the Bar instead of the top.
        """
        target_index = 1 if not set_bottom else 0
        self.set_value(self._goal_value_range[target_index] + value, set_bottom)

    def set_percentage(self, percentage: float, set_bottom: bool = False) -> None:
        """
        Sets the Bar to a new percentage value.

        Args:
            percentage (float): New percentage value for the Bar.
            set_bottom (bool): Set the new value to the bottom of the Bar instead of the top.
        """
        value_for_percent = percentage / 100 * self.max_value_range[1]
        self.set_value(value_for_percent, set_bottom)

    def modify_percentage(self, percentage: float, set_bottom: bool = False) -> None:
        """
        Increase the Bar's current value by the given percantage value.

        Args:
            percentage (float): Percentage value that should be added to the current value of the Bar.
            set_bottom (bool): Set the new value to the bottom of the Bar instead of the top.
        """
        value_for_percent = percentage / 100 * self.max_value_range[1]
        self.modify_value(value_for_percent, set_bottom)

    def _get_bar_width(self, value: float) -> int:
        bg_width = self.rect.width - 2 * self.bar_border_width
        ratio_filled = value / self.max_value_range[1]
        return round(bg_width * ratio_filled)

    def _get_bar_height(self, value: float) -> int:
        bg_height = self.rect.height - 2 * self.bar_border_width
        ratio_filled = value / self.max_value_range[1]
        return round(bg_height * ratio_filled)

    def get_bar_size(self) -> tuple[int, int]:
        """
        Returns the size of the Bar rect.

        Returns:
            tuple[int, int]: The size of the Bar rect.
        """
        bar_min = min(self._display_range)
        bar_max = max(self._display_range)

        if self.start_fill_side == Placement.LEFT:
            return (self._get_bar_width(bar_max) - self._get_bar_width(bar_min),
                    self.rect.height - 2 * self.bar_border_width)
        else:
            return (self.rect.width - 2 * self.bar_border_width,
                    self._get_bar_height(bar_max) - self._get_bar_height(bar_min))

    def render(self, display: pygame.Surface | None = None) -> None:
        """
        Renders the Bar.

        Args:
            display (pygame.Surface | None): Display surface, automatically uses the Display object if one is defined.
        """
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        bar_display = display
        self.rect.render(display)

        if self.start_fill_side == Placement.LEFT:
            bar_x = self.rect.x + self.bar_border_width + self._get_bar_width(min(self._display_range))
            bar_y = self.rect.y + self.bar_border_width
        else:
            bar_x = self.rect.x + self.bar_border_width
            bar_y = self.rect.y + self.bar_border_width + self._get_bar_height(self.max_value_range[1] -
                                                                               max(self._display_range))
        bar_size = self.get_bar_size()

        if self.bar_bg_img is not None:
            self.bar_bg_img.render(display)

        color = self.bar_color
        if self._display_range[0] > self._display_range[1] and self.bar_inverse_color is not None:
            color = self.bar_inverse_color

        if self.rect.corner_radius_all != 0 or self.rect.corner_radius_specific is not None:
            # Creating rounded surface
            trans_color = (255, 0, 0) if (255, 0, 0) != color else (0, 255, 0)
            corner_rect_cuts = pygame.Surface((self.rect.width - 2 * self.bar_border_width,
                                               self.rect.height - 2 * self.bar_border_width))
            corner_rect_cuts.set_colorkey((255, 255, 255))
            corner_rect_cuts.fill(trans_color)
            if self.rect.corner_radius_all != 0:
                fill_rect = Rect(0, 0, self.rect.width - 2 * self.bar_border_width,
                                 self.rect.height - 2 * self.bar_border_width,
                                 self.rect.corner_radius_all - self.bar_border_width, color=(255, 255, 255))
            else:
                cuts_corner_radius = {}
                for corners, corner_value in self.rect.corner_radius_specific.items():
                    cuts_corner_radius[corners] = corner_value - self.bar_border_width

                fill_rect = Rect(0, 0, self.rect.width - 2 * self.bar_border_width,
                                 self.rect.height - 2 * self.bar_border_width,
                                 corner_radius_specific=cuts_corner_radius, color=(255, 255, 255))
            fill_rect.render(corner_rect_cuts)

            # Adding bar
            bar_rect_surface = pygame.Surface(bar_size, pygame.SRCALPHA)
            bar_rect_surface.set_colorkey(trans_color)
            bar_rect = Rect(-bar_x + self.rect.x, 0, self.rect.width, self.rect.height, color=color)
            bar_rect.render(bar_rect_surface)

            # Removing corners
            if self.start_fill_side == Placement.LEFT:
                bar_rect_surface.blit(corner_rect_cuts, (self.rect.x - bar_x + self.bar_border_width, 0))
            elif self.start_fill_side == Placement.BOTTOM:
                bar_rect_surface.blit(corner_rect_cuts, (0, self.rect.y - bar_y + self.bar_border_width))

            bar_display = bar_rect_surface

        if self.bar_closed:
            if self.start_fill_side == Placement.LEFT:
                stop_width = self.bar_border_width
                stop_height = self.rect.height - 2 * self.bar_border_width
            else:
                stop_width = self.rect.width - 2 * self.bar_border_width
                stop_height = self.bar_border_width

            if self.max_value_range[0] <= self._display_range[1] < self.max_value_range[1]:
                if self.start_fill_side == Placement.LEFT:
                    max_stop_block = Rect(bar_x + bar_size[0], bar_y, stop_width, stop_height,
                                          color=self.rect.color)
                else:
                    max_stop_block = Rect(bar_x, bar_y - self.bar_border_width, stop_width, stop_height,
                                          color=self.rect.color)

                max_stop_block.render(bar_display)

            if self.max_value_range[0] < self._display_range[0] <= self.max_value_range[1]:
                if self.start_fill_side == Placement.LEFT:
                    max_stop_block = Rect(bar_x - self.bar_border_width, self.rect.y + self.bar_border_width,
                                          stop_width, stop_height, color=self.rect.color)
                else:
                    max_stop_block = Rect(self.rect.x + self.bar_border_width,
                                          bar_y + bar_size[1] - self.bar_border_width, stop_width, stop_height,
                                          color=self.rect.color)

                max_stop_block.render(bar_display)

        if self.rect.corner_radius_all != 0 or self.rect.corner_radius_specific is not None:
            display.blit(bar_display, (bar_x, bar_y))
        else:
            bar_rect = Rect(bar_x, bar_y, bar_size[0], bar_size[1], color=color)
            bar_rect.render(display)

        if self.text is not None:
            self.text.render(display)

    def process_bar_movement(self) -> None:
        """
        Process Bar movents towards their target values using the set speed.
        """
        for side in range(2):
            if self._display_range[side] != self._goal_value_range[side]:
                delta_value = self._goal_value_range[side] - self._display_range[side]
                move_level = self.bar_speed * delta_value / self._display_fps
                move_level = int(move_level if move_level % 1 == 0 else move_level + (1 if delta_value > 0 else -1))

                self._display_range[side] = min(max(self._display_range[side] + move_level,
                                                    self.max_value_range[0]), self.max_value_range[1])

        if self._display_range == self._goal_value_range and self in Bar._moving_bars:
            Bar._moving_bars.remove(self)

    @classmethod
    def process_all_bar_movement(cls) -> None:
        """
        Process the movement of all active Bars.
        """
        for bar in cls._moving_bars:
            bar.process_bar_movement()


class Scene:
    """
    Scenes can be used to group large amounts of DisplayObjects, and be able to change which are visible and which ones
        are not.

    Attributes:
        active_scenes (ClassVar[list[Scene]]): List containing all Scenes which are visible.
        all_scenes (ClassVar[list[Scene]]): List containing all Scenes.
        universal_objects (ClassVar[list[DisplayObject]]): List containing DisplayObjects which should always be
            displayed.
        name (str): Name of the Scene.
        bg_color (T_COLOR): Background color used when displaying the Scene.
        objects (Iterable[DisplayObject | Callable] | MutableMapping[str, DisplayObject | Callable]): Objects to display
            and functions to call when the Scene is active.
    """
    active_scenes: ClassVar[list[Scene] | None] = []
    all_scenes: ClassVar[list[Scene] | None] = []
    universal_objects: ClassVar[list[DisplayObject] | None] = []

    def __init__(self, name: str | None = None, bg_color: T_COLOR = (0, 0, 0),
                 objects: Iterable[DisplayObject | Callable] | MutableMapping[str, DisplayObject | Callable] | None =
                 None) -> None:
        if name in [scene.name for scene in Scene.all_scenes]:
            raise ValueError('name already taken')
        else:
            self.name = name
        self.bg_color = bg_color
        self.objects = objects
        Scene.all_scenes.append(self)

    @property
    def objects_list(self) -> list:
        """
        All DisplayObjects within the Scene.

        Returns:
            list: All DisplayObjects within the Scene.
        """
        if isinstance(self.objects, Mapping):
            objects_list = self.objects.values()
        elif isinstance(self.objects, Iterable):
            objects_list = self.objects
        else:
            return NotImplemented
        return [obj for obj in objects_list if isinstance(obj, DisplayObject)]

    def activate(self, deactivate_all: bool = True) -> None:
        """
        Activate the Scene.

        Args:
            deactivate_all (bool): Deactivates all active Scenes when True.
        """
        if deactivate_all:
            Scene.active_scenes = [self]
        else:
            Scene.active_scenes.insert(-1, self)

    def deactivate(self, deactivate_all: bool = False) -> None:
        """
        Deactivate the Scene.

        Args:
            deactivate_all (bool): Deactivates all active Scenes when True.
        """
        if deactivate_all:
            Scene.active_scenes = []
        else:
            if self in Scene.active_scenes:
                Scene.active_scenes.remove(self)

    def detect_object(self, obj: DisplayObject) -> bool:
        """
        Checks if a given object is saves within the Scene.

        Args:
            obj (DisplayObject): The object to check.

        Returns:
            bool: True if the object is saved within the Scene, False otherwise.
        """
        return obj in self.objects_list

    def detect_object_key(self, key: Hashable) -> bool:
        """
        Checks if an object is saved in the Scene using the given key.

        Args:
            key (Hashable): The key to check.

        Returns:
            bool: True if the object is saved in the Scene using the given key. False otherwise.
        """
        if isinstance(self.objects, Mapping):
            return key in self.objects.keys()
        else:
            return NotImplemented

    def render(self, display: pygame.Surface | None = None) -> None:
        """
        Renders the all objects within the Scene and calls all functions.

        Args:
            display (pygame.Surface | None): Display surface, automatically uses the Display object if one is defined.
        """
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        display.fill(self.bg_color)

        render_objects = self.objects_list + Scene.universal_objects

        for obj in render_objects:
            if isinstance(obj, DisplayObject):
                obj.render(display)
            elif isinstance(obj, Callable):
                obj(display)
            else:
                raise NotImplementedError('Cannot render objects which are not DisplayObject')

    @classmethod
    def find_scene(cls, name: str) -> Scene | None:
        """
        Find a Scene with the given name.

        Args:
            name (str): Name of the Scene.

        Returns:
            Scene | None: Scene with the given name, if no Scene is found, then None.
        """
        for scene in cls.all_scenes:
            if name == scene.name:
                return scene
        return None
