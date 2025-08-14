# Put these at the top of your file
import pygame
import pygame.locals
import hmsysteme
import qrcode
import socket
import math
import os
from io import BytesIO

def startscreen(wifi_ssid=None, wifi_password=None, debug_flag = False):
    
    # Initialize Pygame
    pygame.init()
    
    # Get screen size
    size = hmsysteme.get_size()
    if debug_flag:
        screen = pygame.display.set_mode(size)
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()
    
    # Colors
    BACKGROUND = (30, 30, 35)
    WIFI_BG = (106, 137, 103)     # #6A8967
    SERVER_BG = (56, 73, 89)      # #384959
    TEXT_COLOR = (255, 255, 255)
    ACCENT_COLOR = (100, 200, 255)
    QR_BG = (255, 255, 255)
    BORDER_COLOR = (200, 200, 200)
    SHADOW_COLOR = (20, 20, 25)
    
    # Fonts
    title_font = pygame.font.Font(None, 48)
    subtitle_font = pygame.font.Font(None, 32)
    text_font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)
    
    # Load icon images - don't pre-scale, let draw_icon handle it properly
    try:
        wifi_icon_img = pygame.image.load("wifi.png")
        # Don't scale here - let draw_icon handle aspect ratio properly
    except:
        wifi_icon_img = None
    
    try:
        server_icon_img = pygame.image.load("webserver.png")
        # Don't scale here - let draw_icon handle aspect ratio properly
    except:
        server_icon_img = None
    
    def draw_icon(surface, x, y, size, color, icon_img, fallback_func):
        """Draw icon image or fallback to drawn icon"""
        if icon_img:
            # For the WiFi icon (640x360), maintain proper aspect ratio
            original_rect = icon_img.get_rect()
            aspect_ratio = original_rect.width / original_rect.height
            
            # Calculate dimensions that fit within the size while maintaining aspect ratio
            if aspect_ratio > 1:  # Wider than tall (like 640x360)
                new_width = size
                new_height = int(size / aspect_ratio)
            else:  # Taller than wide or square
                new_width = int(size * aspect_ratio)
                new_height = size
            
            # Scale maintaining aspect ratio
            scaled_icon = pygame.transform.scale(icon_img, (new_width, new_height))
            
            # Center the scaled icon within the allocated space
            icon_x = x + (size - new_width) // 2
            icon_y = y + (size - new_height) // 2
            
            surface.blit(scaled_icon, (icon_x, icon_y))
        else:
            fallback_func(surface, x, y, size, color)
    
    def get_server_url():
        """Get the server URL"""
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return f"http://{ip}:8081"
        except:
            return "http://192.168.1.1:8081"
        """Get the server URL"""
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return f"http://{ip}:8081"
        except:
            return "http://192.168.1.1:8081"
    
    def generate_wifi_qr_data(ssid, password=None):
        """Generate WiFi QR code data"""
        if password:
            return f"WIFI:T:WPA;S:{ssid};P:{password};;"
        else:
            return ssid  # Just the SSID name if no password
    
    def generate_qr_surface(data, size=200):
        """Generate QR code as pygame surface"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create PIL image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to pygame surface
        img_str = BytesIO()
        qr_img.save(img_str, format='PNG')
        img_str.seek(0)
        qr_surface = pygame.image.load(img_str)
        
        # Scale to desired size
        return pygame.transform.scale(qr_surface, (size, size))
    
    def draw_rounded_rect(surface, color, rect, radius):
        """Draw a rectangle with rounded corners"""
        x, y, w, h = rect
        
        # Draw main rectangles
        pygame.draw.rect(surface, color, (x + radius, y, w - 2 * radius, h))
        pygame.draw.rect(surface, color, (x, y + radius, w, h - 2 * radius))
        
        # Draw corners
        pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + w - radius, y + radius), radius)
        pygame.draw.circle(surface, color, (x + radius, y + h - radius), radius)
        pygame.draw.circle(surface, color, (x + w - radius, y + h - radius), radius)
    
    def draw_wifi_icon(surface, x, y, size, color):
        """Draw a WiFi icon"""
        center_x, center_y = x + size // 2, y + size // 2
        
        # Draw WiFi arcs (simplified as crescents)
        for i, (radius, thickness) in enumerate([(size//6, 6), (size//4, 6), (size//3, 6)]):  # Increased thickness
            # Draw arc segments
            start_angle = 225  # degrees
            end_angle = 315
            
            # Create points for arc
            points = []
            for angle in range(start_angle, end_angle + 1, 5):
                rad = math.radians(angle)
                px = center_x + radius * math.cos(rad)
                py = center_y + radius * math.sin(rad)
                points.append((px, py))
            
            if len(points) > 1:
                pygame.draw.lines(surface, color, False, points, thickness)
        
        # Draw center dot (bigger)
        pygame.draw.circle(surface, color, (center_x, center_y + size // 8), size // 8)
    
    def draw_step_number(surface, x, y, number, color, bg_color):
        """Draw a large circled step number"""
        radius = 40
        center_x = x + radius
        center_y = y + radius
        
        # Draw circle background
        pygame.draw.circle(surface, bg_color, (center_x, center_y), radius)
        pygame.draw.circle(surface, color, (center_x, center_y), radius, 4)
        
        # Draw number
        number_font = pygame.font.Font(None, 72)
        number_text = number_font.render(str(number), True, color)
        number_rect = number_text.get_rect(center=(center_x, center_y))
        surface.blit(number_text, number_rect)
    
    def draw_server_icon(surface, x, y, size, color):
        """Draw a server/computer icon"""
        # Main server body
        body_width = size * 2 // 3
        body_height = size // 2
        body_x = x + size // 6
        body_y = y + size // 4
        
        pygame.draw.rect(surface, color, (body_x, body_y, body_width, body_height), 6)  # Thicker lines
        
        # Server segments
        for i in range(3):
            seg_y = body_y + 16 + i * (body_height - 32) // 3  # Adjusted spacing
            pygame.draw.line(surface, color, (body_x + 16, seg_y), (body_x + body_width - 16, seg_y), 4)  # Thicker lines
            # Small status dots (bigger)
            pygame.draw.circle(surface, color, (body_x + body_width - 32, seg_y), 4)
    
    def draw_qr_section(surface, qr_surface, icon_func, title, subtitle, bg_color, x, y, width, height, step_number):
        """Draw a complete QR section with background, icon, and text"""
        # Draw shadow
        shadow_offset = 8
        draw_rounded_rect(surface, SHADOW_COLOR, 
                         (x + shadow_offset, y + shadow_offset, width, height), 20)
        
        # Draw main background
        draw_rounded_rect(surface, bg_color, (x, y, width, height), 20)
        
        # Draw step number (top left corner)
        step_x = x + 20
        step_y = y + 20
        draw_step_number(surface, step_x, step_y, step_number, TEXT_COLOR, bg_color)
        
        # Draw icon (use image if available, otherwise fallback to drawn icon)
        icon_size_wifi = 240  # Triple size: 60 -> 180
        icon_x_wifi = x + width // 2 - icon_size_wifi // 2
        icon_y_wifi = y + 65  # Moved down to make space for larger icons
        icon_size_server = 150  # Triple size: 60 -> 180
        icon_x_server = x + width // 2 - icon_size_server // 2
        icon_y_server = y + 100  # Moved down to make space for larger icons
        
        # Determine which icon to use
        if "WiFi" in title or "wifi" in title.lower():
            draw_icon(surface, icon_x_wifi, icon_y_wifi, icon_size_wifi, TEXT_COLOR, wifi_icon_img, draw_wifi_icon)
        else:
            draw_icon(surface, icon_x_server, icon_y_server, icon_size_server, TEXT_COLOR, server_icon_img, draw_server_icon)
        
        # Draw title (moved down)
        title_text = title_font.render(title, True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(x + width // 2, icon_y_server + icon_size_server + 30))
        surface.blit(title_text, title_rect)
        
        # Draw QR code or message
        if qr_surface:
            # Draw QR code background
            qr_size = qr_surface.get_width()
            qr_x = x + width // 2 - qr_size // 2
            qr_y = title_rect.bottom + 40  # Position below title
            
            # QR background with rounded corners and no border
            padding = 15
            qr_bg_rect = (qr_x - padding, qr_y - padding, qr_size + 2*padding, qr_size + 2*padding)
            draw_rounded_rect(surface, QR_BG, qr_bg_rect, 20)  # Increased radius from 10 to 20
            
            # Draw QR code
            surface.blit(qr_surface, (qr_x, qr_y))
            
            # Draw subtitle below QR code
            subtitle_y = qr_y + qr_size + 40
        else:
            # No QR code, just show message
            subtitle_y = title_rect.bottom + 60
        
        # Draw subtitle (handle multi-line text) - ensure it stays within bounds
        lines = subtitle.split('\n')
        line_height = 35
        total_text_height = len(lines) * line_height
        
        # Ensure text stays within the section bounds
        max_subtitle_y = y + height - total_text_height - 20  # 20px padding from bottom
        final_subtitle_y = min(subtitle_y, max_subtitle_y)
        
        for i, line in enumerate(lines):
            if line.strip():  # Only render non-empty lines
                subtitle_text = subtitle_font.render(line, True, TEXT_COLOR)
                subtitle_rect = subtitle_text.get_rect(center=(x + width // 2, final_subtitle_y + i * line_height))
                surface.blit(subtitle_text, subtitle_rect)
    
    # Generate QR codes (only once since they don't change)
    server_url = get_server_url()
    server_qr = generate_qr_surface(server_url, 180)
    
    # WiFi QR code only if password is provided
    if wifi_password:
        wifi_qr_data = generate_wifi_qr_data(wifi_ssid or "HM01", wifi_password)
        wifi_qr = generate_qr_surface(wifi_qr_data, 180)
    else:
        wifi_qr = None  # No QR code, just show text message
    
    # Main loop
    running = True
    screen_drawn = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
        
        # Only redraw if not drawn yet (minimal redrawing)
        if not screen_drawn:
            # Fill background
            screen.fill(BACKGROUND)
            
            # Draw main title at top (white color) - moved down from very top
            main_title = title_font.render("Connection Steps", True, TEXT_COLOR)
            title_rect = main_title.get_rect(center=(size[0] // 2, 60))  # Changed from 30 to 60
            screen.blit(main_title, title_rect)
            
            # Calculate layout - increase section height to accommodate larger content
            screen_width, screen_height = size
            section_width = screen_width // 2 - 60
            section_height = screen_height - 120  # Increased from 140 to accommodate content
            
            # Draw WiFi section (left) - Step 1
            wifi_title = "Connect to WiFi"
            if wifi_password:
                wifi_subtitle = f"Scan QR code to connect\nto network: {wifi_ssid or 'HM01'}"
            else:
                wifi_subtitle = f"Please connect to WiFi network:\n\n'{wifi_ssid or 'HM01'}'"
            
            draw_qr_section(screen, wifi_qr, draw_wifi_icon, wifi_title, wifi_subtitle,
                          WIFI_BG, 30, 90, section_width, section_height, 1)
            
            # Draw Server section (right) - Step 2
            server_title = "Open Web Interface"
            server_subtitle = f"Scan QR code or visit:\n{server_url}"
            
            draw_qr_section(screen, server_qr, draw_server_icon, server_title, server_subtitle,
                          SERVER_BG, screen_width // 2 + 30, 90, section_width, section_height, 2)
            
            pygame.display.flip()
            screen_drawn = True
        
        # Small delay to prevent high CPU usage
        clock.tick(30)  # Very low FPS since we're not animating

if __name__ == '__main__':
    startscreen(None, None, True, "HM01", None)