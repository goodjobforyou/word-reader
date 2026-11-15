# 人教版英语五年级上册U4-U6单词库

手机优先的英语点读页面，使用 GitHub Pages 静态托管。

- U4：黑体 7 项、白体 13 项。
- U5：黑体 8 项、白体 12 项。
- U6：黑体 7 项、白体 16 项。
- 整词、完整音标、音节、每个音素、例句均可点击朗读。
- 英式词典整词与音素；英式合成例句与部分音节。
- 连读模式：只读单词／单词＋拆读＋例句。每项读一次，到本组末尾停止。
- 所有音频随页面部署，无第三方字体、脚本、语音接口或分析跟踪。

词表与黑白体分类来自提供的课本词表图片；星号保留。例句及中文翻译为教学编写。连读中的拆读依次包含音节、音素。`o…e` 等表示不相邻的字母组合；不发音的字母显示“ 不发音 ”。`Mrs` 为缩写，不按字母名称拆读。

## 发布

GitHub Settings → Pages → Deploy from a branch → `main` → `/(root)`。

发布文件：`index.html`、`u4.json`、`u5.json`、`u6.json`、`.nojekyll`。

## 修改与生成

1. 修改 `build.py` 的词表及 `phonics.py` 的字母／音素对应。
2. `python3 build.py` 生成 `words.json` 与 `jobs.json`。
3. 新版音频对应见 `audio-sources.json`。使用本地 `recordings/` 素材运行 `python3 package_recordings.py`。

2026-11-15：全部264个音频引用已替换。整词为剑桥／有道英音；39个音素采用剑桥英式录音；例句采用Google en-GB；音节采用英音同音词及Amazon Polly Amy的IPA合成。close和wind使用明确音标生成。MP3原样打包，不再使用Apple Daniel/Flo。原有 `voice.m` 和 `package.py` 仅保留历史参考。

来源：https://dictionary.cambridge.org/help/phonetics.html 、有道词典、Google Translate en-GB、https://ttsmp3.com/text-to-speech/British%20English/ 。第三方录音不声明为本项目原创或开源授权。

## 验证范围

已校验全部词条和音频引用。浏览器中验证手机布局、分类切换和播放。手机微信内的最终可达性与播放需通过实际手机测试；GitHub Pages 的网络可达性受使用者网络影响。
