import io
import traceback
import numpy as np
from pydub import AudioSegment
import gradio as gr
import asyncio

import torch
from pluginInterface import TTSPluginInterface
import os
import edge_tts

from plugins.rvc.rmvpe import RMVPE
from plugins.rvc.vc_infer_pipeline import VC
from plugins.rvc.lib.infer_pack.models import (
    SynthesizerTrnMs256NSFsid,
    SynthesizerTrnMs256NSFsid_nono,
    SynthesizerTrnMs768NSFsid,
    SynthesizerTrnMs768NSFsid_nono,
)
from plugins.rvc.config import Config
import librosa
from fairseq import checkpoint_utils
from scipy.io import wavfile


class rvc(TTSPluginInterface):
    current_module_directory = os.path.dirname(__file__)
    rvc_models_dir = os.path.join(
        current_module_directory, "rvc_models")
    TTS_OUTPUT_FILENAME = os.path.join(
        current_module_directory, "edgetts_output.mp3")
    RVC_OUTPUT_FILENAME = os.path.join(
        current_module_directory, "RVC_output.mp3")

    voices = []
    rvc_models = []
    hubert_model = None
    rmvpe_model = None
    config = Config()
    vc = VC(config)

    def init(self):
        self.names = []
        for name in os.listdir(self.rvc_models_dir):
            if name.endswith(".pth"):
                self.names.append(name)
        index_paths = []
        # for root, dirs, files in os.walk(index_root, topdown=False):
        #     for name in files:
        #         if name.endswith(".index") and "trained" not in name:
        #             index_paths.append("%s/%s" % (root, name))

    def synthesize(self, text):

        print(f'Outputting audio to {self.TTS_OUTPUT_FILENAME}')
        # print(f'{string}')
        VOICE = "en-GB-SoniaNeural"
        communicate = edge_tts.Communicate(text, VOICE)
        asyncio.run(communicate.save(self.TTS_OUTPUT_FILENAME))

        # Load the MP3 file
        audio = AudioSegment.from_mp3(self.TTS_OUTPUT_FILENAME)

        # Convert it to WAV format
        wav_filename = self.TTS_OUTPUT_FILENAME.replace('.mp3', '.wav')
        audio.export(wav_filename, format='wav')

        print('Running RVC')
        audio = self.tts(self.TTS_OUTPUT_FILENAME, "kikuri.pth")
        print(audio)
        wavfile.write(self.RVC_OUTPUT_FILENAME, 44100, audio.astype(np.int16))
        # with open(self.RVC_OUTPUT_FILENAME, "wb") as file:
        #     file.write(audio)

        # audio = AudioSegment.from_wav(self.RVC_OUTPUT_FILENAME)
        # samples = np.array(audio.get_array_of_samples())

        # Gradio expects (sample_rate, audio_array)
        # return (audio.frame_rate, samples)
        return None

    def create_ui(self):
        with gr.Accordion(label="rvc Options", open=False):
            with gr.Tabs():
                with gr.TabItem(("模型推理")):
                    with gr.Row():
                        sid0 = gr.Dropdown(label=(
                            "推理音色"), choices=sorted(self.names))
                        with gr.Column():
                            refresh_button = gr.Button(
                                ("刷新音色列表和索引路径"), variant="primary"
                            )
                            clean_button = gr.Button(
                                ("卸载音色省显存"), variant="primary")
                        spk_item = gr.Slider(
                            minimum=0,
                            maximum=2333,
                            step=1,
                            label=("请选择说话人id"),
                            value=0,
                            visible=False,
                            interactive=True,
                        )
                        clean_button.click(
                            fn=self.clean, inputs=[], outputs=[sid0], api_name="infer_clean"
                        )
                    with gr.TabItem(("单次推理")):
                        with gr.Group():
                            with gr.Row():
                                with gr.Column():
                                    vc_transform0 = gr.Number(
                                        label=("变调(整数, 半音数量, 升八度12降八度-12)"), value=0
                                    )
                                    input_audio0 = gr.Textbox(
                                        label=("输入待处理音频文件路径(默认是正确格式示例)"),
                                        placeholder="C:\\Users\\Desktop\\audio_example.wav",
                                    )
                                    file_index1 = gr.Textbox(
                                        label=("特征检索库文件路径,为空则使用下拉的选择结果"),
                                        placeholder="C:\\Users\\Desktop\\model_example.index",
                                        interactive=True,
                                    )
                                    file_index2 = gr.Dropdown(
                                        label=(
                                            "自动检测index路径,下拉式选择(dropdown)"),
                                        choices=sorted(self.index_paths),
                                        interactive=True,
                                    )
                                    f0method0 = gr.Radio(
                                        label=(
                                            "选择音高提取算法,输入歌声可用pm提速,harvest低音好但巨慢无比,crepe效果好但吃GPU,rmvpe效果最好且微吃GPU"
                                        ),
                                        choices=["pm", "harvest",
                                                 "crepe", "rmvpe"]
                                        if self.config.dml == False
                                        else ["pm", "harvest", "rmvpe"],
                                        value="rmvpe",
                                        interactive=True,
                                    )

                                with gr.Column():
                                    resample_sr0 = gr.Slider(
                                        minimum=0,
                                        maximum=48000,
                                        label=("后处理重采样至最终采样率，0为不进行重采样"),
                                        value=0,
                                        step=1,
                                        interactive=True,
                                    )
                                    rms_mix_rate0 = gr.Slider(
                                        minimum=0,
                                        maximum=1,
                                        label=(
                                            "输入源音量包络替换输出音量包络融合比例，越靠近1越使用输出包络"),
                                        value=0.25,
                                        interactive=True,
                                    )
                                    protect0 = gr.Slider(
                                        minimum=0,
                                        maximum=0.5,
                                        label=(
                                            "保护清辅音和呼吸声，防止电音撕裂等artifact，拉满0.5不开启，调低加大保护力度但可能降低索引效果"
                                        ),
                                        value=0.33,
                                        step=0.01,
                                        interactive=True,
                                    )
                                    filter_radius0 = gr.Slider(
                                        minimum=0,
                                        maximum=7,
                                        label=(
                                            ">=3则使用对harvest音高识别的结果使用中值滤波，数值为滤波半径，使用可以削弱哑音"
                                        ),
                                        value=3,
                                        step=1,
                                        interactive=True,
                                    )
                                    index_rate1 = gr.Slider(
                                        minimum=0,
                                        maximum=1,
                                        label=("检索特征占比"),
                                        value=0.75,
                                        interactive=True,
                                    )
                                    f0_file = gr.File(
                                        label=("F0曲线文件, 可选, 一行一个音高, 代替默认F0及升降调"), visible=False
                                    )

                                    refresh_button.click(
                                        fn=self.change_choices,
                                        inputs=[],
                                        outputs=[sid0, file_index2],
                                        api_name="infer_refresh",
                                    )
                                    # file_big_npy1 = gr.Textbox(
                                    #     label=("特征文件路径"),
                                    #     value="E:\\codes\py39\\vits_vc_gpu_train\\logs\\mi-test-1key\\total_fea.npy",
                                    #     interactive=True,
                                    # )
                        with gr.Group():
                            with gr.Column():
                                but0 = gr.Button(("转换"), variant="primary")
                                with gr.Row():
                                    vc_output1 = gr.Textbox(label=("输出信息"))
                                    vc_output2 = gr.Audio(
                                        label=("输出音频(右下角三个点,点了可以下载)"))

                                but0.click(
                                    self.vc.vc_single,
                                    [
                                        spk_item,
                                        input_audio0,
                                        vc_transform0,
                                        f0_file,
                                        f0method0,
                                        file_index1,
                                        file_index2,
                                        # file_big_npy1,
                                        index_rate1,
                                        filter_radius0,
                                        resample_sr0,
                                        rms_mix_rate0,
                                        protect0,
                                    ],
                                    [vc_output1, vc_output2],
                                    api_name="infer_convert",
                                )
            gr.Markdown(
                "test")

    def model_data(self, model_name):
        pth_path = f'{self.current_module_directory}/rvc_models/{model_name}'

        cpt = torch.load(pth_path, map_location="cpu")
        tgt_sr = cpt["config"][-1]
        cpt["config"][-3] = cpt["weight"]["emb_g.weight"].shape[0]  # n_spk
        if_f0 = cpt.get("f0", 1)
        version = cpt.get("version", "v1")
        if version == "v1":
            if if_f0 == 1:
                net_g = SynthesizerTrnMs256NSFsid(*cpt["config"], is_half=True)
            else:
                net_g = SynthesizerTrnMs256NSFsid_nono(*cpt["config"])
        elif version == "v2":
            if if_f0 == 1:
                net_g = SynthesizerTrnMs768NSFsid(*cpt["config"], is_half=True)
            else:
                net_g = SynthesizerTrnMs768NSFsid_nono(*cpt["config"])
        else:
            raise ValueError("Unknown version")
        del net_g.enc_q
        net_g.load_state_dict(cpt["weight"], strict=False)
        print("Model loaded")
        net_g.eval()
        net_g = net_g.half()
        vc = VC(tgt_sr, self.rvc_config)
        # n_spk = cpt["config"][-3]

        index_file = ''

        return tgt_sr, net_g, vc, version, index_file, if_f0

    def tts(self,
            output_file,
            model_name,
            f0_up_key=1,
            f0_method='rmvpe',
            index_rate=1,
            protect=0.33,
            filter_radius=3,
            resample_sr=0,
            rms_mix_rate=0.25,
            ):
        try:
            edge_output_filename = output_file

            tgt_sr, net_g, vc, version, index_file, if_f0 = self.model_data(
                model_name)

            audio, sr = librosa.load(edge_output_filename, sr=16000, mono=True)
            duration = len(audio) / sr

            print(f"Audio duration: {duration}s")

            f0_up_key = int(f0_up_key)

            if not self.hubert_model:
                self.load_hubert()
            if f0_method == "rmvpe":
                vc.model_rmvpe = self.rmvpe_model
            times = [0, 0, 0]
            audio_opt = vc.pipeline(
                self.hubert_model,
                net_g,
                0,
                audio,
                edge_output_filename,
                times,
                f0_up_key,
                f0_method,
                index_file,
                # file_big_npy,
                index_rate,
                if_f0,
                filter_radius,
                tgt_sr,
                resample_sr,
                rms_mix_rate,
                version,
                protect,
                None,
            )
            if tgt_sr != resample_sr >= 16000:
                tgt_sr = resample_sr
            info = f"Success."
            print(info)
            return audio_opt
        except EOFError:
            info = (
                "It seems that the edge-tts output is not valid. "
                "This may occur when the input text and the speaker do not match. "
                "For example, maybe you entered Japanese (without alphabets) text but chose non-Japanese speaker?"
            )
            print(info)

        except:
            info = traceback.format_exc()
            print(info)
            return info, None, None

    def load_hubert(self):
        models, _, _ = checkpoint_utils.load_model_ensemble_and_task(
            [f"{self.current_module_directory}/hubert_base.pt"],
            suffix="",
        )
        self.hubert_model = models[0]
        self.hubert_model = self.hubert_model.to(self.rvc_config.device)
        if self.rvc_config.is_half:
            self.hubert_model = self.hubert_model.half()
        else:
            self.hubert_model = self.hubert_model.float()
        return self.hubert_model.eval()

    def clean(self):
        return {"value": "", "__type__": "update"}

    def change_choices(self):
        names = []
        for name in os.listdir(self.rmvpe_model):
            if name.endswith(".pth"):
                names.append(name)
        index_paths = []
        for root, dirs, files in os.walk(self.rvc_models_dir, topdown=False):
            for name in files:
                if name.endswith(".index") and "trained" not in name:
                    index_paths.append("%s/%s" % (root, name))
        return {"choices": sorted(names), "__type__": "update"}, {
            "choices": sorted(index_paths),
            "__type__": "update",
        }
