import gradio as gr
import pandas as pd
from typing import Dict, List, Tuple
import random
import os
from c_3d import addData, predict # pyright: ignore[reportMissingImports]


# 创建界面
def create_ui() -> "gr.Blocks":
    with gr.Blocks(title="彩票数据管理系统") as demo:
        gr.Markdown("# 彩票数据管理系统")
        
        with gr.Tab("获取数据"):
            gr.Markdown("## 获取预测数据")
            with gr.Row():
                get_btn = gr.Button("获取", variant="primary")
            
            with gr.Tabs():
                with gr.Tab("预测号码"):
                    predict_table = gr.Dataframe(
                        headers=["百位", "十位", "个位", "购买倍数"],
                        interactive=False
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
            
            get_btn.click(
                fn=predict,
                outputs=[predict_table, other_table, impossible_table]
            )
        
        with gr.Tab("增加期数"):
            gr.Markdown("## 增加新的期数数据")
            with gr.Row():
                with gr.Column():
                    period_input = gr.Textbox(label="期号", placeholder="请输入期号")
                    hundred_input = gr.Number(label="百位", precision=0, minimum=0, maximum=9)
                    ten_input = gr.Number(label="十位", precision=0, minimum=0, maximum=9)
                    unit_input = gr.Number(label="个位", precision=0, minimum=0, maximum=9)
                    check_code_input = gr.Textbox(label="校验码", placeholder="请输入4位校验码")
                    add_btn = gr.Button("增加", variant="primary")
                
                with gr.Column():
                    result_output = gr.Textbox(label="结果", visible=False)
            
            add_btn.click(
                fn=addData,
                inputs=[period_input, hundred_input, ten_input, unit_input, check_code_input],
                outputs=[result_output]
            )
    return demo

def is_env_enabled(env_var: str, default: str = "0") -> bool:
    r"""Check if the environment variable is enabled."""
    return os.getenv(env_var, default).lower() in ["true", "y", "1"]

def fix_proxy(ipv6_enabled: bool = False) -> None:
    r"""Fix proxy settings for gradio ui."""
    os.environ["no_proxy"] = "localhost,127.0.0.1,0.0.0.0"
    if ipv6_enabled:
        os.environ.pop("http_proxy", None)
        os.environ.pop("HTTP_PROXY", None)


def main():
    gradio_ipv6 = is_env_enabled("GRADIO_IPV6")
    gradio_share = is_env_enabled("GRADIO_SHARE")
    server_name = os.getenv("GRADIO_SERVER_NAME", "[::]" if gradio_ipv6 else "0.0.0.0")
    print("Visit http://ip:port for Web UI, e.g., http://127.0.0.1:7860")
    fix_proxy(ipv6_enabled=gradio_ipv6)
    create_ui().queue().launch(share=gradio_share, server_name=server_name, inbrowser=True)

if __name__ == '__main__':
    main()