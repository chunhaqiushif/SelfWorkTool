import time
import os
import sys
import zipfile
import pandas as pd
import util
from PyQt5.QtCore import QThread, pyqtSignal


root_path = os.path.abspath('.')
config_csv_path = root_path + "\\" + "config" + "\\" + "compress_conf.csv"
zip_path = root_path + "\\" + "zip"
log_path = root_path + "\\" + "log"


class ResourceCompressToZip(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    config_dict = {}
    config_csv = util.csv_load(config_csv_path)

    def __init__(self, parent=None):
        super().__init__()
        self.analyse_config()
        
    
    def run(self):
        self.config_load()
        self.analyse_config()
        self.compress()

        # 发送完成信号
        self.finished_signal.emit()

    # config.csv 读取
    def config_load(self):
        self.config_csv= util.csv_load(config_csv_path)
            

    # config.csv 保存
    def config_save(self):
        util.csv_save(self.config_csv, config_csv_path)


    # config.csv 特定格修改
    def config_edit(self, index, col, value, save_path, isSaveNow):
        util.csv_edit(self.config_csv, index, col - 1, value, save_path, True)
        self.config_dict[index]["isCompress"] = (value == 1)


    # 配置文件分析
    def analyse_config(self):
        for row in self.config_csv.itertuples():
            index = row[0]
            name = row[1]
            isCompress = row[2]
            res_path = row[3]
            if not pd.isna(row[4]):
                tgt_path = zip_path + "\\" + row[4]
            else:
                tgt_path = zip_path
            tgt_f_suffix_list = util.text_split(row[5],"|")
            exc_file_list = util.text_split(row[6],"|")
            exc_folder_list = util.text_split(row[7],"|")
            last_output_time = ""
            if pd.isna(row[8]):
                last_output_time = str("-")
            else:
                last_output_time = row[8]


            self.config_dict[index] = {
                "index":index,
                "name":name,
                "isCompress":isCompress == 1, 
                "res_path": res_path, 
                "tgt_path": tgt_path,
                "tgt_f_suffix_list":tgt_f_suffix_list,
                "exc_file_list":exc_file_list,
                "exc_folder_list":exc_folder_list,
                "last_output_time":last_output_time
            }
            
            
    # 执行压缩
    def compress(self):
        compress_time = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time()))
        for index in self.config_dict:
            if self.config_dict[index]["isCompress"] != True:
                continue
            p_res = self.config_dict[index]["res_path"]
            p_tgt = self.config_dict[index]["tgt_path"] + "\\" + compress_time
            l_tgt_sufx = self.config_dict[index]["tgt_f_suffix_list"]
            l_exc_file = self.config_dict[index]["exc_file_list"]
            l_exc_folder = self.config_dict[index]["exc_folder_list"]
            if self.zip_files_in_dir(p_res, p_tgt, l_tgt_sufx, l_exc_file, l_exc_folder):
                self.add_log_text(compress_time, self.config_dict[index]["name"], self.config_dict[index]["res_path"], self.config_dict[index]["tgt_path"])
                self.config_edit(self.config_dict[index]["index"], 8, compress_time, config_csv_path, True)
            else:
                self.log_signal.emit(util.get_time_token() + "压缩操作中断，请检查配置")
                self.log_signal.emit("==============================================================")
                self.finished.emit()
                return
        self.log_signal.emit(util.get_time_token() + "全部压缩完成")
        self.log_signal.emit("==============================================================")
        self.finished.emit()


    # 生成当次操作log条目
    def add_log_text(self, compress_time, path_name, from_path, to_path):
        log_file_path = log_path + "\\" + compress_time + ".txt"
        log_file = open(log_file_path, 'a+')
        time_token = time.strftime('[%H:%M:%S]', time.localtime(time.time()))
        msg = time_token + "" + path_name + "从 " + from_path + " 打包至 " + to_path + "\n"
        log_file.writelines(msg)
        log_file.close()


    # 判断排除情况对指定目录下文件进行压缩
    def zip_files_in_dir(self, dir_path, tgt_path, target_file_suffix = [], exclude_file_name = [], exclude_folder_name = []):
        try:
            dir_name = os.path.basename(dir_path)
            zip_file = os.path.join(tgt_path, dir_name)
            zip_file = zip_file + '.zip'
            zip_file_name = os.path.basename(zip_file)
            
            if not os.path.exists(tgt_path):
                os.makedirs(tgt_path)
            
            if os.path.exists(dir_path):
                zip = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
                
                for root, dirs, files in os.walk(dir_path):
                    fpath = root.replace(dir_path, '')
                    fpath = fpath.replace("\\", "")
                    if fpath in exclude_folder_name:
                        continue
                    for filename in files:
                        file_only_name = filename.split(".")[0]
                        file_suffix = filename.split(".")[1]
                        if target_file_suffix != [] and not file_suffix in target_file_suffix:
                            continue
                        if file_only_name in exclude_file_name:
                            continue
                        if filename == zip_file_name:
                            continue
                        zip.write(os.path.join(root, filename), os.path.join(fpath, filename))
                zip.close()
                self.log_signal.emit(util.get_time_token() + "压缩完成：" + dir_path)
                return True
            else:
                self.log_signal.emit(util.get_time_token() + "资源目录不存在，无法压缩: " + dir_path)
                return False
        except Exception as e:
            self.log_signal.emit(f"未处理的异常：{e}")
            return False