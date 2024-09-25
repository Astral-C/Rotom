
from __future__ import absolute_import

import sys
import math
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from camera import OrbitCamera as Camera
from rotom_editor import RotomEditor
from rotom_map import RotomMap, RotomMapObject
from imgui.integrations.glfw import GlfwRenderer
from pyrr import matrix44, Matrix44, Vector4, Vector3, Quaternion
import imgui
import glfw

import PalkiaPy

def on_resize(window, w, h):
    glViewport(0, 0, w, h)

def main():
    size = 1280, 720

    cam = Camera(distance=1000.0, pitch=30.0, yaw=45.0)

    if(not glfw.init()):
        raise Exception("Couldn't init GLFW")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 6)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_DEBUG_CONTEXT, glfw.TRUE)
    glfw.window_hint(glfw.DEPTH_BITS, 24)
    glfw.window_hint(glfw.SAMPLES, 4)

    window = glfw.create_window(1280, 720, "Rotom", None, None)
    if(not window):
        glfw.terminate()
        raise Exception("Couldn't setup window")

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, on_resize)

    PalkiaPy.init()

    editor = RotomEditor()
    if(not editor.openProject(editor.projects[0]["name"])):
        print("Error Opening Project")
        exit(1)

    #bad
    mapID = 0
    currentObject = 0
    location = 0
    projectID = 0
    tileX = 0
    tileY = 0

    projectNames = [p["name"] for p in editor.projects]
#    objectNames = ["Object {0}".format(x) for x in range(0, editor.getCurrentMap().objectCount)]
    tile = None
    running = True


    imgui.create_context()
    impl = GlfwRenderer(window)

    io = imgui.get_io()
    io.display_size = size

    while(not glfw.window_should_close(window)):
        glfw.poll_events()
        impl.process_inputs()
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            cam.rotate(1.0, 0.0)
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            cam.rotate(-1.0, 0.0)
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            cam.rotate(0.0, 1.0)
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            cam.rotate(0.0, -1.0)
        
        if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
            if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
                cam.target[1] += 1.0
                cam.update()
            else:
                cam.zoom(50)
        if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
            if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
                cam.target[1] -= 1.0
                cam.update()
            else:
                cam.zoom(-50)


        imgui.new_frame()

        glEnable(GL_DEPTH_TEST)
        glClearColor(0.25, 0.3, 0.4, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        width, height = glfw.get_framebuffer_size(window)
        
        glViewport(0, 0, width, height)
        imgui.get_io().display_size = width, height

        proj = matrix44.create_perspective_projection_matrix(45.0, width/height, 0.1, 100000.0)

        PalkiaPy.setCamera(
            proj.ravel().tolist(),
            cam.view_matrix.ravel().tolist()
        )

        editor.currentMap.draw(editor.locationNames[location])

        imgui.begin("Project Settings")
        projectChanged, projectID = imgui.listbox("", projectID, projectNames)
        if(projectChanged):
            currentObject = 0
            editor.openProject(projectNames[projectID])
            editor.setCurrentMap(mapID)
        imgui.end()
    
        imgui.begin("Map")
        changed, location = imgui.combo("##locationname", location, editor.locationNames)
        if(changed):
            editor.setCurrentMap(editor.locationNames[location])
        
        imgui.text("Current Map Matrix")
        changed, currentObject = imgui.combo("##mapmatrix", currentObject, [str(m) for m in editor.currentMapMatries])
        if(changed):
            editor.setCurrentMatrix(currentObject)

        imgui.end()

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
    
    glfw.terminate()

if __name__ == "__main__":
    main()