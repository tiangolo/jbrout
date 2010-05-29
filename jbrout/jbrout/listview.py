# -*- coding: utf-8 -*-

"""
changelog:
 - right button doesn't deselect anymore, on a selection
 - click on a already selected item in a selection, make this the only selected
 - better display text under thumbnails
"""
import gtk
import gobject
import pango
import sys

import time
import os
import gc

BORDER_SIZE = 2
CELL_BORDER_WIDTH = 4
SELECTION_THICKNESS = 2

gobject.threads_init()



class Selection:
    def __init__(self):
        self.real_selection = []
        self.frozen = False
        self.notify_callbacks = []

    def __iter__(self):
        return iter(self.real_selection)

    def __len__(self):
        return len(self.real_selection)

    def __getitem__(self, key):
        return self.real_selection[key]

    def __setitem__(self, key, value):
        old_selection = self.real_selection[:]
        self.real_selection[key] = value
        self.notify_changes(old_selection)

    def __delitem__(self, key):
        old_selection = self.real_selection[:]
        del self.real_selection[key]
        self.notify_changes(old_selection)

    def append(self, val):
        old_selection = self.real_selection[:]
        self.real_selection.append(val)
        self.notify_changes(old_selection)

    def remove(self, val):
        old_selection = self.real_selection[:]
        self.real_selection.remove(val)
        self.notify_changes(old_selection)

    def empty(self):
        old_selection = self.real_selection[:]
        self.real_selection = []
        self.notify_changes(old_selection)

    def set(self, val):
        old_selection = self.real_selection[:]
        self.real_selection = val
        self.notify_changes(old_selection)


    def freeze(self):
        self.frozen = True
        self.old_selection = self.real_selection[:]

    def thaw(self):
        self.frozen = False
        self.notify_changes(self.old_selection)

    def notify_changes(self, old_selection):
        if self.frozen:
            return
        if old_selection == self.real_selection:
            return
        for callback in self.notify_callbacks:
            callback(old_selection)

    def add_notify_callback(self, callback):
        self.notify_callbacks.append(callback)

selection = Selection()

class ThumbnailsView(gtk.Layout):
    scroll_value = 0
    scroll = False

    real_focus_cell = 0

    # initial thumbnail size
    real_thumbnail_width = 160
    thumbnail_height = 160

    sort_by = 'date'
    reversed_sort_order = False

    priority_loads=[]

    def __init__(self):
        gtk.Layout.__init__(self, None, None)

        w = gtk.Window()    # create a fake window
        w.realize()         # realize it ...
        style=w.get_style() # ... to obtain the REAL theme style
        del(w)              # it's the only trick i've found
        BACKGROUND = style.base[gtk.STATE_NORMAL]

        self.modify_bg(gtk.STATE_NORMAL, BACKGROUND)
        self.loading_pixbuf = gtk.gdk.pixbuf_new_from_file('data/gfx/refresh.png')
        self.selection = selection

        self.thumbnail_pixbufs = {}
        self.exif_tags = {}

        self.connect('expose-event', self.on_expose_event)
        self.connect('size-allocate', self.on_size_allocate)
        self.connect('set-scroll-adjustments', self.on_set_scroll_adjustments)
        self.connect('key-press-event', self.on_key_press)
        self.connect('button-press-event', self.on_button_press)
        self.set_flags(gtk.CAN_FOCUS)

        self.items = []
        self.update_layout()
        selection.add_notify_callback(self.notify_selection_change)
        self.hdl=None

    def __load_thumbnails_bg(self):
        while True:
            if self.priority_loads:
                idx = self.priority_loads.pop(0)
                self.get_thumb(idx)
                self.invalidate_cell(idx)
            time.sleep(0.01)
            yield True

    def stop(self):
        """ stop background process which load thumbs """
        if self.hdl:
            gobject.source_remove(self.hdl)
            self.hdl=None

    def start(self):
        """ start background process to load thumbs """
        if not self.hdl:
            self.hdl=gobject.idle_add(self.__load_thumbnails_bg().next)

    def set_photos(self, photos):
        self.stop()

        self.items = photos
        #~ self.sort_photos(photos)
        self.update_layout()
        self.selection.empty()
        self.set_focus_cell(0)

        self.priority_loads = []

        self.start()
        self.invalidate_view()

    def invalidate_view(self):
        if self.bin_window:
            rect = apply(gtk.gdk.Rectangle, tuple(self.allocation))
            rect.x = 0
            rect.y = 0
            rect.height = max(rect.height, self.get_vadjustment().upper)
            self.bin_window.invalidate_rect(rect, False)

    def get_thumbnail_width(self):
        return self.real_thumbnail_width
    def set_thumbnail_width(self, value):
        self.thumbnail_height = value #int(value * 3./4)
        self.real_thumbnail_width = int(value)
        self.invalidate_view()
        self.update_layout()
    thumbnail_width = property(get_thumbnail_width, set_thumbnail_width)


    def get_focus_cell(self):
        return self.real_focus_cell

    def set_focus_cell(self, value):
        if value < 0:
            value = 0
        if value >= len(self.items):
            value = len(self.items)-1
        if value != self.real_focus_cell:
            self.invalidate_cell(value)
            self.invalidate_cell(self.real_focus_cell)
            self.real_focus_cell = value

    focus_cell = property(get_focus_cell, set_focus_cell)

    def on_key_press(self, widget, event):
        shift = event.state & gtk.gdk.SHIFT_MASK
        ctrl = event.state & gtk.gdk.CONTROL_MASK
        focus_old = self.focus_cell
        if event.keyval == gtk.keysyms.Down:
            self.focus_cell += self.cells_per_row
        elif event.keyval == gtk.keysyms.Left:
            if ctrl and shift:
                self.focus_cell -= self.focus_cell % self.cells_per_row
            else:
                self.focus_cell -= 1
        elif event.keyval == gtk.keysyms.Right:
            if ctrl and shift:
                self.focus_cell += self.cells_per_row - (self.focus_cell % self.cells_per_row) - 1
            else:
                self.focus_cell += 1
        elif event.keyval == gtk.keysyms.Up:
            self.focus_cell -= self.cells_per_row
        elif event.keyval == gtk.keysyms.Home:
            self.focus_cell = 0
        elif event.keyval == gtk.keysyms.End:
            self.focus_cell = len(self.items) - 1
        elif ctrl and event.keyval == ord('a'): # select All
            self.selection.set( range(0,len(self.items)) )
        else:
            return False

        self.focus_cell = max(self.focus_cell, 0)
        self.focus_cell = min(self.focus_cell, len(self.items)-1)

        if self.focus_cell == focus_old:
            # so up from the first or down from the last doesn't tab
            # to the prev/next widget
            return True

        self.selection.freeze()

        if shift:
            if focus_old != self.focus_cell and focus_old in self.selection and self.focus_cell in self.selection:
                for i in range(min(focus_old, self.focus_cell)+1, max(focus_old, self.focus_cell)+1):
                    if i in self.selection:
                        self.selection.remove(i)
            else:
                for i in range(min(focus_old, self.focus_cell), max(focus_old, self.focus_cell)+1):
                    if not i in self.selection:
                        self.selection.append(i)

        else:
            self.selection.set([self.focus_cell])

        self.selection.thaw()

        self.scroll_to(self.focus_cell)
        return True

    def notify_selection_change(self, old_selection):
        for cell in old_selection:
            if not cell in self.selection:
                self.invalidate_cell(cell)
        for cell in self.selection:
            if not cell in old_selection:
                self.invalidate_cell(cell)

    def on_button_press(self, widget, event):
        cell_num = self.cell_at_position(event.x, event.y, False)
        if cell_num < 0:
            self.selection.empty()
            return False

        if event.type == gtk.gdk.BUTTON_PRESS:
            self.grab_focus()
            ctrl = event.state & gtk.gdk.CONTROL_MASK
            shift = event.state & gtk.gdk.SHIFT_MASK
            self.selection.freeze()
            if ctrl or event.button==2:
                if cell_num in self.selection:
                    self.selection.remove(cell_num)
                else:
                    self.selection.append(cell_num)
            elif shift:
                for i in range(min(self.focus_cell, cell_num), max(self.focus_cell, cell_num)+1):
                    if not i in self.selection:
                        self.selection.append(i)
            else:
                if (event.button==3 or event.button==1) and cell_num not in self.selection:#don't set selection if target is already selected
                    self.selection.set([cell_num])

            self.focus_cell = cell_num  # needed before thaw() ! else it will not be good in notification event !!!!!
            self.selection.thaw()

            self.queue_resize()

            #~ if event.button != 1:
                #~ return True

            return False

        #~ if event.type == gtk.gdk._2BUTTON_PRESS and event.button == 1:
            #~ self.focus_cell = cell_num
            #~ self.app.on_fullscreen_activate()



    def invalidate_cell(self, order):
        vadjustment = self.get_vadjustment()
        hadjustment = self.get_hadjustment()

        cell_area = self.cell_bounds(order)
        cell_area.width -= 1
        cell_area.height -= 1
        visible = gtk.gdk.Rectangle(int(hadjustment.value), int(vadjustment.value),
                self.allocation.width, self.allocation.height)
        cell_area = cell_area.intersect(visible)
        if self.bin_window and cell_area.width != 0:
            self.bin_window.invalidate_rect(cell_area, False)



    def cell_at_position(self, x, y, crop_visible = True):
        vadjustment = self.get_vadjustment()
        hadjustment = self.get_hadjustment()
        if crop_visible and (
                (y < vadjustment.value or y > vadjustment.value + self.allocation.height) or (
                x < hadjustment.value or x > hadjustment.value + self.allocation.width)):
            return -1

        if x < BORDER_SIZE or x >= BORDER_SIZE + self.cells_per_row * self.cell_width:
            return -1

        if y < BORDER_SIZE or y >= BORDER_SIZE + (len(self.items) / self.cells_per_row + 1) * self.cell_height:
            return -1

        column = int((x - BORDER_SIZE) / self.cell_width)
        row = int((y - BORDER_SIZE) / self.cell_height)
        cell_num = column + row * self.cells_per_row

        if cell_num < len(self.items):
            return cell_num
        else:
            return -1


    def on_set_scroll_adjustments(self, widget, hadjustment, vadjustment):
        if vadjustment:
            vadjustment.connect('value-changed', self.on_adjustment_value_changed)

    def on_adjustment_value_changed(self, widget, *args):
        self.do_scroll()

    def do_scroll(self):
        vadjustment = self.get_vadjustment()
        hadjustment = self.get_hadjustment()


    def on_size_allocate(self, widget, rectangle):
        self.update_layout(rectangle)
        return True

    def update_layout(self, rectangle = None):
        if rectangle is None:
            rectangle = self.allocation
        #print 'updating layout'
        self.available_width = rectangle[2] - 2 * BORDER_SIZE
        self.cell_width = self.thumbnail_width + 2 * CELL_BORDER_WIDTH
        self.cell_height = self.thumbnail_height + 2 * CELL_BORDER_WIDTH
        self.cells_per_row = max(int(self.available_width / self.cell_width), 1)
        self.cell_width += (self.available_width - self.cells_per_row * self.cell_width) / self.cells_per_row

        if True: # display date
            metrics = self.get_pango_context().get_metrics(self.style.font_desc,
                    pango.Language('en_US'))
            self.cell_height += pango.PIXELS(metrics.get_ascent() + metrics.get_descent())

        self.num_thumbnails = len(self.items)
        self.num_rows = int(self.num_thumbnails / self.cells_per_row)
        if self.num_thumbnails % self.cells_per_row:
            self.num_rows += 1

        self.height = int(self.num_rows * self.cell_height + 2 * BORDER_SIZE)

        vadjustment = self.get_vadjustment()
        hadjustment = self.get_hadjustment()
        vadjustment.step_increment = self.cell_height
        x = hadjustment.value
        y = self.height * self.scroll_value
        self.set_size(x, y, self.allocation.width, self.height)

    def set_size(self, x, y, width, height):
        vadjustment = self.get_vadjustment()
        hadjustment = self.get_hadjustment()

        xchange = False
        ychange = False

        hadjustment.upper = max(self.allocation.width, width)
        vadjustment.upper = max(self.allocation.height, height)

        if self.scroll:
            xchange = (hadjustment.value != x)
            ychange = (vadjustment.value != y)
            self.scroll = False

        if self.flags() & gtk.REALIZED:
            self.bin_window.freeze_updates()

        if xchange or ychange:
            if self.flags() & gtk.REALIZED:
                self.bin_window.move_resize(-x, -y, hadjustment.upper, vadjustment.upper)
                vadjustment.value = y
                hadjustment.value = x

        if self.scroll:
            self.scroll = False

        if width != self.allocation.width or height != self.allocation.height:
            gtk.Layout.set_size(self, self.allocation.width, height)

        if xchange or ychange:
            vadjustment.change_value()
            hadjustment.change_value()

        if self.flags() & gtk.REALIZED:
            self.bin_window.thaw_updates()
            self.bin_window.process_updates(True)



    def on_expose_event(self, widget, event):
        self.draw_all_cells(event.area)
        return True

    def get_cell_position(self, cell_num):
        if self.cells_per_row == 0:
            return 0, 0

        row, col = divmod(cell_num, self.cells_per_row)

        x = col * self.cell_width + BORDER_SIZE
        y = row * self.cell_height + BORDER_SIZE

        return x, y

    def draw_all_cells(self, area):
        #print 'draw_all_cells', area.x, area.y, area.width, area.height
        if self.cell_width == 0 or self.cell_height == 0:
            return

        start_cell_column = max((area[0] - BORDER_SIZE)/self.cell_width, 0)
        start_cell_row = max((area[1] - BORDER_SIZE)/self.cell_height, 0)
        start_cell_num = start_cell_column + start_cell_row * self.cells_per_row

        start_cell_x, cell_y = self.get_cell_position(start_cell_num)

        end_cell_column = int(max((area[0] + area[2] - BORDER_SIZE) / self.cell_width, 0))
        end_cell_row = int(max((area[1] + area[3] - BORDER_SIZE) / self.cell_height, 0))

        num_rows = end_cell_row - start_cell_row + 1;
        num_cols = min(end_cell_column - start_cell_column + 1,
                self.cells_per_row - start_cell_column)

        i = 0
        cell_num = start_cell_num
        while i < num_rows and cell_num < len(self.items):
            cell_x = start_cell_x
            j = 0
            while j < num_cols and cell_num + j < len(self.items):
                #print '  ',
                self.draw_cell(cell_num + j, area)
                cell_x += self.cell_width
                j += 1

            cell_y += self.cell_height
            cell_num += self.cells_per_row
            i += 1


    def cell_bounds(self, cell):
        x, y = self.get_cell_position(cell)
        return gtk.gdk.Rectangle(x, y, self.cell_width, self.cell_height)


    def get_text(self, thumbnail_num):
        return ""
    def is_thumb(self, thumbnail_num):
        return False
    def get_thumb(self, thumbnail_num):
        return None

    def get_thumbnail_pixbuf(self, thumbnail_num):
        if not self.is_thumb(thumbnail_num):
            if thumbnail_num in self.priority_loads:
                self.priority_loads.remove(thumbnail_num)
            self.priority_loads.insert(0,thumbnail_num)
            pixbuf = self.loading_pixbuf
        else:
            pixbuf = self.get_thumb(thumbnail_num)
            if pixbuf.get_width() > pixbuf.get_height():
                wx, wy = self.thumbnail_width, self.thumbnail_height
            else:
                r = float(pixbuf.get_height()) / self.thumbnail_height
                wx, wy = int(pixbuf.get_width()/r), self.thumbnail_height
            #~ pixbuf = pixbuf.scale_simple(wx, wy, gtk.gdk.INTERP_BILINEAR)
            pixbuf = pixbuf.scale_simple(wx, wy, gtk.gdk.INTERP_NEAREST)    #speedest
        return pixbuf

    def draw_cell(self, thumbnail_num, area):
        #print 'drawing cell', thumbnail_num, self.items[thumbnail_num]
        #~ filename = self.items[thumbnail_num]

        bounds = self.cell_bounds(thumbnail_num)

        if not bounds.intersect(area).width:
            return

        thumbnail = self.get_thumbnail_pixbuf(thumbnail_num)
        selected = thumbnail_num in self.selection
        if selected:
            if self.flags() & gtk.HAS_FOCUS:
                cell_state = gtk.STATE_SELECTED
            else:
                cell_state = gtk.STATE_ACTIVE
        else:
            cell_state = gtk.STATE_NORMAL
        if thumbnail != self.loading_pixbuf:
            self.style.paint_flat_box(self.bin_window, cell_state,
                    gtk.SHADOW_OUT, area, self, 'ThumbnailsView',
                    bounds.x, bounds.y, bounds.width-1, bounds.height-1)

        def inflate(rect, x, y):
            return gtk.gdk.Rectangle(rect.x-x, rect.y-y, rect.width+2*x, rect.height+2*y)

        isFocused=False
        if self.flags() & gtk.HAS_FOCUS and thumbnail_num == self.focus_cell:
            focus = inflate(bounds, -3, -3)
            self.style.paint_focus(self.bin_window, cell_state,
                    area, self, None, focus.x, focus.y, focus.width, focus.height)
            isFocused=True

        region = gtk.gdk.Rectangle(0,0,0,0)
        image_bounds = inflate(bounds, -CELL_BORDER_WIDTH, -CELL_BORDER_WIDTH)

        if selected:
            expansion = SELECTION_THICKNESS
        else:
            expansion = 0
        image_bounds = inflate(image_bounds, expansion+1, expansion+1).intersect(area)
        if image_bounds.width:
            def fit(orig_width, orig_height, dest_width, dest_height):
                if orig_width == 0 or orig_height == 0:
                    return 0, 0
                scale = min(dest_width/orig_width, dest_height/orig_height)
                if scale > 1:
                    scale = 1
                fit_width = scale * orig_width
                fit_height = scale * orig_height
                return fit_width, fit_height

            # resizing during the painting (pn.getThumb give some 160x160)
            w, h = fit(thumbnail.get_width(), thumbnail.get_height(), self.thumbnail_width,self.thumbnail_width)

            # resizing during the extraction (pn.getThumb desired size)
            # w, h = fit(thumbnail.get_width(), thumbnail.get_height(), 160, 160)

            region = gtk.gdk.Rectangle(
                    bounds.x + (bounds.width - w) / 2,
                    bounds.y + self.thumbnail_height - h + CELL_BORDER_WIDTH,
                    w, h)

            region = inflate(region, expansion, expansion)   # EXPAND WHEN SELECTED !
            region.width = max(1, region.width)
            region.height = max(1, region.height)
            if region.width != thumbnail.get_width() and region.height != thumbnail.get_height():
                temp_thumbnail = thumbnail.scale_simple(region.width, region.height,
                        gtk.gdk.INTERP_NEAREST) # the speedest
            else:
                temp_thumbnail = thumbnail


            region.width = temp_thumbnail.get_width()
            region.height = temp_thumbnail.get_height()

            draw = inflate(region, 1, 1)

            if thumbnail != self.loading_pixbuf:
                self.style.paint_shadow(self.bin_window, cell_state, gtk.SHADOW_OUT,
                        area, self, 'ThumbnailsView', draw.x, draw.y, draw.width, draw.height)

            draw = region.intersect(area)
            if draw.width:
                self.bin_window.draw_pixbuf(
                        self.style.white_gc,
                        temp_thumbnail,
                        draw.x - region.x,
                        draw.y - region.y,
                        draw.x, draw.y,
                        draw.width, draw.height,
                        gtk.gdk.RGB_DITHER_NONE,
                        draw.x, draw.y)

        layout_bounds = gtk.gdk.Rectangle(0,0,0,0)

        item = self.items[thumbnail_num]
        if item:
            layout = pango.Layout(self.get_pango_context())
            layout.set_font_description(self.style.font_desc)
            layout.set_text(self.get_text(thumbnail_num))

            #~ if isFocused:
            layout.set_width((region.width+6)*1000)
            layout.set_wrap(1)

            layout_bounds.width, layout_bounds.height = layout.get_pixel_size()
            layout_bounds.y = bounds.y + bounds.height - CELL_BORDER_WIDTH - layout_bounds.height + 3
            layout_bounds.x = bounds.x + (bounds.width - layout_bounds.width)/2

            region = layout_bounds.intersect(area)
            if region.width:
                self.style.paint_flat_box(self.bin_window, cell_state,
                        gtk.SHADOW_OUT, area, self, 'ThumbnailsView',
                        layout_bounds.x, layout_bounds.y, layout_bounds.width, layout_bounds.height)

                self.style.paint_layout(self.bin_window, cell_state, True, area, self,
                        'ThumbnailsView', layout_bounds.x, layout_bounds.y, layout)


    def scroll_to(self, cell_num, center = True):
        if not (self.flags() & gtk.REALIZED):
            return
        adjustment = self.get_vadjustment()
        x, y = self.get_cell_position(cell_num)
        if y + self.cell_height > adjustment.upper:
            self.update_layout()

        if center:
            t = y + self.cell_height / 2 - adjustment.page_size / 2
            if t < 0:
                t = 0
            elif t + adjustment.page_size > adjustment.upper:
                t = adjustment.upper - adjustment.page_size
            adjustment.value = t
        else:
            adjustment.value = y

class ListView(ThumbnailsView):
    allow_drag=True
    allow_drop=True

    def __init__(self):
        ThumbnailsView.__init__(self)

        if self.allow_drag:
            # allow drag'n'drop from
            self.drag_source_set(gtk.gdk.BUTTON1_MASK | gtk.gdk.BUTTON2_MASK,
                  [('STRING', 0, 111),], gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)

        if self.allow_drop:
            # allow drag'n'drop to
            self.drag_dest_set(gtk.DEST_DEFAULT_ALL, [('STRING', 0, 111),],
                gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
            self.connect("drag_data_received",
                              self.on_drag_data_received_data)


    def on_drag_data_received_data(self, widget, object,x,y,sdata,code,time):
        """ event drop notified """
        cell_num = self.cell_at_position(x,y, False)
        if cell_num >=0:
            if cell_num not in self.selection:
                self.selection.set([cell_num])
            print "drop good !!!!!!!!!!!!!!!!!!!!!!!!!!!"

    def notify_selection_change(self,old):
        """ event selection changed """
        ThumbnailsView.notify_selection_change(self,old)
        print "select change",self.selection.real_selection


    def getSelected(self):
        return [self.items[i] for i in self.selection.real_selection]

    def init(self,l):
        self.set_photos(l)

    def refresh(self):
        """ refresh the layout """
        self.update_layout()

    def get_text(self,idx):
        item = self.items[idx]
        return item.display

    def get_thumb(self,idx):
        item = self.items[idx]
        return Cache.get(item)

    def is_thumb(self,idx):
        item = self.items[idx]
        return Cache.exists(item)

class TestLayoutMgr(gtk.Dialog):
    def __init__(self, path_base):
        gtk.Dialog.__init__(self, 'TestLayout', None,
                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                   (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                   gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.path_base = path_base
        self.create_gui()

    def create_gui(self):
        self.icon_view = ListView()

        self.icon_view.connect('key-press-event', self.on_key_press)
        self.icon_view.connect('button-press-event', self.on_button_press)

        l=ImageFile.load(self.path_base)

        self.icon_view.set_photos(l)
        sclwin = gtk.ScrolledWindow()
        sclwin.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        sclwin.add(self.icon_view)
        print self.icon_view.get_parent()
        ss=sclwin.get_vscrollbar()
        ss.set_value(550)
        self.icon_view.grab_focus()
        self.vbox.pack_start(sclwin)
        hbox = gtk.HBox()
        self.vbox.pack_start(hbox, False, False)
        hscale = gtk.HScale()
        hscale.set_size_request(100, -1)
        hscale.set_property('draw-value', False)
        hscale.set_range(50, 160)
        hscale.connect('value-changed', self.zoom_changed)
        hscale.set_value(160)
        hbox.pack_end(hscale, False, False)
        self.resize(580, 320)
        self.show_all()


    def on_key_press(self,widget,event):
        print "pression touche",gtk.gdk.keyval_name(event.keyval).lower()

    def on_button_press(self,widget,event):
        print "pression button",event.button,event.type

    def zoom_changed(self, widget):
        self.icon_view.thumbnail_width = int(widget.get_value())



class Cache:
    __buf={}

    @staticmethod
    def exists(item):
        return item.file in Cache.__buf

    @staticmethod
    def get(item):
        if not Cache.exists(item):
            Cache.__buf[item.file]=item.getThumb()
        return Cache.__buf[item.file]

class ImageFile(object):

    def __getAff(self): return os.path.basename(self.__file)
    display=property(__getAff)

    def __getFile(self): return self.__file
    file=property(__getFile)

    def __init__(self,file):
        """ constructor of a ImageFile """
        self.__file=file

    @staticmethod
    def load(path):
        """ constructor of a list of ImageFile """
        ll=[]
        for filename in os.listdir(path):
            if not os.path.splitext(filename)[1].lower() in ('.jpg', '.jpeg'):
                continue
            ll.append(ImageFile(os.path.join(path, filename)))
        return ll

if __name__ == '__main__':
    THUMBNAILS_CACHE_SIZE = 10 # so it tests lazy-loading
    if len(sys.argv) == 2:
        path_base = sys.argv[1]
    else:
        path_base = '/media/data/photos/pierre/'

    p = TestLayoutMgr(path_base)
    p.run()
    p.destroy()

