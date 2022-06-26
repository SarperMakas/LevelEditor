import pygame
import numpy
from tkinter import *
from tkinter import filedialog as fd
import numpy as np
import pickle


class LevelEditor:
    """Level Editor"""

    def __init__(self):
        pygame.init()

        # get screen info
        self.screen = pygame.display.set_mode()
        self.width, self.height = self.screen.get_size()
        pygame.display.toggle_fullscreen()

        self.run = True

        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.gray = (120, 120, 120)

        self.linesSize = 35

        self.drawLines = False

        # poses of the screen
        self.screenX = 0
        self.screenY = 0

        self.images = []

        cellSize = 35
        self.partRect = pygame.rect.Rect((self.width - cellSize * 6 - 24 - 12, 33),
                                         (cellSize * 6 + 14, self.height - 59))
        self.isMouseClicked = False
        self.selectedImage = None

        self.array = np.empty((self.width//self.linesSize, self.height//self.linesSize), dtype=pygame.Surface)
        self.partMove = 0

        self.screenx = 0
        self.screeny = 0

        self.transparentC1 = (200, 153, 153)
        self.transparentC2 = (153, 102, 102)
        self.isBgTransparent = False



    def addImageToPart(self):
        """Now we will add a image to the selection part"""
        try:
            Tk().withdraw()
            filename = fd.askopenfilename(title="Select Image", filetypes=(("PNG", "*.png"), (".JPG", "*.png")))
            self.images.append(pygame.transform.scale(pygame.image.load(filename), (35, 35)))
        except:
            pass

    def addImagesToPart(self):
        """Now we will add a images to the selection part"""
        try:
            Tk().withdraw()
            filenames = fd.askopenfilenames(title="Select Image", filetypes=(("PNG", "*.png"), (".JPG", "*.png")))
            for filename in filenames:
                self.images.append(pygame.transform.scale(pygame.image.load(filename), (35, 35)))
        except:
            pass

    def saveAsPNG(self):
        """Save project as png"""
        size = 35
        img = pygame.Surface((self.array.shape[0]*size, self.array.shape[1]*size), pygame.SRCALPHA).convert_alpha()
        for r in range(self.array.shape[0]):
            for c in range(self.array.shape[1]):
                if type(self.array[r][c]) == pygame.Surface:
                    img.blit(pygame.transform.scale(self.array[r][c], (size, size)), (r*size, c*size))

        pygame.image.save(img, fd.asksaveasfilename(title="Save As Image"))

    def save(self):
        """Save project as csv"""

        Tk().withdraw()
        filename = open(fd.asksaveasfilename(title="Save File"), "wb")
        try:
            arr = np.empty(self.array.shape, dtype=str).tolist()

            for r in range(self.array.shape[0]):
                for c in range(self.array.shape[1]):
                    if type(self.array[r][c]) == pygame.Surface:
                        print(pygame.image.tostring(self.array[r][c], "RGB"))
                        arr[r][c] = pygame.image.tostring(self.array[r][c], "RGB")
                    else:
                        arr[r][c] = ""
            pickle.dump(arr, filename)
        except:
            pass

    def open(self):
        """Make new project from csv folder"""
        Tk().withdraw()
        filename = open(fd.askopenfilename(title="Select Data"), "rb")
        if filename != "":
            arr = pickle.load(filename)
            self.array = np.empty((len(arr), len(arr[0])), dtype=pygame.Surface)
            for r in range(len(arr)):
                for c in range(len(arr[0])):
                    if arr[r][c] == "":
                        self.array[r][c] = ""
                    else:
                        self.array[r][c] = pygame.image.fromstring(arr[r][c], (self.linesSize, self.linesSize), "RGB")


    def event(self):
        """Event loop"""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False


            keys = pygame.key.get_pressed()
            ctrl = (keys[pygame.K_RCTRL] or keys[pygame.K_LCTRL])
            shift = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
            x, y = pygame.mouse.get_pos()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.isBgTransparent = not self.isBgTransparent
            # quit app
            if keys[pygame.K_ESCAPE] == 1:
                self.run = False
            if ctrl == 1 and keys[pygame.K_l] == 1:
                self.drawLines = not self.drawLines
            # check adding image
            elif ctrl == 1 and shift and keys[pygame.K_a] == 1:
                self.addImagesToPart()  # add multiple images
            elif ctrl == 1 and keys[pygame.K_a] == 1:
                self.addImageToPart()  # add one image
            elif ctrl == 1 and shift and keys[pygame.K_s] == 1:
                self.saveAsPNG()
            elif ctrl == 1 and keys[pygame.K_s] == 1:
                self.save()
            elif ctrl == 1 and keys[pygame.K_o] == 1:
                self.open()

            # move screen
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.screenx -= 1
                self.array = np.vstack((self.array, np.empty((1, self.array.shape[1]))))
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.screenx += 1
                self.array = np.vstack((np.empty((1, self.array.shape[1])), self.array))
            elif keys[pygame.K_w] or keys[pygame.K_UP]:
                self.screeny += 1
                self.array = np.hstack((np.empty((self.array.shape[0], 1)), self.array))
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.screeny -= 1
                self.array = np.hstack((self.array, np.empty((self.array.shape[0], 1))))

            self.screenX = self.screenx*self.linesSize
            self.screenY = self.screeny * self.linesSize

            if not (self.partRect.left < x < self.partRect.right and self.partRect.top < y < self.partRect.bottom):
                leftClick = pygame.mouse.get_pressed(3)[0]
                rightClick = pygame.mouse.get_pressed(3)[2]
                # draw screen
                if x // self.linesSize == 0: xPos = 0
                else: xPos = x // self.linesSize - self.screenX // self.linesSize + 1
                if y // self.linesSize == 0: yPos = 0
                else: yPos = y // self.linesSize - self.screenY // self.linesSize

                if self.selectedImage is not None and leftClick:
                    self.array[xPos][yPos] = self.selectedImage
                elif rightClick:
                    self.array[xPos][yPos] = None

            # cmake cell sizes bigger or smaller
            if event.type == pygame.MOUSEBUTTONDOWN:

                self.isMouseClicked = True
                isInPart = (self.partRect.left < x < self.partRect.right) and (self.partRect.top < y < self.partRect.bottom)

                # change sizes of the lines
                if event.button == 4 and isInPart is False:
                    self.linesSize += 1
                    self.screenX += 1
                    self.screenY += 1
                elif event.button == 4 and isInPart is True and self.images != []:
                    self.partMove += 35

                if event.button == 5 and isInPart is False:
                    self.linesSize -= 1
                    self.screenX -= 1
                    self.screenY -= 1
                elif event.button == 5 and isInPart is True  and self.images != []:
                    self.partMove -= 35

                # makes linesSize, x and y to fix
                if self.linesSize < 2:
                    self.linesSize = 2
                    self.screenX = -33
                    self.screenY = -33

            elif event.type == pygame.MOUSEBUTTONUP:
                self.isMouseClicked = False

    def main(self):
        """Main Function"""
        while self.run:
            self.event()
            self.draw()

    def createLines(self):
        """Create Lines"""
        # create vertical lines
        for x in range(-abs(self.screenX), self.width-self.screenX, self.linesSize):
            pygame.draw.line(self.screen, self.gray, (x+self.screenX, 0), (x+self.screenX, self.height))
            # add column
            if x/self.linesSize > self.array.shape[0]:
                while x/self.linesSize != self.array.shape[0]:
                    self.array = np.vstack((self.array, np.empty((1, self.array.shape[1]))))

        # create horizontal lines
        for y in range(-abs(self.screenY), self.height+abs(self.screenY), self.linesSize):
            pygame.draw.line(self.screen, self.gray, (0, y), (self.width, y))
            # add row
            if y/self.linesSize > self.array.shape[1]:
                while y/self.linesSize != self.array.shape[1]:
                    self.array = np.hstack((self.array, np.empty((self.array.shape[0], 1))))

    def drawSqOfMouse(self):
        """Draw sq of mouse"""
        x, y = pygame.mouse.get_pos()
        if not (self.partRect.left < x < self.partRect.right and self.partRect.top < y < self.partRect.bottom):

            if self.selectedImage is not None:
                img = pygame.transform.scale(self.selectedImage, (self.linesSize, self.linesSize))
                self.screen.blit(img, (int(x // self.linesSize) * self.linesSize, int(y // self.linesSize) * self.linesSize))

            # create rect
            rect = pygame.rect.Rect(
                (int(x // self.linesSize) * self.linesSize, int(y // self.linesSize) * self.linesSize),
                (self.linesSize, self.linesSize))
            # draw rects
            pygame.draw.rect(self.screen, self.gray, rect, 2)

    def drawImagesPart(self):
        """We need a part for select images"""
        cellSize = 35
        pygame.draw.rect(self.screen, self.gray, self.partRect)

        row = 0
        col = 0
        for image in self.images:
            # draw image
            rect = image.get_rect(topleft=(self.partRect.left+col*cellSize+2*(col+1), self.partRect.top+row*cellSize+2*(row+1)+self.partMove))

            if self.partRect.left < rect.x < self.partRect.right and self.partRect.top < rect.y < self.partRect.bottom:
                self.screen.blit(image, rect)
            col += 1

            # check click of the image
            x, y = pygame.mouse.get_pos()
            if rect.left <= x <= rect.right and rect.top <= y <= rect.bottom and self.isMouseClicked is True:
                self.selectedImage = image

            # go from next col
            if col == 6:
                col = 0
                row += 1

    def drawTile(self):
        """Draw all the tiles """
        for r in range(self.array.shape[1]):
            for c in range(self.array.shape[0]):
                if type(self.array[c][r]) == pygame.Surface:
                    img = pygame.transform.scale(self.array[c][r], (self.linesSize, self.linesSize))  # get img from array
                    rect = img.get_rect(topleft=(c * self.linesSize+self.screenX-self.linesSize, r * self.linesSize+self.screenY))  # create rect
                    self.screen.blit(img, rect)

    def drawTransparentBg(self):
        """Draw transparent bg"""
        if self.isBgTransparent is True:
            size = 5
            first = True
            for x in range(0, self.width, size):
                for y in range(0, self.height, size):
                    rect = pygame.rect.Rect((x, y), (size, size))
                    # draw
                    if first is True:
                        pygame.draw.rect(self.screen, self.transparentC1, rect)
                    elif first is False:
                        pygame.draw.rect(self.screen, self.transparentC2, rect)
                    first = not first  # change first
                first = not first  # change first

    def draw(self):
        """Draw"""
        if self.drawLines is False: self.createLines()
        self.screen.fill(self.black)
        self.drawTransparentBg()
        self.drawTile()
        self.drawSqOfMouse()
        if self.drawLines is True: self.createLines()
        self.drawImagesPart()
        pygame.display.flip()


if __name__ == '__main__':
    LevelEditor().main()