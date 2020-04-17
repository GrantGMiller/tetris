import time
from tkinter import Canvas, Tk
from threading import Timer
import random

COLORS = [
    'red',
    'orange',
    'yellow',
    'green',
    'blue',
    'purple',
    'white',
    'grey',
]


class Game:
    BLOCK_SIZE = 40

    def __init__(self, cWidth, cHeight):
        self.root = Tk()
        self.root.bind('<Key>', self.HandleKeyboard)
        self._canvas = Canvas(self.root, width=cWidth, height=cHeight, background='black')
        self._canvas.pack()

        self.width = int(cWidth / self.BLOCK_SIZE)
        self.height = int(cHeight / self.BLOCK_SIZE)
        print('Game.width=', self.width)
        print('Game.height=', self.height)

        self.blocks = []
        self._shape = None  # the current falling shape

        self.speed = 0.1

    def HandleKeyboard(self, event):
        print('HandleKeyboard(', event)
        if self._shape:
            if event.keysym.lower() == 'left':
                shouldMoveLeft = True
                for block in self._shape.blocks:
                    if block.x == 0 or (block.below and block.below.shape != block.shape):
                        shouldMoveLeft = False
                        break
                if shouldMoveLeft:
                    for block in self._shape.blocks:
                        block.x -= 1

            elif event.keysym.lower() == 'right':
                shouldMoveRight = True
                for block in self._shape.blocks:
                    if block.x >= self.width - 1 or (block.below and block.below.shape != block.shape):
                        shouldMoveRight = False
                        break
                if shouldMoveRight:
                    for block in self._shape.blocks:
                        block.x += 1

            elif event.keysym.lower() == 'down':
                while not self._shape.ShouldStop():
                    self._shape.Drop()

    def AddBlock(self, x, y, color):
        block = Block(game, x, y, color)
        ID = self._canvas.create_rectangle(
            *block.coords,
            fill=block.color
        )
        block.ID = ID
        self.blocks.append(block)
        print('self.blocks=', self.blocks)
        return block

    def NewShape(self):
        shapeMap = [
            [1, random.randint(0, 1)],
            [random.randint(0, 1), random.randint(0, 1)],
        ]
        startingX = self.width / 2
        startingY = 0
        color = random.choice(COLORS)
        blocks = []
        if shapeMap[0][0]:
            blocks.append(self.AddBlock(startingX, startingY, color))
        if shapeMap[0][1]:
            blocks.append(self.AddBlock(startingX + 1, startingY, color))
        if shapeMap[1][0]:
            blocks.append(self.AddBlock(startingX, startingY + 1, color))
        if shapeMap[1][1]:
            blocks.append(self.AddBlock(startingX + 1, startingY + 1, color))
        print('blocks=', blocks)
        shape = Shape(blocks=blocks)
        self._shape = shape

    def BlockAt(self, x, y):
        print('BlockAt(', x, y)
        print('self.blocks=', self.blocks)
        ret = None
        for block in self.blocks:
            if block.x == x and block.y == y:
                ret = block
                break
        print('return', ret)
        return ret

    def DeleteRows(self):
        # check for a row of blocks
        for rowIndex in range(0, self.height):
            blocksInThisRow = []
            for colIndex in range(0, self.width):

                thisBlock = self.BlockAt(x=colIndex, y=rowIndex)

                blocksInThisRow.append(thisBlock)
                if thisBlock is None:
                    break  # check the next row
                    pass
                else:
                    print('thisBlock=', thisBlock)
            else:
                # this row is full of blocks, remove them

                for block in blocksInThisRow:
                    self.blocks.remove(block)
                    self._canvas.delete(block.ID)

    def Update(self):
        print('Update')
        # move blocks down
        if self._shape:
            if self._shape.ShouldStop():
                self.NewShape()
                self.speed *= 0.99
                Timer(self.speed, self.DeleteRows).start()

            self._shape.Drop()

        # draw all the blocks
        for block in self.blocks:
            self._canvas.coords(block.ID, block.coords)


class Block:  # a 1x1 square
    def __init__(self, host, x, y, color):
        self.host = host
        self.x = x
        self.y = y
        self.color = color
        self.shape = None  # the parent shape
        # self.below = None # the block below, None means no block below

    @property
    def coords(self):
        return (
            self.x * self.host.BLOCK_SIZE,
            self.y * self.host.BLOCK_SIZE,
            self.x * self.host.BLOCK_SIZE + self.host.BLOCK_SIZE,
            self.y * self.host.BLOCK_SIZE + self.host.BLOCK_SIZE,
        )

    @property
    def below(self):
        for b in self.host.blocks:
            if b.x == self.x and b.y == self.y + 1:
                return b
        return None

    def Drop(self):
        print('Block.Drop()')
        self.y += 1

    def __str__(self):
        return f'<Block x={self.x}, y={self.y}, color={self.color}>'

    def __repr__(self):
        return str(self)


class Shape:  # hold a collection of Block objecs
    def __init__(self, blocks):
        self.blocks = blocks
        for b in self.blocks:
            b.shape = self

    def Drop(self):
        print('Shape.Drop()')
        for block in self.blocks:
            block.Drop()

    def ShouldStop(self):
        for block in self.blocks:
            if block.below:
                if block.below.shape != self:
                    return True
            elif block.y >= block.host.height - 1:
                return True

        return False


game = Game(400, 800)
game.NewShape()


def Loop():
    while True:
        game.Update()
        time.sleep(0.1)


Timer(0, Loop).start()
game.root.mainloop()
