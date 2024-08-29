from window import Window
from renderer import Renderer
from media import Video, Gif
from multiprocessing import Process, Queue
import uuid
import sys
from pathlib import Path

class MediaPlayer:
    def __init__(self, gifs_path, vids_path, fullscreen=True):
        self.gifs_path = Path(gifs_path)
        self.vids_path = Path(vids_path)
        self.queue = Queue()
        self.renderer = None
        self.media = {}

        self.active_media = None
        self.current_time = 0
        self.last_update_time = -1

        self.fullscreen = fullscreen

    def run(self):
        # Initialize the renderer and media for playing. 
        # Happens in run so that the player can run on a separate process from the main program.
        self.window = Window(800, 600, "MEDIA PLAYER", self.fullscreen)
        self.renderer = Renderer(window=self.window)
        self.media = self.load_media()
        try:
            while not self.window.should_close():
                self.window.update()
                self.check_queue()
                if(self.active_media is not None):
                    self.play_media()
                self.renderer.draw(self.active_media)
        except Exception as e:
            print(f"Error in Media Player's run method: {e}")
            raise e
        finally:
            self.terminate()
        
    ####################
    ###PUBLIC METHODS###
    ####################
    
    # After creating the MediaPlayer object, call this method to start the player on a new process
    def start_on_new_process(self):
        process = Process(target=self.run)
        process.start()
        return process

    # Called from the Main Program when they want to change to a new piece media
    def queue_media(self, ID):
        self.queue.put(ID)

    ######################
    ###INTERNAL METHODS###
    #####################

    def play_media(self):
        self.current_time = self.window.time()
        if self.current_time - self.last_update_time >= self.active_media.get_frame_duration():
            self.active_media.go_to_next_frame()
            self.last_update_time = self.current_time
        if self.active_media.is_finished():
            self.active_media.restart()
            self.last_update_time = self.current_time

    def get_media(self, ID):
        return self.media[ID]

    def update_active_media(self, ID):
        self.prev_media = self.active_media
        self.active_media = self.get_media(ID)
        if self.active_media is not self.prev_media:
            self.active_media.open()
            if self.prev_media is not None:
                self.prev_media.close()

    def check_queue(self):
        if not self.queue.empty():
            try:
                message = self.queue.get_nowait()
                print(f"Received instruction to play: {message}")
            except Exception as e:
                raise e
            if message is not None:
                self.update_active_media(message)

    def load_media(self):
        media = {}
        print("Loading visuals...")
        for gif in self.gifs_path.iterdir():
            gif = Gif(gif)
            gif.texture_UUID = self.get_texture_UUID_for_media(gif)
            media[gif.ID] = gif
        for vid in self.vids_path.iterdir():
            vid = Video(vid)
            vid.texture_UUID = self.get_texture_UUID_for_media(vid)
            vid.pbo_UUID = self.get_pbo_UUID_for_video(vid)
            media[vid.ID] = vid
        print("Visuals loaded.")
        return media
    
    def get_texture_UUID_for_media(self, media):
        if media.texture_UUID is None:
            size = media.size
            is_video = True if isinstance(media, Video) else False
            UUID = str(uuid.uuid5(uuid.NAMESPACE_DNS, f'{type(media).__name__}{size}'))
            self.renderer.create_textures(UUID, size, is_video)
            return UUID
        return media.texture_UUID
    
    def get_pbo_UUID_for_video(self, media):
        if media.pbo_UUID is None:
            size = media.size
            num_pbos = 2
            UUID = str(uuid.uuid5(uuid.NAMESPACE_DNS, f'{type(media).__name__}{size}{num_pbos}'))
            self.renderer.create_pbos(UUID, size, num_pbos)
            return UUID
        return media.pbo_UUID
    
    def terminate(self):
        self.renderer.terminate()
        self.window.terminate()
        sys.exit(0)
    
if __name__ == "__main__":
    GIFS_PATH  = "./data/gifs/"
    VIDS_PATH = "./data/vids/"
    mp = MediaPlayer(GIFS_PATH, VIDS_PATH, fullscreen=False)
    mp.start_on_new_process()
    mp.queue_media("stock")
