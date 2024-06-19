import pygame
from dataclasses import dataclass, field
from collections.abc import Callable, Sequence, Iterable, MutableSequence, Mapping, MutableMapping, Hashable
from typing import ClassVar, Protocol, runtime_checkable
pygame.font.init()

T_COLOR = Sequence[int, int, int] | Sequence[int, int, int, int] | tuple[int, int, int]


@runtime_checkable
class DisplayObject(Protocol):
    def render(self, display) -> None: ...


class Placement:
    CENTER: int = 0
    LEFT: int = 1
    RIGHT: int = 2
    TOP: int = 3
    BOTTOM: int = 4
    LEFT_OUT: int = 5
    RIGHT_OUT: int = 6
    TOP_OUT: int = 7
    BOTTOM_OUT: int = 8
    TOP_LEFT: int = 9
    TOP_RIGHT: int = 10
    BOTTOM_LEFT: int = 11
    BOTTOM_RIGHT: int = 12

    _indicies = list(range(13))

    @classmethod
    def real_placement(cls, placement: int) -> bool:
        return placement in cls._indicies

    @classmethod
    def double_placement(cls, placement: int) -> bool:
        if not cls.real_placement(placement):
            raise ValueError('Not a valid Placement')

        return placement in (cls.TOP_LEFT, cls.TOP_RIGHT, cls.BOTTOM_LEFT, cls.BOTTOM_RIGHT, cls.CENTER)

    @classmethod
    def split(cls, placement: int) -> int | tuple[int, int]:
        if not cls.real_placement(placement):
            raise ValueError('Not a valid Placement')

        if not cls.double_placement(placement):
            return placement
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
    _frame: int = 0

    @classmethod
    def increase(cls, amount: int = 1) -> int:
        if isinstance(amount, int):
            cls._frame += amount
            return cls._frame
        else:
            return NotImplemented("Frame can only increase using intergers")

    @classmethod
    def set(cls, amount: int = 0) -> int:
        if isinstance(amount, int):
            cls._frame = amount
            return cls._frame
        else:
            return NotImplemented("Frame can only be set to an integer")

    @classmethod
    def get(cls) -> int:
        return cls._frame

    @classmethod
    def get_delta(cls, value: int) -> int:
        if not isinstance(value, int):
            return NotImplemented
        return cls.get() - value

    def __repr__(self) -> str:
        return f'Frame: {Frame.get()}'


class Display:
    CLOCK = pygame.time.Clock()
    fps: ClassVar[int] = 60
    _win: None = None

    @classmethod
    def window(cls):
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
        return self.display.get_width()

    @property
    def height(self) -> int:
        return self.display.get_height()

    def fill(self, color: T_COLOR) -> None:
        self.display.fill(color)

    @staticmethod
    def update() -> None:
        pygame.display.update()

    @classmethod
    def tick_frame(cls, increase_frame: int = 1):
        cls.CLOCK.tick(cls.fps)
        Frame.increase(increase_frame)


@dataclass(kw_only=True)
class Shape:
    color: T_COLOR = (0, 0, 0)
    border: int = 0

    def __repr__(self) -> str:
        return f'Shape: {self.color}'


@dataclass
class Rect(Shape):
    _corner_placement_names: ClassVar[dict[int, str]] = {
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
        return self._rect

    def __setattr__(self, key, value) -> None:
        super().__setattr__(key, value)
        if key in ['x', 'y', 'width', 'height'] and self._rect is not None:
            self._rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        if self.corner_radius_specific is None:
            pygame.draw.rect(display, self.color, self.rect, self.border, self.corner_radius_all)
        else:
            corner_radius = {Rect._corner_placement_names[key]: value for key, value in
                             self.corner_radius_specific.items()}
            pygame.draw.rect(display, self.color, self.rect, self.border, self.corner_radius_all,
                             **corner_radius)

    def __repr__(self) -> str:
        return f'Rect: ({self.x}, {self.y}) - ({self.width}, {self.height})'


@dataclass
class Circle(Shape):
    _corner_placement_names: ClassVar[dict[int, str]] = {
        Placement.TOP_LEFT: 'draw_top_left',
        Placement.TOP_RIGHT: 'draw_top_right',
        Placement.BOTTOM_LEFT: 'draw_bottom_left',
        Placement.BOTTOM_RIGHT: 'draw_bottom_right'
    }
    corner_base_dict: ClassVar[dict[int, bool]] = {Placement.TOP_LEFT: True, Placement.TOP_RIGHT: True,
                                                   Placement.BOTTOM_LEFT: True, Placement.BOTTOM_RIGHT: True}
    _circle: tuple[int, int, int] = field(default=None, kw_only=True)
    x: int = 0
    y: int = 0
    _radius: int = 0
    remove_corner_specific: dict[int, bool] | None = None

    def __post_init__(self):
        self._circle = (self.x, self.y, self._radius)

    @property
    def circle(self) -> tuple[int, int, int]:
        return self._circle

    @property
    def center(self) -> tuple[int, int]:
        return self.circle[0], self.circle[1]

    @property
    def radius(self) -> int:
        return self.circle[2]

    @radius.setter
    def radius(self, value: object) -> None:
        if isinstance(value, int | float):
            self._radius = value
        else:
            raise NotImplemented

    @property
    def diameter(self) -> int:
        return self.radius * 2

    @diameter.setter
    def diameter(self, value: object) -> None:
        if isinstance(value, int | float):
            self.radius = 0.5 * value

    @property
    def width(self) -> int:
        return self.diameter

    @width.setter
    def width(self, value: object) -> None:
        self.diameter = value

    @property
    def height(self) -> int:
        return self.diameter

    @height.setter
    def height(self, value: object) -> None:
        self.diameter = value

    def __setattr__(self, key, value) -> None:
        super().__setattr__(key, value)
        if key in ['x', 'y', '_radius'] and self._circle is not None:
            self._circle = (self.x, self.y, self._radius)

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        if self.remove_corner_specific is None:
            pygame.draw.circle(display, self.color, self.center, self.radius, self.border)
        else:
            draw_corners = Circle.corner_base_dict.copy()
            draw_corners.update(self.remove_corner_specific)
            draw_corners_strings = {Circle._corner_placement_names[key]: value for key, value in draw_corners.items()}
            pygame.draw.circle(display, self.color, self.center, self.radius, self.border,
                               **draw_corners_strings)

    def __repr__(self) -> str:
        return f'Circle: ({self.center}) - ({self.radius})'


@dataclass
class Polygon(Shape):
    polygon_points: MutableSequence[tuple[int, int]] | None = None

    def __post_init__(self) -> None:
        self.polygon_points = self.polygon_points if self.polygon_points is not None else [(0, 0), (0, 0), (0, 0)]

    def insert_point(self, coordinate: tuple[int, int], point_index: int = -1) -> None:
        if not isinstance(self.polygon_points, MutableSequence):
            raise TypeError('Polygon point insertion only possible on MutableSequence')
        elif not isinstance(coordinate, Sequence):
            raise TypeError('Polygon points must be Sequence[int, int] type')

        if coordinate not in self.polygon_points:
            self.polygon_points.insert(point_index, coordinate)

    def remove_point(self, coordinate: tuple[int, int] = (0, 0)) -> int | None:
        if not isinstance(self.polygon_points, MutableSequence):
            raise TypeError('Polygon point removal only possible on MutableSequence')
        if not isinstance(coordinate, Sequence):
            raise TypeError('Polygon points must be Sequence[int, int] type')

        if coordinate in self.polygon_points:
            point_index = self.polygon_points.index(coordinate)
            self.polygon_points.remove(coordinate)
            return point_index
        else:
            return

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        pygame.draw.polygon(display, self.color, self.polygon_points, self.border)

    def __repr__(self) -> str:
        return f'Polygon: ({len(self.polygon_points)} - {self.polygon_points})'


@dataclass
class Ellipse(Shape):
    _ellipse: pygame.Rect = field(default=None, kw_only=True)
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    def __post_init__(self) -> None:
        self._ellipse: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def ellipse(self) -> pygame.Rect:
        return self._ellipse

    def __setattr__(self, key, value) -> None:
        super().__setattr__(key, value)
        if key in ['x', 'y', 'width', 'height'] and self._ellipse is not None:
            self._ellipse = pygame.Rect(self.x, self.y, self.width, self.height)

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        pygame.draw.ellipse(display, self.color, self.ellipse, self.border)

    def __repr__(self) -> str:
        return f'Ellipse: ({self.x}, {self.y}) - ({self.width}, {self.height})'


@dataclass
class Text:
    _text: str = field(default='', kw_only=True)

    text: str
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
    multi_line_splitted: MutableSequence['Text'] | None = None

    multi_line_height_factor: ClassVar[int] = 0.75
    multi_line_spacing_factor: ClassVar[int] = 1.4

    def __post_init__(self) -> None:
        if self.dynamic_multi_line:
            if None in [self.resize_max_width, self.resize_max_height]:
                raise ValueError('Provide resize_max_width and resize_max_height arguments to use dynamic multilines')

            self.multi_line_splitted = []
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
                self.multi_line_splitted.append(line_text_obj)

        else:
            if self.font_size is None:
                self.font_size = 300
                self.update_font()
                self.auto_size_font()
            self.update_font()

    def auto_size_font(self, resize: bool = True) -> int:
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
        self._text_font_processed = pygame.font.SysFont(self.font, self.font_size, self.bold, self.italic)

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: object) -> None:
        if isinstance(value, str):
            self._text = value

            if self.resize_max_width is not None or self.resize_max_height is not None:
                self.auto_size_font()
        else:
            raise NotImplemented

    @property
    def text_size_rect(self) -> Rect:
        return Rect(self.x, self.y, self.resize_max_width, self.resize_max_height)

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        if self.dynamic_multi_line:
            for text_obj in self.multi_line_splitted:
                text_obj.render(display)

        else:
            text_render = self._text_font_processed.render(self.text, True, self.color)

            text_y = self.y - text_render.get_height() // 2

            if Placement.double_placement(self.alignment):
                x_align, y_align = Placement.split(self.alignment)

                match y_align:
                    case Placement.CENTER:
                        text_y = self.y + (self.resize_max_height - text_render.get_height()) // 2
                    case Placement.TOP:
                        text_y = self.y + self.margin // 2
                    case Placement.BOTTOM:
                        text_y = self.y - (text_render.get_height() - self.margin) // 2
                    case _:
                        return NotImplemented("Unusable text alignment")
            else:
                x_align = self.alignment

            match x_align:
                case Placement.CENTER:
                    text_x = self.x + (self.resize_max_width - text_render.get_width()) // 2
                case Placement.LEFT:
                    text_x = self.x + self.margin // 2
                case Placement.RIGHT:
                    text_x = self.x - (text_render.get_width() - self.margin) // 2
                case _:
                    return NotImplemented("Unusable text alignment")

            display.blit(text_render, (text_x, text_y))

    def __repr__(self):
        return f'"{self.text}", ({self.x}, {self.y}), {self.color}, size={self.font_size}'


@dataclass
class InputField:
    active_input: ClassVar[None] = None
    rect_not_active_color: T_COLOR = field(default=None, kw_only=True)

    input_rect: Sequence[int, int, int, int, T_COLOR] | Rect = (0, 0, 0, 0, (0, 0, 0))
    rect_active_color: T_COLOR | None = None

    _text: Text | None = None
    _empty_text: Text | None = None
    replace_text_char: str | None = True
    _hidden_text: str = ''

    character_max: int | None = None
    restricted_characters: str = ''
    allow_letters: bool = False
    allow_numbers: bool = False
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

    @property
    def text_str(self) -> str:
        return self._text.text

    @text_str.setter
    def text_str(self, value) -> None:
        if isinstance(value, str):
            if self.replace_text_char:
                self._text.text = len(value) * self.replace_text_char
                self._hidden_text = value
            else:
                self._text.text = value
        else:
            raise NotImplemented

    @property
    def text(self) -> Text:
        return self._text

    @text.setter
    def text(self, value) -> None:
        if isinstance(value, Text):
            self._text = value
        else:
            raise NotImplemented

    @property
    def text_hidden(self) -> str:
        if self.replace_text_char:
            return self._hidden_text
        else:
            return self.text_str

    @property
    def empty_text(self) -> str:
        return self._empty_text.text

    @empty_text.setter
    def empty_text(self, value) -> None:
        if isinstance(value, str):
            self._empty_text.text = value
        else:
            raise NotImplemented

    @property
    def empty_text_raw(self) -> Text:
        return self._empty_text

    @empty_text_raw.setter
    def empty_text_raw(self, value) -> None:
        if isinstance(value, Text):
            self._empty_text = value
        else:
            raise NotImplemented

    @property
    def rect_color(self) -> T_COLOR:
        return self.input_rect.color

    def is_allowed(self, char: str) -> bool:
        if char in self.restricted_characters:
            return False
        if not self.allow_numbers and not self.allow_letters and self.allow_special == '':
            return True

        if self.allow_numbers and char.isnumeric():
            return True
        if self.allow_letters and char.isalpha():
            return True
        if char in self.allow_special:
            return True
        return False

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        self.input_rect.render(display)

        text_x, text_y = self.input_rect.x, self.input_rect.y + self.input_rect.height // 2
        if self.text_str == '' and not self == InputField.active_input:
            self.empty_text_raw.x, self.empty_text_raw.y = text_x, text_y
            self.empty_text_raw.render(display)
        else:
            self.text.x, self.text.y = text_x, text_y
            self.text.render(display)

    @classmethod
    def activate(cls, input_field) -> None:
        if cls.active_input is not None:
            cls.active_input.input_rect.color = input_field.rect_not_active_color

        cls.active_input = input_field
        if input_field is not None and input_field.rect_active_color is not None:
            input_field.input_rect.color = input_field.rect_active_color

    @classmethod
    def deactivate(cls) -> None:
        if cls.active_input is not None:
            cls.active_input.input_rect.color = cls.active_input.rect_not_active_color
            cls.active_input = None

    @classmethod
    def process_input(cls, event) -> None | str:
        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_BACKSPACE):
            if event.key == pygame.K_ESCAPE and cls.active_input.exit_esc:
                cls.deactivate()
                return

            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return_text = None

                if cls.active_input.submit_return:
                    return_text = cls.active_input.text_hidden

                if cls.active_input.clear_on_submit:
                    cls.active_input.text_str = ''

                return return_text

            elif event.key == pygame.K_BACKSPACE and cls.active_input.can_del:
                if len(cls.active_input.text_str) >= 1:
                    cls.active_input.text_str = cls.active_input.text_str[:-1]
                return

        elif len(cls.active_input.text_str) < cls.active_input.character_max and \
                cls.active_input.is_allowed(event.unicode):
            cls.active_input.text_str += event.unicode
            return

        print(f'Input processing is not implemented for {event.unicode}')
        return

    def __repr__(self) -> str:
        return f'pos: ({self.input_rect.x}, {self.input_rect.y}) - text: {self.text_str}'


@dataclass
class Image:
    assests_folder_path: str = field(default=None, kw_only=True)
    image: pygame.Surface = field(default=None, kw_only=True)
    border_rect: Rect = field(default=None, kw_only=True)

    _path: str = ''
    x: int = 0
    y: int = 0
    resize_to: Sequence[int, int] | None = None

    alpha: T_COLOR | None = None
    hide: bool = False
    direct_path: bool = False

    border: int = 0
    border_color: T_COLOR = (0, 0, 0)

    def __post_init__(self) -> None:
        self.image = pygame.image.load(self.path)

        if self.resize_to is not None:
            self.resize(self.resize_to)

        self.set_border()

    @property
    def width(self) -> int:
        if self.image is not None:
            return self.image.get_width()

    @width.setter
    def width(self, value) -> None:
        if isinstance(value, int) and self.image is not None:
            self.image.width = value

    @property
    def height(self) -> int:
        if self.image is not None:
            return self.image.get_height()

    @height.setter
    def height(self, value) -> None:
        if isinstance(value, int) and self.image is not None:
            self.image.height = value

    @property
    def path(self) -> str:
        if Image.assests_folder_path is not None and not self.direct_path:
            if Image.assests_folder_path[-1] != '\\':
                return Image.assests_folder_path + '\\' + self._path
            else:
                return Image.assests_folder_path + self._path
        else:
            return self._path

    def set_border(self) -> None:
        if self.border > 0:
            self.border_rect = Rect(self.x - self.border, self.y - self.border, self.width + 2 * self.border,
                                    self.height + 2 * self.border, color=self.border_color, border=self.border)

    def resize(self, size: Sequence[int | None, int | None] | None = None) -> None:
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
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        if not self.hide:
            display.blit(self.image, (self.x, self.y))
            if self.border > 0:
                self.border_rect.render(display)

    def __repr__(self) -> str:
        return f'pos: ({self.x}, {self.y}) - hidden: {self.hide} - src: {self.path}'


class ObjectAnimation:
    @dataclass
    class Action:
        display_fps: ClassVar[int] = Display.fps if Display.fps is not None else 60

        SCALE: int = 0
        SCALE_TO: int = 1
        MOVE: int = 2
        MOVE_TO: int = 3
        CHANGE_CORNER_RADIUS: int = 4
        CHANGE_CORNER_RADIUS_TO: int = 5
        CHANGE_OBJECT: int = 6
        SET_COLOR_TO: int = 7
        CHANGE_BORDER_WIDTH_TO: int = 8

        @classmethod
        def execute(cls, objects, index, start_action_time, action: int = None, **kwargs):
            wait_time = 0
            object_index = None
            cur_object = objects[index]

            if action is None:
                return wait_time, object_index

            if 'time' in kwargs.keys():
                if action in (cls.SCALE_TO, cls.MOVE_TO, cls.CHANGE_CORNER_RADIUS_TO, cls.CHANGE_BORDER_WIDTH_TO):
                    wait_time = start_action_time - Frame.get() + kwargs['time']
                else:
                    wait_time = kwargs['time']
                transform_factor = 1 / max(wait_time, 1)
            else:
                transform_factor = 1

            try:
                match action:
                    case cls.SCALE:
                        if 'width' in kwargs.keys():
                            step_size = int(kwargs['width'] * transform_factor)
                            cur_object.width += step_size
                        if 'height' in kwargs.keys():
                            step_size = int(kwargs['height'] * transform_factor)
                            cur_object.height += step_size

                        if 'width' not in kwargs.keys() and 'height' not in kwargs.keys():
                            raise KeyError('width and/or height key should be given to use SCALE action')

                    case cls.SCALE_TO:
                        if 'width' in kwargs.keys():
                            delta_w = kwargs['width'] - cur_object.width
                            step_size = int(delta_w * transform_factor)
                            cur_object.width += step_size
                        if 'height' in kwargs.keys():
                            delta_h = kwargs['height'] - cur_object.height
                            step_size = int(delta_h * transform_factor)
                            cur_object.height += step_size

                        if 'width' not in kwargs.keys() and 'height' not in kwargs.keys():
                            raise KeyError('width and/or height key should be given to use SCALE_TO action')

                    case cls.MOVE:
                        if 'x' in kwargs.keys():
                            step_size = int(kwargs['x'] * transform_factor)
                            cur_object.x += step_size
                        if 'y' in kwargs.keys():
                            step_size = int(kwargs['y'] * transform_factor)
                            cur_object.y += step_size

                        if 'x' not in kwargs.keys() and 'y' not in kwargs.keys():
                            raise KeyError('x and/or y key should be given to use MOVE action')

                    case cls.MOVE_TO:
                        if 'x' in kwargs.keys():
                            delta_x = kwargs['x'] - cur_object.x
                            step_size = int(delta_x * transform_factor)
                            cur_object.x += step_size
                        if 'y' in kwargs.keys():
                            delta_y = kwargs['y'] - cur_object.y
                            step_size = int(delta_y * transform_factor)
                            cur_object.y += step_size

                        if 'x' not in kwargs.keys() and 'y' not in kwargs.keys():
                            raise KeyError('x and/or y key should be given to use MOVE_TO action')

                    case cls.CHANGE_CORNER_RADIUS:
                        if 'radius' in kwargs.keys():
                            step_size = int(kwargs['radius'] * transform_factor)
                            cur_object.corner_radius_all += step_size
                        else:
                            raise KeyError('radius key should be given to use CHANGE_CORNER_RADIUS action')

                    case cls.CHANGE_CORNER_RADIUS_TO:
                        if 'radius' in kwargs.keys():
                            delta_r = kwargs['radius'] - cur_object.corner_radius_all
                            step_size = int(delta_r * transform_factor)
                            cur_object.corner_radius_all += step_size
                        else:
                            raise KeyError('radius key should be given to use CHANGE_CORNER_RADIUS_TO action')

                    case cls.CHANGE_OBJECT:
                        try:
                            object_index = kwargs['index']

                            if cur_object.trace:
                                objects[object_index].width = cur_object.width
                                objects[object_index].height = cur_object.height

                        except KeyError:
                            raise KeyError('index key should be given to use CHANGE_OBJECT action')

                    case cls.SET_COLOR_TO:
                        if 'color' in kwargs.keys():
                            cur_object.color = kwargs['color']
                        else:
                            raise KeyError('color key should be given to use SET_COLOR_TO action')

                    case cls.CHANGE_BORDER_WIDTH_TO:
                        if 'border' in kwargs.keys():
                            delta_b = kwargs['border'] - cur_object.border
                            step_size = int(delta_b * transform_factor)
                            cur_object.border += step_size
                        else:
                            raise KeyError('border key should be given to use CHANGE_BORDER_WIDTH_TO action')

                    case _:
                        raise ValueError('Invalid Action value')

            except AttributeError:
                raise AttributeError('The animation object misses attributes to be compatible with this Action')

            return wait_time, object_index

    running_animations: MutableSequence = []

    def __init__(self, action_sequence: MutableSequence[Sequence[int, dict[str, int]]],
                 animation_objects: Sequence, trace_objects: bool = True, stop_reset: bool = True):
        self.action_sequence = action_sequence
        self.animation_objects = animation_objects
        self._start_object_setting = animation_objects[:]
        self.trace = trace_objects
        self.started_move = False
        self.action_index = 0
        self.object_index = 0
        self.start_action_frame = 0
        self.next_frame = 0
        self.stop_reset = stop_reset

    def start(self):
        if self not in ObjectAnimation.running_animations:
            self.start_action_frame = Frame.get()
            ObjectAnimation.running_animations.append(self)
        else:
            print('Animation already running')

    def stop(self):
        if self in ObjectAnimation.running_animations:
            # ObjectAnimation.running_animations.remove(self)
            ObjectAnimation.running_animations[ObjectAnimation.running_animations.index(self)] = None

        if self.stop_reset:
            self.reset()

    def reset(self):
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
        self.animation_objects = self._start_object_setting.copy()

    def render(self):
        self.animation_objects[self.object_index].render()

    def process_animation(self):
        current_action = self.action_sequence[self.action_index]

        wait_time, object_index = ObjectAnimation.Action.execute(self.animation_objects, self.object_index,
                                                                 self.start_action_frame, current_action[0],
                                                                 **current_action[1])

        if object_index is not None:
            self.object_index = object_index

        if Frame.get() >= self.next_frame:
            self.start_action_frame = Frame.get()
            self.next_frame = self.start_action_frame + wait_time - 1
            if self.started_move:
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
        for animation in cls.running_animations:
            if animation is not None:
                animation.process_animation()

        cls.running_animations = [a for a in cls.running_animations if a is not None]


@dataclass
class Button:
    BUTTON_TYPES: ClassVar[tuple[str, ...]] = ('switch', 'push')

    active_buttons: ClassVar[list] = []

    _text: Text = field(default=None, kw_only=True)

    rect: Sequence[int, int, int, int, T_COLOR] | Rect = (0, 0, 0, 0, (0, 0, 0))
    pressed_color: T_COLOR | None = None

    text_obj: Text | None = None
    fit_text: bool = True

    img: Image | None = None
    img_margin: int = 0
    img_fill_button: bool = True
    img_alignment: int = Placement.CENTER

    pressed: bool = False
    button_type: str = 'switch'
    target_scene_on_press: str | None = None
    call_on_press: Callable | list[Callable] or None = None
    call_on_press_kwargs: dict | list[dict] | None = None

    def __post_init__(self) -> None:
        if isinstance(self.rect, Sequence):
            self.rect = Rect(*self.rect[:4], color=self.rect[4])

        self.not_pressed_color = self.rect.color
        if self.pressed_color is not None:
            self.rect.color = self.pressed_color

        if self.fit_text and self.text is not None:
            self.text.x = self.rect.x
            self.text.y = self.rect.y
            self.text.resize_max_width = self.rect.width
            self.text.resize_max_height = self.rect.height
            self.text.auto_size_font()

        if self.img is not None:
            if self.img_fill_button:
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
                    self.img.y = self.rect.y + self.rect.width - self.img.width - self.img_margin
                else:
                    self.img_y = self.rect.y + (self.rect.width - self.img.width) // 2

        Button.active_buttons.append(self)

    @property
    def text_str(self) -> str:
        return self._text.text

    @text_str.setter
    def text_str(self, value) -> None:
        if isinstance(value, str):
            self._text.text = value
        else:
            raise NotImplemented

    @property
    def text(self) -> Text:
        return self._text

    @text.setter
    def text(self, value) -> None:
        if isinstance(value, Text):
            self._text = value
        else:
            raise NotImplemented

    def call_func(self, kwargs_list: list[dict] = None, **kwargs) -> None:
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

                        if len(kwargs_list) > index:
                            callable_kwargs.update(**kwargs_list[index])

                        func(**callable_kwargs)

    def render(self, display: pygame.Surface | None = None) -> None:
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
    def check_all_collisions(cls):
        mouse_position = pygame.mouse.get_pos()

        for button in cls.active_buttons:
            button.check_collision(mouse_position)

    @classmethod
    def release_push_buttons(cls) -> None:
        for button in cls.active_buttons:
            if button.button_type == 'push' and button.pressed is True:
                button.pressed = False

    def __repr__(self) -> str:
        return f'Button: ({self.rect.x}, {self.rect.y}) - target: {self.target_scene_on_press}'


@dataclass
class Bar:
    display_fps: ClassVar[int] = Display.fps if Display.fps is not None else 60
    moving_bars: ClassVar[list] = []
    active_bars: ClassVar[list] = []

    # _bar_id_counter: ClassVar[int] = 0

    rect: Sequence[int, int, int, int, T_COLOR] | Rect = (0, 0, 0, 0, (0, 0, 0))
    max_value_range: list[float] | None = None
    goal_value_range: list[float] | None = field(default=None, kw_only=True)
    display_range: list[float] | None = field(default=None, kw_only=True)

    bar_border_width: int = 2

    bar_color: T_COLOR = None
    _text: Text | None = None
    bar_bg_img: Image | None = None

    bar_closed: bool = False

    start_fill_side: int = Placement.LEFT
    bar_speed: float = 3.0
    starting_frame: int = Frame.get()

    # _bar_id = _bar_id_counter

    def __post_init__(self) -> None:
        # Bar._bar_id_counter += 1
        Bar.active_bars.append(self)

        if isinstance(self.rect, Sequence):
            self.rect = Rect(*self.rect[:4], color=self.rect[4], border=self.bar_border_width)
        elif isinstance(self.rect, Rect):
            if self.rect.border == 0:
                self.rect.border = self.bar_border_width
            else:
                self.bar_border_width = self.rect.border

        if self.bar_color is None:
            self.bar_color = tuple(255 - self.rect.color[c] for c in self.rect.color)

        self.max_value_range = [0.0, 100.0] if self.max_value_range is None else self.max_value_range
        self.goal_value_range = self.max_value_range
        self.display_range = self.max_value_range

        if self.start_fill_side not in (Placement.LEFT, Placement.BOTTOM):
            self.start_fill_side = Placement.LEFT

        if self.bar_bg_img is not None:
            self.bar_bg_img.x, self.bar_bg_img.y = self.rect.x + self.rect.border, self.rect.y + self.rect.border

    @property
    def text_str(self) -> str:
        return self._text.text

    @text_str.setter
    def text_str(self, value: object) -> None:
        if isinstance(value, str):
            self._text.text = value
        else:
            raise NotImplemented

    @property
    def text(self) -> Text:
        return self._text

    @text.setter
    def text(self, value: object) -> None:
        if isinstance(value, Text):
            self._text = value
        else:
            raise NotImplemented

    def set_value(self, value: float, set_bottom: bool = False) -> None:
        set_value = min(max(value, self.max_value_range[0]), self.max_value_range[1])
        target_index = 1 if not set_bottom else 0

        self.goal_value_range[target_index] = set_value

        if self not in Bar.moving_bars:
            Bar.moving_bars.append(self)

    def modify_value(self, value: float, set_bottom: bool = False) -> None:
        target_index = 1 if not set_bottom else 0
        self.set_value(self.goal_value_range[target_index] + value, set_bottom)

    def set_percentage(self, percentage: float, set_bottom: bool = False) -> None:
        value_for_percent = percentage / 100 * self.max_value_range[1]
        self.set_value(value_for_percent, set_bottom)

    def modify_percentage(self, percentage: float, set_bottom: bool = False) -> None:
        value_for_percent = percentage / 100 * self.max_value_range[1]
        self.modify_value(value_for_percent, set_bottom)

    def get_bar_width(self, value: float) -> int:
        bg_width = self.rect.width - 2 * self.bar_border_width
        ratio_filled = value / self.max_value_range[1]
        return int(bg_width * ratio_filled)

    def get_bar_height(self, value: float) -> int:
        bg_height = self.rect.height - 2 * self.bar_border_width
        ratio_filled = value / self.max_value_range[1]
        return int(bg_height * ratio_filled)

    def get_bar_size(self) -> tuple[int, int]:
        if self.start_fill_side == Placement.LEFT:
            return (self.get_bar_width(self.display_range[1] - self.display_range[0]),
                    self.rect.height - 2 * self.bar_border_width)
        else:
            return (self.rect.width - 2 * self.bar_border_width,
                    self.get_bar_height(self.display_range[1] - self.display_range[0]))

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        self.rect.render(display)

        if self.start_fill_side == Placement.LEFT:
            bar_x = self.rect.x + self.bar_border_width + self.get_bar_width(self.display_range[0])
            bar_y = self.bar_bg_img.y = self.rect.y + self.bar_border_width
        else:
            bar_x = self.rect.x + self.bar_border_width
            bar_y = self.rect.y + self.bar_border_width + self.get_bar_width(self.max_value_range[1] -
                                                                             self.display_range[1])
        bar_size = self.get_bar_size()

        if self.bar_bg_img is not None:
            self.bar_bg_img.x = bar_x
            self.bar_bg_img.y = bar_y
            self.bar_bg_img.resize(bar_size)

            self.bar_bg_img.render(display)
        else:
            bar_rect = Rect(bar_x, bar_y, bar_size[0], bar_size[1], color=self.bar_color)
            bar_rect.render(display)

        if self.bar_closed:
            if self.start_fill_side == Placement.LEFT:
                stop_width = self.bar_border_width
                stop_height = self.rect.height
            else:
                stop_width = self.rect.width
                stop_height = self.bar_border_width

            if (self.display_range[1] > self.max_value_range[0] + self.rect.border and
                    self.display_range[1] != self.max_value_range[1]):

                if self.start_fill_side == Placement.LEFT:
                    max_stop_block = Rect(self.rect.x + self.bar_border_width + bar_size[0],
                                          self.rect.y + self.bar_border_width, stop_width, stop_height,
                                          color=self.rect.color)
                else:
                    max_stop_block = Rect(self.rect.x + self.bar_border_width,
                                          self.rect.y + self.bar_border_width +
                                          self.get_bar_width(self.max_value_range[1] - self.display_range[1]),
                                          stop_width, stop_height,
                                          color=self.rect.color)

                max_stop_block.render(display)

            elif (self.display_range[0] > self.max_value_range[0] + self.rect.border and
                  self.display_range[0] != self.max_value_range[1]):

                if self.start_fill_side == Placement.LEFT:
                    max_stop_block = Rect(self.rect.x + self.bar_border_width +
                                          self.get_bar_width(self.display_range[0]),
                                          self.rect.y + self.bar_border_width, stop_width, stop_height,
                                          color=self.rect.color)
                else:
                    max_stop_block = Rect(self.rect.x + self.bar_border_width,
                                          self.rect.y + self.bar_border_width +
                                          self.get_bar_width(self.max_value_range[1] - self.display_range[1]),
                                          stop_width, stop_height,
                                          color=self.rect.color)

                max_stop_block.render(display)

        if self.text is not None:
            self.text.render(display)

    def process_bar_movement(self) -> None:
        for side in range(2):
            if self.display_range[side] != self.goal_value_range[side]:
                delta_value = self.goal_value_range[side] - self.display_range[side]

                self.display_range[side] = min(max(self.display_range[side] +
                                                   int(delta_value / (self.bar_speed * self.display_fps)),
                                                   self.max_value_range[0]), self.max_value_range[1])

                if self.display_range[side] == self.goal_value_range[side] and self in Bar.moving_bars:
                    Bar.moving_bars.remove(self)

    @classmethod
    def process_all_bar_movement(cls) -> None:
        for bar in cls.moving_bars:
            bar.process_bar_movement()


class Scene:
    current_scene: MutableSequence | None = []
    all_scenes: MutableSequence | None = []
    universal_objects: list | None = []

    def __init__(self, name: str | None = None, bg_color: T_COLOR | None = (0, 0, 0),
                 objects: Iterable | MutableMapping | None = None) -> None:
        if name in [scene.name for scene in Scene.all_scenes]:
            raise ValueError('name already taken')
        else:
            self.name = name
        self.bg_color = bg_color
        self.objects = objects
        Scene.all_scenes.append(self)

    @property
    def objects_list(self) -> list:
        if isinstance(self.objects, Mapping):
            objects_list = self.objects.values()
        elif isinstance(self.objects, Iterable):
            objects_list = self.objects
        else:
            return NotImplemented
        return list(objects_list)

    def activate(self, deactivate_all: bool = True) -> None:
        if deactivate_all:
            Scene.current_scene = [self]
        else:
            Scene.current_scene.insert(-1, self)

    def deactivate(self, deactivate_all: bool = False) -> None:
        if deactivate_all:
            Scene.current_scene = []
        else:
            if self in Scene.current_scene:
                Scene.current_scene.remove(self)

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display.window()
        if display is None:
            raise ValueError('Display argument missing')

        if self.bg_color is not None:
            display.fill(self.bg_color)

        render_objects = self.objects_list + Scene.universal_objects

        for obj in render_objects:
            if isinstance(obj, DisplayObject):
                obj.render(display)
            else:
                raise NotImplementedError('Cannot render objects which are not DisplayObject')

    def detect_object(self, obj: object) -> bool:
        return obj in self.objects_list

    def detect_object_key(self, obj: Hashable) -> bool:
        if isinstance(self.objects, Mapping):
            return obj in self.objects.keys()
        else:
            return NotImplemented

    @classmethod
    def find_scene(cls, name: str) -> 'Scene':
        for scene in cls.all_scenes:
            if name == scene.name:
                return scene
