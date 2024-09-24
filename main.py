
from __future__ import absolute_import

import sys
import math
from camera import OrbitCamera as Camera
from rotom_editor import RotomEditor
from rotom_map import RotomMap, RotomMapObject
from pyrr import matrix44, Matrix44, Vector4, Vector3, Quaternion

import PalkiaPy

def on_resize(window, w, h):
    glViewport(0, 0, w, h)

def main():
    size = 1280, 720

    cam = Camera(distance=1000.0, pitch=30.0, yaw=45.0)



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
#    objectNames = ["Object {0}".format(x) for x in range(0, editor.getCurrentMap().objectCount)]
    currentObject = None
    tile = None
    running = True


    while(running):

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


        glEnable(GL_DEPTH_TEST)
        glClearColor(0.25, 0.3, 0.4, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        width, height = glfw.get_framebuffer_size(window)
        
        glViewport(0, 0, width, height)
        #imgui.get_io().display_size = width, height

        proj = matrix44.create_perspective_projection_matrix(45.0, width/height, 0.1, 100000.0)

        PalkiaPy.setCamera(
            proj.ravel().tolist(),
            cam.view_matrix.ravel().tolist()
        )

        editor.maps["Twinleaf Town"].draw()

    

if __name__ == "__main__":
    main()