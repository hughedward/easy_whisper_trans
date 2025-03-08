# easy_whisper_trans
<img width="799" alt="image" src="https://github.com/user-attachments/assets/3d818346-ac55-4245-a3ad-59e79e596e48" />
利用openAi-whisper实现的语音转录文字；
采用streamlit构建

运行start.sh
<img width="1280" alt="image" src="https://github.com/user-attachments/assets/fbe2ff57-d124-4b6c-a7fd-a597e2d40294" />
## 使用说明
上传音频文件（支持mp3、wav、m4a、ogg、mp4格式）
选择模型大小（tiny最快但准确度较低，large最慢但准确度最高）
选择音频语言（如果确定语言可以提高准确度）
等待处理完成后可以查看结果
点击转换按钮可以查看SRT格式的字幕
点击"下载文本文件"后，系统会在时间戳文件夹中生成多种格式的字幕文件

## 注意事项
处理时间取决于音频长度和选择的模型大小
建议先用小模型测试，确认效果后再使用大模型
如遇到错误请检查音频文件格式是否正确
生成的字幕文件包括：JSON、SRT、TSV、TXT、VTT格式
可以随时点击"取消转录"按钮停止转录过程

