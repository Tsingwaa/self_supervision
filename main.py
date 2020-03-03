"""
@Author: Tsingwaa Tsang
@Date: 2020-02-16 22:25:05
@LastEditors: Tsingwaa Tsang
@LastEditTime: 2020-02-16 22:25:05
@Description: Null
"""

import os
from copy import deepcopy

from torch.nn import CrossEntropyLoss
from torch.optim import SGD, lr_scheduler
from torchvision.models import resnet18
from tqdm import tqdm

from data_loader.my_dataloader import get_dataloader
from model.metric import *
from model.model import Net8FC

os.environ["CUDA_kVISIBLE_DEVICES"] = "0"


def train():
    # 定义变量
    # all_classes = 32
    aug_classes = 5
    num_classes = 8

    epochs = 3

    # get dataloader
    mean_std_path = './data/mean_std.json'
    data_root = './data/'
    loader = get_dataloader(mean_std_path, data_root)  # loader dict:'train','valid', 'test'

    copy_resnet18 = deepcopy(resnet18(pretrained=True))
    # model = Net1FC(copy_resnet18, all_classes).cuda()
    model = Net8FC(copy_resnet18, num_classes, aug_classes).cuda()

    # 初始化损失函数
    # criterion0 = CrossEntropyLoss()
    # criterion1 = CrossEntropyLoss()
    # criterion2 = CrossEntropyLoss()
    # criterion3 = CrossEntropyLoss()
    # criterion4 = CrossEntropyLoss()
    # criterion5 = CrossEntropyLoss()
    # criterion6 = CrossEntropyLoss()
    # criterion7 = CrossEntropyLoss()
    #
    # criterion_list = [criterion0, criterion1, criterion2, criterion3, criterion4, criterion5, criterion6, criterion7]
    criterion_list = [CrossEntropyLoss() for i in range(8)]



    # 设置优化器
    opt = SGD(model.parameters(), lr=1e-2, momentum=0.9)
    scheduler = lr_scheduler.StepLR(opt, step_size=40, gamma=0.1)

    model.train()

    # 作为其余7个多余的损坏函数的拟合目标
    # pesdo_target = torch.tensor([0.01 for i in range(4)]).cuda()

    for epoch in range(1, epochs + 1):
        pred_list = []
        target_list = []
        total_loss = 0.0

        for batch_idx, (data, label, target) in tqdm(enumerate(loader['train'])):
            # 收集rot_label序列
            target_list.extend(target)

            data, target = data.cuda(), target.cuda()
            target_batch_list = [target for i in range(8)]

            for i in range(8):
                for j, target_elem in enumerate(target):
                    if target_elem != i:
                        target_batch_list[i][j] = 4  # 其他分类器输出target修改输出，未知类rot_label=4

            # print(target_batch_dict[2])

            opt.zero_grad()
            output = model(data, label, "train")  # 得到含有8个分类器输出的列表
            # 收集预测标签序列，与目的标签一起进行评估
            # pred_list.extend(torch.argmax(output, dim=0).tolist())

            # 对8个分类器的输出，求损失函数
            # print
            batch_loss = criterion_list[0](output[0], target_batch_list[0])
            for idx in range(1, 8):
                batch_loss += criterion_list[idx](output[idx], target_batch_list[idx])

            total_loss += batch_loss.item()

            # my_metric2()

            batch_loss.backward()

            opt.step()

        print()
        # 每几个epoch结束，进行测试调节优化，
        if epoch % 5 == 0:
            valid(model, valid())

        scheduler.step(epoch)


def valid(model, val_loader):
    for index, (data, label, rot_label) in enumerate(val_loader):


if __name__ == '__main__':
    train()
