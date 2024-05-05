def distance(x2, y2):
    """
    Distance formula assuming that the correct ball placement is the origin
    Example: Correct blue ball is origin (0, 0) and the test subject placed the blue ball down two cells and right one cell
        This would make the test ball offset by (1, 2) as down and right are positive and up and left are negative
    """
    return ((x2 ** 2) + (y2 ** 2)) ** 0.5


def main():
    # Add a call to the distance function for each test ball.  If there's  an extra ball, use the next closest ball as the origin for the hallucinated ball
    distances = [distance(1, 0), distance(1, -1), distance(1, 2), distance(4, 0)]
    cumm_dist = sum(distances)
    print(f"{cumm_dist:.3f}")


if __name__ == "__main__":
    main()

