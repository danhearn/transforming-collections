import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer

from media import Video, Gif

import sys, ctypes
import numpy as np

class Renderer:
    def __init__(self, window):
        self.window = window
        self._imgui = window._imgui 
        self.vao = self.create_vertex_array_object()
        self.vbo, self.ebo = self.create_vertex_buffer()
        self.pbos = {}
        self.textures = {}
        self.current_texture = None
        self.program_id, self.shader_ids = self.load_shaders()
        self.show_settings = True
        self.current_time = 0
        self.frame_times = []

    def draw(self, media):
        self.clear()
        if media is not None:
            self.set_uniforms(media)
            self.set_texture(media)
        self.draw_elements()
        self.gui()  

    def gui(self):
        window = self.window
        imgui.new_frame()
        if window.show_settings:
            _, window.show_settings = imgui.begin("Settings", True)
            imgui.text(f"{len(window.monitors)} possible monitors found:")
            if imgui.begin_combo("Monitor", f"{window.monitor_choice}"):
                for i, monitor in enumerate(window.monitors):
                    clicked, selected = imgui.selectable(f"Monitor {i}", window.monitor_choice == i)
                    if clicked:
                        window.monitor_choice = i
                imgui.end_combo()
            if imgui.button("Toggle Fullscreen"):
                window.toggle_fullscreen()
            imgui.text(f"FPS: {self.fps()}")
            imgui.end()
        imgui.render()
        self._imgui.render(imgui.get_draw_data())
    
    def set_uniforms(self, media):
        self.set_uniform("window_w", self.window.width)
        self.set_uniform("window_h", self.window.height)
        self.set_uniform("tex_w", media.size[0])
        self.set_uniform("tex_h", media.size[1])
        if type(media) is Video:
            self.set_uniform("is_flipped", True)
        else:
            self.set_uniform("is_flipped", False)

    def set_uniform(self, name, value):
        gl.glUniform1f(gl.glGetUniformLocation(self.program_id, name), value)

    def set_texture(self, media):
        gl.glActiveTexture(gl.GL_TEXTURE0)
        tex = self.get_textures_from_UUID(media.texture_UUID)
        self.bind_texture(tex)
        if type(media) is Gif:
            self.tex_image_2D(media.size, media._frame_data, is_video=False)
        elif type(media) is Video and media._frame_data is not None:
            pbos = self.get_pbos_from_UUID(media.pbo_UUID)
            size = media.size[0]*media.size[1]*4
            index = media._buffer_index = (media._buffer_index + 1) % 2
            self.bind_pbo(pbos[index])
            self.set_pbo_data_ptr(media._frame_data, size)
            self.tex_sub_image_2D(media.size)
            self.unbind_pbo()

    def fps(self):
        # Calculate the frames per second.
        prev_time = self.current_time
        self.current_time = self.window.time()
        delta_time = self.current_time - prev_time

        # Keep track of the frame times of the last second.
        self.frame_times.append((self.current_time, delta_time))
        self.frame_times = [(t, dt) for (t, dt) in self.frame_times if self.current_time - t < 1.0]

        # Calculate the average FPS over the last second.
        average_fps = len(self.frame_times) / sum(dt for t, dt in self.frame_times) if self.frame_times else 0
        return average_fps
    
    def create_textures(self, UUID, size, is_video):
        if self.textures.get(UUID) is None:
            tex = self.gen_textures(1)
            gl.glActiveTexture(gl.GL_TEXTURE0)
            self.bind_texture(tex)
            self.set_tex_params()
            if is_video:
                self.tex_image_2D(size, bytes=None, is_video=True)
            self.unbind_texture()
            self.textures[UUID] = tex
        return
    
    def create_pbos(self, UUID, size, num_pbos):
        if self.pbos.get(UUID) is None:
            pbos = []
            for _ in range(num_pbos):
                pbo = gl.glGenBuffers(1)
                gl.glBindBuffer(gl.GL_PIXEL_UNPACK_BUFFER, pbo)
                gl.glBufferData(gl.GL_PIXEL_UNPACK_BUFFER, size[0]*size[1]*4, None, gl.GL_STREAM_DRAW)
                gl.glBindBuffer(gl.GL_PIXEL_UNPACK_BUFFER, 0)
                pbos.append(pbo)
            self.pbos[UUID] = pbos
        return
    
    def get_textures_from_UUID(self, UUID):
        return self.textures[UUID]
    
    def get_pbos_from_UUID(self, UUID):
        return self.pbos[UUID]

    def create_vertex_array_object(self):
        # The vertex buffer object has to be attached to a VAO to be rendered.
        vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(vao)
        return vao
    
    def create_vertex_buffer(self):
        # Gif Player just needs a single fullscreen quad to render the gif textures. This function 
        # gives the renderer the necesary vertex data to render the quad.

        # Since OpenGL works with triangles, we define 4 points and 6 indices to create a quad.
        # The vertex data also includes the UV coordinates for the texture, at attribute index 1.
        position_attr_id = 0
        uv_attr_id = 1
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

        # Create and bind the vertex buffer
        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, gl.GL_STATIC_DRAW)
        # Create and bind the indices buffer
        ebo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)

        # Assign the position data to the vertex buffer
        gl.glVertexAttribPointer(position_attr_id, 3, gl.GL_FLOAT, False, 5*vertex_data.itemsize, None)
        gl.glEnableVertexAttribArray(position_attr_id)
        # Assign the UV data to the vertex buffer
        gl.glVertexAttribPointer(uv_attr_id, 2, gl.GL_FLOAT, False, 5*vertex_data.itemsize, ctypes.c_void_p(3*vertex_data.itemsize))
        gl.glEnableVertexAttribArray(uv_attr_id)
        return vbo, ebo
    
    def load_shader_source(self, file_path):
        # Loads shader source code from a file and returns the data as a string.
        with open(file_path,'r') as file:
            return file.read()
    
    def load_shaders(self):
        # This function loads, compiles and links the vertex and fragment shaders for the gif player.

        shaders = {
            gl.GL_VERTEX_SHADER: self.load_shader_source("./media_shader/media.vert"),
            gl.GL_FRAGMENT_SHADER: self.load_shader_source("./media_shader/media.frag")
        }

        # Creates a shader program.
        program_id = gl.glCreateProgram()
        
        shader_ids = []
        for shader_type, shader_src in shaders.items():
            shader_id = gl.glCreateShader(shader_type)
            gl.glShaderSource(shader_id, shader_src)
            gl.glCompileShader(shader_id)

            #check if compilation succeeded
            result = gl.glGetShaderiv(shader_id, gl.GL_COMPILE_STATUS)
            info_log_len = gl.glGetShaderiv(shader_id, gl.GL_INFO_LOG_LENGTH)
            if info_log_len:
                logmsg = gl.glGetShaderInfoLog(shader_id)
                print("Shader compile error:" + logmsg.decode('utf-8'))
                sys.exit(1)
           
            # If compilation succeeded, attach the shader to the program
            gl.glAttachShader(program_id, shader_id)
            shader_ids.append(shader_id)

        # Link the program
        gl.glLinkProgram(program_id)

        # check if linking succeeded, if so use the program
        info_log_len = gl.glGetProgramiv(program_id, gl.GL_INFO_LOG_LENGTH)
        if info_log_len:
            logmsg = gl.glGetProgramInfoLog(program_id)
            print("Shader linking error:" + logmsg.decode('utf-8'))
            sys.exit(1)
        
        gl.glUseProgram(program_id)
        return program_id, shader_ids
    
    def tex_image_2D(self, size, bytes=None, is_video=False):
        if is_video:
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, size[0], size[1], 0, gl.GL_BGR, gl.GL_UNSIGNED_BYTE, bytes)
        else:
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, size[0], size[1], 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, bytes)

    def tex_sub_image_2D(self, size):
        gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, size[0], size[1], gl.GL_BGR, gl.GL_UNSIGNED_BYTE, None)

    def generate_mipmaps(self):
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    def set_tex_params(self, mip_map=False):
        if mip_map is True:
            min = gl.GL_LINEAR_MIPMAP_LINEAR
        else:
            min = gl.GL_LINEAR
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, min)
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    def gen_textures(self, n):
        return gl.glGenTextures(n)

    def bind_pbo(self, pbo):
        gl.glBindBuffer(gl.GL_PIXEL_UNPACK_BUFFER, pbo)

    def unbind_pbo(self):
        gl.glBindBuffer(gl.GL_PIXEL_UNPACK_BUFFER, 0)

    def bind_texture(self, texture):
        if self.current_texture is not texture:
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
            self.current_texture = texture

    def unbind_texture(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        self.current_texture = None

    def set_pbo_data_ptr(self, data, size):
        ptr = gl.glMapBufferRange(gl.GL_PIXEL_UNPACK_BUFFER, 0, size, gl.GL_MAP_WRITE_BIT | gl.GL_MAP_INVALIDATE_BUFFER_BIT)#| gl.GL_MAP_FLUSH_EXPLICIT_BIT | gl.GL_MAP_UNSYNCHRONIZED_BIT)
        ctypes.memmove(ptr, data, len(data))
        gl.glUnmapBuffer(gl.GL_PIXEL_UNPACK_BUFFER)
    
    def clear(self, color=None):
        if color is not None:
            gl.glClearColor(*color, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    
    def draw_elements(self):
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)

    def terminate(self):
        # In case the program closes, it's good practice to clean up the resources.
        safe_execute(gl.glDisableVertexAttribArray, 0)
        safe_execute(gl.glDeleteBuffers, 1, [self.vbo])
        safe_execute(gl.glDeleteBuffers, 1, [self.ebo])
        safe_execute(gl.glDeleteVertexArrays, 1, [self.vao])
        for shader_id in self.shader_ids:
            safe_execute(gl.glDetachShader, self.program_id, shader_id)
            safe_execute(gl.glDeleteShader, shader_id)
        safe_execute(gl.glUseProgram, 0)
        safe_execute(gl.glDeleteProgram, self.program_id)

def safe_execute(func, *args):
    try:
        func(*args)
    except Exception:
        pass