if __name__ == "__main__":
    import wave

    import numpy as np
    import pyaudio

    from TTService import TTService
    import os
    current_module_directory = os.path.dirname(__file__)

    model_dir = os.path.join(current_module_directory, "models")
    output_dir = os.path.join(current_module_directory, "output.wav")
    config_combo = [
            #( os.path.join(model_dir, "chisato.json"), os.path.join(model_dir, "chisato.pth")),
            ( os.path.join(model_dir, "xiangling-english_config.json"), os.path.join(model_dir, "D_xiangling.pth")),
        ]


    for cfg, model in config_combo:
        a = TTService(cfg, model, 'test', 1)
        p = pyaudio.PyAudio()
        audio = a.read('[EN]Ah, this is great! I feel so relaxed all over, I could almost float away.[EN]')
        # audio = a.read('[ZH]今天天气真好！[ZH]')
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=a.hps.data.sampling_rate,
                        output=True
                        )
        data = audio.astype(np.float32).tobytes()
        stream.write(data)
        # Set the output file name
        output_file = output_dir

        # Set the audio properties
        num_channels = 1
        sample_width = 2  # Assuming 16-bit audio
        frame_rate = a.hps.data.sampling_rate

        # Convert audio data to 16-bit integers
        audio_int16 = (audio * np.iinfo(np.int16).max).astype(np.int16)

        # Open the output file in write mode
        with wave.open(output_file, 'wb') as wav_file:
            # Set the audio properties
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(frame_rate)

            # Write audio data to the file
            wav_file.writeframes(audio_int16.tobytes())