from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from pytube import YouTube
import threading
import ffmpeg
import subprocess
from cv2 import cv2
import math


class Save():
    def __init__(self):
        self.arrayChunks = []
        self.isDownloadStopped = False #False - продолжить загрузку кусков, True - остановить

    def save(self, chunk):
        self.arrayChunks.append(chunk)

    def load(self):
        buffer = self.arrayChunks[0]
        self.arrayChunks.pop(0)
        if (len(self.arrayChunks) == 0): # == 0, значит всё уже забрал клиент
            self.isDownloadStopped = False #продолжить загрузку
        return buffer



class Loader(threading.Thread):

    def __init__(self, urlVideo, urlAudio, classSave, startPosition, sizeChunk, fps, vformat, aformat, vcodec, acodec, height, width):
        threading.Thread.__init__(self)
        self.urlAudio = ffmpeg.input(urlAudio, format=aformat, ss=startPosition)
        self.classSave = classSave
        self.height = height
        self.width = width
        self.sizeChunk = sizeChunk
        self.chunk = b""
        self.process1 = (
            ffmpeg
            .input(urlVideo, format='webm', ss=startPosition, r=fps)
            .output(self.urlAudio, 'pipe:', format='webm', r=fps, vcodec='vp8')
            .run_async(pipe_stdout=True)
        )

    def run(self):
        while True:
            if (classSave.isDownloadStopped == False):
                in_bytes = self.process1.stdout.read( int(self.width) * int(self.height) * 3)
                if not in_bytes:
                    break
                self.chunk += in_bytes


                self.classSave.save(self.chunk)
                self.chunk = b""

                if (len(classSave.arrayChunks) >= 10): #максимальное количество кусков 10
                    classSave.isDownloadStopped = True




classSave = Save()

arrayStreamsVideo = []
arrayStreamsAudio = []
arrayNormalVideo = []

threads = []

def deleteData():
    if (len(threads) > 0):
        arrayNormalVideo.clear()
        arrayStreamsAudio.clear()
        arrayStreamsVideo.clear()
        classSave.arrayChunks.clear()
        threads[0].process1.kill()
        subprocess.Popen.kill(threads[0].process1)
        threads.clear()

def index(request):
    deleteData()
    return render(request, 'index/index.html')

def loadCapacity(request):
    deleteData()

    try:
        yt = YouTube(request.POST["ref"])

        array = []

        #нормальное видео - это видео + звук
        #отделяю ссылки на нормальное видео, для скачивания
        for i in yt.streams.filter(mime_type="video/mp4", video_codec="avc1.42001E", audio_codec="mp4a.40.2", progressive="True", type="video"):
            arrayNormalVideo.append(i)

        #все возможные качества нормальных видео
        for capacity in arrayNormalVideo:
            array.append(int(str(capacity.resolution).replace("p", "")))

        array.sort(reverse=True)

        stringCapacityNormalVideo = ''
        for i in array:
            stringCapacityNormalVideo += str(i) + "p/"

        array.clear()

        #отделяю аудио потоки (ссылки на аудио дорожки)
        for i in yt.streams.filter(type='audio', mime_type='audio/webm'):
            arrayStreamsAudio.append(i)

        #сохранение качеств видео
        for capacity in yt.streams.filter(type='video'):
            array.append(capacity.resolution)
            arrayStreamsVideo.append(capacity)

        newArray = []
        for i in array:
            if (i):
                if int(i.replace("p", "")) not in newArray:
                    newArray.append(int(i.replace("p", "")))

        newArray.sort(reverse=True)

        stringCapacity = ''
        for i in newArray:
            stringCapacity += str(i) + "p/"

        return JsonResponse({
            'string': stringCapacity,
            'title': yt.title,
            'stringNormalVideo': stringCapacityNormalVideo,
        })
    except :
        return JsonResponse({
            'string': "",
            'title': "",
            'stringNormalVideo': "",
        })


def creatingALoader(request):
    deleteData()

    for stream in arrayStreamsVideo:
        if (stream.type == 'video' and
        str(stream.resolution) == str(request.POST['capacity']) and
        stream.mime_type == 'video/webm'):
            fps = cv2.VideoCapture(stream.url).get(cv2.CAP_PROP_FPS)
            duration = math.floor(cv2.VideoCapture(stream.url).get(cv2.CAP_PROP_FRAME_COUNT) / fps)
            sizeChunk = (stream.filesize / cv2.VideoCapture(stream.url).get(cv2.CAP_PROP_FRAME_COUNT)) * 1000
            width = cv2.VideoCapture(stream.url).get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cv2.VideoCapture(stream.url).get(cv2.CAP_PROP_FRAME_HEIGHT)

            vformat = str(stream.mime_type).split('/')[1]
            urlVideo = stream.url
            vcodec = stream.video_codec
            break

    print("1 sec ------------------- {}".format(sizeChunk))
    print("fps ------------------- {}".format(fps))
    print("duration ------------------- {}".format(duration))
    print("vcodec ------------------- {}".format(vcodec))
    print("vformat ------------------- {}".format(vformat))
    print("size ------------------- {}x{}".format(width, height) )

    urlAudio = arrayStreamsAudio[0].url
    aformat = str(arrayStreamsAudio[0].mime_type).split('/')[1]
    print("aformat ------------------- {}".format(aformat))


    threads.append(Loader(urlVideo, urlAudio, classSave, float(request.POST['currentTime']), sizeChunk, fps, vformat, aformat, 'webm', 'opus', height, width))
    threads[len(threads) - 1].start()

    return JsonResponse({
        "duration": duration,
        "vcodec": "vp8",
        "acodec": "opus",
        "mimeType": "video/{}".format('webm'),
    })


def chunkLoad(request):
    while True:
        if (len(classSave.arrayChunks) > 0):
            chunk = classSave.load()
            return HttpResponse(chunk)


def download(request):
    for i in arrayNormalVideo:
        if (str(i.resolution) == str(request.POST['resolution'])):
            return HttpResponse(i.url)
    return HttpResponse("")
