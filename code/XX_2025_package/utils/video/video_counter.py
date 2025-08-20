import os

class VideoCounter:
    ptr_file = os.path.join(os.path.dirname(__file__), "./video_counter_ptr.txt")
    
    @staticmethod
    def get_video_counter():
        if not os.path.exists(VideoCounter.ptr_file):
            with open(VideoCounter.ptr_file, "w") as f:
                f.write("0")
        with open(VideoCounter.ptr_file, "r") as f:
            return int(f.read().strip())
        
    @staticmethod
    def increment_video_counter():
        current_count = VideoCounter.get_video_counter()
        new_count = current_count + 1
        if new_count == 10:
            new_count = 0
        with open(VideoCounter.ptr_file, "w") as f:
            f.write(str(new_count))
        return new_count
    