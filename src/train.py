import argparse, shutil, os
from NERClassifier import NERClassifier


def main():
    parser = argparse.ArgumentParser()

    # parameters 
    # parser.add_argument("--data_dir",
    #                     default="conll",
    #                     type=str,
    #                     help="the dataset directory.")
    parser.add_argument("--dataset_name",
                        default="Wikigold",
                        type=str,
                        help="the dataset directory.")
    parser.add_argument("--pretrained_model", 
                        default='roberta-base', 
                        type=str,
                        help="pre-trained language model, default to roberta base.")
    parser.add_argument('--temp_dir',
                        type=str,
                        default="temp",
                        help="temporary directory for saved models")
    parser.add_argument("--output_dir",
                        default='output',
                        type=str,
                        help="the output directory where the final model checkpoint will be saved.")
    parser.add_argument("--max_seq_length",
                        default=128,
                        type=int,
                        help="the maximum input sequence length.")
    parser.add_argument("--tag_scheme",
                        default='io',
                        type=str,
                        choices=['iob', 'io'],
                        help="the tagging scheme used.")


    # training settting parameters
    parser.add_argument("--do_train",
                        action='store_true',
                        help="whether to run training.")
    parser.add_argument("--do_eval",
                        action='store_true',
                        help="whether to run eval on eval set or not.")
    parser.add_argument("--eval_on",
                        default="test",
                        choices=['valid', 'test'],
                        help="run eval on valid/test set.")
    parser.add_argument("--loss_type",
                        default="MAE",
                        type=str,
                        help="run eval on valid/test set.")
    parser.add_argument("--train_batch_size",
                        default=32,
                        type=int,
                        help="effective batch size for training.")
    parser.add_argument('--gradient_accumulation_steps',
                        type=int,
                        default=1,
                        help="number of updates steps to accumulate before performing a backward/update pass.")
    parser.add_argument("--eval_batch_size",
                        default=32,
                        type=int,
                        help="batch size for eval.")
    parser.add_argument("--noise_train_update_interval",
                        default=200,
                        type=int,
                        help="number of batches to periodically perform noisy label removal for noise robust training.")
    parser.add_argument("--self_train_update_interval",
                        default=100,
                        type=int,
                        help="number of batches to periodically compute new soft labels for self-training.")
    parser.add_argument("--train_lr",
                        default=2e-5,
                        type=float,
                        help="the peak learning rate for noise robust training.")
    parser.add_argument("--curriculum_train_lr",
                        default=1e-5,
                        type=float,
                        help="the peak learning rate for ensemble model training.")
    parser.add_argument("--train_epochs",
                        default=1,
                        type=int,
                        help="total number of training epochs for noise robust training.")
    parser.add_argument("--curriculum_train_epochs",
                        default=5,
                        type=int,
                        help="total number of training epochs for ensemble model training.")
    parser.add_argument("--curriculum_train_sub_epochs",
                        default=2,
                        type=int,
                        help="total number of training epochs for ensemble model training.")
    parser.add_argument("--num_models",
                        default=5,
                        type=int,
                        help="total number of models to ensemble.")
    parser.add_argument("--warmup_proportion", 
                        default=0.1,
                        type=float, 
                        help="proportion of learning rate warmup.")
    parser.add_argument("--weight_decay",
                        default=0.01,
                        type=float,
                        help="weight decay for model training.")
    parser.add_argument("--drop_other",
                        default=0.1,
                        type=float,
                        help="dropout ratio")
    parser.add_argument("--drop_entity",
                        default=0.1,
                        type=float,
                        help="dropout ratio")
    parser.add_argument('--seed',
                        type=int,
                        default=42,
                        help="random seed for training")
    parser.add_argument("--student1_lr",
                        default=1e-5,
                        type=float,
                        help="the peak learning rate for self-training.")
    parser.add_argument("--self_train_lr",
                        default=1e-5,
                        type=float,
                        help="the peak learning rate for self-training.")
    parser.add_argument("--self_train_epochs",
                        default=10,
                        type=int,
                        help="the peak learning rate for self-training.")
    parser.add_argument("--student2_lr",
                        default=1e-5,
                        type=float,
                        help="the peak learning rate for self-training.")
    parser.add_argument("--entity_threshold",
                        default=0.8,
                        type=float,
                        help="the peak learning rate for self-training.")
    parser.add_argument("--ratio",
                        default=0.1,
                        type=float,
                        help="the peak learning rate for self-training.")
    parser.add_argument("--m",
                        default=10,
                        type=float,
                        help="the peak learning rate for self-training.")

    args = parser.parse_args()

    if args.dataset_name == "Twitter":
        args.priors = [0.007169434612941283, 0.004696433433160904, 0.0018150467374534894, 0.0046056810962882295, 0.003993102822397677, 0.014838007078682276, 0.012296941646247391, 0.001656230147926309, 0.0014520373899627916, 0.0025864416008712222] 
    elif args.dataset_name == "Wikigold":
        args.priors = [0.04167473565978543, 0.03787908129671947, 0.04562531469073163, 0.0345869321042643]
        # args.priors = [0.03, 0.03, 0.03, 0.03]
    elif args.dataset_name == "CoNLL2003_KB":
        args.priors = [0.0314966102568, 0.0376880632424, 0.0354240324761, 0.015502139428]
    elif args.dataset_name == "Webpage":
        # args.priors = [ 0.09814323607427056, 0.026525198938992044, 0.16887709991158267, 0.0000000001]
        args.priors = [0.04167473565978543, 0.03787908129671947, 0.04562531469073163, 0.0345869321042643]
    elif args.dataset_name == "OntoNote" or args.dataset_name == "Onto5":
        # args.priors = [0.0018085539128337492, 0.0009625941805170074, 0.0011001076348765798, 0.017837150951614703, 0.004008769182586909, 0.0021318185254381892, 0.0014975287176330406, 0.02404037567811772, 0.00662944443844473, 0.02832561170088304, 0.02245141131282151, 0.0021548574287863897, 0.00026782725142283226, 0.006633764232822518, 0.0026350745704504467, 0.008747583615019925, 0.003134010821084916, 0.002650193850772703]
        args.priors = [0.0018034225918876403, 0.0007039866503272235, 0.0006952954571133071, 0.014179681728504506, 0.0044629277153460396, 0.0010863991517395424, 0.00092561207728209, 0.015844045228969487, 0.005006127291215811, 0.020446032035738186, 0.017312856882121346, 0.0017034738699276024, 9.560312535307972e-05, 0.004910524165862731, 0.0018121137851015566, 0.005975195334567483, 0.002242327849190415, 0.002155415917051252]
    elif "QTL" in args.dataset_name:
        args.priors = [0.0382405850627, 0.00994870190668]
    else:
        args.priors = [0.0314966102568, 0.0376880632424, 0.0354240324761, 0.015502139428]

    args.temp_dir = f"../data/{args.dataset_name}/{args.temp_dir}"
    args.output_dir = f"../data/{args.dataset_name}/{args.output_dir}"

    # print(args)

    print("========== args ==============\n")
    for k, v in sorted(vars(args).items()):
        print(k, v)
    print("\n==============================\n")

    if args.do_train:
        # classifier = NERClassifier(args)
        for i in range(args.num_models):
            classifier = NERClassifier(args)
            classifier.train(i)
            args.seed = args.seed + 1

        args.drop_other = 0.0
        args.drop_entity = 0.0
        classifier = NERClassifier(args)
        classifier.token_hardness_score(classifier.temp_dir)
        classifier.ensemble_pred(classifier.temp_dir)
        # classifier.ensemble_eval()
        classifier.curriculum_train()


    # print("startssssssssssssss")
    # if args.do_train:
    #     # train K voters 
    #     if os.path.exists(args.temp_dir):
    #         shutil.rmtree(args.temp_dir)
    #     if os.path.exists(args.output_dir):
    #         shutil.rmtree(args.output_dir)

    #     for i in range(args.num_models):
    #         classifier = NERClassifier(args)
    #         classifier.train(i)
    #         args.seed = args.seed + 1
    #         pass

    #     args.drop_other = 0.0
    #     args.drop_entity = 0.0
    #     print("init:::::::::::")
    #     classifier = NERClassifier(args)
    #     print("hardness:::::::::::")
    #     classifier.token_hardness_score(classifier.temp_dir)
    #     classifier.ensemble_pred(classifier.temp_dir)
    #     # classifier.ensemble_eval()
    #     classifier.curriculum_train()
    #     # # # # classifier.aug()
    #     # exit()

        # classifier.self_train()
        # ts = TeacherStudentFramework(args)
        # ts.train(20)

    # if args.do_eval:
    #     classifier = NERClassifier(args)
    #     classifier.predict_data()


if __name__ == "__main__":
    main()