import subprocess
import os
import shutil
import time
import tempfile
import argparse
import shlex

class Runner:

    def __init__(self, command, directory=None, config=None) -> None:
        """Initialize the Runner.

        Args:
            command (str): The command to run.
            directory (str): The directory where the command will run. If None, a temp directory will be used.
            config (dict): Configuration options, including log directory, artifacts, symlink preference, and verbosity.
        """
        
        self.command = command
        self.dir = directory
        self.config = config
        self.log_filename = None

        self.initialize()

    def check_and_create_dir(self, dir):
        if os.path.exists(dir):
            if not os.path.isdir(dir):
                raise ValueError(f"{dir} exists but is not a directory.")
        else:
            os.makedirs(dir)

    def log_message(self, message, color=None):
        log_dir = self.config.get("log_dir", ".")
        if log_dir is None:
            log_dir = "./logs"

        # log_filename = os.path.join(log_dir, f"run_log_{time.time()}.txt")

        with open(self.log_filename, "a") as log_file:
            log_file.write(message + "\n")

        if self.config.get("verbose", False):
            if color:
                print(f"\033[{color}m{message}\033[0m")
            else:
                print(message)

    def initialize(self):

        cwd = os.getcwd()

        log_dir = self.config.get("log_dir", cwd)
        if log_dir is None:
            log_dir = os.path.abspath(os.path.join(cwd, "work"))
        else:
            log_dir = os.path.join(cwd, log_dir)

        self.check_and_create_dir(log_dir)
        
        self.log_filename = os.path.join(log_dir, f"run_log_{time.time()}.txt")
        # with open(self.log_filename, "w") as f:
        #     f.write("")

        # If self.directory is not None, validate and create the directory.
        if self.dir:
            self.check_and_create_dir(self.dir)
        elif self.config.get("persist"):
            # Use a persistent directory (not temporary).
            self.dir = os.path.join(log_dir, f"run_workspace_{time.time()}")
            self.check_and_create_dir(self.dir)
            os.chdir(self.dir)
        else:
            # Create a temporary directory and go to this directory.
            self.dir = tempfile.mkdtemp()
            os.chdir(self.dir)

        # Symlink or copy artifacts to the specified directory.
        if self.config.get("artifacts"):
            for artifact in self.config["artifacts"]:
                source_path = os.path.abspath(os.path.join(cwd, artifact))
                dest_path = os.path.join(self.dir, os.path.basename(artifact))

                # Check if the source file or directory exists before creating the symlink
                if os.path.exists(source_path):
                    if self.config.get("symlink_to_artifacts", False):
                        os.symlink(source_path, dest_path)
                    else:
                        shutil.copy2(source_path, dest_path)
                else:
                    raise FileNotFoundError(f"Source file or directory not found: {source_path}")

        # Log the message "Workspace initiated".
        self.log_message(f"Workspace initiated at {self.dir}", color="32")  # Green color for initialization

    def run(self):
        with open(self.log_filename, "a") as f:
            f.write("")
        
        changed_files_before_run = set(os.path.join(root, file) for root, dirs, files in os.walk(self.dir) for file in files)
        changed_dirs_before_run = set(os.path.join(root, dir) for root, dirs, files in os.walk(self.dir) for dir in dirs)

        split_cmd = shlex.split(self.command)

        # Launch the command as a subprocess.
        try:
            # List all files that changed or were created compared to before running.
            with open(self.log_filename, "a") as log_file:
                subprocess.run(split_cmd, cwd=self.dir, stdout=log_file, stderr=subprocess.PIPE, check=True)
                log_file.write("Command executed successfully.\n")

        except subprocess.CalledProcessError as e:
            # If the command fails, add a copy of standard error to the main logging file.
            self.log_message(f"Command terminated with error:", color="31")  # Red color for failure
            self.log_message(f"{e.stderr.decode()}", color="31")  # Red color for error
        finally:
            changed_files_after_run = set(os.path.join(root, file) for root, dirs, files in os.walk(self.dir) for file in files)
            changed_dirs_after_run = set(os.path.join(root, dir) for root, dirs, files in os.walk(self.dir) for dir in dirs)

            # Calculate changed files and directories
            changed_files = changed_files_after_run - changed_files_before_run
            changed_dirs = changed_dirs_after_run - changed_dirs_before_run

            self.log_message("Command side effects:", color="32")
            # Log changed files and directories
            self.log_message(f"\tChanged or created files:\n\t\t{list(changed_files)}", color="36")  # Cyan color for changed files
            self.log_message(f"\tChanged or created directories:\n\t\t{list(changed_dirs)}", color="36")  # Cyan color for changed directories


def main():
    parser = argparse.ArgumentParser(description='Run a command with logging and artifact management.')
    parser.add_argument('--log-dir', type=str, help='Directory for log files')
    parser.add_argument('--artifacts', nargs='+', help='Artifacts to be symlinked or copied')
    parser.add_argument('--symlink-to-artifacts', action='store_true', help='Use symlinks instead of copying artifacts')
    parser.add_argument('--verbose', "-v", action='store_true', help='Print additional logs to the screen')
    parser.add_argument('--no-persist', dest='persist', action='store_false', help='Use a temporary workspace')
    parser.add_argument('command', nargs=argparse.REMAINDER, help='Command to run with options and arguments')

    args = parser.parse_args()
    config = {
        "log_dir": args.log_dir,
        "artifacts": args.artifacts,
        "symlink_to_artifacts": args.symlink_to_artifacts,
        "verbose": args.verbose,
        "persist": args.persist
    }

    if args.command[0] == "--": args.command = args.command[1:]
    command = ' '.join(args.command)

    runner = Runner(command, config=config)
    runner.run()

if __name__ == "__main__":
    main()