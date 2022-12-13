"""Worm tracker script"""
import sys
import argparse
import warnings

warnings.filterwarnings("ignore")

import yaml

import numpy as np
import pandas as pd
import cv2
import trackpy as tp

from src.capture import LazyCapture
from src.frames import select_channel, remove_outside_petri, annotate
from src.labels import map_labels, larr2i


def parse_args(args):
    """Parse arguments"""
    parser = argparse.ArgumentParser(description="Worm tracker")
    parser.add_argument(
        "-I", "--input", help="path of the input capture", required=True
    )
    parser.add_argument(
        "-O", "--output", help="path of the output labels", required=True
    )
    parser.add_argument(
        "-A",
        "--annotation",
        help="path of the annotated output capture",
        required=False,
    )
    parser.add_argument(
        "-C", "--configuration", help="path of the custom configuration", required=False
    )

    results = parser.parse_args(args)
    return (results.input, results.output, results.annotation, results.configuration)


def preprocess_capture(capture, configuration):
    """Preprocess the input capture"""
    capture.apply(select_channel(1), shape=(capture.W(), capture.H(), 1))
    if configuration["remove_outside_petri"]["apply"]:
        capture.apply(
            remove_outside_petri(
                configuration["remove_outside_petri"]["center"],
                configuration["remove_outside_petri"]["radius"],
            )
        )
    return capture


def background_subtraction(capture, configuration):
    """Apply background subtraction to every frame"""

    def apply_background_subtraction(i, frame, acc):
        frame = acc.apply(frame[:, :, 0])
        frame = cv2.blur(frame, (5, 5))
        return frame[:, :, np.newaxis], acc

    background_subtractor = cv2.createBackgroundSubtractorMOG2(
        history=configuration["history"],
        varThreshold=configuration["varTreshold"],
        detectShadows=False,
    )
    background_subtractor.setNMixtures(configuration["NMixtures"])

    capture.apply(apply_background_subtraction, acc=background_subtractor)
    return capture


def trackpy_locate(capture, configuration):
    """Locate worm candidates in every frame"""
    locate_options = {
        "minmass": configuration["minmass"],
        "maxsize": None,
        "separation": configuration["separation"],
        "noise_size": 1,
        "smoothing_size": None,
        "threshold": 1,
        "invert": False,
        "percentile": configuration["percentile"],
        "topn": configuration["topn"],
        "preprocess": False,
        "max_iterations": 10,
        "characterize": False,
    }
    k = 0
    locations_list = []
    for i, frame in capture.frames():
        tmp_locations = tp.locate(
            frame[:, :, 0], configuration["diameter"], **locate_options
        )
        tmp_locations["frame"] = i
        locations_list.append(tmp_locations)
        if k % 100 == 0:
            print("    Located {}/{} frames".format(k, capture.length()))
        k += 1
    print("    Located {}/{} frames".format(k, capture.length()))

    locations = pd.concat(locations_list)
    return locations


def trackpy_link(locations, configuration):
    """Link candidate locations into trajectories"""
    tp.quiet()
    links = tp.link(
        locations, configuration["search_range"], memory=configuration["memory"]
    )
    return links


def find_worm(links, configuration):
    """Determine which trajectory corresponds to the worm"""
    particles = links["particle"].value_counts()
    particles = particles[particles > configuration["min_points"]]
    worm = links.merge(particles, how="inner", left_on="particle", right_index=True)
    worm = worm.sort_values(
        ["frame", "particle_y"], ascending=[True, False]
    ).drop_duplicates("frame")
    worm = worm.drop(columns=["particle_x", "particle_y"])
    worm["particle"] = 0
    return worm


def compute_labels(worm, capture):
    """Computes the labels from the worm trajectory"""
    worm = (
        worm.set_index("frame")
        .reindex(np.arange(capture.length()))
        .reset_index()
        .ffill()
    )
    labels = {
        int(row["frame"]): np.array([row["x"], row["y"]]) for _, row in worm.iterrows()
    }
    return labels


def main():
    """Main function"""
    arg_input, arg_output, arg_annotation, arg_configuration = parse_args(sys.argv[1:])
    print("Worm tracker - Starting...")
    configuration = None
    if arg_configuration is None:
        with open("default_configuration.yaml", "r") as file:
            configuration = yaml.safe_load(file)
        print("# Using default configuration")
    else:
        with open(arg_configuration, "r") as file:
            configuration = yaml.safe_load(file)
        print("# Using custom configuration")

    print()

    capture = LazyCapture.load(arg_input)
    assert (
        capture.W() == configuration["capture"]["width"]
        and capture.H() == configuration["capture"]["height"]
    )
    print("> Capture loaded: it has {} frames".format(capture.length()))

    capture = preprocess_capture(capture, configuration["preprocessing"])
    print("> Capture preprocessed.")
    capture = background_subtraction(capture, configuration["background_subtraction"])
    print("> Capture background subtracted.")

    print("> Starting trackpy location...")
    locations = trackpy_locate(capture, configuration["trackpy"]["locate"])
    print("> Trackpy location ended.")

    print("> Starting trackpy linking...")
    links = trackpy_link(locations, configuration["trackpy"]["link"])
    print("> Trackpy linking ended.")

    worm = find_worm(links, configuration["find_worm"])
    print("> Worm found.")

    labels = compute_labels(worm, capture)
    print("> Labels computed.")

    with open(arg_output, "w") as file:
        file.write("frame;x;y\n")
        file.writelines(
            ["{};{:.2f};{:.2f}\n".format(f, x, y) for f, (x, y) in labels.items()]
        )
    print("> Labels printed out.")

    if arg_annotation is not None:
        print("+ Starting annotation...")
        annotation = LazyCapture.load(arg_input)
        annotation.apply(
            annotate(map_labels(labels, lambda l: larr2i(l)), color=[0, 255, 0])
        )
        annotation.write(arg_annotation)
        print("+ Annotation printed out.")
    print("Finished.")


if __name__ == "__main__":
    main()
