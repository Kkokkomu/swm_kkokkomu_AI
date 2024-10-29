import os
from google.cloud import speech_v1p1beta1 as speech
import io
from moviepy.editor import ImageClip, concatenate_videoclips, CompositeAudioClip, TextClip, CompositeVideoClip, AudioFileClip, VideoFileClip
from pydub import AudioSegment

def transcribe_audio_with_timing(audio_path):
    client = speech.SpeechClient()

    with io.open(audio_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=24000,
        language_code="ko-KR",
        enable_word_time_offsets=True  # 타이밍 정보 활성화
    )

    response = client.recognize(config=config, audio=audio)

    words_info = []
    for result in response.results:
        alternative = result.alternatives[0]
        for word_info in alternative.words:
            word = word_info.word
            start_time = word_info.start_time.total_seconds()
            end_time = word_info.end_time.total_seconds()
            words_info.append({
                'word': word,
                'start': start_time,
                'end': end_time
            })
    
    return words_info

def wrap_text(text, max_chars_per_line):
    """주어진 텍스트를 최대 너비를 초과하지 않도록 줄바꿈합니다."""
    import textwrap
    return "\n".join(textwrap.wrap(text, width=max_chars_per_line))
os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

def create_subtitle_clips(video, sentences, words_info, chunk_size=5, fontsize=50, font='NanumBarunGothic-Bold', color='white', stroke_color='black', stroke_width=2, max_chars_per_line=20):
    subtitle_clips = []
    
    for sentence_idx, (sentence_start_time, sentence_end_time) in enumerate(sentences):
        # Extract words for the current sentence
        sentence_words = [word_info for word_info in words_info if sentence_start_time <= word_info['end'] <= sentence_end_time]
        
        for i in range(0, len(sentence_words), chunk_size):
            chunk = sentence_words[i:i + chunk_size]
            text = " ".join([word['word'] for word in chunk])
            start_time = chunk[0]['start']
            end_time = chunk[-1]['end']
            duration = end_time - start_time

            wrapped_text = wrap_text(text, max_chars_per_line)
            text_lines = wrapped_text.count('\n') + 1
            text_clip_height = text_lines * fontsize

            position_y = video.size[1] - 400 - (text_clip_height // 2)
            
            subtitle_clip = (TextClip(wrapped_text, fontsize=fontsize, font=font, color=color, 
                                      stroke_color=stroke_color, stroke_width=stroke_width, 
                                      size=(video.size[0] - 40, None), method='caption')
                             .set_position(("center", position_y))
                             .set_start(start_time)
                             .set_duration(duration))
            subtitle_clips.append(subtitle_clip)
    
    return subtitle_clips

def convert_mp3_to_wav(mp3_path, wav_path):
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")

def concatenate_audios(audio_paths, output_path, silence_duration=0):
    combined = AudioSegment.empty()
    silence = AudioSegment.silent(duration=silence_duration)  # 무음
    for path in audio_paths:
        audio = AudioSegment.from_file(path)
        combined += audio + silence
    combined.export(output_path, format="wav")

def create_image_sequence_video(image_paths, durations, output_path, fps=24):
    clips = []
    target_aspect_ratio = 9/16  # 9:16 비율
    target_width = 1080  # 기준 너비 (영상 크기를 설정할 수 있음)
    target_height = int(target_width / target_aspect_ratio)

    for image_path, duration in zip(image_paths, durations):
        clip = ImageClip(image_path, duration=duration)

        # 현재 이미지의 가로, 세로 비율 계산
        current_aspect_ratio = clip.w / clip.h
        
        # 이미지가 더 넓은 경우: 가로 크기를 유지하고 세로 여백만 추가
        new_width = target_width
        new_height = int(new_width / current_aspect_ratio)
        
        # 이미지 크기 조정
        clip = clip.resize(newsize=(new_width, new_height))
        
        # 위아래에 여백 추가
        clip = clip.on_color(size=(new_width, target_height), color=(0, 0, 0), pos=("center", "center"))
        
        clips.append(clip)
    
    video = concatenate_videoclips(clips, method="compose")
    video.write_videofile(output_path, fps=fps, codec="libx264")

def getBgmBySection(section):
    if section == "정치":
        path = './resource/bgm/politics.mp3'
    elif section == "경제":
        path = './resource/bgm/economy.mp3'
    elif section == "사회":
        path = './resource/bgm/social.mp3'
    elif section == "세계":
        path = './resource/bgm/world.mp3'
    elif section == "생활":
        path = './resource/bgm/living.mp3'
    elif section == "IT":
        path = './resource/bgm/it.mp3'
    elif section == "스포츠":
        path = './resource/bgm/sports.mp3'
    elif section == "연예":
        path = './resource/bgm/entertain.mp3'
    
    return path

def generate_video(section, title):
    # 파일 경로
    audio_paths = [
        './resource/sentence_0.wav',
        './resource/sentence_1.wav',
        './resource/sentence_2.wav'
    ]
    image_paths = [
        './resource/sentence_0.png',
        './resource/sentence_1.png',
        './resource/sentence_2.png'
    ]
    bgm_path = getBgmBySection(section)
    combined_audio_path = './resource/combined_audio.wav'
    video_output_path = './resource/generated_video.mp4'
    output_directory = './resource'
    final_output_path = os.path.join(output_directory, 'final_output.mp4')
    

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_stt_secret.json"

    # 여러 개의 오디오 파일을 하나로 결합
    concatenate_audios(audio_paths, combined_audio_path)

    # 각 오디오 파일의 길이를 가져옴 (딜레이 없이 계산)
    durations = [AudioSegment.from_file(path).duration_seconds for path in audio_paths]
    print("duration[0] : " + str(durations[0]))
    print("duration[1] : " + str(durations[1]))
    print("duration[2] : " + str(durations[2]))


    # 이미지 시퀀스를 사용하여 비디오 생성
    create_image_sequence_video(image_paths, durations, video_output_path)

    # 생성된 비디오와 오디오 클립 불러오기
    video = VideoFileClip(video_output_path)
    audio = AudioFileClip(combined_audio_path)

    video = video.set_audio(audio)

    # 결합된 음성 파일로부터 단어 타이밍 정보 추출
    words_info = transcribe_audio_with_timing(combined_audio_path)

    # 각 문장의 시작과 끝 시간을 저장 (딜레이 없이)
    sentence_times = [
        (0, durations[0]),  # sentence_0
        (durations[0], durations[0] + durations[1]),  # sentence_1
        (durations[0] + durations[1], sum(durations))  # sentence_2
    ]

    # 단어 타이밍 정보로부터 자막 클립 생성
    subtitle_clips = create_subtitle_clips(video, sentence_times, words_info)

    # **추가된 코드: 제목 클립 생성**
    max_chars_per_line = 20
    
    title = wrap_text(title, max_chars_per_line)

    title_clip = (TextClip(title, fontsize=50, font='NanumBarunGothic-Bold', color='white', stroke_color='black', stroke_width=2, size=(video.size[0] - 40, None), method='caption')
                  .set_position(("center", 300))  # 영상 상단에 제목 배치
                  .set_duration(video.duration))   # 전체 영상 길이 동안 제목을 표시

    # 비디오와 자막 합치기
    final_video = CompositeVideoClip([video, title_clip, *subtitle_clips])

    # 배경 음악 추가
    bgm_audio = AudioSegment.from_mp3(bgm_path)
    video_duration = final_video.duration * 1000  # 밀리초 단위로 변환
    bgm_audio = bgm_audio[:video_duration]  # 영상 길이에 맞게 자르기
    bgm_audio.export('./resource/bgm_cut.wav', format='wav')

    bgm_clip = AudioFileClip('./resource/bgm_cut.wav').volumex(0.05)  # 볼륨 조정
    final_video = final_video.set_audio(CompositeAudioClip([final_video.audio, bgm_clip]))

    # 결과물 저장
    final_video.write_videofile(final_output_path, codec='libx264', audio_codec='aac', fps=24)

    # 저장된 결과물의 자막 정보 출력
    for word_info in words_info:
        print(f"Word: {word_info['word']}, Start: {word_info['start']}, End: {word_info['end']}")

def addAdVideo():
    output_directory = './resource'
    ad_video_path = './resource/ad.mp4'
    final_video_path = './resource/final_output.mp4'
    final_output_path = './resource/final_output_withad.mp4'

    # 광고 영상 이어붙이기
    ad_video = VideoFileClip(ad_video_path)
    final_video = VideoFileClip(final_video_path)
    
    # 두 개의 비디오 클립을 이어붙임
    final_video_with_ad = concatenate_videoclips([final_video, ad_video], method="compose")

    # 결과물(광고 포함) 저장
    final_video_with_ad.write_videofile(final_output_path, codec='libx264', audio_codec='aac', fps=24)