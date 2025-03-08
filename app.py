import streamlit as st
from faster_whisper import WhisperModel
import tempfile
import os
import json
from datetime import datetime
import time
import torch

"""
hughadward123@gmail.com
2025-03-02
xigua_trans v0.0.2
"""


# 初始化session_state
if 'cancel_transcription' not in st.session_state:
    st.session_state.cancel_transcription = False
if 'progress' not in st.session_state:
    st.session_state.progress = 0

def format_timestamp(seconds):
    """将秒数转换为SRT格式的时间戳"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def convert_to_srt(segments):
    """将Whisper的识别结果转换为SRT格式"""
    srt_content = ""
    for i, segment in enumerate(segments, start=1):
        start_time = format_timestamp(segment['start'])
        end_time = format_timestamp(segment['end'])
        text = segment['text'].strip()
        # 添加空行分隔，确保格式正确
        srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
    return srt_content.rstrip()

def convert_to_vtt(segments):
    """将Whisper的识别结果转换为VTT格式"""
    vtt_content = "WEBVTT\n\n"
    for i, segment in enumerate(segments, start=1):
        start_time = format_timestamp(segment['start']).replace(',', '.')
        end_time = format_timestamp(segment['end']).replace(',', '.')
        text = segment['text'].strip()
        vtt_content += f"{start_time} --> {end_time}\n{text}\n\n"
    return vtt_content

def convert_to_tsv(segments):
    """将Whisper的识别结果转换为TSV格式"""
    tsv_content = "start\tend\ttext\n"
    for segment in segments:
        tsv_content += f"{segment['start']}\t{segment['end']}\t{segment['text'].strip()}\n"
    return tsv_content

##### 1. 页面布局  ######################################
# 设置页面标题和图标
st.set_page_config(
    page_title="西瓜转录 - 语音转文字",
    page_icon="🍉",
    layout="wide"
)

# 页面标题
st.title("🍉 西瓜转录 - 语音转文字")
# 创建两列布局
col1, col2 = st.columns([1, 1])

with col1:
    # 文件上传组件
    uploaded_file = st.file_uploader("选择音频文件", type=['mp3', 'wav', 'm4a', 'ogg', 'mp4'])
    
    # 模型选择
    model_type = st.selectbox(
        "选择模型大小-建议medium",
        ["medium", "tiny", "base", "small", "large"]
    )
    
    # 语言选择
    language = st.selectbox(
        "选择语言",
        ["中文", "自动检测", "英语", "日语", "韩语", "法语", "德语", "西班牙语", "俄语"]
    )
    
    # 语言代码映射
    language_code = {
        "自动检测": None,
        "中文": "zh",
        "英语": "en",
        "日语": "ja",
        "韩语": "ko",
        "法语": "fr",
        "德语": "de",
        "西班牙语": "es",
        "俄语": "ru"
    }
    # 转换按钮
    convert_clicked = st.button("开始转录字幕")
    # 取消转录
    cancel_btn = st.button("取消转录", type="secondary")

    # 进度条
    progress_bar = st.progress(0)
    status_text = st.empty()

    # 处理取消按钮点击事件
    if cancel_btn:
        st.session_state.cancel_transcription = True
        st.session_state.progress = 0
        progress_bar.progress(0)
        status_text.text("已取消转录")
        if 'result' in st.session_state:
            del st.session_state.result

    # ######2.功能实现################################
    # 以点击按钮事件为触发条件
    # 点击开始转录按钮后，执行以下代码
    if convert_clicked:
        # 重置取消标志和进度
        st.session_state.cancel_transcription = False
        st.session_state.progress = 0
        
        # 清理之前的结果
        if 'result' in st.session_state:
            del st.session_state.result

        # 记录开始时间
        start_time = time.time()

        # 显示处理状态
        with st.spinner("正在处理音频文件..."):
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                audio_path = tmp_file.name
            try:
                # 更新进度：开始加载模型
                st.session_state.progress = 10
                progress_bar.progress(st.session_state.progress)
                status_text.text("正在加载模型...")
                
                try:
                    # 加载模型
                    model = WhisperModel(model_type, device="cuda" if torch.cuda.is_available() else "cpu", compute_type="float16" if torch.cuda.is_available() else "int8")
                    
                    # 检查是否已取消
                    if st.session_state.cancel_transcription:
                        del model  # 确保释放模型资源
                        raise Exception("用户取消了转录")

                    # 更新进度：开始转录
                    st.session_state.progress = 30
                    progress_bar.progress(st.session_state.progress)
                    status_text.text("正在转录音频...")

                    # 转录音频
                    segments, info = model.transcribe(
                        audio_path,
                        language=language_code[language],
                        task="transcribe"
                    )
                    # 将segments转换为列表，以便后续多次使用
                    segments_list = list(segments)

                    # 打印segments和info
                    print(f"segments: {segments_list}")
                    print(f"info: {info}")
                    # 更新进度：处理转录结果
                    st.session_state.progress = 70
                    progress_bar.progress(st.session_state.progress)
                    status_text.text("正在处理转录结果...")

                    # 将segments转换为whisper格式的结果
                    st.session_state.result = {
                        "text": "\n".join([segment.text for segment in segments_list]),
                        "segments": [
                            {
                                "start": segment.start,
                                "end": segment.end,
                                "text": segment.text
                            } for segment in segments_list
                        ],
                        "language": info.language
                    }


                    # 检查是否已取消
                    if st.session_state.cancel_transcription:
                        del model  # 确保释放模型资源
                        raise Exception("用户取消了转录")

                    # 计算耗时
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    elapsed_minutes = int(elapsed_time // 60)
                    elapsed_seconds = int(elapsed_time % 60)

                    # 更新进度：完成
                    st.session_state.progress = 100
                    progress_bar.progress(st.session_state.progress)
                    status_text.text(f"转录完成！任务耗时：{elapsed_minutes}分{elapsed_seconds}秒")

                    # 显示结果
                    st.success("处理完成！")

                finally:
                    # 确保在任何情况下都释放模型资源
                    if 'model' in locals():
                        del model

            except Exception as e:
                if str(e) == "用户取消了转录":
                    st.warning("转录已取消")
                else:
                    st.error(f"处理音频文件时出错: {e}")
                # 重置进度
                st.session_state.progress = 0
                progress_bar.progress(0)
            finally:
                # 删除临时文件
                if os.path.exists(audio_path):
                    os.remove(audio_path)

with col2:
    # 转录结果预览(SRT格式)
    if 'result' in st.session_state and st.session_state.result is not None:
        srt_content = convert_to_srt(st.session_state.result["segments"])
        st.text_area("转录结果(SRT格式)", srt_content, height=400)
    else:
        st.text_area("转录结果预览", "", height=400)
    
    # 导出路径
    output_dir = st.text_input("导出路径", os.getcwd())
    # 导出按钮
    export_btn = st.button("导出结果")

    # 点击导出按钮后，执行以下代码
    if export_btn and 'result' in st.session_state and st.session_state.result is not None:
        try:
            # 创建时间戳文件夹
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, timestamp)
            os.makedirs(output_path, exist_ok=True)
            
            # 获取文件名（不包含扩展名）
            base_name = os.path.splitext(os.path.basename(uploaded_file.name))[0]
            
            # 使用with语句统一管理文件操作
            with open(os.path.join(output_path, f"{base_name}.srt"), 'w', encoding='utf-8') as f:
                f.write(convert_to_srt(st.session_state.result["segments"]))
            
            with open(os.path.join(output_path, f"{base_name}.tsv"), 'w', encoding='utf-8') as f:
                f.write(convert_to_tsv(st.session_state.result["segments"]))
            
            with open(os.path.join(output_path, f"{base_name}.txt"), 'w', encoding='utf-8') as f:
                f.write(st.session_state.result["text"])
            
            with open(os.path.join(output_path, f"{base_name}.vtt"), 'w', encoding='utf-8') as f:
                f.write(convert_to_vtt(st.session_state.result["segments"]))
            
            with open(os.path.join(output_path, f"{base_name}.json"), 'w', encoding='utf-8') as f:
                json.dump(st.session_state.result, f, ensure_ascii=False, indent=2)
            
            st.success(f"所有格式的字幕文件已保存到 {output_path} 文件夹")

            # 清理session_state中的结果
            del st.session_state.result

        except Exception as e:
            st.error(f"导出文件时出错: {e}")

# 添加使用说明
st.markdown("---")
st.markdown("""
### 使用说明
1. 上传音频文件（支持mp3、wav、m4a、ogg、mp4格式）
2. 选择模型大小（tiny最快但准确度较低，large最慢但准确度最高）
3. 选择音频语言（如果确定语言可以提高准确度）
4. 等待处理完成后可以查看结果
5. 点击"转换为SRT"按钮可以查看SRT格式的字幕
6. 点击"下载文本文件"后，系统会在时间戳文件夹中生成多种格式的字幕文件

### 注意事项
- 处理时间取决于音频长度和选择的模型大小
- 建议先用小模型测试，确认效果后再使用大模型
- 如遇到错误请检查音频文件格式是否正确
- 生成的字幕文件包括：JSON、SRT、TSV、TXT、VTT格式
- 可以随时点击"取消转录"按钮停止转录过程
""")
    




