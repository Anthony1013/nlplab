###
 # @Author: your name
 # @Date: 2021-04-15 10:54:17
 # @LastEditTime: 2021-04-15 11:00:54
 # @LastEditors: Please set LastEditors
 # @Description: In User Settings Edit
 # @FilePath: /BERT-NER-Pytorch/run.sh
### 
CUDA_VISIBLE_DEVICES=0 nohup python run_ner.py --data_dir=data_zz/ \
--bert_model=pretrain_models/bert-base-chinese/ \
--task_name=ner \
--output_dir=output/zz \
--max_seq_length=100 \
--do_train --train_batch_size=32 --num_train_epochs 3 \
--do_eval --warmup_proportion=0.4 > log.log 2>&1 & echo $! > run.pid