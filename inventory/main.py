import inventory
import request
import api
import multiprocessing as mp


# import ray


def main():

    while True:
        inventory.main(request.main())


if __name__ == "__main__":
    main()
