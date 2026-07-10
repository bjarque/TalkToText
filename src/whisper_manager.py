import subprocess
import time
import requests


class WhisperServer:

    def __init__(
        self,
        whisper_path,
        model_path,
        port=8080
    ):
        self.port = port

        self.command = [
            whisper_path,
            "-m",
            model_path,
            "--port",
            str(port)
        ]

        self.process = None


    def start(self):

        print("Starting Whisper server...")

        self.process = subprocess.Popen(
            self.command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )


        for _ in range(30):

            try:
                requests.get(
                    f"http://127.0.0.1:{self.port}"
                )

                print(
                    "Whisper server ready"
                )

                return True

            except requests.exceptions.ConnectionError:

                time.sleep(1)


        raise RuntimeError(
            "Whisper server did not start"
        )


    def stop(self):

        if self.process:

            self.process.terminate()