import logging
import mypack.stock_tools as stl


def init_logger(save_dir_path, log_file_path):
    """
    初始化日志记录器，设置日志记录级别和日志文件路径。

    :param save_dir_path: 存放目录
    :param log_file_path: 日志文件路径名
    :return: 日志记录器
    """
    # 创建保存数据目录
    stl.ensure_dir_exists(save_dir_path)
    # 配置日志记录器
    logging.basicConfig(
        level=logging.INFO,  # 设置日志级别为 DEBUG
        format='%(asctime)s - %(levelname)s - %(message)s',  # 设置日志格式
        filename=log_file_path,  # 将日志输出到文件
        filemode='w'  # 每次运行时覆盖日志文件
    )
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console_handler)