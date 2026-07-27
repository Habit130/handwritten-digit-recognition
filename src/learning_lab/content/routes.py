from learning_lab.config import LabPaths


def build_routes(paths: LabPaths) -> list[dict[str, object]]:
    return [
        {
            "id": "direct",
            "level": "01",
            "name": "直接运行",
            "term": "Run a pretrained model",
            "tagline": "先跑通真实闭环，再理解它为什么有效。",
            "responsibilities": [
                "创建并激活项目 Python 环境",
                "确认项目提供的预训练模型位于固定位置",
                "加载模型，在真实实验中完成一次手写识别",
            ],
            "model_path": str(
                paths.route_models["direct"].relative_to(paths.repo_root)
            ),
            "commands": [
                "python -m learning_lab",
            ],
            "code_files": [
                str(path.relative_to(paths.repo_root))
                for path in paths.route_code["direct"]
            ],
        },
        {
            "id": "practical",
            "level": "02",
            "name": "跟随训练",
            "term": "Guided training",
            "tagline": "运行完整训练代码，看见数据、loss 与模型文件的关系。",
            "responsibilities": [
                "运行完整训练程序下载 MNIST",
                "观察 batch、loss、backward 和 optimizer step",
                "保存自己的 model.pth，再回到真实实验加载它",
            ],
            "model_path": str(
                paths.route_models["practical"].relative_to(paths.repo_root)
            ),
            "commands": [
                "python workspace/practical/train.py",
                "python -m learning_lab",
            ],
            "code_files": [
                str(path.relative_to(paths.repo_root))
                for path in paths.route_code["practical"]
            ],
        },
        {
            "id": "challenge",
            "level": "03",
            "name": "核心挑战",
            "term": "Core code challenge",
            "tagline": "在受控骨架里亲手完成模型、训练循环与保存。",
            "responsibilities": [
                "完成 model.py 中的标准网络结构",
                "完成 train.py 中的训练循环和 state_dict 保存",
                "下载 MNIST、训练并在真实实验中验证产物",
            ],
            "model_path": str(
                paths.route_models["challenge"].relative_to(paths.repo_root)
            ),
            "commands": [
                "python workspace/challenge/train.py",
                "python -m learning_lab",
            ],
            "code_files": [
                str(path.relative_to(paths.repo_root))
                for path in paths.route_code["challenge"]
            ],
        },
    ]
