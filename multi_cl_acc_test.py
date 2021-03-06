import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
from torch.autograd import Variable
import torch.nn.functional as F 
from models import Encoder, ClassClassifier 
from dataset import get_dataloader 

import os

os.environ["CUDA_VISIBLE_DEVICES"] = "5"

num_classes = 31
# Parameters
batch_size = 15
data_dir = '/home/lucliu/dataset/domain_adaptation/office31'
src_dir = 'amazon'
#tgt_dir = 'webcam'
tgt_dir = 'dslr'
test_dir = 'test'
cuda = torch.cuda.is_available()
test_loader = get_dataloader(data_dir, tgt_dir, batch_size=15, train=False)

# load the pretrained and fine-tuned alex model
encoder = Encoder()
classifier = ClassClassifier(num_classes=31)

encoder.load_state_dict(torch.load('./checkpoints/a2w/src_encoder_final.pth'))
classifier.load_state_dict(torch.load('./checkpoints/a2w/src_classifier_final.pth'))



criterion = nn.CrossEntropyLoss()

if cuda:
    encoder = encoder.cuda()
    classifier = classifier.cuda() 
    criterion = criterion.cuda() 

encoder.eval()
classifier.eval()
# begin train
for epoch in range(1, 51):
    correct = torch.zeros(num_classes)
    total = torch.zeros(num_classes)
    for batch_idx, (test_data, label) in enumerate(test_loader):
        if cuda:
            test_data, label = test_data.cuda(), label.cuda()
        test_data, label = Variable(test_data), Variable(label)
        test_feature = encoder(test_data)
        output = classifier(test_feature)
        output = F.softmax(output, dim=1)
        loss = criterion(output, label)
        pred = output.data.max(1, keepdim=True)[1]

        one_hot_pred = torch.zeros(pred.size(0), num_classes).scatter_(1, pred.cpu(), 1)
        one_hot_label = torch.zeros(label.data.size(0), num_classes).scatter_(1, label.data.view_as(pred).cpu(), 1)
        
        
        # correct += pred.eq(label.data.view_as(pred)).cpu().sum()
        # acc for each category
        correct += sum(one_hot_pred * one_hot_label)
        total += sum(one_hot_label)
    #print(correct)
    #print(total)
    acc = sum(correct / total) / num_classes
    print("epoch: %d, loss: %f, acc: %f"%(epoch, loss.data[0], acc))