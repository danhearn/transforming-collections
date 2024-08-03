import sys, os, ctypes
import numpy as np

import OpenGL.GL as gl
import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer

from queue import Empty

from PIL import Image, ImageSequence
# from PIL.Image import Transpose

class GifPlayer:
    def __init__(self, gifs_path="./data/gifs", queue=None):

        # The Gif Player contains a basic OpenGL renderer and GLFW context which opens in a new window.
        # The init method sets this renderer up and loads gifs from the directory specified in the
        # constructor.

        # The Gif's are stored in a 2D list where each gif is a list of frames. Stored like this:
        #   [
        #       [gif1_frame1, gif1_frame2, gif1_frame3, ...],
        #       [gif2_frame1, gif2_frame2, gif2_frame3, ...],
        #       [etc...]   
        #   ] 
        # Each frame also contains the width and height of the gif so the renderer can adjust the texture.
        # Later, this could be changed if all of the gifs have a uniform size.
        
        self.gifs_path = gifs_path
        self.queue = queue

        # Create some variables to play the gifs in time. 
        self.current_time = 0
        self.last_update_time = 0
        self.frame_index = 0
        self.active_gif_index = 0
        self.active_gif = None

    def run(self):
        imgui.create_context()
        self.window, self.window_width, self.window_height, self.primary_monitor = self.impl_glfw_init()
        self.impl = GlfwRenderer(self.window)
        self.load_bind_all_data()
        # self.active_gif = self.gif_textures[self.active_gif_index]
        try:
            while self.should_run():
                self.update_window()
                self.update_active_gif()
                # TODO: Update render to only happen when frame has updated to save resources.
                self.render()
        except Exception as e:
            print(f"An error occurred in GifPlayer's run method: {e}")
        finally:
            self.terminate()

    def render(self):
        self.background()
        if self.active_gif is not None:
            self.draw_active_gif()
        imgui.new_frame()
        imgui.begin("Custom window", True)
        imgui.text(f"FPS: {self.fps()}")
        imgui.end()
        imgui.render()

        self.impl.render(imgui.get_draw_data())
        

    def update_frame_index(self):
        # Update the frame index to the next frame if the time has passed the frame duration.

        self.current_time = glfw.get_time()
        if self.current_time - self.last_update_time >= self.active_gif[self.frame_index][3] / 1000:
            self.frame_index = (self.frame_index + 1) % len(self.active_gif)
            self.last_update_time = self.current_time

    def update_active_gif(self):

        prev = self.active_gif
        message = None

        if self.queue is not None:
            try:
                message = self.queue.get_nowait()
                print(message)
            except Empty:
                pass
            except Exception as e:
                raise e
            if message is not None:
                print("found message: ", message)
                message = message.lstrip("gif-")
                index = int(message) - 1
                self.frame_index = 0
                self.active_gif_index = index
                self.active_gif = self.gif_textures[self.active_gif_index]

        ## DEBUG USER INPUT TO CHANGE GIFS
        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS: 
            self.frame_index = 0
            self.active_gif_index = (self.active_gif_index+1)%len(self.gif_textures)
            self.active_gif = self.gif_textures[self.active_gif_index]

        if self.active_gif is not None:
            active_texture, w, h, dur = self.active_gif[self.frame_index]
            if prev != self.active_gif:
                self.set_tex_dimensions(w, h)
            self.update_frame_index()
            gl.glBindTexture(gl.GL_TEXTURE_2D, active_texture)

    def set_tex_dimensions(self, w, h):
        # Send the gif's dimensions to the shader so it can adjust the texture coordinates
        # In case the final gifs have varying dimensions.

        gl.glUniform1f(gl.glGetUniformLocation(self.program_id, "tex_w"), w)
        gl.glUniform1f(gl.glGetUniformLocation(self.program_id, "tex_h"), h)
        return

    def should_run(self):
        return not glfw.window_should_close(self.window) and glfw.get_key(self.window, glfw.KEY_ESCAPE) != glfw.PRESS
    
    def draw_active_gif(self):
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)

    def background(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    def framebuffer_size_callback(self, window, width, height):
        gl.glViewport(0, 0, width, height)
        self.window_width = width
        self.window_height = height
    
    def update_window(self):
        glfw.set_framebuffer_size_callback(self.window, self.framebuffer_size_callback)
        gl.glUniform1f(gl.glGetUniformLocation(self.program_id, "window_w"), self.window_width)
        gl.glUniform1f(gl.glGetUniformLocation(self.program_id, "window_h"), self.window_height)
        glfw.swap_buffers(self.window)
        glfw.poll_events()
        self.impl.process_inputs()
    
    def fps(self):
        # Calculate the frames per second.

        prev_time = self.current_time
        self.current_time = glfw.get_time()
        delta_time = self.current_time - prev_time
        fps = 1.0 / delta_time if delta_time > 0 else 0
        return fps
    


    #################################################################################
    ###################### OPENGL, SETUP AND LOADING FUNCTIONS ######################
    #################################################################################


    def impl_glfw_init(self):
        if not glfw.init():
            sys.exit(1)
        try:
            # Set the OpenGL version (should be OSX compatible)
            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
            glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
            glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
            
            # Create the window
            title = "~GIF+PLAYER*"
            primary_monitor = glfw.get_primary_monitor()
            window_width = 640
            window_height = 480
            window = glfw.create_window(window_width, window_height, title, None, None)
            if not window:
                glfw.terminate()
                sys.exit(1)

            # Attach the OpenGL context to the window
            glfw.make_context_current(window)
            gl.glViewport(0, 0, window_width, window_height)
            gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        except Exception as e:
            print("GLFW INITIALIZATION FAILED")
            glfw.terminate()
            raise e
        finally:
            return (window, window_width, window_height, primary_monitor)
        
    
    def load_bind_all_data(self):
        # Loads all of the data needed to render the gifs from now on. The gifs need to be converted into
        # a format which can be rendered in the window, AKA textures.
        gifs_data = self.load_gifs()
        self.gif_textures = self.load_all_textures(gifs_data)
        self.vao = self.create_vertex_array_object()
        self.vbo, self.ebo = self.create_vertex_buffer()
        self.program_id, self.shader_ids = self.load_shaders()

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
            gl.GL_VERTEX_SHADER: self.load_shader_source("./gif_shader/gif.vert"),
            gl.GL_FRAGMENT_SHADER: self.load_shader_source("./gif_shader/gif.frag")
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
            
    def load_gifs(self):
        # Using PILLOW to load the gifs and convert them to byte format, to be used by OpenGL.

        gifs = []
        file_names = sorted(os.listdir(self.gifs_path), key=lambda name: int(name.lstrip("gif-").rstrip(".gif")))
        for file_name in file_names:
            if file_name.endswith('.gif') or file_name.endswith('.GIF'):
                gif_path = os.path.join(self.gifs_path, file_name)
                print(gif_path)
                with Image.open(gif_path) as im:
                    frames = []
                    for frame in ImageSequence.Iterator(im):
                        frame_rgb = frame.convert("RGB")
                        image_bytes = frame_rgb.tobytes("raw", "RGBX", 0, -1)
                        width, height = frame.size
                        dur = frame.info['duration']
                        frame_data = (image_bytes, width, height, dur)
                        frames.append(frame_data)
                    gifs.append(frames)
        return gifs
    
    def make_texture_from_frame(self, frame_data):
        image_bytes, w, h, dur = frame_data

        # Generate a texture and bind it (this makes it active when we set parameters below)
        tex = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex)

        # Set the texture parameters
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
        gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        # Assign an image to the texture and generate the mip map
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, w, h, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image_bytes)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

        return tex, w, h, dur

    def load_all_textures(self, gifs_data):
        # Now that gifs have been converted to byte format we create textures from them
        # which can be displayed in the window.
        
        # The frame data is a tuple of (image_bytes, width, height) in case the gifs
        # are not all the same size and we need to adjust the texture coordinates.
        all_gif_textures = []
        for gif in gifs_data:
            all_textures_from_this_gif = []
            for frame_data in gif:
                single_frame_texture = self.make_texture_from_frame(frame_data)
                all_textures_from_this_gif.append(single_frame_texture)
            all_gif_textures.append(all_textures_from_this_gif)
        return all_gif_textures
    
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
        safe_execute(glfw.terminate)

def safe_execute(func, *args):
    try:
        func(*args)
    except Exception:
        pass

if __name__ == '__main__':
    player = GifPlayer(gifs_path="./data/gifs", queue=None)
    player.run()