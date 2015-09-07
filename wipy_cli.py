
import argparse
import wipy


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build a wipy')
    parser.add_argument('--src', type=str)
    parser.add_argument('--dest', type=str)
    parser.add_argument('-f', '--force', type=bool, default=False)
    args = parser.parse_args()

    wipy = wipy.build(args.src, args.dest, args.force)
