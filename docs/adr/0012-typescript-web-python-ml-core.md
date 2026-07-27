# 采用 TypeScript Web 与 Python PyTorch 本地核心

浏览器侧使用 TypeScript 承担动画、网络结构展示、代码对照和手写交互，本地侧使用 Python 与 PyTorch 统一承担训练、`.pth` 加载、推理和内部数据采集，两侧通过稳定的本地 API 通信。我们不在浏览器中重新实现模型，也不让前端直接执行学习者的 Python 代码，从而让视觉体验与真实机器学习工作流各自使用合适的技术边界；具体 Web 与 API 框架另行决定。
