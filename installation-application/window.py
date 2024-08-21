import OpenGL.GL as gl
import glfw
import imgui
from renderer import safe_execute
from imgui.integrations.glfw import GlfwRenderer
import sys

class Window:
    def __init__(self, width="480", height="640", title="MEDIA PLAYER"):
        self.title = title
        self.width = width
        self.height = height
        self.monitors = None
        self.monitor_choice = 0
        self.show_settings = False
        self.is_fullscreen = False
        imgui.create_context()
        self.window, self.monitors, self._imgui = self.impl_glfw_init()

    def impl_glfw_init(self):
        if not glfw.init():
            sys.exit(1)
        try:
            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
            glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
            glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)

            monitors = glfw.get_monitors()
            window = glfw.create_window(self.width, self.height, self.title, None, None)

            if not window:
                glfw.terminate()
                sys.exit(1)

            glfw.make_context_current(window)
            _imgui = GlfwRenderer(window)
            glfw.swap_interval(0)
            gl.glViewport(0, 0, self.width, self.height)
            gl.glClearColor(0.0, 0.0, 0.0, 1.0)

            glfw.set_framebuffer_size_callback(window, self.framebuffer_size_callback)
            glfw.set_key_callback(window, self.key_callback)
            
        except Exception as e:
            print("GLFW INITIALIZATION FAILED")
            glfw.terminate()
            raise e
        finally:
            return (window, monitors, _imgui)
        
    def framebuffer_size_callback(self, window, width, height):
        gl.glViewport(0, 0, width, height)
        self.width = width
        self.height = height

    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            self.show_settings = not self.show_settings
        if key == glfw.KEY_F11 and action == glfw.PRESS:
            self.toggle_fullscreen()

    def toggle_fullscreen(self):
        # Toggle the window between fullscreen and windowed mode.
        if not self.is_fullscreen:
            # Get the video mode of the primary monitor
            mode = glfw.get_video_mode(self.monitors[self.monitor_choice])
            glfw.set_window_monitor(self.window, self.monitors[self.monitor_choice], 0, 0, mode.size.width, mode.size.height, glfw.DONT_CARE)
            glfw.set_window_size(self.window, mode.size.width, mode.size.height)
            self.is_fullscreen = True
        else:
            glfw.set_window_monitor(self.window, None, 0, 0, 640, 480, glfw.DONT_CARE)
            self.is_fullscreen = False

    def should_close(self):
        return glfw.window_should_close(self.window)
    
    def time(self):
        return glfw.get_time()

    def update(self):
        self._imgui.process_inputs()
        glfw.swap_buffers(self.window)
        glfw.poll_events()
    
    def terminate(self):
        safe_execute(glfw.terminate(), 0)
        print("Window terminated.")