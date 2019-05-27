
from __future__ import absolute_import

import sys
import math
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from rotom_editor import RotomEditor
from imgui.integrations.pygame import PygameRenderer
import imgui


# This entire file is garbo and temporary
# It only exists as a way for me to get more familliar with how dppt maps work
# Once I figure all that stuff out ill rework this to be less garbage or start from scratch
# for now though, enjoy the garbo

def main():
    pygame.init()
    size = 800, 600

    display = pygame.display.set_mode(size, pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption("Rotom")

    editor = RotomEditor()
    if(not editor.openProject(editor.projects[0]["name"])):
        print("Error Opening Project")
        exit(1)
    
    glEnable(GL_DEPTH_TEST)
    gluPerspective(45, (size[0]/size[1]), 0.1, 200.0)
    glTranslatef(-15.0, 15.0, -50)

    #bad
    mapID = 0
    objectID = 0
    projectID = 0
    tileX = 0
    tileY = 0

    projectNames = [p["name"] for p in editor.projects]
    objectNames = ["Object {0}".format(x) for x in range(0, editor.getCurrentMap().objectCount)]
    currentObject = None
    tile = None

    if(editor.getCurrentMap().objectCount > 0):
        currentObject = editor.getCurrentMap().MapObjects[0]

    imgui.create_context()
    impl = PygameRenderer()

    io = imgui.get_io()
    io.display_size = size

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            impl.process_event(event)

        imgui.new_frame()
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #Gross
        glPointSize(8)
        glBegin(GL_POINTS)
        t = 0
        for obj in editor.getCurrentMap().MapObjects:
            glColor3f(255, 255, 255)
            if(t == objectID):
                glColor3f(100, 0, 100)
            glVertex3f(obj.x+16, -(obj.z+16), 2)
            t += 1
        glEnd()

        #Also Very Gross
        glPointSize(10)
        glBegin(GL_POINTS)
        for y in range(0, 32):
            for x in range(0, 32):
                if(editor.getCurrentMap().getTilePermissions(x, y)[1] == 0x00):
                    if(editor.getCurrentMap().getTilePermissions(x, y)[0] == 0xA9):
                        glColor3f(0, 0, 100)
                    else:
                        glColor3f(0, 100, 0)
                else:
                    glColor3f(100, 0, 0)

                glVertex3f(x, -y, 2)
        glEnd()

        
        imgui.begin("Project Settings")
        projectChanged, projectID = imgui.listbox("", projectID, projectNames)
        if(projectChanged):
            objectID = 0
            editor.openProject(projectNames[projectID])
            editor.setCurrentMap(mapID)
            objectNames = ["Object {0}".format(x) for x in range(0, editor.getCurrentMap().objectCount)]
        imgui.end()

        imgui.begin("Map Objects")
        imgui.text("Current Map ID")
        mapChanged, mapID = imgui.input_int("", mapID)
        if mapChanged:
            objectID = 0
            editor.setCurrentMap(mapID)
            objectNames = ["Object {0}".format(x) for x in range(0, editor.getCurrentMap().objectCount)]
        
        imgui.text("Current Object")
        if(currentObject is not None):
            objectChanged, objectID = imgui.listbox("", objectID, objectNames)
            if(objectID < editor.getCurrentMap().objectCount):
                c, editor.getCurrentMap().MapObjects[objectID].modelID = imgui.input_int("Model ID", editor.getCurrentMap().MapObjects[objectID].modelID)
                c, editor.getCurrentMap().MapObjects[objectID].x = imgui.input_float("x Pos", editor.getCurrentMap().MapObjects[objectID].x)
                c, editor.getCurrentMap().MapObjects[objectID].y = imgui.input_float("y Pos", editor.getCurrentMap().MapObjects[objectID].y)
                c, editor.getCurrentMap().MapObjects[objectID].z = imgui.input_float("z Pos", editor.getCurrentMap().MapObjects[objectID].z)
        else:
            imgui.text("Map Has No Objects")

        if(imgui.button("Save Map")):
            editor.saveCurrentMap()
        
        if(imgui.button("Save Rom")):
            editor.saveProject()
        imgui.end()

        imgui.render()
        impl.render(imgui.get_draw_data())

        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()