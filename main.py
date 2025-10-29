import sys
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class Planet:
    def __init__(self, radius, distance, rotation_speed, revolution_speed, color, has_rings=False):
        self.radius = radius
        self.distance = distance
        self.rotation_angle = 0
        self.revolution_angle = 0
        self.rotation_speed = rotation_speed
        self.revolution_speed = revolution_speed
        self.color = color
        self.has_rings = has_rings
        self.moons = []

class SolarSystem:
    def __init__(self):
        self.planets = []
        self.stars = []
        self.light_position = [5.0, 5.0, 5.0, 1.0]
        self.camera_distance = 15.0
        self.camera_angle_x = 0
        self.camera_angle_y = 0
        self.mouse_dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        
    def create_solar_system(self):
        sun = Planet(2.0, 0, 0.5, 0, [1.0, 0.8, 0.0])
        
        mercury = Planet(0.2, 3.0, 2.0, 1.5, [0.7, 0.7, 0.7])
        venus = Planet(0.4, 4.5, 1.5, 1.2, [0.9, 0.7, 0.3])
        earth = Planet(0.5, 6.0, 1.0, 1.0, [0.2, 0.4, 0.9])
        mars = Planet(0.3, 7.5, 1.2, 0.8, [0.8, 0.3, 0.2])
        jupiter = Planet(1.2, 10.0, 0.8, 0.5, [0.8, 0.6, 0.4])
        saturn = Planet(1.0, 13.0, 0.7, 0.4, [0.9, 0.8, 0.5], has_rings=True)
        
        moon = Planet(0.1, 1.0, 3.0, 2.0, [0.8, 0.8, 0.8])
        earth.moons.append(moon)
        
        self.planets = [sun, mercury, venus, earth, mars, jupiter, saturn]
        self.light_position = [0, 0, 0, 1.0]

def draw_sphere(radius, slices, stacks, color):
    glColor3f(*color)
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluSphere(quadric, radius, slices, stacks)
    gluDeleteQuadric(quadric)

def draw_ring(inner_radius, outer_radius, color):
    glColor3f(*color)
    glBegin(GL_QUAD_STRIP)
    for i in range(0, 361, 10):
        angle = math.radians(i)
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        
        glVertex3f(inner_radius * cos_angle, 0, inner_radius * sin_angle)
        glVertex3f(outer_radius * cos_angle, 0, outer_radius * sin_angle)
    glEnd()

def draw_orbit(distance):
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_LINE_LOOP)
    for i in range(0, 361, 5):
        angle = math.radians(i)
        x = distance * math.cos(angle)
        z = distance * math.sin(angle)
        glVertex3f(x, 0, z)
    glEnd()

def init_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    light_ambient = [0.2, 0.2, 0.2, 1.0]
    light_diffuse = [1.0, 1.0, 1.0, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    
    material_specular = [1.0, 1.0, 1.0, 1.0]
    material_shininess = [50.0]
    
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

class Simulation:
    def __init__(self):
        self.solar_system = SolarSystem()
        self.solar_system.create_solar_system()
        self.time_speed = 1.0
        
    def init_gl(self, width, height):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        
        init_lighting()
        
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        camera_x = self.solar_system.camera_distance * math.cos(math.radians(self.solar_system.camera_angle_y)) * math.sin(math.radians(self.solar_system.camera_angle_x))
        camera_y = self.solar_system.camera_distance * math.sin(math.radians(self.solar_system.camera_angle_y))
        camera_z = self.solar_system.camera_distance * math.cos(math.radians(self.solar_system.camera_angle_y)) * math.cos(math.radians(self.solar_system.camera_angle_x))
        
        gluLookAt(camera_x, camera_y, camera_z,
                  0, 0, 0,
                  0, 1, 0)
        
        glLightfv(GL_LIGHT0, GL_POSITION, self.solar_system.light_position)
        
        for planet in self.solar_system.planets:
            glPushMatrix()
            
            planet.revolution_angle += planet.revolution_speed * 0.1 * self.time_speed
            glRotatef(planet.revolution_angle, 0, 1, 0)
            glTranslatef(planet.distance, 0, 0)
            
            draw_orbit(planet.distance)
            
            planet.rotation_angle += planet.rotation_speed * 0.5 * self.time_speed
            glRotatef(planet.rotation_angle, 0, 1, 0)
            
            draw_sphere(planet.radius, 50, 50, planet.color)
            
            if planet.has_rings:
                glPushMatrix()
                glRotatef(45, 1, 0, 0)
                draw_ring(planet.radius * 1.5, planet.radius * 2.2, [0.8, 0.7, 0.4])
                glPopMatrix()
            
            for moon in planet.moons:
                glPushMatrix()
                moon.revolution_angle += moon.revolution_speed * 0.1 * self.time_speed
                glRotatef(moon.revolution_angle, 0, 1, 0)
                glTranslatef(moon.distance, 0, 0)
                draw_orbit(moon.distance)
                moon.rotation_angle += moon.rotation_speed * 0.5 * self.time_speed
                glRotatef(moon.rotation_angle, 0, 1, 0)
                draw_sphere(moon.radius, 30, 30, moon.color)
                glPopMatrix()
            
            glPopMatrix()
        
        glutSwapBuffers()
        
    def reshape(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
    def mouse(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                self.solar_system.mouse_dragging = True
                self.solar_system.last_mouse_x = x
                self.solar_system.last_mouse_y = y
            else:
                self.solar_system.mouse_dragging = False
        elif button == 3:
            self.solar_system.camera_distance = max(5.0, self.solar_system.camera_distance - 1.0)
        elif button == 4:
            self.solar_system.camera_distance = min(50.0, self.solar_system.camera_distance + 1.0)
        
    def motion(self, x, y):
        if self.solar_system.mouse_dragging:
            dx = x - self.solar_system.last_mouse_x
            dy = y - self.solar_system.last_mouse_y
            
            self.solar_system.camera_angle_x += dx * 0.5
            self.solar_system.camera_angle_y += dy * 0.5
            self.solar_system.camera_angle_y = max(-89.0, min(89.0, self.solar_system.camera_angle_y))
            
            self.solar_system.last_mouse_x = x
            self.solar_system.last_mouse_y = y
            
    def keyboard(self, key, x, y):
        key = key.decode('utf-8').lower()
        if key == 'q' or key == '\x1b':
            sys.exit()
        elif key == '+':
            self.time_speed *= 1.5
        elif key == '-':
            self.time_speed /= 1.5
        elif key == 'r':
            self.time_speed = 1.0
            self.solar_system.camera_distance = 15.0
            self.solar_system.camera_angle_x = 0
            self.solar_system.camera_angle_y = 0

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1200, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"pyUniverse")
    
    simulation = Simulation()
    simulation.init_gl(1200, 800)
    
    glutDisplayFunc(simulation.display)
    glutReshapeFunc(simulation.reshape)
    glutMouseFunc(simulation.mouse)
    glutMotionFunc(simulation.motion)
    glutKeyboardFunc(simulation.keyboard)
    glutIdleFunc(simulation.display)
    
    glutMainLoop()

if __name__ == "__main__":
    main()