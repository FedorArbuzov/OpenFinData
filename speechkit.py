import xml.etree.ElementTree as XmlElementTree
import subprocess
import httplib2
import requests
import uuid
import random
from config import SETTINGS, YANDEX_API_KEY
from ffmpy import FFmpeg

YANDEX_ASR_HOST = 'asr.yandex.net'
YANDEX_ASR_PATH = '/asr_xml'
CHUNK_SIZE = 1024 ** 2
PATH_TO_FFMPEG = SETTINGS.get('PATH_TO_FFMPEG')
TTS_URL = 'https://tts.voicetech.yandex.net/generate'


def convert_to_ogg(in_filename: str = None, in_content: bytes = None):
    ff = FFmpeg(
        executable=PATH_TO_FFMPEG,
        inputs={'pipe:0': None},
        outputs={'pipe:1': ['-f', 'ogg', '-acodec', 'libopus']}
    )
    stdout = None

    if in_filename:
        stdout, stderr = ff.run(input_data=open(in_filename, 'br').read(), stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    elif in_content:
        stdout, stderr = ff.run(input_data=in_content, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return stdout


def convert_to_mp3(in_filename: str = None, in_content: bytes = None):
    ff = FFmpeg(
        executable=PATH_TO_FFMPEG,
        inputs={'pipe:0': None},
        outputs={'pipe:1': ['-f', 'mp3', '-acodec', 'libmp3lame']}
    )
    stdout = None

    if in_filename:
        stdout, stderr = ff.run(input_data=open(in_filename, 'br').read(), stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    elif in_content:
        stdout, stderr = ff.run(input_data=in_content, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return stdout


def convert_to_pcm16b16000r(in_filename=None, in_bytes=None):
    ff = FFmpeg(
        executable=PATH_TO_FFMPEG,
        inputs={'pipe:0': None},
        outputs={'pipe:1': ['-f', 's16le', '-acodec', 'pcm_s16le', '-ar', '16000']}
    )
    stdout = None

    if in_filename:
        stdout, stderr = ff.run(input_data=open(in_filename, 'br').read(), stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    elif in_bytes:
        stdout, stderr = ff.run(input_data=in_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return stdout


def read_chunks(chunk_size, bytes):
    while True:
        chunk = bytes[:chunk_size]
        bytes = bytes[chunk_size:]

        yield chunk

        if not bytes:
            break


def text_to_speech(text, lang='ru-RU', filename=None, file_like=None, convert=True, as_audio=False):
    # speaker = random.choice(['jane', 'oksan', 'alyss', 'omazh', 'zahar', 'ermil'])  # Голоса озвучки текста
    speaker = 'zahar'
    emotion = random.choice(['neutral', 'good'])

    url = TTS_URL + '?text={}&format={}&lang={}&speaker={}&key={}&emotion={}&speed={}'.format(
        text, 'mp3', lang, speaker, YANDEX_API_KEY, emotion, '1.0')

    print('{}: {}-{}-{}'.format(__name__, text, speaker, emotion))

    r = requests.get(url)
    if r.status_code == 200:
        response_content = r.content
    else:
        raise Exception('{}: {}'.format(__name__, r.text))

    if not as_audio and convert:
        response_content = convert_to_ogg(in_content=response_content)

    if filename:
        with open(filename, 'bw') as file:
            file.write(response_content)
    elif file_like:
        file_like.write(response_content)

    return response_content


def speech_to_text(filename=None, bytes=None, request_id=uuid.uuid4().hex, topic='notes', lang='ru-RU'):
    if filename:
        with open(filename, 'br') as file:
            bytes = file.read()
    if not bytes:
        raise Exception('Neither file name nor bytes provided.')

    bytes = convert_to_pcm16b16000r(in_bytes=bytes)

    url = YANDEX_ASR_PATH + '?uuid=%s&key=%s&topic=%s&lang=%s' % (
        request_id,
        YANDEX_API_KEY,
        topic,
        lang
    )
    chunks = read_chunks(CHUNK_SIZE, bytes)

    connection = httplib2.HTTPConnectionWithTimeout(YANDEX_ASR_HOST)

    connection.connect()
    connection.putrequest('POST', url)
    connection.putheader('Transfer-Encoding', 'chunked')
    connection.putheader('Content-Type', 'audio/x-pcm;bit=16;rate=16000')
    connection.endheaders()

    for chunk in chunks:
        connection.send(('%s\r\n' % hex(len(chunk))[2:]).encode())
        connection.send(chunk)
        connection.send('\r\n'.encode())

    connection.send('0\r\n\r\n'.encode())
    response = connection.getresponse()

    if response.code == 200:
        response_text = response.read()
        xml = XmlElementTree.fromstring(response_text)

        if int(xml.attrib['success']) == 1:
            max_confidence = - float("inf")
            text = ''

            for child in xml:
                if float(child.attrib['confidence']) > max_confidence:
                    text = child.text
                    max_confidence = float(child.attrib['confidence'])

            if max_confidence != - float("inf"):
                return text
            else:
                raise SpeechException('No text found.\n\nResponse:\n%s\n\nRequest id: %s' % (response_text, request_id))
        else:
            raise SpeechException('No text found.\n\nResponse:\n%s\n\nRequest id: %s' % (response_text, request_id))
    else:
        raise SpeechException('Unknown error.\nCode: %s\n\n%s' % (response.code, response.read()))


class SpeechException(Exception):
    pass
