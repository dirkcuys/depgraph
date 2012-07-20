import cairo

class SimpleSVG:
    def __init__(self, filename):
        #self.surface = cairo.SVGSurface(filename, 16384, 8192)
        self.surface = cairo.SVGSurface(filename, 5000, 5000)
        self.context = cairo.Context(self.surface)
        
    def drawRect(self, x, y, w, h ):
        self.context.set_source_rgb(0.0, 0.0, 0.0)
        self.context.set_line_width(1)
        self.context.rectangle(x, y, w, h)
        self.context.stroke()
        
        
    def drawText(self, x, y, text):
        self.context.set_source_rgb(0.0, 0.0, 0.0)
        self.context.set_line_width(1)
        self.context.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        self.context.set_font_size(10)
        x_bearing, y_bearing, width, height = self.context.text_extents(text)[:4]
        self.context.move_to(x - x_bearing, y - height / 2 - y_bearing)
        self.context.text_path(text)
        self.context.fill()
        
    def drawLine(self, x1, y1, x2, y2):
        #self.context.paint_with_alpha(0.4)
        self.context.set_source_rgb(0.0, 0.0, 0.0)
        self.context.set_line_width(1)
        self.context.move_to(x1, y1)
        self.context.line_to(x2, y2)
        self.context.stroke()
        
    def finish(self):
        print('SimpleSVG.finish');
        self.surface.write_to_png('test.png')
        print('SimpleSVG.finish: after write_to_png()');
        self.surface.finish()
