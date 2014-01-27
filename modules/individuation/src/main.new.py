#!/usr/bin/env python
#-*- coding:utf-8 -*-

# Copyright (C) 2011 ~ 2012 Deepin, Inc.
#               2011 ~ 2012 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
from deepin_utils.file import get_parent_dir
sys.path.append(os.path.join(get_parent_dir(__file__, 4), "dss"))

import gtk
from module_frame import ModuleFrame
from dtk.ui.iconview import IconView, IconItem
from math import radians
from dtk.ui.utils import get_optimum_pixbuf_from_file, cairo_disable_antialias, color_hex_to_cairo, is_in_rect, get_content_size, cairo_state
from dtk.ui.draw import draw_shadow, draw_pixbuf, draw_text
from dtk.ui.scrolled_window import ScrolledWindow
from theme import app_theme
import gobject
import deepin_gsettings
import urllib
from dtk.ui.thread_pool import MissionThread, MissionThreadPool
from cache_manager import SMALL_SIZE, cache_manager
import random
from dtk.ui.threads import post_gui
import common
from nls import _
import time
from helper import event_manager
from cache_manager import cache_thread_pool
import copy
from bizhi360 import Bizhi360
from xdg_support import get_download_wallpaper_dir

background_gsettings = deepin_gsettings.new("com.deepin.dde.background")

MODULE_NAME = "individuation"

current_background_url = None

class WallpaperView(IconView):

    def __init__(self):
        super(WallpaperView, self).__init__(padding_x=30, padding_y=10)
        self.backgrounds_dir = os.path.join(get_parent_dir(__file__, 2), "backgrounds")
        self.default_background_files = map(lambda filename: os.path.join(self.backgrounds_dir, filename), os.listdir(self.backgrounds_dir))
        self.first_part_background_files = self.default_background_files[0:20]
        self.second_part_backgroun_files = self.default_background_files[20::]
        self.local_background_load_finish = False
        self.add_items(map(lambda background_file: WallpaperItem(background_file), self.first_part_background_files))
        
        self.download_dir = get_download_wallpaper_dir()
        self.__fetch_thread_id = 0
        self.network_interface = Bizhi360()
        
    def draw_background(self, widget, cr):
        rect = widget.allocation
        
        # Draw background.
        cr.set_source_rgba(1, 1, 1)
        cr.rectangle(rect.x, rect.y, rect.width, rect.height)
        cr.fill()
        
    def load_more_background(self, *args):
        if args[1] == "bottom":
            if not self.local_background_load_finish:
                self.add_items(map(lambda background_file: WallpaperItem(background_file), self.second_part_backgroun_files))
                self.local_background_load_finish = True
            else:
                self.try_to_fetch()
        
    def fetch_failed(self):
        event_manager.emit("fetch-failed", None)
        pass
    
    def emit_download(self):
        download_items = self.items
        if download_items:
            image_items = map(lambda item: item.image_object, download_items)
            event_manager.emit("download-images", image_items)
    
    def fetch_successed(self):
        pass
        
    def try_to_fetch(self):    
        self.network_interface.clear()
        self.__fetch_thread_id += 1
        fetch_thread_id = copy.deepcopy(self.__fetch_thread_id)
        common.ThreadFetch(
            fetch_funcs=(self.fetch_images, ()),
            success_funcs=(self.load_images, (fetch_thread_id,)),
            fail_funcs=(self.fetch_failed, ())
            ).start()
        
    def fetch_images(self):    
        return self.network_interface.fetch_images()
    
    @post_gui
    def load_images(self, ret, thread_id):
        cache_items = []
        thread_items = []
        images = self.network_interface.get_images()
        
        self.set_loading(True)
        for image in images:
            cache_item = CacheItem(image, self.download_dir)
            if not cache_item.is_loaded:
                thread_items.append(cache_item)
            cache_items.append(cache_item)    
            
        if thread_items:    
            cache_thread_pool.add_missions(thread_items)
        self.add_items(cache_items)
        self.set_loading(False)
        self.fetch_successed()
        
gobject.type_register(WallpaperView)

ICON_SIZE = {"x" : 38, "y" : 38}
ITEM_PADDING_X = 20
ITEM_PADDING_Y = 10

class WallpaperItem(IconItem):

    def __init__(self, image_path):
        super(WallpaperItem, self).__init__()
        self.image_path = image_path
        
        self.wallpaper_width = SMALL_SIZE["x"]
        self.wallpaper_height = SMALL_SIZE["y"]

        self.pixbuf = None
        self.is_hover = False
        
        self.width = self.wallpaper_width + ITEM_PADDING_X * 2
        self.height = self.wallpaper_height + ITEM_PADDING_Y * 2
        
        self.hover_stroke_dcolor = app_theme.get_color("globalHoverStroke")
        
        self.hover_response_rect = gtk.gdk.Rectangle(
            ITEM_PADDING_X, ITEM_PADDING_Y,
            self.wallpaper_width, self.wallpaper_height
            ) 
    def emit_redraw_request(self):
        self.emit("redraw-request")
        
    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
    
    def render(self, cr, rect):
        '''
        Render item.
        
        This is IconView interface, you should implement it.
        '''
        # Init.
        if self.pixbuf == None:
            self.pixbuf = get_optimum_pixbuf_from_file(self.image_path, self.wallpaper_width, self.wallpaper_height)
            
        wallpaper_x = rect.x + (rect.width - self.wallpaper_width) / 2
        wallpaper_y = rect.y + (rect.height - self.wallpaper_height) / 2
        
        # Draw shadow.
        drop_shadow_padding = 7
        drop_shadow_radious = 7
        draw_shadow(
            cr,
            wallpaper_x,
            wallpaper_y,
            self.wallpaper_width + drop_shadow_padding,
            self.wallpaper_height + drop_shadow_padding,
            drop_shadow_radious,
            app_theme.get_shadow_color("window_shadow")
            )

        outside_shadow_padding = 4
        outside_shadow_radious = 5
        draw_shadow(
            cr,
            wallpaper_x - outside_shadow_padding,
            wallpaper_y - outside_shadow_padding,
            self.wallpaper_width + outside_shadow_padding * 2,
            self.wallpaper_height + outside_shadow_padding * 2,
            outside_shadow_radious,
            app_theme.get_shadow_color("window_shadow")
            )
        
        # Draw wallpaper.
        draw_pixbuf(cr, self.pixbuf, wallpaper_x, wallpaper_y)    
        
        # Draw wallpaper frame.
        with cairo_disable_antialias(cr):
            cr.set_line_width(2)
            cr.set_source_rgba(1, 1, 1, 1)
            cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
            cr.stroke()
            
        if self.is_hover:    
            cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
            cr.set_source_rgb(*color_hex_to_cairo(self.hover_stroke_dcolor.get_color()))
            cr.stroke()
            
    def icon_item_motion_notify(self, x, y):
        '''
        Handle `motion-notify-event` signal.
        
        This is IconView interface, you should implement it.
        '''
        if is_in_rect((x, y), (self.hover_response_rect.x,
                               self.hover_response_rect.y,
                               self.hover_response_rect.width,
                               self.hover_response_rect.height)):
            self.is_hover = True
            
        else:    
            self.is_hover = False
            
        self.emit_redraw_request()
        
    def icon_item_lost_focus(self):
        '''
        Lost focus.
        
        This is IconView interface, you should implement it.
        '''
        
        self.is_hover = False
        self.emit_redraw_request()
        
    def icon_item_highlight(self):
        '''
        Highlight item.
        
        This is IconView interface, you should implement it.
        '''
        self.highlight_flag = True

        self.emit_redraw_request()
        
    def icon_item_normal(self):
        '''
        Set item with normal status.
        
        This is IconView interface, you should implement it.
        '''
        self.highlight_flag = False
        
        self.emit_redraw_request()
    
    def icon_item_button_press(self, x, y):
        '''
        Handle button-press event.
        
        This is IconView interface, you should implement it.
        '''
        pass
    
    def icon_item_button_release(self, x, y):
        '''
        Handle button-release event.
        
        This is IconView interface, you should implement it.
        '''
        pass
    
    def icon_item_single_click(self, x, y):
        '''
        Handle single click event.
        
        This is IconView interface, you should implement it.
        '''
        background_gsettings.set_string("picture-uris", "file://" + self.image_path + ";")

    def icon_item_release_resource(self):
        if self.pixbuf:
            del self.pixbuf
        self.pixbuf = None    
        
        # Return True to tell IconView call gc.collect() to release memory resource.
        return True

gobject.type_register(WallpaperItem)        
        
class Download(MissionThread):
    
    def __init__(self, url, save_path, finish_callback):
        global current_background_url         
        
        MissionThread.__init__(self)
        
        self.url = url
        self.save_path = save_path
        self.finish_callback = finish_callback
        
        current_background_url = url
        
    def start_mission(self):
        urllib.urlretrieve (self.url, self.save_path)
        self.finish_callback()

class CacheItem(gobject.GObject, MissionThread):
    '''
    Icon item.
    '''
	
    __gsignals__ = {
        "redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
    }
    
    def __init__(self, image_object, download_dir=None):
        '''
        Initialize ItemIcon class.
        
        @param pixbuf: Icon pixbuf.
        '''
        gobject.GObject.__init__(self)
        MissionThread.__init__(self)
      
        self.image_path = None
        self.is_loaded = False
        self.is_downloaded = False
        self.hover_flag = False
        self.highlight_flag = False
        self.wallpaper_width = SMALL_SIZE["x"]
        self.wallpaper_height = SMALL_SIZE["y"]
        self.padding_x = 8
        self.width = self.wallpaper_width + self.padding_x * 2
        self.height = self.wallpaper_height + ITEM_PADDING_Y * 2
        self.image_object = image_object
        self.download_dir = download_dir
        self.pixbuf = None
        self.create_cache_pixbuf()
        
        self.is_hover = False
        self.hover_stroke_dcolor = app_theme.get_color("globalHoverStroke")
        self.hover_response_rect = gtk.gdk.Rectangle(
            self.padding_x, ITEM_PADDING_Y ,
            self.wallpaper_width, self.wallpaper_height
            ) 
        
        self.tick_normal_dpixbuf = app_theme.get_pixbuf("individuation/tick_normal.png")
        self.tick_gray_dpixbuf = app_theme.get_pixbuf("individuation/tick_gray.png")
        self.is_tick = False

        self.loop_dpixbuf = app_theme.get_pixbuf("individuation/loop.png")
        self.is_loop = False

    def download_start(self):
        self.is_loop = True
        self.degree = 0
        self.refresh_loading()
        
        download_pool.add_missions([Download(self.image_object.big_url, self.image_object.get_save_path(), self.download_finish)])

    @common.threaded
    def refresh_loading(self):
        while self.is_loop:
            self.degree += 10
            self.emit_redraw_request()
            time.sleep(0.1)

    def download_finish(self):                                
        global current_background_url         
        
        self.is_loop = False
        self.is_downloaded = True
        self.emit_redraw_request()
        self.image_path = self.image_object.get_save_path()
        
        if current_background_url == self.image_object.big_url:
            background_gsettings.set_string("picture-uris", "file://" + self.image_object.get_save_path() + ";")

    def create_cache_pixbuf(self):
        image_path = cache_manager.get_image(self.image_object, try_web = False)
        
        if image_path != None:
            self.is_downloaded = os.path.exists(self.download_dir + "/" +  image_path.split("/")[-1])
            if self.is_downloaded:
                self.image_path = self.download_dir + "/" +  image_path.split("/")[-1]
        
        self.pixbuf, self.is_loaded = cache_manager.get_image_pixbuf(self.image_object)

    def start_mission(self):    
        image_path = cache_manager.get_image(self.image_object, try_web=True)
        if image_path:
            self.delay_render_image(image_path)
            
    def delay_render_image(self, image_path):        
        gobject.timeout_add(200 + random.randint(1, 10),  self.render_image, image_path)
            
    @post_gui    
    def render_image(self, image_path):
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file(image_path)
        except:    
            pass
        else:
            self.pixbuf = pixbuf
            self.emit_redraw_request()
            
        return False
        
    def emit_redraw_request(self):
        '''
        Emit `redraw-request` signal.
        
        This is IconView interface, you should implement it.
        '''
        self.emit("redraw-request")
        
    def get_width(self):
        '''
        Get item width.
        
        This is IconView interface, you should implement it.
        '''
        return self.width
        
    def get_height(self):
        '''
        Get item height.
        
        This is IconView interface, you should implement it.
        '''
        return self.height
    
    def render(self, cr, rect):
        '''
        Render item.
        
        This is IconView interface, you should implement it.
        '''
        if self.pixbuf == None:
            self.create_cache_pixbuf()
            
        wallpaper_x = rect.x + (rect.width - self.wallpaper_width) / 2
        wallpaper_y = rect.y + (rect.height - self.wallpaper_height) / 2
        
        # Draw shadow.
        drop_shadow_padding = 7
        drop_shadow_radious = 7
        draw_shadow(
            cr,
            wallpaper_x,
            wallpaper_y,
            self.wallpaper_width + drop_shadow_padding,
            self.wallpaper_height + drop_shadow_padding,
            drop_shadow_radious,
            app_theme.get_shadow_color("window_shadow")
            )

        outside_shadow_padding = 4
        outside_shadow_radious = 5
        draw_shadow(
            cr,
            wallpaper_x - outside_shadow_padding,
            wallpaper_y - outside_shadow_padding,
            self.wallpaper_width + outside_shadow_padding * 2,
            self.wallpaper_height + outside_shadow_padding * 2,
            outside_shadow_radious,
            app_theme.get_shadow_color("window_shadow")
            )
        
        # Draw wallpaper.
        draw_pixbuf(cr, self.pixbuf, wallpaper_x, wallpaper_y)    
        
        # Draw wallpaper frame.
        with cairo_disable_antialias(cr):
            cr.set_line_width(2)
            cr.set_source_rgba(1, 1, 1, 1)
            cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
            cr.stroke()
            
        if self.is_hover:    
            cr.rectangle(wallpaper_x, wallpaper_y, self.wallpaper_width, self.wallpaper_height)
            cr.set_source_rgb(*color_hex_to_cairo(self.hover_stroke_dcolor.get_color()))
            cr.stroke()

        if self.is_downloaded:
            downloaded_str = _("Downloaded")
            downloaded_padding = 4
            downloaded_str_width, downloaded_str_height = get_content_size(downloaded_str)
            cr.rectangle(wallpaper_x + 1, 
                         wallpaper_y + self.wallpaper_height - downloaded_str_height - downloaded_padding, 
                         self.wallpaper_width - 2, 
                         downloaded_str_height - 1 + downloaded_padding)
            cr.set_source_rgba(0, 0, 0, 0.4)
            cr.fill()
            draw_text(cr, 
                      downloaded_str, 
                      wallpaper_x + (self.wallpaper_width - downloaded_str_width) / 2, 
                      wallpaper_y + self.wallpaper_height - downloaded_str_height - downloaded_padding / 1.5, 
                      self.wallpaper_width, 
                      downloaded_str_height, 
                      text_color = "#FFFFFF")
            
        if self.is_loop:
            loop_pixbuf = self.loop_dpixbuf.get_pixbuf()
            loop_x = wallpaper_x + (self.wallpaper_width - loop_pixbuf.get_width()) / 2
            loop_y = wallpaper_y + (self.wallpaper_height - loop_pixbuf.get_height()) / 2
            self.draw_loop_pixbuf(cr, loop_pixbuf, loop_x, loop_y)
    
    def draw_loop_pixbuf(self, cr, loop_pixbuf, loop_x, loop_y):
        width = loop_pixbuf.get_width()
        height = loop_pixbuf.get_height()
        ox = loop_x + width * 0.5
        oy = loop_y + height * 0.5 

        with cairo_state(cr):
            cr.translate(ox, oy)
            cr.rotate(radians(self.degree))                      
            cr.translate(-width * 0.5, -height * 0.5)
            draw_pixbuf(cr, loop_pixbuf, 0, 0)
    
    def icon_item_motion_notify(self, x, y):
        '''
        Handle `motion-notify-event` signal.
        
        This is IconView interface, you should implement it.
        '''
        
        if is_in_rect((x, y), (self.hover_response_rect.x,
                               self.hover_response_rect.y,
                               self.hover_response_rect.width,
                               self.hover_response_rect.height)):
            self.is_hover = True
            
        else:    
            self.is_hover = False
            
        self.emit_redraw_request()    
        
    def icon_item_lost_focus(self):
        '''
        Lost focus.
        
        This is IconView interface, you should implement it.
        '''
        
        self.is_hover = False
        self.emit_redraw_request()

        
    def icon_item_highlight(self):
        '''
        Highlight item.
        
        This is IconView interface, you should implement it.
        '''
        self.highlight_flag = True

        self.emit_redraw_request()
        
    def icon_item_normal(self):
        '''
        Set item with normal status.
        
        This is IconView interface, you should implement it.
        '''
        self.highlight_flag = False
        
        self.emit_redraw_request()
    
    def icon_item_button_press(self, x, y):
        '''
        Handle button-press event.
        
        This is IconView interface, you should implement it.
        '''
        self.emit_redraw_request()
        
        if os.path.exists(self.image_object.get_save_path()):
            background_gsettings.set_string("picture-uris", "file://" + self.image_object.get_save_path() + ";")
        else:
            self.download_start()
    
    def icon_item_button_release(self, x, y):
        '''
        Handle button-release event.
        
        This is IconView interface, you should implement it.
        '''
        pass
    
    def icon_item_single_click(self, x, y):
        '''
        Handle single click event.
        
        This is IconView interface, you should implement it.
        '''
        pass

    def icon_item_double_click(self, x, y):
        '''
        Handle double click event.
        
        This is IconView interface, you should implement it.
        '''
        pass
    
    def icon_item_release_resource(self):
        # Return True to tell IconView call gc.collect() to release memory resource.
        if self.pixbuf:
            del self.pixbuf
        self.pixbuf = None    
        return True
    
if __name__ == '__main__':
    gtk.gdk.threads_init()
    module_frame = ModuleFrame(os.path.join(get_parent_dir(__file__, 2), "config.ini"))

    scrolled_window = ScrolledWindow()
    scrolled_window.set_size_request(788, 467)
    wallpaper_view = WallpaperView()
    scrolled_window.add_child(wallpaper_view)
    module_frame.add(scrolled_window)
    
    scrolled_window.connect("vscrollbar-state-changed", wallpaper_view.load_more_background)
    
    download_pool = MissionThreadPool(5)
    download_pool.start()
    
    def message_handler(*message):
        (message_type, message_content) = message
        if message_type == "show_again":
            module_frame.send_module_info()
        elif message_type == "exit":
            module_frame.exit()

    module_frame.module_message_handler = message_handler        
    module_frame.run()
