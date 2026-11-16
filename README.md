# 人教版英语五年级上册U1-U6单词库

手机竖屏优先的英语点读页，使用 GitHub Pages 发布。六个单元通过同一链接访问，按单元、黑体和白体分类；保留课本星号。

| 单元 | 总数 | 黑体 | 白体 |
| --- | --- | --- | --- |
| U1 | 18 | 9 | 9 |
| U2 | 17 | 6 | 11 |
| U3 | 20 | 8 | 12 |
| U4 | 20 | 7 | 13 |
| U5 | 20 | 8 | 12 |
| U6 | 23 | 7 | 16 |

共 118 项，Monday 按课本同时保留在 U2 白体和 U3 黑体。

2026-11-16 点读性能更新：音频按三个词拆成小包，独立音素共用小文件。先加载当前词，再预取邻近内容；切换时取消过时下载。点读优先使用已解码的 Web Audio 缓存，避免每次点击重新初始化媒体文件，并保留原生音频回退。

整词、完整音标、逐音素和例句可点击朗读。例句及中文翻译为小学教学编写。连续朗读支持只读单词或单词、已有音节、音素和例句，每项一次，到本组末尾停止。切换单元、单词或离开页面时停止播放。

2026-11-16：U4、U5 分音节使用明确 IPA 生成的英式女声并校准音量，保留首尾留白；不同于上一版混合音节来源。different 为 /dɪf/、/rənt/。heavy 修正为 /hev/、/i/，也已补录。U1、U2、U3、U6 其余缺少的新音节按使用者要求后续分天补齐；待补录按钮为灰色，连续朗读会跳过它们。

单词和例句主要使用 en-GB-SoniaNeural 女声；close、wind 保留明确读音的 Amy 女声，Mrs 保留词典整词。音素来自 Cambridge Dictionary UK 的独立录音。多音节拆读来自 Amazon Polly Emma en-GB，通过 ttsMP3 免费额度制作。单音节词复用完整单词录音。

音频随页面部署，不在手机端调用第三方语音接口。无外部字体、脚本或跟踪服务。第三方录音不声明为原创或开源授权。

素材来源：[Cambridge Dictionary](https://dictionary.cambridge.org/help/phonetics.html)、[ttsMP3](https://ttsmp3.com/text-to-speech/British%20English/)、Microsoft Edge Read Aloud，以及历史保留录音的有道词典。ttsMP3 允许音频用于网站和教学。

## 生成和发布

`build.py` 结合 `units123.py`、`phonics.py` 生成词表。`prepare_female_audio.py` 准备适配语音提供方的 IPA；`process_female_audio.py` 按显式停顿分离录音并校准音量；`package_v2.py` 从本地录音目录生成 `release/`。发布 `release/` 中的文件到 GitHub Pages 根目录。制作所需的原始录音保存在本机备份中。

保留原有 U4–U6 词条编号，既有定位链接仍有效。GitHub Pages 在不同地区、运营商和微信内的实际可达性需要用目标手机验证。
