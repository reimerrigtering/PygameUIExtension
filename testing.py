import pygame
from ui_classes import (Display, Rect, Circle, Polygon, Ellipse, Text, Bar, Placement, ObjectAnimation as oa, Button,
                        InputField)


display_window = Display((800, 800), 'testing')

rectangle = Rect(20, 70, 130, 200, border=3)
circle = Circle(155, 275, 80, {Placement.TOP_LEFT: False}, color=(0, 150, 255), border=10)

polygon1 = Polygon([(80, 398), (100, 410), (100, 430), (80, 442), (60, 430), (60, 410)], color=(50, 0, 100))
polygon2 = Polygon([(100, 428), (120, 440), (120, 460), (100, 472), (80, 460), (80, 440)], color=(100, 0, 50))

ellipse1 = Ellipse(300, 50, 100, 200, color=(150, 0, 150), border=10)
ellipse2 = Ellipse(275, 75, 200, 100, color=(0, 150, 150), border=10)

text_single = Text('Double line test...', 400, 370, (50, 0, 200), alignment=Placement.LEFT, resize_max_width=250,
                   resize_max_height=100)

text = Text(
    """Testing Text DML:
- Use 1 & 2     > empty
- Use 3 & 4     > inc & dec the bar top value
- Use 5 & 6     > inc & dec the bar bottom value
- Use 7         > add poly corners
                  and dec ellipse sizes
- Use 8         > remove poly corners
                  and inc ellipse sizes
- Use 9         > info dump""",
    400, 400, (0, 125, 255), alignment=Placement.TOP_LEFT, resize_max_width=250, resize_max_height=250,
    dynamic_multi_line=True, margin=20)
text_surround_rect = Rect(400, 400, 250, 250, color=(200, 200, 200))

bar = Bar(rectangle, bar_color=(255, 125, 0), bar_inverse_color=(255, 0, 0), bar_closed=True,
          start_fill_side=Placement.LEFT)

moving_block = Rect(50, 500, 50, 50, color=(255, 0, 0), border=20)
moving_block_sqr = Rect(48, 498, 94, 94, color=(0, 0, 0), border=2)
move_amount = 40
moving_block_seq_pos = 0

moving_block_right = oa([(oa.Action.MOVE, {'x': move_amount, 'time': 20})],
                        animation_objects=[moving_block])
moving_block_left = oa([(oa.Action.MOVE, {'x': -move_amount, 'time': 20})],
                       animation_objects=[moving_block])
moving_block_up = oa([(oa.Action.MOVE, {'y': -move_amount, 'time': 20})],
                     animation_objects=[moving_block])
moving_block_down = oa([(oa.Action.MOVE, {'y': move_amount, 'time': 20})],
                       animation_objects=[moving_block])

blue_block_color = oa([(oa.Action.SET_COLOR_TO, {'color': (150, 150, 255)})],
                      animation_objects=[moving_block])
red_block_color = oa([(oa.Action.SET_COLOR_TO, {'color': (255, 0, 0)})],
                     animation_objects=[moving_block])

block_border = oa([(oa.Action.CHANGE_BORDER_WIDTH_TO, {'border': 20, 'time': 10})],
                  animation_objects=[moving_block])
no_block_border = oa([(oa.Action.CHANGE_BORDER_WIDTH_TO, {'border': 5, 'time': 10})],
                     animation_objects=[moving_block])

command_field = InputField(Rect(50, 700, 500, 60, color=(200, 200, 200), corner_radius_all=20, border=5),
                           _empty_text=Text('command here', color=(150, 150, 150)), rect_active_color=(0, 150, 0))


def move_block() -> None:
    global moving_block_seq_pos
    moves = (moving_block_right, moving_block_down, moving_block_left, moving_block_up)
    moves[moving_block_seq_pos].start()

    if moving_block_seq_pos % 2 == 0:
        blue_block_color.start()
        block_border.start()
    else:
        red_block_color.start()
        no_block_border.start()

    if moving_block_seq_pos < 3:
        moving_block_seq_pos += 1
    else:
        moving_block_seq_pos = 0


move_block_button = Button(Rect(150, 500, 100, 50, color=(200, 200, 200)), _text=Text('Move Block', margin=3),
                           button_type='push', call_on_press=move_block)


def update_window():
    display_window.fill((255, 255, 255))
    circle.render()
    polygon1.render()
    polygon2.render()
    ellipse1.render()
    ellipse2.render()
    bar.render()

    text_surround_rect.render()
    text.render()
    text_single.render()

    moving_block_sqr.render()
    moving_block.render()
    move_block_button.render()

    command_field.render()

    Button.release_push_buttons()
    Bar.process_all_bar_movement()
    oa.update_animations()
    display_window.update()


def main():
    run = True

    while run:
        Display.tick_frame()

        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    run = False

                case pygame.KEYDOWN:
                    match InputField.active_input.process_input(event):
                        case 'block':
                            move_block()

                    match event.key:
                        # case pygame.K_1:

                        # case pygame.K_2:

                        case pygame.K_3:
                            bar.modify_value(10)
                            print(f'{bar.display_range} -> {bar.goal_value_range} / {bar.max_value_range}')

                        case pygame.K_4:
                            bar.modify_value(-10)
                            print(f'{bar.display_range} -> {bar.goal_value_range} / {bar.max_value_range}')

                        case pygame.K_5:
                            bar.modify_value(10, set_bottom=True)
                            print(f'{bar.display_range} -> {bar.goal_value_range} / {bar.max_value_range}')

                        case pygame.K_6:
                            bar.modify_value(-10, set_bottom=True)
                            print(f'{bar.display_range} -> {bar.goal_value_range} / {bar.max_value_range}')

                        case pygame.K_7:
                            polygon1.insert_point((100, 398), 1)
                            polygon2.insert_point((80, 472), 4)

                            ellipse2.width = max(ellipse2.width - 10, 100)
                            ellipse1.height = max(ellipse1.height - 10, 100)

                        case pygame.K_8:
                            polygon1.remove_point((100, 398))
                            polygon2.remove_point((80, 472))

                            ellipse2.width = min(ellipse2.width + 10, 300)
                            ellipse1.height = min(ellipse1.height + 10, 300)

                        case pygame.K_9:
                            print(f'{bar.percentage}')

                        case pygame.K_i:
                            print(f'block_pos: {moving_block.x}, {moving_block.y}')

                case pygame.MOUSEBUTTONDOWN:
                    Button.check_all_collisions()
                    InputField.check_all_collisions()

        update_window()


if __name__ == "__main__":
    main()
