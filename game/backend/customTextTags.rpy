init python:
    import random
    import math

    class DisplaytxtStyles(): #this dictionaries help us to maintain what styles we want to apply and help us
        custom_tags = ["st", "rt", "bt", "move" "xpld","xpldH","glitch", "Grd", "Grd2"]
        accepted_tags = ["", "b", "s", "u", "i", "color", "alpha", "font", "size", "outlineC", "plain"]
        custom_cancel_tags = ["/" + tag for tag in custom_tags]
        cancel_tags = ["/" + tag for tag in accepted_tags]
        def __init__(self):
            self.tags = {}

        def add_tags(self, char):
            tag, _, value = char.partition("=") # Separate the tag and its info
            # Add tag to dictionary if we accept it
            if tag in self.accepted_tags or tag in self.custom_tags:
                if value == "":
                    self.tags[tag] = True
                else:
                    self.tags[tag] = value
                return True
            # Remove mark tag as cleared if should no longer apply it
            if tag in self.cancel_tags or tag in self.custom_cancel_tags:
                tag = tag.replace("/", "")
                self.tags.pop(tag)
                return True
            return False#this makes other tags pass if we got other

        #applynig all styles to the string
        def apply_style(self, char):
            new_string = ""
            # Go through and apply all the tags
            new_string += self.start_tags()
            # Add the character in the middle
            new_string += char
            # Now close all the tags we opened
            new_string += self.end_tags()
            return new_string

        def start_tags(self):
            new_string = ""
            # Go through the custom tags
            for tag in self.custom_tags:
                if tag in self.tags:
                    if self.tags[tag] == True:
                        new_string += "{" + tag + "}"
                    else:
                        new_string += "{" + tag + "=" +self.tags[tag] + "}"
            # Go through the standard tags
            for tag in self.accepted_tags:
                if tag in self.tags:
                    if self.tags[tag] == True:
                        new_string += "{" + tag + "}"
                    else:
                        new_string += "{" + tag + "=" +self.tags[tag] + "}"
            return new_string

        def end_tags(self):
            new_string = ""
            # The only tags we are required to end are any custom text tags.
            # And should also end them in the reverse order they were applied.
            reversed_cancels = [tag for tag in self.custom_cancel_tags]
            reversed_cancels.reverse()
            for tag in reversed_cancels:
                temp = tag.replace("/", "")
                if temp in self.tags:
                    new_string += "{" + tag + "}"
            return new_string

    def color_gradient(color_1, color_2, range, index):
        if index == 0:
            return color_1
        if range == index:
            return color_2
        start_col = Color(color_1)
        end_col = Color(color_2)
        return start_col.interpolate(end_col, index * 1.0/range).hexcode

    '''
    Here are all the new text classes
    '''

    class ShakeText(renpy.Displayable):
        def __init__(self, child, square = 2, **kwargs):
            super(ShakeText, self).__init__(**kwargs)

            self.child = child
            self.square = square #this define the size of the movement space for the random motion of the text

        def render(self, width, height, st, at):
            #this applies the random motion to the offset of the text's render
            xoff = (random.random()-.5) * float(self.square)
            yoff = (random.random()-.5) * float(self.square)

            child_render = renpy.render(self.child, width, height, st, at)
            self.width, self.height = child_render.get_size()
            render = renpy.Render(self.width, self.height)

            render.subpixel_blit(child_render, (xoff, yoff))
            renpy.redraw (self, 0)
            return render

        def visit(self):
            return [self.child]

    class RotationText(renpy.Displayable):
        def __init__(self, child, speed=300, **kwargs):
            super(RotationText, self).__init__(**kwargs)

            self.child = child
            self.speed = speed #the speed of the rotation

        def render(self, width, height, st, at):

            theta = math.radians(st * float(self.speed))
            t = Transform(child=self.child, rotate=s*float(self.speed))
            child_render = renpy.render(t, width, height/2, st, at)

            self.width, self.height = child_render.get_size()
            render = renpy.Render(self.width, self.height/2)

            render.blit(child_render, (0,0))
            renpy.redraw(self, 0)
            return render

        def visit(self):
            return[self.child]

    class BounceText(renpy.Displayable):
        def __init__(self, child, char_offset, amp=20, period=4.0, speed = 1.0, **kwargs):

            super(BounceText, self).__init__(**kwargs) 

            self.child = child
            self.amp = amp # The amplitude of the sine wave
            self.char_offset = char_offset # The offset into the sine wave
            self.period = period # Affects the distance between peaks in the wave.
            self.speed = speed   # Affects how fast our wave moves as a function of time.

        def render(self, width, height, st, at):

            curr_height = math.sin(self.period*((st * self.speed)+(float(self.char_offset) * -.1))) * float(self.amp)

            ####  A Transform can be used for several effects   ####
            # t = Transform(child=self.child,  alpha = curr_height)


            child_render = renpy.render(self.child, width, height, st, at)

            self.width, self.height = child_render.get_size()
            render = renpy.Render(self.width, self.height)

            # This will position our child's render. Replacing our need for an offset Transform
            render.subpixel_blit(child_render, (0, curr_height))

            renpy.redraw(self, 0) # This lets it know to redraw this indefinitely
            return render

        def event(self, ev, x, y, st):
            return self.child.event(ev, x, y, st)

        def visit(self):
            return [ self.child ]

    class ExplodeText(renpy.Displayable):
        def __init__(self, child, timer=2, **kwargs):
            super(ExplodeText, self).__init__(**kwargs)
            self.child = child
            self.curr_x = 0
            self.curr_y = 0
            self.timer = timer
            self.gravity = 300
            self.v0_x = (renpy.random.random() - 0.5) * 800.0
            self.v0_y = renpy.random.random() * -700.0

        def render(self, width, height, st, at):
            curr_x = 0
            curr_y = 0
            if st > self.timer:
                st -= self.timer
                curr_x = self.v0_x * st
                curr_y = self.v0_y * st + self.gravity * pow(st,2)
            child_render = renpy.render(self.child, width, height, st, at)

            self.width, self.height = child_render.get_size()
            render = renpy.Render(self.width, self.height)

            # This will position our child's render. Replacing our need for an offset Transform
            render.subpixel_blit(child_render, (curr_x, curr_y))
            if curr_y < 2000:
                renpy.redraw(self, 0) # This lets it know to redraw this indefinitely
            return render

        def visit(self):
            return [ self.child ]

    class ExplodeHalfText(renpy.Displayable):
        def __init__(self, child, length, id, explode_point, timer=2, **kwargs):
            super(ExplodeHalfText, self).__init__(**kwargs)
            self.child = child
            self.curr_x = 0
            self.curr_y = 0
            self.timer = timer
            self.length = length
            self.id = id
            self.gravity = 300
            self.v0_x = (id - explode_point) * 100
            self.v0_y = math.cos((id - explode_point) * math.pi * (1.0/(2.0 * length))) * -900
            # self.v0_y = (-abs(id - explode_point) + length) * -35

        def render(self, width, height, st, at):
            curr_x = 0
            curr_y = 0
            if st > self.timer:
                st -= self.timer
                curr_x = self.v0_x * st
                curr_y = self.v0_y * st + self.gravity * pow(st,2)
            child_render = renpy.render(self.child, width, height, st, at)

            self.width, self.height = child_render.get_size()
            render = renpy.Render(self.width, self.height)

            # This will position our child's render. Replacing our need for an offset Transform
            render.subpixel_blit(child_render, (curr_x, curr_y))
            if curr_y < 2000:
                renpy.redraw(self, 0) # This lets it know to redraw this indefinitely
            return render

        def visit(self):
            return [ self.child ]

    class GlitchText(renpy.Displayable):
        def __init__(self, child, amount, **kwargs):
            super(GlitchText, self).__init__(**kwargs)
            if isinstance(child, (str, unicode)):
                self.child = Text(child)
            else:
                self.child = child
            self.amount = amount

        def render(self, width, height, st, at):
            child_render = renpy.render(self.child, width, height, st, at)

            self.width, self.height = child_render.get_size()
            render = renpy.Render(self.width, self.height)
            y = 0
            while y < self.height:
                glitch_occurs = renpy.random.random() * 100 < self.amount
                if glitch_occurs:
                    curr_height = renpy.random.randint(-10,10)
                else:
                    curr_height = renpy.random.randint(0,10)
                curr_offset = renpy.random.randint(-10,10)
                curr_surface = child_render.subsurface((0,y,self.width,curr_height))
                if glitch_occurs:
                    render.subpixel_blit(curr_surface, (curr_offset, y))
                else:
                    render.subpixel_blit(curr_surface, (0, y))
                if curr_height > 0:
                    y += curr_height
                else:
                    y -= curr_height
            renpy.redraw(self,0)
            return render

    class GradientText(renpy.Displayable):
        def __init__(self, char, col_list, id, list_end, **kwargs):

            super(GradientText, self).__init__(**kwargs)

            self.char = char
            self.child = Text(char)
            self.col_list = col_list # Calling it grad_list for gradient might be more appropriate.
            self.id = id
            self.list_end = list_end
            # Figure out which gradient we are in
            for i, element in enumerate(col_list):
                if self.id < element[2]:
                    self.curr_grad = i
                    break
            # Determine the current range (for color_gradient func later)
            if self.curr_grad is 0:
                self.curr_range = self.col_list[0][2]
            else:
                self.curr_range = self.col_list[self.curr_grad][2] - self.col_list[self.curr_grad - 1][2]

        def render(self, width, height, st, at):
            my_style = DisptxtStyles()
            # Get the color to apply to the text
            if self.curr_grad == 0:
                my_style.add_tags("color=" + color_gradient(self.col_list[self.curr_grad][0], self.col_list[self.curr_grad][1], self.curr_range, self.id))
            else: # color_gradient() expects id to be within the range given. So must reduce to that if exceeding it.
                my_style.add_tags("color=" + color_gradient(self.col_list[self.curr_grad][0], self.col_list[self.curr_grad][1], self.curr_range, self.id - self.col_list[self.curr_grad - 1][2]))

            # Usual retrieval and drawing of child render
            self.child.set_text(my_style.apply_style(self.char))
            child_render = renpy.render(self.child, width, height, st, at)
            self.width, self.height = child_render.get_size()
            render = renpy.Render(self.width, self.height)
            render.subpixel_blit(child_render, (0, 0))
            renpy.redraw(self, 0)

            # Iterate id for next render
            self.id += 1
            # If we are at the end of the range update gradient
            if self.id > self.col_list[self.curr_grad][2]:
                self.curr_grad += 1
                # If at the end of our color list, reset back to 0
                if self.curr_grad == self.list_end:
                    self.curr_grad = 0
                    self.id = 0
                    self.curr_range = self.col_list[0][2]
                # Otherwise just update the range
                else:
                    self.curr_range = self.col_list[self.curr_grad][2] - self.col_list[self.curr_grad - 1][2]

            return render

        def visit(self):
            return [ self.child ]



    def shake_tag(tag, argument, contents):
        new_list = [ ]
        if argument == "":
            argument = 5
        my_style = DisplaytxtStyles()
        for kind,text in contents:
            if kind == renpy.TEXT_TEXT:
                for char in text:
                    char_text = Text(my_style.apply_style(char))
                    char_disp = ShakeText(char_text, argument)
                    new_list.append((renpy.TEXT_DISPLAYABLE, char_disp))
            elif kind == renpy.TEXT_TAG:
                if text.find("image") != -1:
                    tag, _, value = text.partition("=")
                    my_img = renpy.displayable(value)
                    img_disp = ShakeText(my_img, argument)
                    new_list.append((renpy.TEXT_DISPLAYABLE, img_disp))
                elif not my_style.add_tags(text):
                    new_list.append((kind, text))
            else:
                new_list.append((kind,text))

        return new_list

    def rotate_tag(tag, argument, contents):
        new_list = [ ]
        # Argument here will reprsent the desired speed of the rotation.
        if argument == "":
            argument = 400
        else:
            argument = int(argument)
        my_style = DisplaytxtStyles()
        for kind,text in contents:
            if kind == renpy.TEXT_TEXT:
                for char in text:
                    char_text = Text(my_style.apply_style(char))
                    char_disp = RotationText(char_text, argument)
                    new_list.append((renpy.TEXT_DISPLAYABLE, char_disp))
            elif kind == renpy.TEXT_TAG:
                if text.find("image") != -1:
                    tag, _, value = text.partition("=")
                    my_img = renpy.displayable(value)
                    img_disp = RotationText(my_img, argument)
                    new_list.append((renpy.TEXT_DISPLAYABLE, img_disp))
                elif not my_style.add_tags(text):
                    new_list.append((kind, text))
            else:
                new_list.append((kind,text))

        return new_list    

    def bounce_tag(tag, argument, contents):
        new_list = [ ] # The list we will be appending our displayables into
        amp, period, speed = 20, 4.0, 1.0
        if argument == "": # If the argument received is blank, insert a default value
            amp = 20
        else:
            argument = argument.split('-')
            if len(argument) == 1 and argument[0][0].isdigit(): # Default behavior to ensure backward compatibility
                amp = int(argument[0])
            else:
                for arg in argument:
                    if arg[0] == 'a':
                        amp = int(arg[1:])
                    elif arg[0] == 'p':
                        period = float(arg[1:])
                    elif arg[0] == 's':
                        speed = float(arg[1:])

        char_offset = 0
        my_style = DisplaytxtStyles()
        for kind,text in contents:
            if kind == renpy.TEXT_TEXT:
                for char in text:
                    char_text = Text(my_style.apply_style(char))
                    char_disp = BounceText(char_text, char_offset, amp=amp, period=period, speed=speed)
                    new_list.append((renpy.TEXT_DISPLAYABLE, char_disp)) 
                    char_offset += 1
            elif kind == renpy.TEXT_TAG:
                if text.find("image") != -1:
                    tag, _, value = text.partition("=")
                    my_img = renpy.displayable(value)
                    img_disp = BounceText(my_img, char_offset, amp=amp, period=period, speed=speed)
                    new_list.append((renpy.TEXT_DISPLAYABLE, img_disp))
                    char_offset += 1
                elif not my_style.add_tags(text):
                    new_list.append((kind, text))
            elif kind == renpy.TEXT_DISPLAYABLE:
                char_disp = BounceText(text, char_offset, amp=amp, period=period, speed=speed)
                new_list.append((renpy.TEXT_DISPLAYABLE, char_disp))
                char_offset += 1
            else: 
                new_list.append((kind,text))

        return new_list
    def move_tag(tag, argument, contents):
        new_list = [ ]
        my_style = DisplaytxtStyles()
        for kind,text in contents:
            if kind == renpy.TEXT_TEXT:
                for char in text:
                    char_text = Text(my_style.apply_style(char))
                    char_disp = MoveText(char_text)
                    new_list.append((renpy.TEXT_DISPLAYABLE, char_disp))
            elif kind == renpy.TEXT_TAG:
                if text.find("image") != -1:
                    tag, _, value = text.partition("=")
                    my_img = renpy.displayable(value)
                    img_disp = MoveText(my_img)
                    new_list.append((renpy.TEXT_DISPLAYABLE, img_disp))
                elif not my_style.add_tags(text):
                    new_list.append((kind, text))
            else:
                new_list.append((kind,text))
        return new_list

    def explode_tag(tag, argument, contents):
        new_list = [ ]
        if argument == "":
            argument = 2
        else:
            argument = float(argument)
        my_style = DisplaytxtStyles()
        for kind,text in contents:
            if kind == renpy.TEXT_TEXT:
                for char in text:
                    char_text = Text(my_style.apply_style(char))
                    char_disp = ExplodeText(char_text, argument)
                    new_list.append((renpy.TEXT_DISPLAYABLE, char_disp))
            elif kind == renpy.TEXT_TAG:
                if text.find("image") != -1:
                    tag, _, value = text.partition("=")
                    my_img = renpy.displayable(value)
                    img_disp = ExplodeText(my_img, argument)
                    new_list.append((renpy.TEXT_DISPLAYABLE, img_disp))
                elif not my_style.add_tags(text):
                    new_list.append((kind, text))
            else:
                new_list.append((kind,text))
        return new_list

    def explodeHalf_tag(tag, argument, contents):
        new_list = [ ]
        if argument == "":
            time_arg = 2
            center_arg = -1
        else:
            center_arg, _, time_arg = argument.partition("-")
            time_arg = float(time_arg)
            center_arg = int(center_arg)
        my_style = DisplaytxtStyles()
        total_length = 0
        for kind,text in contents:
            if kind == renpy.TEXT_TEXT:
                total_length += len(text)
            elif kind == renpy.TEXT_TAG:
                if text.find("image") != -1:
                    curr_id += 1
        curr_id = 0
        if center_arg == -1:
            center_arg = total_length / 2
        for kind,text in contents:
            if kind == renpy.TEXT_TEXT:
                for char in text:
                    char_text = Text(my_style.apply_style(char))
                    char_disp = ExplodeHalfText(char_text, total_length, curr_id, center_arg, time_arg)
                    new_list.append((renpy.TEXT_DISPLAYABLE, char_disp))
                    curr_id += 1
            elif kind == renpy.TEXT_TAG:
                if text.find("image") != -1:
                    tag, _, value = text.partition("=")
                    my_img = renpy.displayable(value)
                    img_disp = ExplodeHalfText(my_img, total_length, curr_id, center_arg, time_arg)
                    new_list.append((renpy.TEXT_DISPLAYABLE, img_disp))
                    curr_id += 1
                elif not my_style.add_tags(text):
                    new_list.append((kind, text))
            else:
                new_list.append((kind,text))
        return new_list

    def glitch_tag(tag, argument, contents):
        new_list = [ ]
        if argument == "":
            argument = 10.0
        else:
            argument = float(argument)
        my_style = DisplaytxtStyles()
        for kind,text in contents:
            if kind == renpy.TEXT_TEXT:
                char_disp = GlitchText(my_style.apply_style(text), argument)
                new_list.append((renpy.TEXT_DISPLAYABLE, char_disp))
            elif kind == renpy.TEXT_TAG:
                if text.find("image") != -1:
                    tag, _, value = text.partition("=")
                    my_img = renpy.displayable(value)
                    img_disp = GlitchText(my_img, argument)
                    new_list.append((renpy.TEXT_DISPLAYABLE, img_disp))
                elif not my_style.add_tags(text):
                    new_list.append((kind, text))
            else:
                new_list.append((kind,text))
        return new_list



        new_list = [ ]
        if argument == "":
            return
        else: # Note: All arguments must be supplied
            arg_num, _, argument = argument.partition('-') # Number of gradients to read
        arg_num = int(arg_num)
        # Get all arguments
        col_list = []
        end_num = 0
        for i in range(arg_num):
            col_1, _, argument = argument.partition('-')   # Color 1
            col_2, _, argument = argument.partition('-')   # Color 2
            end_num_arg, _, argument = argument.partition('-') # Gradient Length
            end_num += int(end_num_arg) # Converts gradient length into it's ending position
            col_list.append((col_1, col_2, end_num))

        my_index = 0
        my_style = DisplaytxtStyles()
        for kind,text in contents:
            if kind == renpy.TEXT_TEXT:
                for char in text:
                    if char == ' ':
                        new_list.append((renpy.TEXT_TEXT, ' '))
                        continue
                    char_disp = GradientText(my_style.apply_style(char), col_list, my_index, arg_num)
                    new_list.append((renpy.TEXT_DISPLAYABLE, char_disp))
                    my_index += 1
                    # Wrap around if reached the end of the gradient list.
                    if my_index >= col_list[arg_num-1][2]:
                        my_index = 0
            elif kind == renpy.TEXT_TAG:
                if not my_style.add_tags(text):
                    new_list.append((kind, text))
            else:
                new_list.append((kind,text))
        return new_list

    def gradient_tag(tag, argument, contents):
        new_list = [ ]
        if argument == "":
            return
        else: # Note: all arguments must be supplied
            col_1, _, col_2 = argument.partition('-')
        # Get a count of all the letters we will be applying colors to
        count = 0
        for kind,text in contents:
            if kind == renpy.TEXT_TEXT:
                for char in text:
                    if char == ' ':
                        continue
                    count += 1
        count -= 1
        my_index = 0
        my_style = DisplaytxtStyles()
        for kind,text in contents:
            if kind == renpy.TEXT_TEXT:
                for char in text:
                    if char == ' ':
                        new_list.append((renpy.TEXT_TEXT, ' '))
                        continue
                    new_list.append((renpy.TEXT_TAG, "color=" + color_gradient(col_1, col_2, count, my_index)))
                    new_list.append((renpy.TEXT_TEXT, char))
                    new_list.append((renpy.TEXT_TAG, "/color"))
                    my_index += 1
            elif kind == renpy.TEXT_TAG:
                if not my_style.add_tags(text):
                    new_list.append((kind, text))
            else:
                new_list.append((kind,text))
        return new_list


    def gradient2_tag(tag, argument, contents):
        new_list = [ ]
        if argument == "":
            return
        else: # Note: All arguments must be supplied
            arg_num, _, argument = argument.partition('-') # Number of gradients to read
        arg_num = int(arg_num)
        # Get all arguments
        col_list = []
        end_num = 0
        for i in range(arg_num):
            col_1, _, argument = argument.partition('-')   # Color 1
            col_2, _, argument = argument.partition('-')   # Color 2
            end_num_arg, _, argument = argument.partition('-') # Gradient Length
            end_num += int(end_num_arg) # Converts gradient length into it's ending position
            col_list.append((col_1, col_2, end_num))

        my_index = 0
        my_style = DisplaytxtStyles()
        for kind,text in contents:
            if kind == renpy.TEXT_TEXT:
                for char in text:
                    if char == ' ':
                        new_list.append((renpy.TEXT_TEXT, ' '))
                        continue
                    char_disp = GradientText(my_style.apply_style(char), col_list, my_index, arg_num)
                    new_list.append((renpy.TEXT_DISPLAYABLE, char_disp))
                    my_index += 1
                    # Wrap around if reached the end of the gradient list.
                    if my_index >= col_list[arg_num-1][2]:
                        my_index = 0
            elif kind == renpy.TEXT_TAG:
                if not my_style.add_tags(text):
                    new_list.append((kind, text))
            else:
                new_list.append((kind,text))
        return new_list

    #the new text tags
    config.custom_text_tags["st"] = shake_tag
    config.custom_text_tags["rt"] = rotate_tag
    config.custom_text_tags["bt"] = bounce_tag
    config.custom_text_tags["move"] = move_tag
    config.custom_text_tags["xpld"] = explode_tag
    config.custom_text_tags["xpldH"] = explodeHalf_tag
    config.custom_text_tags["glitch"] = glitch_tag
    config.custom_text_tags["Grd"] = gradient_tag
    config.custom_text_tags["Grd2"] = gradient2_tag