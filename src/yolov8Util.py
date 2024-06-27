from PIL import ImageGrab, Image
from ultralytics import YOLO
from utils import timer_log
from loguru import logger
import time
import threading
from datetime import datetime
import os
from utils import get_real_path, get_log_path

# # Load a pretrained YOLOv8n model
# Load a model
MONITOR_WIDTH, MONITOR_HEIGHT = ImageGrab.grab().size


file_path = get_real_path("yolov8/best.pt", "resource")
model = YOLO(file_path)  # pretrained YOLOv8n model
# images = get_real_path("test.png", "resource")
# results = model.predict(source=images, conf=0.6)


def result_save(result, ts):
    logger.info(f"save_result: {ts}")
    result.save(filename=f"./debug/{ts}_boss.jpg")


# @timer_log
def get_boss_result(image: Image.Image, conf, save=False):
    try:
        global model
        results = model.predict(source=image, conf=conf, save=save)
        # results = model(image)
        for result in results:
            boxes = result.boxes  # Boxes object for bounding box outputs
            for b in boxes:
                class_item = b.cls.item()
                class_conf = b.conf.item()
                class_xywh = b.xywh.tolist()[0]
                if class_item == float(1):
                    # # yolobbox2bbox(*class_xywh)
                    # if save:
                    now_time = datetime.now()
                    ts = now_time.strftime("%m-%d_%H_%M_%S")
                    t = threading.Thread(target=result_save, args=(result, ts))
                    t.start()
                    return True
        return False
    except Exception as e:
        import traceback

        traceback.print_exc()

        with open(get_log_path(), "a", encoding="utf-8") as f:
            f.write(traceback.format_exc() + "\n")
            f.write(f"{e}\n")
        return False


# def draw_rect(x, y, x1, y1):
#     import win32gui, win32api

#     brush = win32gui.CreateSolidBrush(win32api.RGB(255, 0, 0))

#     dc = win32gui.GetDC(0)
#     x, y, x1, y1 = int(x), int(y), int(x1), int(y1)
#     logger.info(f"draw_rect: {x, y, x1,y1}")
#     win32gui.FrameRect(dc, (x, y, x1, y1), brush)
#     # win32gui.ReleaseDC(0, dc)


# def yolobbox2bbox(x, y, w, h):
#     x1, y1 = x - w / 2, y - h / 2
#     x2, y2 = x + w / 2, y + h / 2
#     draw_rect(x1, y1, x2, y2)
#     return x1, y1, x2, y2


# def detect():
#     image = ImageGrab.grab(bbox=(0, 0, MONITOR_WIDTH, MONITOR_HEIGHT))
#     image.save("test.png")
#     results = model(image)
#     for result in results:
#         boxes = result.boxes  # Boxes object for bounding box outputs
#         for b in boxes:
#             class_xywh = b.xywh.tolist()[0]
#             yolobbox2bbox(*class_xywh)


# def timer_draw(event):
#     import win32gui, win32api

#     frame = 1 / 30
#     while True:
#         if event.is_set():
#             break
#         detect()
#         time.sleep(frame)
#         dc = win32gui.GetDC(0)
#         win32gui.ReleaseDC(0, dc)


# draw_rect(1365, 87, 1866, 1033)
# detect()
# get_boss_result(ImageGrab.grab([0, 0, 1000, 2000]))
