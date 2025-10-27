# A train sample code
from utils.trainer import CustomTrainer
# from utils.trainer import DetTrainer


def main():
    model = CustomTrainer(cfg='')
    model.train()

    # save_dir = ''
    # train a custom signal detect model
    # model = DetTrainer(model_name='yolo')
    # model.train(save_dir=save_dir)


if __name__ == '__main__':
    main()