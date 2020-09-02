# code checking
pyflakes .

# activate the fedml environment
source "$HOME/miniconda/etc/profile.d/conda.sh"
conda activate fedml

# 1. distributed base framework
cd ./fedml_experiments/distributed/base
sh run_base_distributed_pytorch.sh &

sleep 15
killall mpirun
cd ./../../../

# 2. decentralized base framework
cd ./fedml_experiments/distributed/decentralized_demo
sh run_decentralized_demo_distributed_pytorch.sh &

sleep 15
killall mpirun
cd ./../../../