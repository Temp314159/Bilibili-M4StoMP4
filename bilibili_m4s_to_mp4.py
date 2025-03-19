# -*- coding:utf-8 -*-
# based on python 3.9
# 2023/8/21 20:23
# by L.P.

# Version 231206

# 确保已配置ffmpeg
# 官网https://www.ffmpeg.org/
# 下载编译好的版本（有ffmpeg.exe）
# 配置好环境变量，将bin目录加入path（计算机-属性-高级系统设置-环境变量-path）

import os
import sys
import time
import shutil
import json
import send2trash

def illegal_string_replace(input_str):
    '''
    替换非法文件名字符
    '''
    illegal_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for char in illegal_chars:
        input_str = input_str.replace(char, chr(ord(char)+65248))  # unicode编码中全角半角相差65248
    return input_str

def exist_path_replace(input_path):
    '''
    重命名已存在文件路径
    '''
    while os.path.exists(input_path):
        pref, suf = os.path.splitext(input_path)
        input_path = pref + '_new' + suf
    return input_path

work_folder = os.path.dirname(os.path.abspath(sys.argv[0]))

get_out = True  # 文件放到最外层
copy_out = True  # 以复制方式移动文件（否则剪切）
delete_old = True  # 删除原文件
out_folder = work_folder

for root, dirs, files in os.walk(work_folder):
    # 执行类型（m4s还是blv）
    run_type = None

    # 输出文件名基本参数（放后面if下可以提高效率，但如果前面要赋值title之类容易出事，懒得处理了）
    default_bvid = 'unknown'
    bvid = default_bvid
    title = 'out'
    subtitle = 'out'
    page = '0'

    # 类型判定
    # 若文件夹里有video.m4s和audio.m4s
    if 'video.m4s' in files and 'audio.m4s' in files:
        run_type = 'm4s'
    # 若文件夹里只有video.m4s
    elif 'video.m4s' in files:
        run_type = 'm4s_video'
    else:
        m4s_list = []
        for file in files:
            file_ext = os.path.splitext(file)[1]
            if file_ext == '.m4s':
                m4s_list.append(file)
        # 若文件夹里恰有1个m4s，认为它是video（方便浏览器插件下载的文件处理）
        if len(m4s_list) == 1:
            run_type = 'm4s_video'
            video_m4s = m4s_list[0]
            # 输出文件名title默认采用原文件名
            title = os.path.splitext(video_m4s)[0]
            # 修改文件名以免出现非法情况
            old_video_m4s_path = os.path.join(root, video_m4s)
            new_video_m4s_path = os.path.join(root, 'video.m4s')
            os.rename(old_video_m4s_path, new_video_m4s_path)
        # 若文件夹里恰有2个m4s，认为它们是video和audio（方便浏览器插件下载的文件处理）
        elif len(m4s_list) == 2:
                run_type = 'm4s'
                # 通过文件大小判定video和audio
                file_size = [os.path.getsize(os.path.join(root, m4s_file)) for m4s_file in m4s_list]
                if file_size[0] >= file_size[1]:
                    video_m4s, audio_m4s = m4s_list
                else:
                    audio_m4s, video_m4s = m4s_list
                # 输出文件名title默认采用原文件名
                title = os.path.splitext(video_m4s)[0]
                # 修改文件名以免出现非法情况
                old_video_m4s_path = os.path.join(root, video_m4s)
                new_video_m4s_path = os.path.join(root, 'video.m4s')
                os.rename(old_video_m4s_path, new_video_m4s_path)
                old_audio_m4s_path = os.path.join(root, audio_m4s)
                new_audio_m4s_path = os.path.join(root, 'audio.m4s')
                os.rename(old_audio_m4s_path, new_audio_m4s_path)
    # 判定blv（若已判定m4s则跳过）
    if run_type is None:
        # 若文件夹里有0.blv（旧版）
        if'0.blv' in files:
            run_type = 'blv'
        else:
            blv_list = []
            for file in files:
                file_ext = os.path.splitext(file)[1]
                if file_ext == '.blv':
                    blv_list.append(file)
                    # 若文件夹里恰有1个blv，认为它是0.blv
                if len(blv_list) == 1:
                    run_type = 'blv'
                    video_blv = blv_list[0]
                    # 输出文件名title默认采用原文件名
                    title = os.path.splitext(video_blv)[0]
                    # 修改文件名以免出现非法情况
                    old_video_blv_path = os.path.join(root, video_blv)
                    new_video_blv_path = os.path.join(root, '0.blv')
                    os.rename(old_video_blv_path, new_video_blv_path)

    # 开始执行
    if run_type:
        updir, tgdir = os.path.split(root)
        # 读取entry.json，获得输出文件名
        if 'entry.json' in os.listdir(updir):
            with open(os.path.join(updir, 'entry.json'), 'r', encoding='UTF-8') as f:
                try:
                    etjs = json.load(f)
                except:
                    etjs = dict()
            if 'bvid' in etjs:
                if etjs['bvid']:
                    bvid = etjs['bvid']
            if bvid == default_bvid and 'avid' in etjs:
                bvid = 'av' + str(etjs['avid'])
            if 'title' in etjs:
                title = etjs['title']
            if 'page_data' in etjs:
                if 'page' in etjs['page_data']:
                    page = etjs['page_data']['page']
                if 'part' in etjs['page_data']:
                    subtitle = etjs['page_data']['part']
        out_name = f'{title}_{subtitle}_{bvid}_p{page}'

        # 双m4s模式
        if run_type == 'm4s':
            video_path = os.path.join(root, 'video.m4s')
            audio_path = os.path.join(root, 'audio.m4s')
            out_file_name = illegal_string_replace(f'{out_name}.mp4')
            out_path = exist_path_replace(os.path.join(root, out_file_name))
            default_out_path = exist_path_replace(os.path.join(root, 'out.mp4'))  # 先输出out.mp4，避免ffmpeg无法识别输入，出错
            # 命令，调用ffmpeg合并m4s
            command = f'ffmpeg -loglevel quiet -i "{video_path}" -i "{audio_path}" -c copy -y "{default_out_path}"'
            os.system(command)
            # 时延，以防执行失败
            time_delay = 0.5
            time_out = 2
            time_count = 0
            time_out_flag = 0
            while not os.path.exists(default_out_path):
                time.sleep(time_delay)
                time_count += time_delay
                if time_count > time_out:
                    time_out_flag = 1
                    print(f'转换超时：\t{out_file_name}')
                    print(f'目录：\t{root}')
                    print(f'命令：\t{command}')
                    print('可能文件转换成功但超时，建议检查目录')
                    print('如无文件，可将convert.bat放入该目录运行')
                    print('------------------------------------------')
                    break
            if time_out_flag == 1:
                continue
            time.sleep(time_delay)
            # 将out.mp4改为最终名
            os.rename(default_out_path, out_path)
        # 单video m4s模式
        elif run_type == 'm4s_video':
            # 直接复制为mp4
            video_path = os.path.join(root, 'video.m4s')
            audio_path = None
            out_file_name = illegal_string_replace(f'{out_name}.mp4')
            out_path = exist_path_replace(os.path.join(root, out_file_name))
            shutil.copy(video_path, out_path)
        # blv模式
        elif run_type == 'blv':
            # 直接复制为flv
            video_path = os.path.join(root, '0.blv')
            audio_path = None
            out_file_name = illegal_string_replace(f'{out_name}.flv')
            out_path = exist_path_replace(os.path.join(root, out_file_name))
            shutil.copy(video_path, out_path)
        # 报错
        else:
            raise TypeError('Unknown run type')

        print(f'成功转换：\t{title} P{page}')

        if get_out:
            target_path = os.path.join(out_folder, out_file_name)
            if out_path != target_path:
                target_path = exist_path_replace(target_path)
                if copy_out:
                    shutil.copy(out_path, target_path)
                    print(f'文件目录：\t{out_path}')
                    print(f'复制副本：\t{target_path}')
                else:
                    shutil.move(out_path, target_path)
                    print(f'文件目录：\t{target_path}')
        else:
            print(f'文件目录：\t{out_path}')

        if delete_old:
            tgdir = os.path.join(updir, tgdir)
            if tgdir != work_folder:
                send2trash.send2trash(tgdir)
                print(f'已删除至回收站：\t{tgdir}')
                if updir != work_folder:
                    send2trash.send2trash(updir)
                    print(f'已删除至回收站：\t{updir}')
                    upupdir = os.path.split(updir)[0]
                    if upupdir != work_folder:
                        if len(os.listdir(upupdir)) == 0:
                            send2trash.send2trash(upupdir)
                            print(f'已删除至回收站：\t{upupdir}')
            else:
                send2trash.send2trash(video_path)
                print(f'已删除至回收站：\t{video_path}')
                if audio_path:
                    send2trash.send2trash(audio_path)
                    print(f'已删除至回收站：\t{audio_path}')

        print('------------------------------------------')

print('完成')

time.sleep(20)
