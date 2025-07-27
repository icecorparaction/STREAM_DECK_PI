from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

def change_volume(step):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    
    current = volume.GetMasterVolumeLevelScalar()
    new_volume = min(max(current + step, 0.0), 1.0)  # clamp 0.0–1.0
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    print(f"Громкость: {int(new_volume * 100)}%")

# Пример: прибавить громкость
change_volume(+0.05)

