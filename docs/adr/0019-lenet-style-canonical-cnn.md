# 标准网络采用 LeNet-style CNN

标准网络使用两段“卷积、ReLU、池化”特征提取块，随后 Flatten 并通过带 ReLU 的全连接层输出十个分类 logits；首个版本不加入 BatchNorm、Dropout、Residual block 或 Attention。该结构覆盖初学者需要理解的核心视觉网络概念，层次足以支持丰富的 feature map 动画，同时保持 CPU 训练、逐层映射和真实轨迹采集的可控性，具体维度在实现规格中固定。
