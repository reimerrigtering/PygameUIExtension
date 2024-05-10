import pygame
from ui_classes import Display, Rect, Circle, Polygon, Ellipse, Text, Bar, Placement, ObjectAnimation, Button


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
- Use 1 & 2     > dec & inc the bar and circle r
- Use 3 & 4     > dec & inc the bar bottom value
- Use 5         > empty
- Use 6         > empty
- Use 7         > add poly corners
                  and dec ellipse sizes
- Use 8         > remove poly corners
                  and inc ellipse sizes
- Use 9         > empty""",
    400, 400, (0, 125, 255), alignment=Placement.TOP_LEFT, resize_max_width=250, resize_max_height=250,
    dynamic_multi_line=True, margin=20)
text_surround_rect = Rect(400, 400, 250, 250, color=(200, 200, 200))

bar = Bar(rectangle, bar_color=(255, 125, 0), bar_closed=True, start_fill_side=Placement.BOTTOM)

moving_block = Rect(200, 600, 50, 50, color=(255, 0, 0))
moving_block_bounds = Rect(200, 560, 90, 90, border=4)

moving_block_right = ObjectAnimation([(ObjectAnimation.Action.MOVE, {'x': 40, 'time': 20})],
                                     animation_objects=[moving_block])
moving_block_left = ObjectAnimation([(ObjectAnimation.Action.MOVE, {'x': -40, 'time': 20})],
                                    animation_objects=[moving_block])
moving_block_up = ObjectAnimation([(ObjectAnimation.Action.MOVE, {'y': -40, 'time': 20})],
                                  animation_objects=[moving_block])
moving_block_down = ObjectAnimation([(ObjectAnimation.Action.MOVE, {'y': 40, 'time': 20})],
                                    animation_objects=[moving_block])
moving_block_fill = ObjectAnimation([(ObjectAnimation.Action.MOVE_TO, {'x': 200, 'y': 560, 'time': 10}),
                                     (ObjectAnimation.Action.SCALE_TO, {'width': 90, 'height': 90, 'time': 10})],
                                    animation_objects=[moving_block])

moving_block_sequence_pos = 0


def move_block() -> None:
    global moving_block_sequence_pos
    movement_list = [moving_block_up, moving_block_right, moving_block_down, moving_block_left]

    movement_list[moving_block_sequence_pos].start()

    if moving_block_sequence_pos == 3:
        moving_block_sequence_pos = 0
    else:
        moving_block_sequence_pos += 1


move_block_button = Button(Rect(300, 560, 60, 40, color=(200, 200, 200)), _text=Text('Cycle'), button_type='push',
                           call_on_press=move_block)
fill_block_button = Button(Rect(300, 610, 60, 40, color=(200, 200, 200)), _text=Text('Fill'), button_type='push',
                           call_on_press=moving_block_fill.start)


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

    moving_block.render()
    moving_block_bounds.render()

    move_block_button.render()
    fill_block_button.render()

    Button.release_push_buttons()
    Bar.process_all_bar_movement()
    ObjectAnimation.update_animations()
    display_window.update()


def main():
    run = True
    bar.set_percentage(circle.radius - 30, set_instant=True)

    while run:
        Display.tick_frame()

        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    run = False

                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            run = False

                        case pygame.K_1:
                            circle.radius = max(circle.radius - 10, 30)
                            bar.modify_value(-10)

                        case pygame.K_2:
                            circle.radius = min(circle.radius + 10, 130)
                            bar.modify_value(10)

                        case pygame.K_3:
                            bar.modify_value(-10, set_bottom=True)
                            print(f'{bar.display_range} -> {bar.target_range}')

                        case pygame.K_4:
                            bar.modify_value(10, set_bottom=True)
                            print(f'{bar.display_range} -> {bar.target_range}')

                        # case pygame.K_5:

                        # case pygame.K_6:

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

                        # case pygame.K_9:

                        case pygame.K_i:
                            print(f'block_pos: {moving_block.x}, {moving_block.y}')

                case pygame.MOUSEBUTTONDOWN:
                    move_block_button.check_collision()
                    fill_block_button.check_collision()

        update_window()


if __name__ == "__main__":
    main()
