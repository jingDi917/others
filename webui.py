import gradio as gr
import pandas as pd
from typing import Dict, List, Tuple
import random
import os
from c_3d import addData, predict # pyright: ignore[reportMissingImports]


class Processor:
    @classmethod
    def getPredictData(cls):
        epoch_index, final_res, all_res, impossible_res = predict()
        # 返回一个元组，而不是字典
        return (
            epoch_index,
            cls.convertPrediction2GradioFormat(final_res),
            cls.convertPrediction2GradioFormat(all_res),
            cls.convertPrediction2GradioFormat(impossible_res)
        )

    @classmethod    
    def convertPrediction2GradioFormat(cls, prediction_dict):
        """
        将预测结果的字典格式转换为Gradio需要的Dataframe格式
        
        参数:
            prediction_dict: {百十个: 购买倍数} 格式的字典，例如 {"123": 2, "456": 1}
        
        返回:
            list: 包含百位、十位、个位和购买倍数的列表，例如 [["1","2","3",2], ["4","5","6",1]]
        """
        gradio_format = []
        for number, multiple in prediction_dict.items():
            # 确保号码是3位数
            if len(number) != 3:
                continue
                
            # 分解百位、十位、个位
            hundred = number[0]
            ten = number[1]
            unit = number[2]
            
            gradio_format.append([hundred, ten, unit, multiple])
        
        return gradio_format

# 创建界面
def create_ui() -> "gr.Blocks":
    with gr.Blocks(title="彩票数据管理系统") as demo:
        gr.Markdown("# 彩票数据管理系统")
        
        with gr.Tab("获取数据"):
            gr.Markdown("## 获取预测数据")
            with gr.Row():
                get_btn = gr.Button("获取", variant="primary")
            
            # 期号显示
            epoch_display = gr.Textbox(label="当前期号", interactive=False)
            
            with gr.Tabs():
                with gr.Tab("预测号码"):
                    predict_table = gr.Dataframe(
                        headers=["百位", "十位", "个位", "购买倍数"],                        interactive=False
                    )
                
                with gr.Tab("其他可能号码"):
                    other_table = gr.Dataframe(
                        headers=["百位", "十位", "个位", "购买倍数"],
                        interactive=False
                    )
                
                with gr.Tab("不可能号码"):
                    impossible_table = gr.Dataframe(
                        headers=["百位", "十位", "个位", "购买倍数"],
                        interactive=False
                    )
            
            # 修改点击事件处理，使用列表格式的outputs
            get_btn.click(
                fn=Processor.getPredictData,
                outputs=[epoch_display, predict_table, other_table, impossible_table]
            )
      
        
        with gr.Tab("增加期数"):
            gr.Markdown("## 增加新的期数数据")
            with gr.Row():
                with gr.Column():
                    period_input = gr.Textbox(label="期号", placeholder="请输入期号，如2023001")
                    hundred_input = gr.Number(label="百位", precision=0, minimum=0, maximum=9)
                    ten_input = gr.Number(label="十位", precision=0, minimum=0, maximum=9)
                    unit_input = gr.Number(label="个位", precision=0, minimum=0, maximum=9)
                    check_code_input = gr.Textbox(
                        label="校验码", 
                        placeholder="请输入校验码",
                        info="请输入正确的校验码以验证身份"
                    )
                    add_btn = gr.Button("增加", variant="primary")
                
                with gr.Column():
                    result_output = gr.Textbox(
                        label="操作结果",
                        placeholder="操作结果将显示在这里",
                        interactive=False,
                        visible=True
                    )
            
            # 改进提示信息处理
            def addDataWithMessage(period, hundreds, tens, ones, check_code):
                code, message = addData(period, hundreds, tens, ones, check_code)
                
                # 根据返回码显示不同类型的消息
                if code == 0:
                    return gr.update(value=f"✅ 成功: {message}", visible=True)
                elif code == 1:
                    return gr.update(value=f"❌ 错误: {message}", visible=True)
                elif code == 2:
                    return gr.update(value=f"⚠️ 警告: {message}", visible=True)
                else:
                    return gr.update(value=f"❗ 系统错误: {message}", visible=True)
            
            add_btn.click(
                fn=addDataWithMessage,
                inputs=[period_input, hundred_input, ten_input, unit_input, check_code_input],
                outputs=[result_output]
            )
    
    return demo

def isEnvEnabled(env_var: str, default: str = "0") -> bool:
    r"""Check if the environment variable is enabled."""
    return os.getenv(env_var, default).lower() in ["true", "y", "1"]

def fixProxy(ipv6_enabled: bool = False) -> None:
    r"""Fix proxy settings for gradio ui."""
    os.environ["no_proxy"] = "localhost,127.0.0.1,0.0.0.0"
    if ipv6_enabled:
        os.environ.pop("http_proxy", None)
        os.environ.pop("HTTP_PROXY", None)

def main():
    gradio_ipv6 = isEnvEnabled("GRADIO_IPV6")
    gradio_share = isEnvEnabled("GRADIO_SHARE")
    
    # 外网访问关键配置
    server_name = "0.0.0.0"  # 监听所有网络接口
    server_port = int(os.getenv("GRADIO_SERVER_PORT", 7860))  # 默认7860端口
    
    print(f"Visit http://8.130.122.158:{server_port} for Web UI")
    print(f"Local access: http://127.0.0.1:{server_port}")
    
    fixProxy(ipv6_enabled=gradio_ipv6)
    
    # 启动配置
    create_ui().queue().launch(
        server_name=server_name,
        server_port=server_port,
        share=gradio_share,  # 是否启用gradio临时分享链接
        inbrowser=True,
        # 以下为安全增强配置
        auth=None if not isEnvEnabled("GRADIO_AUTH") else (
            os.getenv("GRADIO_AUTH_USER", "admin"),
            os.getenv("GRADIO_AUTH_PASS", "123456")
        ),
        ssl_verify=False  # 如需HTTPS可配置证书路径
    )

if __name__ == '__main__':
    main()