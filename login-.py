from pynput.mouse import Controller, Button

mouse = Controller()




mouse.position = (1435, 573)
mouse.press(Button.left)
mouse.move(100, 0)
mouse.release(Button.left)

