from gtts import gTTS
import pygame
import time

# 初始化pygame
pygame.mixer.init()

# 生成语音文件并调整语速
def generate_tts(text, filename, speed='fast'):
    tts = gTTS(text, lang='zh-cn', slow=(speed == 'slow'))
    tts.save(filename)

# 生成声音文件，语速调整为快
generate_tts("往左", "left_fast.mp3", speed='fast')
generate_tts("往前", "forward_fast.mp3", speed='fast')
generate_tts("往右", "right_fast.mp3", speed='fast')
generate_tts("往后", "back_fast.mp3", speed='fast')
generate_tts("未识别成功", "bad.mp3", speed='fast')
generate_tts("正确位置", "good.mp3", speed='fast')
generate_tts("正在抓取", "catch.mp3", speed='fast')

# 加载声音文件
sounds = {
    "未识别成功": pygame.mixer.Sound("bad.mp3"),
    "正确位置": pygame.mixer.Sound("good.mp3"),
    "正在抓取": pygame.mixer.Sound("catch.mp3"),
    "左": pygame.mixer.Sound("left_fast.mp3"),
    "前": pygame.mixer.Sound("forward_fast.mp3"),
    "右": pygame.mixer.Sound("right_fast.mp3"),
    "后": pygame.mixer.Sound("back_fast.mp3")
}

def play_sound(direction):
    if direction in sounds:
        sounds[direction].play()
        time.sleep(sounds[direction].get_length())  # 等待声音播放完毕
    else:
        print("无效的方向")

if __name__ == '__main__':
    play_sound("未识别成功")
    play_sound("正确位置")
    play_sound("正在抓取")
    play_sound("左")
    play_sound("前")
    play_sound("右")
    play_sound("后")
