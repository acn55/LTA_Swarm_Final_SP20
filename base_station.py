import time
import pygame
from pygame.locals import *
import ctypes
import socket
import threading
from numpy import arange

### Globals ###

# Localization
AT_ID = None        # Visible AprilTag ID or None if no AT visible or ATs disabled
alt = None          # Last known altitude or None if ATs disabled or not yet found
coords = None       # Last known position (x,y) or None if ATs disabled or not yet found
orient = None       # Last known orientation in deg or None if ATs disabled or not yet found

# Time of flight distances
# Left, center, right
TOF_dist = [0.,0.,0.]

# Time of flight status
# Left, center, right
# 0: OK
# 1: Danger
# 2: Collision imminent
TOF_status = [0, 0, 0]

# While loop variable
running = True

class conn:
    
    def __init__(self, ip, port):
        self.clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.clientSocket.connect((ip,port))
        
    def get_AT(self):
        self.clientSocket.send("at".encode())
        msg, addr = self.clientSocket.recvfrom(1024)
        return msg.decode()
        
    def get_TOF(self):
        self.clientSocket.send("tof".encode())
        msg, addr = self.clientSocket.recvfrom(1024)
        return msg.decode()
        
    def get_wp(self):
        self.clientSocket.send("curr wp".encode())
        msg,addr = self.clientSocket.recvfrom(1024)
        return msg.decode()
        
    def send_acc(self, dir):
        if dir == "forward" or dir == "backward" or dir == "right" \
            or dir == "left" or dir == "up" or dir == "down" or dir == "stop":
            self.clientSocket.send(dir.encode())
        else:
            raise Exception("Acceleration direction not recognized")
            
    def send_wp(self, x, y, z, theta):
        str = "wp " + x + "," + y + "," + z + "," + theta
        self.clientSocket.send(str.encode())
        
    def send_drive(self,mode):
        str = "mode " + mode
        self.clientSocket.send(str.encode())
    
    def exit(self):
        self.clientSocket.send("quit".encode())
        self.clientSocket.recvfrom(1024)
    
    def close(self):
        self.clientSocket.close()

class UI:
    
    # Screen size
    size = width, height = (500, 500)
    
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY_BACK = (218, 210, 216)
    GRAY_DARK = (70, 70, 85)
    GRAYED_OUT = (170, 175, 180)
    BLUE_DARK = (16, 37, 66)
    BLUE_MED = (25, 100, 126)
    BLUE_LIGHT = (15, 139, 141)
    GREEN = (105, 153, 93)
    RED = (168, 32, 26)
    YELLOW = (236, 154, 41)
    LIST_TITLE_COLOR = (16, 89, 20)
    LIST_HEADER_COLOR = (28, 128, 33)
    LIST_ENTRY_COLOR = (194, 237, 197)
    TXT_COLOR_INACTIVE = WHITE
    TXT_COLOR_ACTIVE = pygame.Color('dodgerblue2')
        
    #### Object locations and sizes ####
    
    # General spacing
    vert_space = 15
    title_space = 10
    horiz_space = 40
    
    # Quit button size
    quit_size = (40,20)
    
    # Quit button
    quit_x = width - quit_size[0] - 10
    quit_y = 10
    
    # Header
    header_x = 0.5*quit_x
    header_y = 30
    
    # Navigation mode button size and spacing
    mode_but_size = (80,40)
    mode_but_space = mode_but_size[0] + 20
    
    # AprilTag localization table
    # UL of table
    AT_table_x = 10
    AT_table_y = header_y + 20 + vert_space
    
    # AprilTag localization table row size
    AT_table_size = (3*mode_but_space - 20,20)
    
    # AprilTag localization table number of rows & columns
    AT_table_rows = 3
    AT_table_cols = 4
    
    # Localization information
    # Center of "Location" title text
    loc_x = AT_table_x + AT_table_size[0] + horiz_space
    loc_y = AT_table_y + title_space
    
    # Time of flight (TOF) distances table
    # UL of table
    TOF_table_x = AT_table_x
    TOF_table_y = AT_table_y + AT_table_rows*AT_table_size[1] + vert_space + title_space
    
    # TOF table row size
    TOF_table_size = AT_table_size
    
    # TOF table rows and columns
    global TOF_dist
    TOF_table_rows = 3
    TOF_table_cols = len(TOF_dist)
    
    # Enable switch size
    switch_size = (30,60)
    
    # Enable AprilTag switch UL
    # AT_switch_x = AT_table_x + AT_table_size[0]/(num_switches + 1) - 0.5*switch_size[0]
    # AT_switch_y = AT_table_y + (AT_table_rows)*AT_table_size[1] + vert_space + title_space
    AT_switch_x = AT_table_x + AT_table_size[0] + horiz_space
    AT_switch_y = AT_table_y + 0.5*AT_table_rows*AT_table_size[1] - 0.5*switch_size[1]
    
    # Enable TOF switch UL
    TOF_switch_x = TOF_table_x + TOF_table_size[0] + horiz_space
    TOF_switch_y = TOF_table_y + 0.5*TOF_table_rows*TOF_table_size[1] - 0.5*switch_size[1]
    
    # Enable projector switch UL
    # proj_switch_x = AT_switch_x + AT_table_size[0]/(num_switches + 1)
    # proj_switch_y = AT_switch_y
    proj_switch_x = AT_switch_x + switch_size[0] + horiz_space
    proj_switch_y = AT_switch_y + 0.5*(TOF_switch_y + switch_size[1] - AT_switch_y) - 0.5*switch_size[1]
    
    # Navigation mode buttons
    # UL of leftmost button
    mode_x = TOF_table_x
    mode_y = TOF_table_y + TOF_table_rows*TOF_table_size[1] + vert_space
    
    # Manual control position buttons
    # UL of up arrow key
    pos_x = mode_x + 105
    pos_y = mode_y + mode_but_size[1] + vert_space + title_space
    
    # Manual control altitude buttons
    # UL of up arrow key
    alt_x = pos_x + 200
    alt_y = pos_y
    
    # Waypoint control textbox size
    wp_tb_size = (50,20)
    
    # Current waypoint x center
    curr_wp_x_x = mode_x + 0.5*wp_tb_size[0]
    curr_wp_x_y = mode_y + mode_but_size[1] + vert_space + title_space + 30
    
    # Current waypoint y center
    curr_wp_y_x = curr_wp_x_x + wp_tb_size[0] + 10
    curr_wp_y_y = curr_wp_x_y
    
    # Current waypoint z center
    curr_wp_z_x = curr_wp_y_x + wp_tb_size[0] + 10
    curr_wp_z_y = curr_wp_x_y
    
    # Current waypoint theta center
    curr_wp_theta_x = curr_wp_z_x + wp_tb_size[0] + 10
    curr_wp_theta_y = curr_wp_x_y
    
    # Waypoint control UL x input textbox
    wp_x_x = curr_wp_x_x - 0.5*wp_tb_size[0]
    wp_x_y = curr_wp_x_y + vert_space + title_space + 20
    
    # Waypoint control UL y input textbox
    wp_y_x = wp_x_x + wp_tb_size[0] + 10
    wp_y_y = wp_x_y
    
    # Waypoint control UL z input textbox
    wp_z_x = wp_y_x + wp_tb_size[0] + 10
    wp_z_y = wp_x_y
    
    # Waypoint control UL theta input textbox
    wp_theta_x = wp_z_x + wp_tb_size[0] + 10
    wp_theta_y = wp_x_y
    
    # Waypoint control UL send button
    wp_send_x = wp_theta_x + wp_tb_size[0] + 10
    wp_send_y = wp_x_y
    
    # Center running error text
    err_x = width/2
    err_y = height - 10
    
    # Arrow key images
    up_arrow = pygame.image.load("up_arrow.png")
    down_arrow = pygame.image.load("down_arrow.png")
    right_arrow = pygame.image.load("right_arrow.png")
    left_arrow = pygame.image.load("left_arrow.png")

    def __draw_header(self):
        txt_surf = self.header_font.render("LTA Swarm Base Station", True, self.YELLOW)
        txt_rect = txt_surf.get_rect(center=(self.header_x,self.header_y))
        self.screen.blit(txt_surf, txt_rect)

    def __draw_loc(self):
        # Draw position
        title_surf = self.font.render("Position", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.loc_x,self.loc_y))
        self.screen.blit(title_surf, title_rect)
        txt_surf= self.font.render(coords, True, self.BLACK)
        txt_rect = txt_surf.get_rect(center=(self.loc_x, self.loc_y+20))
        self.screen.blit(txt_surf, txt_rect)

        # Draw altitude
        title_surf = self.font.render("Altitude", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.loc_x,self.loc_y+60))
        self.screen.blit(title_surf, title_rect)
        txt_surf= self.font.render(str(alt), True, self.BLACK)
        txt_rect = txt_surf.get_rect(center=(self.loc_x, self.loc_y+80))
        self.screen.blit(txt_surf, txt_rect)
        
        # Draw orientation
        title_surf = self.font.render("Heading", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.loc_x,self.loc_y+120))
        self.screen.blit(title_surf, title_rect)
        txt_surf= self.font.render(str(orient) + u"\u00b0", True, self.BLACK)
        txt_rect = txt_surf.get_rect(center=(self.loc_x, self.loc_y+140))
        self.screen.blit(txt_surf, txt_rect)
        
    def __draw_quit(self):
        text_surf = self.font.render("QUIT", True, self.WHITE)
        text_rect = text_surf.get_rect(center=(self.quit_x+0.5*self.quit_size[0],self.quit_y+0.5*self.quit_size[1]))
        button_surf = pygame.Surface(self.quit_size)
        button_surf.fill(self.RED)
        self.screen.blit(button_surf,(self.quit_x,self.quit_y))
        self.screen.blit(text_surf,text_rect)
        
    def __draw_table(self,x,y,rows,cols,row_size,title,headers,data,data_en,TOF_table):
    
        # Row & column text coordinates
        col_x = arange(x + 1./(2*cols)*row_size[0],x + row_size[0],1./cols*row_size[0])
        row_y = arange(y + 0.5*row_size[1],y + (rows+0.5)*row_size[1],row_size[1])
    
        # Title background
        back_surf = pygame.Surface(row_size)
        back_rect = (x, y)
        back_surf.fill(self.BLUE_DARK)
        self.screen.blit(back_surf, back_rect)
        
        # Title text
        txt_surf = self.font.render(title, True, self.WHITE)
        txt_rect = txt_surf.get_rect(center=(x + 0.5*row_size[0], row_y[0]))
        self.screen.blit(txt_surf, txt_rect)
        
        # Column headers background
        back_surf = pygame.Surface(row_size)
        back_rect = (x, y + row_size[1])
        back_surf.fill(self.BLUE_MED)
        self.screen.blit(back_surf, back_rect)
        
        # Header text
        for c in range(cols):
            txt_surf = self.font.render(headers[c], True, self.WHITE)
            txt_rect = txt_surf.get_rect(center=(col_x[c], row_y[1]))
            self.screen.blit(txt_surf, txt_rect)
        
        # Data background
        if TOF_table:
            global TOF_status
            for c in range(self.TOF_table_cols):
                back_surf = pygame.Surface((row_size[0]/float(self.TOF_table_cols)+1, row_size[1]))
                back_rect = (x + c*row_size[0]/float(self.TOF_table_cols), y + 2*row_size[1])
                if data_en:
                    if TOF_status[c] == 0:
                        back_surf.fill(self.GREEN)
                    elif TOF_status[c] == 1:
                        back_surf.fill(self.YELLOW)
                    else:
                        back_surf.fill(self.RED)
                else:
                    back_surf.fill(self.GRAYED_OUT)
                self.screen.blit(back_surf, back_rect)
        else:
            back_surf = pygame.Surface((row_size[0],(rows-2)*row_size[1]))
            back_rect = (x, y + 2*row_size[1])
            if data_en:
                back_surf.fill(self.BLUE_LIGHT)
            else:
                back_surf.fill(self.GRAYED_OUT)
            self.screen.blit(back_surf, back_rect)
        
        # Table lines
        for c in range(1,cols):
            pygame.draw.line(self.screen, self.BLACK, (x+(c/float(cols))*row_size[0], y+row_size[1]), (x+(c/float(cols))*row_size[0], y+rows*row_size[1]-1))
        for r in range(1,rows):
            pygame.draw.line(self.screen, self.BLACK, (x, y+r*row_size[1]), (x+row_size[0]-1, y+r*row_size[1]))
        
        # Data text
        for c in range(cols):
            if rows == 3:
                if data[c] is not None:
                    txt_surf = self.font.render(str(data[c]), True, self.BLACK)
                    txt_rect = txt_surf.get_rect(center=(col_x[c], row_y[2]))
                    self.screen.blit(txt_surf, txt_rect)
            else:
                for r in range(rows-2):
                    if data[c][r] is not None:
                        txt_surf = self.font.render(str(data[c][r]), True, self.BLACK)
                        txt_rect = txt_surf.get_rect(center=(col_x[c], row_y[r+2]))
                        self.screen.blit(txt_surf, txt_rect)
        
    def __draw_AT_table(self):
        
        global AT_ID, coords, alt, orient
        title = "AprilTag Robot Localization"
        headers = ["Visible ID", "Position", "Altitude", "Orientation"]
        data = [AT_ID, coords, alt, orient]
        
        self.__draw_table(self.AT_table_x, self.AT_table_y, self.AT_table_rows, self.AT_table_cols, self.AT_table_size, title, headers, data, self.AT_en, False)
            
    def __draw_TOF_table(self):
    
        global TOF_dist
        title = "Time of Flight Distances"
        headers = ["Left", "Forward", "Right"]
        
        self.__draw_table(self.TOF_table_x, self.TOF_table_y, self.TOF_table_rows, self.TOF_table_cols, self.TOF_table_size, title, headers, TOF_dist, self.TOF_en, True)
        
    def __draw_switch(self,x,y,on,title):
        
        # Title
        title_surf = self.font.render(title, True, self.BLACK)
        title_rect = title_surf.get_rect(center=(x + 0.5*self.switch_size[0], y-10))
        
        # Background
        back_surf = pygame.Surface(self.switch_size)
        back_rect = (x,y)
        
        # Switch
        sw_surf = pygame.Surface((self.switch_size[0] - 4, self.switch_size[1]/2 - 4))
        
        if on:
            # Switch in on position
            back_surf.fill(self.GREEN)
            sw_rect = (x+2,y+2)
            sw_surf.fill(self.WHITE)
            txt_surf = self.font.render("ON", True, self.WHITE)
            txt_rect = txt_surf.get_rect(center=(x + 0.5*self.switch_size[0], y + 0.75*self.switch_size[1]))
        else:
            # Switch in off position
            back_surf.fill(self.RED)
            sw_rect = (x+2,y + 0.5*self.switch_size[1] + 2)
            sw_surf.fill(self.WHITE)
            txt_surf = self.font.render("OFF", True, self.WHITE)
            txt_rect = txt_surf.get_rect(center=(x + 0.5*self.switch_size[0], y + 0.25*self.switch_size[1]))
        
        self.screen.blit(title_surf, title_rect)
        self.screen.blit(back_surf, back_rect)
        self.screen.blit(sw_surf, sw_rect)
        self.screen.blit(txt_surf, txt_rect)
        
    def __draw_drive_sel(self):
        txt_x = self.mode_x + self.mode_but_size[0]/2
        txt_y = self.mode_y + self.mode_but_size[1]/2
        for i in range(3):
   
            # Background
            back_surf = pygame.Surface(self.mode_but_size)
            back_rect = (self.mode_x + i*self.mode_but_space, self.mode_y)
            if i == self.drive:
                # Currently in this mode
                back_surf.fill(self.GREEN)
            else:
                # Not in this mode
                back_surf.fill(self.RED)
            self.screen.blit(back_surf, back_rect)
            
            # Text
            if i == 0:
                txt = "Auto"
            elif i == 1:
                txt = "Waypoint"
            elif i == 2:
                txt = "Manual"
            txt_surf = self.font.render(txt, True, self.WHITE)
            txt_rect = txt_surf.get_rect(center=(txt_x + i*self.mode_but_space,txt_y))
            self.screen.blit(txt_surf, txt_rect)
            
    def __draw_man_ctrl(self):
    
        # Position arrows
        pos_surf = self.font.render("Position", True, self.BLACK)
        pos_rect = pos_surf.get_rect(center=(self.pos_x + 35, self.pos_y - 10))
        self.screen.blit(pos_surf,pos_rect)
        self.screen.blit(self.up_arrow, (self.pos_x, self.pos_y))
        self.screen.blit(self.down_arrow, (self.pos_x, self.pos_y+80))
        self.screen.blit(self.right_arrow, (self.pos_x+80, self.pos_y+80))
        self.screen.blit(self.left_arrow, (self.pos_x-80, self.pos_y+80))
        
        # Altitude arrows
        alt_surf = self.font.render("Altitude", True, self.BLACK)
        alt_rect = alt_surf.get_rect(center=(self.alt_x + 35, self.alt_y - 10))
        self.screen.blit(alt_surf,alt_rect)
        self.screen.blit(self.up_arrow, (self.alt_x, self.alt_y))
        self.screen.blit(self.down_arrow, (self.alt_x, self.alt_y+80))
        
    def __draw_wp_ctrl(self):
        
        # Waypoint entry
        if self.wp_x_active:
            x_color = self.TXT_COLOR_ACTIVE
            y_color = self.TXT_COLOR_INACTIVE
            z_color = self.TXT_COLOR_INACTIVE
            theta_color = self.TXT_COLOR_INACTIVE
        elif self.wp_y_active:
            x_color = self.TXT_COLOR_INACTIVE
            y_color = self.TXT_COLOR_ACTIVE
            z_color = self.TXT_COLOR_INACTIVE
            theta_color = self.TXT_COLOR_INACTIVE
        elif self.wp_z_active:
            x_color = self.TXT_COLOR_INACTIVE
            y_color = self.TXT_COLOR_INACTIVE
            z_color = self.TXT_COLOR_ACTIVE
            theta_color = self.TXT_COLOR_INACTIVE
        elif self.wp_theta_active:
            x_color = self.TXT_COLOR_INACTIVE
            y_color = self.TXT_COLOR_INACTIVE
            z_color = self.TXT_COLOR_INACTIVE
            theta_color = self.TXT_COLOR_ACTIVE
        else:
            x_color = self.TXT_COLOR_INACTIVE
            y_color = self.TXT_COLOR_INACTIVE
            z_color = self.TXT_COLOR_INACTIVE
            theta_color = self.TXT_COLOR_INACTIVE
        
        # Draw title
        title_surf = self.font.render("Waypoint to Send", True, self.BLUE_MED)
        title_rect = title_surf.get_rect(center=((self.wp_y_x + self.wp_z_x + self.wp_tb_size[0])/2,self.wp_x_y-30))
        self.screen.blit(title_surf, title_rect)
        
        # Label y position
        label_y = self.wp_x_y - 10
        
        # Draw x textbox
        x_surf = pygame.Surface(self.wp_tb_size)
        x_surf.fill(x_color)
        x_txt_surf = self.font.render(self.wp_x_txt, True, self.BLACK)
        x_rect = pygame.Rect((self.wp_x_x,self.wp_x_y), self.wp_tb_size)
        x_label_surf = self.font.render("x", True, self.BLACK)
        x_label_rect = x_label_surf.get_rect(center=(self.wp_x_x + self.wp_tb_size[0]/2, label_y))
        self.screen.blit(x_surf,x_rect)
        self.screen.blit(x_txt_surf,x_rect)
        self.screen.blit(x_label_surf,x_label_rect)
        
        # Draw y textbox
        y_surf = pygame.Surface(self.wp_tb_size)
        y_surf.fill(y_color)
        y_txt_surf = self.font.render(self.wp_y_txt, True, self.BLACK)
        y_rect = pygame.Rect((self.wp_y_x,self.wp_y_y), self.wp_tb_size)
        y_label_surf = self.font.render("y", True, self.BLACK)
        y_label_rect = y_label_surf.get_rect(center=(self.wp_y_x + self.wp_tb_size[0]/2, label_y))
        self.screen.blit(y_surf,y_rect)
        self.screen.blit(y_txt_surf,y_rect)
        self.screen.blit(y_label_surf,y_label_rect)
        
        # Draw z textbox
        z_surf = pygame.Surface(self.wp_tb_size)
        z_surf.fill(z_color)
        z_txt_surf = self.font.render(self.wp_z_txt, True, self.BLACK)
        z_rect = pygame.Rect((self.wp_z_x,self.wp_z_y), self.wp_tb_size)
        z_label_surf = self.font.render("z", True, self.BLACK)
        z_label_rect = z_label_surf.get_rect(center=(self.wp_z_x + self.wp_tb_size[0]/2, label_y))
        self.screen.blit(z_surf,z_rect)
        self.screen.blit(z_txt_surf,z_rect)
        self.screen.blit(z_label_surf,z_label_rect)
        
        # Draw theta textbox
        theta_surf = pygame.Surface(self.wp_tb_size)
        theta_surf.fill(theta_color)
        theta_txt_surf = self.font.render(self.wp_theta_txt, True, self.BLACK)
        theta_rect = pygame.Rect((self.wp_theta_x,self.wp_theta_y), self.wp_tb_size)
        theta_label_surf = self.font.render(u"\u03B8", True, self.BLACK)
        theta_label_rect = theta_label_surf.get_rect(center=(self.wp_theta_x + self.wp_tb_size[0]/2, label_y))
        self.screen.blit(theta_surf,theta_rect)
        self.screen.blit(theta_txt_surf,theta_rect)
        self.screen.blit(theta_label_surf,theta_label_rect)
        
        # Draw send button
        text_surf = self.font.render("Send", True, self.WHITE)
        text_rect = text_surf.get_rect(center=(self.wp_send_x + self.wp_tb_size[0]/2,self.wp_send_y + self.wp_tb_size[1]/2))
        button_surf = pygame.Surface(self.wp_tb_size)
        button_surf.fill(self.GREEN)
        self.screen.blit(button_surf,(self.wp_send_x,self.wp_send_y))
        self.screen.blit(text_surf,text_rect)
        
    def __draw_curr_wp(self):
        
        # Draw title
        title_surf = self.font.render("Current Waypoint", True, self.BLUE_MED)
        title_rect = title_surf.get_rect(center=((self.curr_wp_y_x + self.curr_wp_z_x)/2,self.curr_wp_x_y-40))
        self.screen.blit(title_surf, title_rect)
        
        # Draw x
        title_surf = self.font.render("x", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.curr_wp_x_x,self.curr_wp_x_y-20))
        self.screen.blit(title_surf, title_rect)
        txt_surf= self.font.render(self.curr_wp_x, True, self.BLACK)
        txt_rect = txt_surf.get_rect(center=(self.curr_wp_x_x,self.curr_wp_x_y))
        self.screen.blit(txt_surf, txt_rect)
        
        # Draw y
        title_surf = self.font.render("y", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.curr_wp_y_x,self.curr_wp_y_y-20))
        self.screen.blit(title_surf, title_rect)
        txt_surf= self.font.render(self.curr_wp_y, True, self.BLACK)
        txt_rect = txt_surf.get_rect(center=(self.curr_wp_y_x,self.curr_wp_y_y))
        self.screen.blit(txt_surf, txt_rect)
        
        # Draw z
        title_surf = self.font.render("z", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.curr_wp_z_x,self.curr_wp_z_y-20))
        self.screen.blit(title_surf, title_rect)
        txt_surf= self.font.render(self.curr_wp_z, True, self.BLACK)
        txt_rect = txt_surf.get_rect(center=(self.curr_wp_z_x,self.curr_wp_z_y))
        self.screen.blit(txt_surf, txt_rect)
        
        # Draw theta
        title_surf = self.font.render(u"\u03B8", True, self.BLACK)
        title_rect = title_surf.get_rect(center=(self.curr_wp_theta_x,self.curr_wp_theta_y-20))
        self.screen.blit(title_surf, title_rect)
        txt_surf= self.font.render(self.curr_wp_theta, True, self.BLACK)
        txt_rect = txt_surf.get_rect(center=(self.curr_wp_theta_x,self.curr_wp_theta_y))
        self.screen.blit(txt_surf, txt_rect)

    def draw_error(self,text):
        self.screen.fill(self.WHITE)
        alt_surf= self.font.render(text, True, self.RED)
        alt_rect = alt_surf.get_rect(center=(self.width/2, self.width/2))
        self.screen.blit(alt_surf, alt_rect)
        pygame.display.flip()
        
    def __draw_error_running(self):
        if self.print_err:
            if time.time() - self.err_time >= 3:
                # Stop printing error after 3 sec
                self.__print_err = False
            else:
                text_surf = self.font.render(self.err_txt, True, self.RED)
                text_rect = text_surf.get_rect(center=(self.err_x,self.err_y))
                self.screen.blit(text_surf,text_rect)
        
    def wait_frame_rate(self):
        self.clock.tick(self.frame_rate)

    def update_screen(self):
        self.screen.fill(self.GRAY_BACK)
        self.__draw_header()
        #self.__draw_loc()
        self.__draw_quit()
        self.__draw_switch(self.AT_switch_x,self.AT_switch_y,self.AT_en,"AprilTags")
        self.__draw_switch(self.proj_switch_x,self.proj_switch_y,self.proj_en,"Projector")
        self.__draw_switch(self.TOF_switch_x,self.TOF_switch_y,self.TOF_en,"TOF Sensors")
        self.__draw_drive_sel()
        self.__draw_AT_table()
        self.__draw_TOF_table()
        self.__draw_error_running()
        if self.drive == 0:
            # Full auto mode
            self.__draw_curr_wp()
        elif self.drive == 1:
            # Waypoint mode
            self.__draw_wp_ctrl()
            self.__draw_curr_wp()
        elif self.drive == 2:
            # Manual mode
            self.__draw_man_ctrl()
        pygame.display.flip()

    def __init__(self):
        pygame.init()

        # window title 
        pygame.display.set_caption("LTA Base Station")
        
        # Fonts and size
        self.font = pygame.font.Font(None, 20)
        self.header_font = pygame.font.Font(None, 40)

        # Set the width and height of the screen [width, height]
        self.screen = pygame.display.set_mode(self.size)
        
        # Enable switch positions
        self.AT_en = True
        self.proj_en = True
        self.TOF_en = True
        
        # Drive type
        # 0 - auto, 1 - waypoint, 2 - manual
        self.drive = 2
        
        # Waypoint text entry
        self.wp_x_active = False
        self.wp_x_txt = ""
        self.wp_y_active = False
        self.wp_y_txt = ""
        self.wp_z_active = False
        self.wp_z_txt = ""
        self.wp_theta_active = False
        self.wp_theta_txt = ""
        
        # Current waypoint
        self.curr_wp_x = '0'
        self.curr_wp_y = '0'
        self.curr_wp_z = '1'
        self.curr_wp_theta = '0'

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()
        self.frame_rate = 30
        
        # Error to be printed
        self.print_err = False
        self.err_txt = ''
        self.err_time = time.time()
        
def get_AT_thread(ip,port):
    global AT_ID, coords, alt, orient
    server = conn(ip,port)
    AT_info = server.get_AT().split(',')
    AT_visible = bool(AT_info[0])
    if AT_visible:
        AT_ID = int(AT_info[1])
        coords = [float(AT_info[2]), float(AT_info[3])]
        alt = float(AT_info[4])
        orient = -1*float(AT_info[5])
        
def get_TOF_thread(ip,port):
    global TOF_dist, TOF_status
    server = conn(ip,port)
    TOF_info = server.get_TOF().split(',')
    for n in range(3):
        TOF_dist[n] = float(TOF_info[n])
        TOF_status[n] = int(TOF_info[n+3])
        
def man_control_thread(ip,port,dir):
    server = conn(ip,port)
    server.send_acc(dir)
    server.close()

def str_is_num(str):
    try:
        float(str)
        return True
    except ValueError:
        return False
    
def wp_control_thread(ip,port,ui):
    
    # Get coordinate strings
    x,y,z,theta = ui.wp_x_txt,ui.wp_y_txt,ui.wp_z_txt,ui.wp_theta_txt
    
    # Fill in default values for blank coordinates
    if x == '':
        x = '0'
    if y == '':
        y = '0'
    if z == '':
        z = '1'
    if theta == '':
        theta = '0'
        
    # Clear textbox selections
    ui.wp_x_active = False
    ui.wp_y_active = False
    ui.wp_z_active = False
    ui.wp_theta_active = False
    
    # Check that all entries are floats before sending
    if str_is_num(x):
        if str_is_num(y):
            if str_is_num(z):
                if str_is_num(theta):
                    server = conn(ip,port)
                    server.send_wp(x, y, z, theta)
                    server.close()
                else:
                    ui.print_err = True
                    ui.err_txt = u"\u03B8" + " value is not a number"
                    ui.err_time = time.time()
                    ui.wp_theta_active = True
            else:
                ui.print_err = True
                ui.err_txt = "z value is not a number"
                ui.err_time = time.time()
                ui.wp_z_active = True
        else:
            ui.print_err = True
            ui.err_txt = "y value is not a number"
            ui.err_time = time.time()
            ui.wp_y_active = True
    else:
        ui.print_err = True
        ui.err_txt = "x value is not a number"
        ui.err_time = time.time()
        ui.wp_x_active = True
        
def get_wp_thread(ip,port,ui):
    server = conn(ip,port)
    ui.curr_wp_x, ui.curr_wp_y, ui.curr_wp_z, ui.curr_wp_theta = server.get_wp().split(',')
    server.close()
        
def send_drive_thread(ip,port,mode):
    server = conn(ip,port)
    server.send_drive(str(mode))
    server.close()
    
def terminate_server(ip,port):
    server = conn(ip,port)
    server.exit()
    server.close()
    

if __name__ == '__main__':
 
    server_ip = '192.168.1.114'
   # server_ip = '127.0.0.1'
    server_port = 12002
    
    ui = UI()
    
    server_counter = 0
    
    try:
        while running:
            
            # Only query drone for current waypoint, AprilTag data, and TOF data every 30 frames
            if ui.drive == 0 and server_counter == 30:
                # Waypoint only changes in auto mode
                wp_thread = threading.Thread(target=get_wp_thread, args=(server_ip,server_port,ui))
                wp_thread.start()
            elif ui.AT_en and server_counter == 60:
                # Update AprilTag if enabled
                at_thread = threading.Thread(target=get_AT_thread, args=(server_ip,server_port))
                at_thread.start()
            elif ui.TOF_en and server_counter == 25:
                # Update TOF distances if enabled
                tof_thread = threading.Thread(target=get_TOF_thread, args=(server_ip,server_port))
                tof_thread.start()
                
            if server_counter == 60:
                server_counter = 1
            else:
                server_counter += 1
            
            # Handle PyGame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # X button
                    running = False
                    break
                elif(event.type is MOUSEBUTTONDOWN):
                    # Mouse click
                    x,y = pygame.mouse.get_pos()
                    
                    # If in waypoint mode and click somewhere else, clear textbox selection
                    if ui.drive == 1:
                        ui.wp_x_active = False
                        ui.wp_y_active = False
                        ui.wp_z_active = False
                        ui.wp_theta_active = False
                        
                    if x > ui.quit_x and x < ui.quit_x + 40 and y < ui.quit_y + 20 and y > ui.quit_y:
                        # Quit button clicked
                        running = False
                        terminate_server(server_ip,server_port)
                    elif x < ui.AT_switch_x + ui.switch_size[0] and x > ui.AT_switch_x and \
                            y < ui.AT_switch_y + ui.switch_size[1] and y > ui.AT_switch_y:
                        # AprilTag enable switch clicked
                        ui.AT_en = not ui.AT_en
                        if not ui.AT_en:
                            # Clear AT and localization info if ATs disabled
                            AT_ID = None
                            coords = None
                            alt = None
                            orient = None
                    elif x < ui.proj_switch_x + ui.switch_size[0] and x > ui.proj_switch_x and \
                            y < ui.proj_switch_y + ui.switch_size[1] and y > ui.proj_switch_y:
                        # Projector enable switch clicked
                        ui.proj_en = not ui.proj_en
                    elif x < ui.TOF_switch_x + ui.switch_size[0] and x > ui.TOF_switch_x and \
                            y < ui.TOF_switch_y + ui.switch_size[1] and y > ui.TOF_switch_y:
                        # Projector enable switch clicked
                        ui.TOF_en = not ui.TOF_en
                    elif x < ui.mode_x + ui.mode_but_size[0] and x > ui.mode_x and \
                            y < ui.mode_y + ui.mode_but_size[1] and y > ui.mode_y:
                        # Auto button clicked
                        ui.drive = 0
                        wp_thread = threading.Thread(target=get_wp_thread, args=(server_ip,server_port,ui))
                        wp_thread.start()
                        time.sleep(0.02)
                        drive_thread = threading.Thread(target=send_drive_thread, args=(server_ip,server_port,ui.drive))
                        drive_thread.start()
                        ui.print_err = True
                        ui.err_txt = "Warning: Auto mode not yet supported"
                        ui.err_time = time.time()
                    elif x < ui.mode_x + ui.mode_but_size[0] + ui.mode_but_space and x > ui.mode_x + ui.mode_but_space and \
                            y < ui.mode_y + ui.mode_but_size[1] and y > ui.mode_y:
                        # Waypoint button clicked
                        ui.drive = 1
                        wp_thread = threading.Thread(target=get_wp_thread, args=(server_ip,server_port,ui))
                        wp_thread.start()
                        time.sleep(0.02)
                        drive_thread = threading.Thread(target=send_drive_thread, args=(server_ip,server_port,ui.drive))
                        drive_thread.start()  
                        ui.print_err = True
                        ui.err_txt = "Warning: Waypoint mode not yet supported"
                        ui.err_time = time.time()                   
                    elif x < ui.mode_x + ui.mode_but_size[0] + 2*ui.mode_but_space and x > ui.mode_x + 2*ui.mode_but_space and \
                            y < ui.mode_y + ui.mode_but_size[1] and y > ui.mode_y:
                        # Manual button clicked
                        ui.drive = 2
                        time.sleep(0.02)
                        drive_thread = threading.Thread(target=send_drive_thread, args=(server_ip,server_port,ui.drive))
                        drive_thread.start()    
                    elif ui.drive == 1:
                        # Waypoint drive mode
                        if x > ui.wp_x_x and x < ui.wp_x_x + ui.wp_tb_size[0] and y > ui.wp_x_y and y < ui.wp_x_y + ui.wp_tb_size[1]:
                            # Waypoint x input clicked
                            ui.wp_x_active = True
                        elif x > ui.wp_y_x and x < ui.wp_y_x + ui.wp_tb_size[0] and y > ui.wp_y_y and y < ui.wp_y_y + ui.wp_tb_size[1]:
                            # Waypoint y input clicked
                            ui.wp_y_active = True
                        elif x > ui.wp_z_x and x < ui.wp_z_x + ui.wp_tb_size[0] and y > ui.wp_z_y and y < ui.wp_z_y + ui.wp_tb_size[1]:
                            # Waypoint z input clicked
                            ui.wp_z_active = True
                        elif x > ui.wp_theta_x and x < ui.wp_theta_x + ui.wp_tb_size[0] and y > ui.wp_theta_y and y < ui.wp_theta_y + ui.wp_tb_size[1]:
                            # Waypoint theta input clicked
                            ui.wp_theta_active = True
                        elif x > ui.wp_send_x and x < ui.wp_send_x + ui.wp_tb_size[0] and y > ui.wp_send_y and y < ui.wp_send_y + ui.wp_tb_size[1]:
                            # Send waypoint clicked
                            move_thread = threading.Thread(target=wp_control_thread, args=(server_ip,server_port,ui))
                            move_thread.start()
                            time.sleep(0.02)
                            wp_thread = threading.Thread(target=get_wp_thread, args=(server_ip,server_port,ui))
                            wp_thread.start()                            
                    elif ui.drive == 2:
                        # Manual drive mode
                        if x > ui.pos_x and x < ui.pos_x + 70 and y > ui.pos_y and y < ui.pos_y + 70:
                            # Forward button clicked
                            move_thread = threading.Thread(target=man_control_thread, args=(server_ip,server_port,"forward"))
                            move_thread.start()
                        elif x > ui.pos_x and x < ui.pos_x + 70 and y > ui.pos_y + 80 and y < ui.pos_y + 150:
                            # Back button clicked
                            move_thread = threading.Thread(target=man_control_thread, args=(server_ip,server_port,"backward"))
                            move_thread.start()
                        elif x > ui.pos_x + 80 and x < ui.pos_x + 150 and y > ui.pos_y + 80 and y < ui.pos_y + 150:
                            # Right button clicked
                            move_thread = threading.Thread(target=man_control_thread, args=(server_ip,server_port,"right"))
                            move_thread.start()
                        elif x > ui.pos_x - 80 and x < ui.pos_x - 10 and y > ui.pos_y + 80 and y < ui.pos_y + 150:
                            # Left button clicked
                            move_thread = threading.Thread(target=man_control_thread, args=(server_ip,server_port,"left"))
                            move_thread.start()
                        elif x > ui.alt_x and x < ui.alt_x + 70 and y > ui.alt_y and y < ui.alt_y + 70:
                            # Up button clicked
                            move_thread = threading.Thread(target=man_control_thread, args=(server_ip,server_port,"up"))
                            move_thread.start()
                        elif x > ui.alt_x and x < ui.alt_x + 70 and y > ui.alt_y + 80 and y < ui.alt_y + 150:
                            # Down button clicked
                            move_thread = threading.Thread(target=man_control_thread, args=(server_ip,server_port,"down"))
                            move_thread.start()
                elif(event.type is MOUSEBUTTONUP) and ui.drive == 2:
                    # Stop motors
                    move_thread = threading.Thread(target=man_control_thread, args=(server_ip,server_port,"stop"))
                    move_thread.start()
                elif(event.type is KEYDOWN) and ui.drive == 1:
                    if event.key == pygame.K_RETURN:
                        move_thread = threading.Thread(target=wp_control_thread, args=(server_ip,server_port,ui))
                        move_thread.start()
                        time.sleep(0.02)
                        wp_thread = threading.Thread(target=get_wp_thread, args=(server_ip,server_port,ui))
                        wp_thread.start()
                    elif ui.wp_x_active:
                        if event.key == pygame.K_BACKSPACE:
                            ui.wp_x_txt = ui.wp_x_txt[:-1]
                        elif event.key == pygame.K_TAB:
                            ui.wp_x_active = False
                            ui.wp_y_active = True
                        else:
                            ui.wp_x_txt += event.unicode
                    elif ui.wp_y_active:
                        if event.key == pygame.K_BACKSPACE:
                            ui.wp_y_txt = ui.wp_y_txt[:-1]
                        elif event.key == pygame.K_TAB:
                            ui.wp_y_active = False
                            ui.wp_z_active = True
                        else:
                            ui.wp_y_txt += event.unicode
                    elif ui.wp_z_active:
                        if event.key == pygame.K_BACKSPACE:
                            ui.wp_z_txt = ui.wp_z_txt[:-1]
                        elif event.key == pygame.K_TAB:
                            ui.wp_z_active = False
                            ui.wp_theta_active = True
                        else:
                            ui.wp_z_txt += event.unicode
                    elif ui.wp_theta_active:
                        if event.key == pygame.K_BACKSPACE:
                            ui.wp_theta_txt = ui.wp_theta_txt[:-1]
                        elif event.key == pygame.K_TAB:
                            ui.wp_theta_active = False
                            ui.wp_x_active = True
                        else:
                            ui.wp_theta_txt += event.unicode
                else:
                    pass
            
            ui.update_screen()
            
            time.sleep(0.02)
            
            ui.wait_frame_rate()
    except:
        pygame.quit()
        raise
    
    pygame.quit()

