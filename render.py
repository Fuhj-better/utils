from pathlib import Path
from typing import Dict, Optional, Any
from jinja2 import Environment, FileSystemLoader, TemplateError
from loguru import logger


def render_template(
    template_path: str, data: Dict[str, Any], output_path: Optional[str] = None
) -> Optional[str]:
    """
    通用模板渲染方法。

    参数:
        template_path (str): 模板文件的相对或绝对路径。
        data (dict): 传递给模板的数据字典。
        output_path (str, optional): 渲染结果的输出文件路径。如果未指定，则返回渲染后的字符串。

    返回:
        str: 如果 output_path 为 None，则返回渲染后的字符串。
        None: 如果 output_path 不为 None，则将渲染结果写入文件并返回 None。

    异常:
        FileNotFoundError: 当模板文件不存在时抛出。
        TemplateError: 当模板渲染失败时抛出。
        IOError: 当写入文件失败时抛出。
    """
    try:
        # 使用 pathlib 处理路径
        tpl_path = Path(template_path).resolve()
        if not tpl_path.exists():
            raise FileNotFoundError(f"Template file not found: {tpl_path}")

        template_dir = str(tpl_path.parent)
        template_file = tpl_path.name

        # 创建 Jinja2 环境
        env = Environment(loader=FileSystemLoader(template_dir))

        # 加载并渲染模板
        template = env.get_template(template_file)
        rendered_content = template.render(data)

        # 写入文件或返回字符串
        if output_path:
            out_path = Path(output_path).resolve()
            # 确保输出目录存在
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(rendered_content)
            logger.info(f"Template successfully rendered and saved to: {out_path}")
            return None
        else:
            return rendered_content

    except FileNotFoundError as e:
        logger.error(f"Template file not found: {e}")
        raise
    except TemplateError as e:
        logger.error(f"Template rendering error: {e}")
        raise
    except IOError as e:
        logger.error(f"File writing error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unknown error: {e}")
        raise
