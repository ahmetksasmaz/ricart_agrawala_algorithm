import os
import argparse
import random
import tqdm

def execute_command(n, e, p, r, s):
    os.system("python3 testricartagrawala.py -n {n_} -e {e_} -p {p_} -r {r_} -s {s_}".format(n_=n, e_=e, p_=p, r_=r, s_=s))

def experiment(N, force_exp_n = None, force_edge_probability = None):
    print("Experiment")
    for x in tqdm.tqdm(range(N)):
        if not force_exp_n:
            if not force_edge_probability:
                for exp_n in tqdm.tqdm(range(8)):
                    for edge_step in tqdm.tqdm(range(10)):
                        for exp_p in tqdm.tqdm(range(10)):
                            execute_command(2**(exp_n+1), edge_step * 0.1, 2**exp_p, 2**(exp_p+6), 0.000005) # Trigger all in 1000/2^6 ms, use critical section for 5us
            else:
                for exp_n in tqdm.tqdm(range(8)):
                    for exp_p in tqdm.tqdm(range(10)):
                        execute_command(2**(exp_n+1), force_edge_probability, 2**exp_p, 2**(exp_p+6), 0.000005) # Trigger all in 1000/2^6 ms, use critical section for 5us
        else:
            if not force_edge_probability:
                for edge_step in tqdm.tqdm(range(10)):
                    for exp_p in tqdm.tqdm(range(10)):
                        execute_command(2**(force_exp_n+1), edge_step * 0.1, 2**exp_p, 2**(exp_p+6), 0.000005) # Trigger all in 1000/2^6 ms, use critical section for 5us
            else:
                for exp_p in tqdm.tqdm(range(10)):
                    execute_command(2**(force_exp_n+1), force_edge_probability, 2**exp_p, 2**(exp_p+6), 0.000005) # Trigger all in 1000/2^6 ms, use critical section for 5us
def main():
    parser = argparse.ArgumentParser(description='Ricart-Agrawala Algorithm Experimenter')
    parser.add_argument('-n', '--force-number-of-nodes', help='Specifically initialize exp(n+1) nodes', required=False, type=int)
    parser.add_argument('-e', '--force-edge-probability', help='Specifically initialize edge probability', required=False, type=float)
    parser.add_argument('-N','--experiment-count', help='Experiment sample count for Monte Carlo Simulation', required=True, type=int)
    args = vars(parser.parse_args())

    force_exp_n = None
    force_edge_probability = None

    if args["experiment_count"] < 1:
        print("Experiment count must be greater than 0.")
        exit()

    if args["force_number_of_nodes"]:
        force_exp_n = args["force_number_of_nodes"]
        if force_exp_n < 0:
            print("Invalid node exponent.")
            exit()
    
    if args["force_edge_probability"]:
        force_edge_probability = args["force_edge_probability"]
        if force_edge_probability < 0.0 or force_edge_probability > 1.0:
            print("Invalid edge probability.")
            exit()

    experiment(args["experiment_count"], force_exp_n, force_edge_probability)

if __name__ == "__main__":
    main()