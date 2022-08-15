# Temporal Ostracod Model

class TemporalOstracod:
    id = 0
    def __init__(self, location, area, frame_start, num_frames = 1):
        self.id = TemporalOstracod.get_id()
        self.location = location            # initial x, y coordinates
        self.area = area                    # area of the contour
        self.frame_start = frame_start      # frame number 
        self.num_frames = num_frames
        self.matches = []                   # indexes of another ostracod in a corresponding stereo frame, match value

    def __repr__(self):
      return('\nid: ' + str(self.id) + '\nlocation: ' + str(self.location) + '\tarea: ' + str(self.area)\
        + '\nframe start: ' + str(self.frame_start) + '\tnum frames: ' + str(self.num_frames))

    @staticmethod
    def get_id():
      TemporalOstracod.id = TemporalOstracod.id + 1
      return TemporalOstracod.id
