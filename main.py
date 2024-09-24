
from __future__ import absolute_import

import sys
import math
from OpenGL.GL import *
from camera import OrbitCamera as Camera
from rotom_editor import RotomEditor
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

    # main
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
                cam.zoom(5)
        if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
            if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
                cam.target[1] -= 1.0
                cam.update()
            else:
                cam.zoom(-5)

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

        editor.getCurrentMap().draw()

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
        glfw.swap_buffers(window)
    
    glfw.terminate()

if __name__ == "__main__":
    main()