import update
import print_novels_ADME
import print_novels_EC50
import repeats_duplicates


def main():
    print_novels_EC50.main()
    print_novels_ADME.main()
    repeats_duplicates.main()

    while True:
        q = input('\nHit Enter, when ready to update CDD vault>>>')
        if q == "":
            update.main()
            break
        else:
            continue


if __name__ == "__main__":
    main()
