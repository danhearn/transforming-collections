import OpenGL.GL as gl
import sys, os
import glfw
from PIL import Image, ImageSequence
from PIL.Image import Transpose
import numpy as np
import ctypes

class GifPlayer:
    def __init__(self, gifs_path):
        # init the window and OpenGL context
        if not glfw.init():
            sys.exit(1)
        try:
            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
            glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
            glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
            
            title = "GIFPLAYER"
            window_width = 500
            window_height= 500
            self.window = glfw.create_window(window_width, window_height, title, None, None)
            if not self.window:
                glfw.terminate()
                sys.exit(2)
            glfw.make_context_current(self.window)
            # glfw.swap_interval(0)
            gl.glViewport(0, 0, window_width, window_height)
            gl.glClearColor(0, 1.0, 0.0, 0)
            
        except Exception as e:
            glfw.terminate()
            raise e
        
        # Load the gifs
        #TODO stress test how many gifs can i load actually? do i need to be smart/cache?
        self.gifs = self.load_gifs(gifs_path)
        self.create_vertex_array_object()
        self.create_vertex_buffer()
        self.load_shaders()

        self.current_time = 0

    def create_vertex_array_object(self):
        self.vertex_array_id = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vertex_array_id)

    def create_vertex_buffer(self):
        vertex_data = np.array([
            # Positions      # UVs
            -1.0, -1.0, 0.0,  0.0, 0.0,
            1.0, -1.0, 0.0,  1.0, 0.0,
            -1.0,  1.0, 0.0,  0.0, 1.0,
            -1.0,  1.0, 0.0,  0.0, 1.0,
            1.0, -1.0, 0.0,  1.0, 0.0,
            1.0,  1.0, 0.0,  1.0, 1.0
        ], dtype=np.float32)

        position_attr_id = 0
        uv_attr_id = 1

        self.vertex_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, gl.GL_STATIC_DRAW)

        # Position attribute
        gl.glVertexAttribPointer(position_attr_id, 3, gl.GL_FLOAT, False, 5*vertex_data.itemsize, None)
        gl.glEnableVertexAttribArray(position_attr_id)

        # UV attribute
        gl.glVertexAttribPointer(uv_attr_id, 2, gl.GL_FLOAT, False, 5*vertex_data.itemsize, ctypes.c_void_p(3*vertex_data.itemsize))
        gl.glEnableVertexAttribArray(uv_attr_id)

    def load_shader_source(self, file_path):
        with open(file_path,'r') as file:
            return file.read()
        
    def load_shaders(self):
        shaders = {
            gl.GL_VERTEX_SHADER: self.load_shader_source("./gif_shader/gif.vert"),
            gl.GL_FRAGMENT_SHADER: self.load_shader_source("./gif_shader/gif.frag")
        }
        self.program_id = gl.glCreateProgram()
        # try:
        self.shader_ids = []
        for shader_type, shader_src in shaders.items():
            shader_id = gl.glCreateShader(shader_type)
            gl.glShaderSource(shader_id, shader_src)

            gl.glCompileShader(shader_id)

            #check if compilation succeeded
            result = gl.glGetShaderiv(shader_id, gl.GL_COMPILE_STATUS)
            info_log_len = gl.glGetShaderiv(shader_id, gl.GL_INFO_LOG_LENGTH)
            if info_log_len:
                logmsg = gl.glGetShaderInfoLog(shader_id)
                print("Shader compile error:" + logmsg)
                sys.exit(10)
            
            gl.glAttachShader(self.program_id, shader_id)
            self.shader_ids.append(shader_id)

        gl.glLinkProgram(self.program_id)

        # check if linking was successful
        result = gl.glGetProgramiv(self.program_id, gl.GL_LINK_STATUS)
        info_log_len = gl.glGetProgramiv(self.program_id, gl.GL_INFO_LOG_LENGTH)
        if info_log_len:
            logmsg = gl.glGetProgramInfoLog(self.program_id)
            print("Shader linking error:" + logmsg)
            sys.exit(11)
        
        gl.glUseProgram(self.program_id)
            

    def load_gifs(self, gifs_path):
        gifs = []
        for file_name in os.listdir(gifs_path):
            if file_name.endswith('.gif'):
                gif_path = os.path.join(gifs_path, file_name)
                with Image.open(gif_path) as im:
                    frames = []
                    for frame in ImageSequence.Iterator(im):
                        frame_data = frame.convert("RGBA").transpose(Transpose.FLIP_TOP_BOTTOM).tobytes()
                        frames.append(frame_data)
                    gifs.append(frames)
        return gifs
    
    def terminate(self):
        gl.glDisableVertexAttribArray(0)
        gl.glDeleteBuffers(1, [self.vertex_buffer])
        gl.glDeleteVertexArrays(1, [self.vertex_array_id])
        for shader_id in self.shader_ids:
            gl.glDetachShader(self.program_id, shader_id)
            gl.glDeleteShader(shader_id)
        gl.glUseProgram(0)
        gl.glDeleteProgram(self.program_id)
        glfw.terminate()

    def fps(self):
        prev_time = self.current_time
        self.current_time = glfw.get_time()
        delta_time = self.current_time - prev_time
        fps = 1.0 / delta_time if delta_time > 0 else 0
        print(f"FPS: {fps:.2f}")

    def run(self):
        while not glfw.window_should_close(self.window) and glfw.get_key(self.window, glfw.KEY_ESCAPE) != glfw.PRESS:
            #Clear the frame
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            
            #RENDER HERE
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)

            self.fps()
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        ## close the window and delete all OpenGL resources
        self.terminate()

if __name__ == '__main__':
    player = GifPlayer("./data/gifs")
    player.run()