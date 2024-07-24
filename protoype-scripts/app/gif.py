import OpenGL.GL as gl
import sys, os, gc
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
            
            title = "~GIF+PLAYER*"
            primary_monitor = glfw.get_primary_monitor()
            video_mode = glfw.get_video_mode(primary_monitor)
            window_width = 1920
            window_height= 1080
            self.window = glfw.create_window(window_width, window_height, title, primary_monitor, None)
            if not self.window:
                glfw.terminate()
                sys.exit(2)
            glfw.make_context_current(self.window)
            # glfw.swap_interval(0) #(turns of V-Sync)
            gl.glViewport(0, 0, window_width, window_height)
            gl.glClearColor(0, 1.0, 0.0, 0)
            
        except Exception as e:
            glfw.terminate()
            raise e
        
        # Load the gifs
        #TODO stress test how many gifs can i load actually? do i need to be smart/cache?
        self.gifs = self.load_gifs(gifs_path)
        self.load_all_textures()
        self.create_vertex_array_object()
        self.create_vertex_buffer()
        self.load_shaders()
        self.current_time = 0
        self.last_update_time = 0
        self.frame_index = 0
        self.frame_duration = 1.0 / 24  # 24 fps
        self.active_gif = 0

    def create_vertex_array_object(self):
        self.vertex_array_id = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vertex_array_id)

    def create_vertex_buffer(self):
        vertex_data = np.array([
            # Positions      # UVs
            1.0, 1.0, 0.0, 1.0, 1.0,    # top right
            1.0, -1.0, 0.0, 1.0, 0.0,   # bottom right
            -1.0, -1.0, 0.0, 0.0, 0.0,  # bottom left
            -1.0, 1.0, 0.0, 0.0, 1.0    # top left
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 3,    # first triangle
            1, 2, 3     # secpod triangle
        ], dtype=np.uint32)

        position_attr_id = 0
        uv_attr_id = 1

        self.vertex_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, gl.GL_STATIC_DRAW)

        self.ebo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)

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
                        frame_rgb = frame.convert("RGB")
                        image_bytes = frame_rgb.tobytes("raw", "RGBX", 0, -1)
                        width, height = frame.size
                        frame_data = (image_bytes, width, height)
                        frames.append(frame_data)
                    gifs.append(frames)
        return gifs
    
    def make_texture_from_frame(self, frame_data):
        image_bytes, w, h = frame_data
        tex = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, w, h, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image_bytes)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        return tex

    def load_all_textures(self):
        self.all_gif_textures = []
        for gif in self.gifs:
            all_textures_from_this_gif = []
            for frame_data in gif:
                single_frame_texture = self.make_texture_from_frame(frame_data)
                all_textures_from_this_gif.append(single_frame_texture)
                del frame_data
            gc.collect()
            self.all_gif_textures.append(all_textures_from_this_gif)
    
    def terminate(self):
        gl.glDisableVertexAttribArray(0)
        gl.glDeleteBuffers(1, [self.vertex_buffer])
        gl.glDeleteBuffers(1, [self.ebo])
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
        return fps

    def update_frame_index(self):
        if self.current_time - self.last_update_time >= self.frame_duration:
            self.frame_index = (self.frame_index + 1) % len(self.all_gif_textures[self.active_gif])
            self.last_update_time = self.current_time

    def render(self):
        # Clear the background
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # Update gif textures
        self.update_frame_index()
        activeTexture = self.all_gif_textures[self.active_gif][self.frame_index]
        gl.glBindTexture(gl.GL_TEXTURE_2D, activeTexture)
        # Draw the gif to screen
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)


    def run(self):
        while not glfw.window_should_close(self.window) and glfw.get_key(self.window, glfw.KEY_ESCAPE) != glfw.PRESS:
            self.render()
            self.fps()
            if glfw.get_key(self.window, glfw.KEY_0) == glfw.PRESS: 
                self.active_gif = 0
                self.frame_index = 0
            if glfw.get_key(self.window, glfw.KEY_1) == glfw.PRESS: 
                self.active_gif = 1
                self.frame_index = 1
            print(self.active_gif)
            glfw.swap_buffers(self.window)
            glfw.poll_events()
        self.terminate()

if __name__ == '__main__':
    player = GifPlayer("./data/gifs")
    player.run()