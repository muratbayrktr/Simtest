# This code compresses log/ and results/ folder together under one archive and keeps the 
# folder structure.
from argparse import ArgumentParser
# and moves it to archive/ folder saving it with the current date and time.
# Then it deletes the log/ and results/ folders.


def archive():
    import os
    import shutil
    import datetime
    current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    # ensure archive folder exists
    if not os.path.exists('archive'):
        os.mkdir('archive')
    # create archive
    shutil.make_archive(f'archive/{current_time}_log', 'zip', 'log')
    shutil.make_archive(f'archive/{current_time}_result', 'zip', 'results')
    shutil.make_archive(f'archive/{current_time}_csv', 'zip', 'csv')
    # delete log and results folders
    shutil.rmtree('log')
    shutil.rmtree('results')
    shutil.rmtree('csv')
    # make sure log and results folders exist
    os.mkdir('log')
    os.mkdir('results')
    os.mkdir('csv')

if __name__ == "__main__":
    # Parse arguments
    parser = ArgumentParser()
    # -y flag to skip warning
    parser.add_argument('-y', action='store_true', help='Skip warning and archive')
    args = parser.parse_args()
    # If -y flag is given, then archive
    if args.y:
        archive()
        exit()
    # Ask user if they want to archive 
    # if yes, then archive
    # if no, then exit
    # Use red color to emphasize warning
    print("\033[91m" + "WARNING: This will delete the log/, csv/ and results/ folders and archive them together under one zip file." + "\033[0m")
    print("Do you want to continue? (y/n)")
    answer = input()
    if answer.lower() == 'y':
        archive()
    else:
        exit()