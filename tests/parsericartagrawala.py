import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt

def plot_message_complexity(df, save_plots):
    plot = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter(df["node"], df["edge"], df["message_per_privilege"])
    ax.set_xlabel("Node Count")
    ax.set_ylabel("Edge Probability")
    ax.set_zlabel("Message Per Privilege Request")
    plt.show()
    if save_plots == True:
        plt.savefig("message_complexity.png")
def plot_forwarded_message_complexity(df, save_plots):
    plot = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter(df["node"], df["edge"], df["forwarded_message_per_privilege"])
    ax.set_xlabel("Node Count")
    ax.set_ylabel("Edge Probability")
    ax.set_zlabel("Forwarded Message Per Privilege Request")
    plt.show()
    if save_plots == True:
        plt.savefig("forwarded_message_complexity.png")


def main():
    parser = argparse.ArgumentParser(description='Raymond\'s Algorithm Benchmark Parser')
    parser.add_argument('-f','--file', help='Benchmark file', default="benchmark_results.csv", required=False, type=str)
    parser.add_argument('-a','--all', help='Plot all benchmark results', action="store_true")
    parser.add_argument('-m','--message-complexity', help='Plot total message over privilege request count w.r.t. node count and edge probability', action="store_true")
    parser.add_argument('-r','--forwarded-message-complexity', help='Plot total forwarded message over privilege request count w.r.t. node count and edge probability', action="store_true")
    parser.add_argument('-s','--save', help='Save plots', action="store_true")
    args = vars(parser.parse_args())

    plot_or_not_message_complexity = False
    plot_or_not_forwarded_message_complexity = False
    save_plots = args["save"]
    if args["all"] == True:
        plot_or_not_message_complexity = True
        plot_or_not_forwarded_message_complexity = True
    else:
        plot_or_not_message_complexity = args["message_complexity"]
        plot_or_not_forwarded_message_complexity = args["forwarded_message_complexity"]
    if plot_or_not_message_complexity == False and plot_or_not_forwarded_message_complexity == False:
        print("Nothing to plot.")
        exit()

    df = pd.read_csv(args["file"], dtype=float, names=[
        "node",
        "edge",
        "privilege",
        "total_want_privilege",
        "total_duplicate_want_privilege",
        "total_used_critical_section",
        "total_released_critical_section",
        "total_request_message_received",
        "total_reply_message_received",
        "total_request_message_sent",
        "total_reply_message_sent",
        "total_forwarded_message"
    ])


    df["total_message"] = df["total_request_message_sent"] + df["total_reply_message_sent"]
    df["message_per_privilege"] = df["total_message"] / df["total_want_privilege"]
    df["forwarded_message_per_privilege"] = df["total_forwarded_message"] / df["total_want_privilege"]

    df = df.groupby(['node', 'edge', 'total_want_privilege']).mean().reset_index()

    if plot_or_not_message_complexity == True:
        plot_message_complexity(df, save_plots)
    if plot_or_not_forwarded_message_complexity == True:
        plot_forwarded_message_complexity(df, save_plots)

if __name__ == "__main__":
    main()