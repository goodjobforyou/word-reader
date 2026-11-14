# 人教版英语五年级上册U4-U6单词库

手机优先的英语点读页面，使用 GitHub Pages 静态托管。

- U4：黑体 7 项、白体 13 项。
- U5：黑体 8 项、白体 12 项。
- U6：黑体 7 项、白体 16 项。
- 整词、完整音标、音节、每个音素、例句均可点击朗读。
- 英式男女声整词与例句；英式男声音节和音素。
- 连读模式：只读单词／单词＋拆读＋例句。每项读一次，到本组末尾停止。
- 所有音频随页面部署，无第三方字体、脚本、语音接口或分析跟踪。

词表与黑白体分类来自提供的课本词表图片；星号保留。例句及中文翻译为教学编写。连读中的拆读依次包含音节、音素。`o…e` 等表示不相邻的字母组合；不发音的字母显示“ 不发音 ”。`Mrs` 为缩写，不按字母名称拆读。

## 发布

GitHub Settings → Pages → Deploy from a branch → `main` → `/(root)`。

发布文件：`index.html`、`u4.json`、`u5.json`、`u6.json`、`.nojekyll`。

## 修改与生成

1. 修改 `build.py` 的词表及 `phonics.py` 的字母／音素对应。
2. `python3 build.py` 生成 `words.json` 与 `jobs.json`。
3. 在已有 Daniel 和 Flo 英式系统语音的 macOS 上，用 `clang -fobjc-arc -framework Foundation -framework AVFoundation voice.m -o /tmp/word-reader-audio/voice` 编译本地音频生成器。
4. 建立 `/tmp/word-reader-audio` 目录，运行 `/tmp/word-reader-audio/voice jobs.json /tmp/word-reader-audio`。
5. 修改 `index.template.html` 和 `app.js`，运行 `python3 package.py` 生成发布文件。编码工具为系统自带 `afconvert`。

音频使用 Apple 系统语音合成。合成器兼容处理仅作用于声音输入，页面保留课本英式音标。请勿将 IPA 参数交给不支持 IPA 的声音；生成器使用 Daniel 处理拆读，并对平台不支持的 /ɡ/ 与 /ɜː/ 作适配。打包阶段会验证音频非空、统一音量，并加入短促音素所需的起止静音。

## 验证范围

已校验全部词条和音频引用。浏览器中验证手机布局、分类切换和播放。手机微信内的最终可达性与播放需通过实际手机测试；GitHub Pages 的网络可达性受使用者网络影响。
