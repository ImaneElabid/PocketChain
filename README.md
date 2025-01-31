# PocketChain: Redefining Blockchain Integration with Resource-Constrained Devices

This repository contains the code to run simulations for the "*PocketChain: Redefining Blockchain Integration with
Resource-Constrained Devices*" paper, submitted in *Future Generation Computer Systems* journal.
The repository includes the implementation of the PocketChain Blockchain on a simulated environment.

### Requirements

| Package      | Version |
|--------------|---------|
| python       | 3.10    |
| cryptography | 42.0.5  |
| numpy        | 1.26.4  |
| matplotlib   | 3.8.4   |

## Evaluation of PocketChain

### Configuration

To evaluate the performance and energy efficiency of the PocketChain protocol (PCC), we considered a P2P network of 500
nodes the following configuration (Unless stated otherwise):

- Total number of nodes: `200`
- Number of announcers: `10`
- Number of processors: `100`
- Number of announcers to subscribe to: `3`
- Minimum number of tips: `100 T`
- Amount of PCs to stake: `100 PCs`

The main protocol parameters are the following:

| Argument          | Description                                                               |
|-------------------|---------------------------------------------------------------------------|
| --mp              | Use message passing (MP) via sockets or shared memory (SM)  (default: MP) |
| --num_nodes       | Number of nodes in the network (default: 500)                             |
| --perc_processors | Percentage of processors nodes (default: 0.2)                             |
| --perc_announcers | Percentage of announcer nodes (default: 0.01)                             |
| --num_byz         | Number of Byzantine nodes in the network (default: 0)                     |
| --Qsub            | Number of announcers to subscribe to (default:3)                          |
| --min_tips        | Minimum number of tips (default: 100)                                     |
| --staked          | Amount of PCs to stake  (default: 100)                                    |
| --stake_expiry    | Stake expiry (default: 10)                                                |
| --min_storage     | Minimum amount of reserved storage  (default: 1GB)                        |
| --max_block_size  | Maximum block size (default: 1MB)                                         |

### Execution of  PocketChain (PC)

`python main.py --num_nodes=500 --perc_announcers=0.05 --perc_processors=0.5 --Qsub=3`

## Energy Analysis

To perform energy analysis of PocketChain simulated on a Linux machine (Ubuntu 20.04), we developed two methods of
energy readings:

- Evaluating the whole program by running the `run.sh` script.
- Evaluating a given method of the protocol using python decorators.

**NB:** you need to disable virtualization from the bios as we shield the program to one physical core.

### Requirement

We have used the following packages: `powerstat`, `cset-shield`, `cpupower`.

### Energy consumption of the whole program

To measure the energy consumption of the whole program run the following:

`./run.sh -c 0 -p avg -r 1 -d 2 -e "python main.py" -a "--num_nodes=200 --Qsub=3"`

Run `./run.sh -h` to get a list of the available options and what are used for.

### Energy consumption of a method

To measure the energy consumption of a given method, use the `@measure_energy` decorator.

For example to evaluation the energy consumption of the local learning step, add the following:

````python
@measure_energy
def init_PC(self, device='cpu', inference=True):
    log('event', 'Starting local training ...')
    ...
````

End.