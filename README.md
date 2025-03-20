# Bilibili-M4StoMP4
一键将手机端bilibili下载的视频文件转换为mp4格式。可以识别旧版blv与新版m4s，可以自动读取视频相关信息形成文件名。

## 使用方法
手机端bilibili下载目录：Android\data\tv.danmaku.bili\download

将整个文件夹或者目标视频所在文件夹直接放到脚本相同文件夹下，并启动脚本（会删除源文件，有需要请备份）。

## 注意事项
需要确保已配置[FFmpeg](https://www.ffmpeg.org/)

下载编译好的版本（有ffmpeg.exe）并配置好环境变量（将bin目录加入 计算机-属性-高级系统设置-环境变量-path）

## 更新计划
- [ ] 内置FFmpeg依赖
- [ ] 打包成多平台工具

## 碎碎念
以前写的，因为功能比较简单，就没想过在github施展copy大法。也算是个小项目，上传一下凑个数。

感觉没必要更新了，别人写的很完整了，还能持续更新[mzky/m4s-converter: 一个跨平台小工具，将bilibili缓存的m4s格式音视频文件合并成mp4](https://github.com/mzky/m4s-converter)
